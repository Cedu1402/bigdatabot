import logging
from typing import List, Dict, Tuple, Optional

import pandas as pd
import torch
import torch.nn.functional as F
from sklearn.preprocessing import MinMaxScaler
from torch import nn, optim
from torch.utils.data import TensorDataset, DataLoader

from constants import PRICE_PCT_CHANGE, PERCENTAGE_OF_1_MILLION_MARKET_CAP, TOTAL_VOLUME_PCT_CHANGE
from data.data_split import flatten_dataframe_list, get_x_y_of_list
from data.feature_engineering import normalize_columns, one_hot_encode_trader_columns
from data.model_data import remove_columns, order_columns
from data.sliding_window import unroll_data, get_sizes_from_data, roll_back_data
from ml_model.base_model import BaseModel
from ml_model.load_model import load_model
from ml_model.model_evaluation import print_evaluation

logger = logging.getLogger(__name__)


class LSTMBaseModel(nn.Module):

    def __init__(self, input_size, hidden_size, output_size, num_layers=5):
        super(LSTMBaseModel, self).__init__()

        # LSTM layer
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)

        # Fully connected layer for output
        self.fc0 = nn.Linear(hidden_size, int(hidden_size / 2))
        self.fc1 = nn.Linear(int(hidden_size / 2), int(hidden_size / 4))
        self.fc2 = nn.Linear(int(hidden_size / 4), output_size)

        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        # Forward pass through LSTM
        lstm_out, (hn, cn) = self.lstm(x)

        # Use the output of the last LSTM timestep (last hidden state)
        last_hidden_state = hn[-1]

        # Pass through fully connected layer
        x = F.relu(self.fc0(last_hidden_state))  # Apply ReLU here
        x = F.relu(self.fc1(x))  # Apply ReLU here

        x = self.fc2(x)  # Final layer (no ReLU if output is logits)
        out = self.sigmoid(x)  # Sigmoid for binary classification

        return out


def convert_to_tensor(data: List[pd.DataFrame]) -> torch.Tensor:
    """
    Convert list of DataFrames into a 3D tensor for LSTM.
    Each sequence will be a 2D tensor with shape (seq_len, input_size).
    """
    # Assuming the data is already in the correct sequence format.
    # Convert each DataFrame to a 2D tensor and stack them into a 3D tensor (batch_size, seq_len, input_size)
    tensor_data = torch.tensor([df.values for df in data], dtype=torch.float32)
    return tensor_data


class LSTMModel(BaseModel):

    def __init__(self, config: Dict):
        super().__init__(config)
        self.columns = list()
        self.config = config
        self.model = None
        self.scaler = None
        self.normalized_columns = [PRICE_PCT_CHANGE, TOTAL_VOLUME_PCT_CHANGE,
                                   PERCENTAGE_OF_1_MILLION_MARKET_CAP]

    def get_columns(self):
        return self.columns

    def build_model(self):
        self.model = LSTMBaseModel(self.config.get("columns", 1), self.config.get("hidden_size", 10), 1, 1)

    def pre_process_dataset(self, df: List[pd.DataFrame], train_set: bool, scaler: Optional[MinMaxScaler]) -> Tuple[
        List[pd.DataFrame], list, Optional[MinMaxScaler]]:
        logger.info("Remove unused columns from data")
        df = remove_columns(df, self.non_training_columns)
        logger.info("Unroll data")
        full_df = unroll_data(df)
        logger.info("Get sizes of data")
        df_sizes = get_sizes_from_data(df)
        logger.info("Normalize data")
        full_df, fit_scaler = normalize_columns(full_df, self.normalized_columns, train_set, scaler, True)
        # logger.info("One hot encode data")
        # full_df = one_hot_encode_trader_columns(full_df)
        logger.info("Rollback data")
        df = roll_back_data(full_df, df_sizes)
        logger.info("Split data into x and y sets")
        x_df, y_df = get_x_y_of_list(df)

        if train_set:
            logger.info("Extract column order for inference")
            self.columns = list(df[0].columns)

        return x_df, y_df, fit_scaler

    def prepare_train_data(self, train: List[pd.DataFrame], val: List[pd.DataFrame], test: List[pd.DataFrame]) -> (
            Tuple)[List[pd.DataFrame], List, List[pd.DataFrame], List, List[pd.DataFrame], List]:

        train_x, train_y, scaler = self.pre_process_dataset(train, True, None)
        self.scaler = scaler

        val_x, val_y, _ = self.pre_process_dataset(val, False, scaler)
        test_x, test_y, _ = self.pre_process_dataset(test, False, scaler)

        return train_x, train_y, val_x, val_y, test_x, test_y

    def prepare_prediction_data(self, data: List[pd.DataFrame], contains_label: bool) -> Tuple[
        List[pd.DataFrame], Optional[List]]:
        raise Exception("Not implemented")

    def train(self, train_x: List[pd.DataFrame], train_y: List, val_x: List[pd.DataFrame], val_y: List):
        # Flatten data and convert to tensors
        logger.info(f"Dataset to tensor {len(train_x)}")
        train_x_tensor = convert_to_tensor(train_x)
        train_y_tensor = torch.tensor(train_y, dtype=torch.float32).view(-1, 1)

        val_x_tensor = convert_to_tensor(val_x)
        val_y_tensor = torch.tensor(val_y, dtype=torch.float32).view(-1, 1)

        # Create DataLoader for batching
        train_dataset = TensorDataset(train_x_tensor, train_y_tensor)
        val_dataset = TensorDataset(val_x_tensor, val_y_tensor)

        train_loader = DataLoader(train_dataset, batch_size=self.config.get('batch_size', 32), shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=self.config.get('batch_size', 32), shuffle=False)

        optimizer = optim.Adam(self.model.parameters(), lr=0.001)
        loss_fn = nn.BCELoss()
        epochs = self.config.get('epochs', 10)
        # Training loop
        for epoch in range(1, epochs + 1):
            self.model.train()  # Set the model to training mode
            epoch_loss = 0.0
            for batch_x, batch_y in train_loader:
                # Forward pass
                output = self.model(batch_x)

                # Compute loss
                loss = loss_fn(output, batch_y)
                epoch_loss += loss.item()

                # Zero gradients, backpropagate, optimize
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

            logger.info(f"Epoch {epoch}/{epochs}, Loss: {epoch_loss / len(train_loader)}")

            # Validation loop
            self.model.eval()  # Set the model to evaluation mode
            val_predictions = []
            val_labels = []
            with torch.no_grad():  # No need to compute gradients during validation
                for batch_x, batch_y in val_loader:
                    output = self.model(batch_x)
                    val_predictions.append(output)
                    val_labels.append(batch_y)

            val_predictions = torch.cat(val_predictions, dim=0)
            val_labels = torch.cat(val_labels, dim=0)

            # Compute and print evaluation metrics (e.g., MSE, Accuracy)
            val_loss = loss_fn(val_predictions, val_labels)
            logger.info(f"Validation Loss: {val_loss.item()}")

            # Convert predictions to binary (0 or 1)
            val_predictions_binary = (val_predictions > 0.5).int().numpy()

            # Print evaluation metrics
            print_evaluation(val_labels.numpy(), val_predictions_binary)

    def save(self):
        # save_to_pickle((self.model, self.bin_edges, self.columns), os.path.join(MODEL_FOLDER, "simple_tree.pkl"))
        pass

    def load_model(self, name):
        self.model, self.bin_edges, self.columns = load_model(name)

    def predict(self, data):
        data = flatten_dataframe_list(data)
        return self.model.predict(data)
