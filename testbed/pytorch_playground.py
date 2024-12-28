import torch
from torch import nn

# Define the LSTM model
lstm = nn.LSTM(input_size=1, hidden_size=50, num_layers=1, batch_first=True)

# Generate some random test data (batch_size=5, seq_len=10, input_size=1)
x_test = torch.randn(5, 10, 1)

# Forward pass through the LSTM
output, (h_n, c_n) = lstm(x_test)

# Print the shapes of the outputs
print("Output shape:", output.shape)  # (5, 10, 50)
print("h_n shape:", h_n.shape)  # (1, 5, 50)
print("h_n[-1] shape", h_n[-1].shape)
print("c_n shape:", c_n.shape)  # (1, 5, 50)


class AirModel(nn.Module):

    def __init__(self):
        super().__init__()
        self.lstm = nn.LSTM(input_size=1, hidden_size=50, num_layers=5, batch_first=True)
        self.linear1 = nn.Linear(50, 10)
        self.linear2 = nn.Linear(10, 1)

    def forward(self, x):
        output, (h_n, c_n) = self.lstm(x)
        x = self.linear1(h_n[-1])
        x = self.linear2(x)
        return x


# Hyperparameters
batch_size = 5  # Number of sequences in a batch
seq_len = 10  # Length of each sequence (number of time steps)
input_size = 1  # Number of features per time step (in your case, it's 1)

# Generate random test data: Shape = (batch_size, seq_len, input_size)
x_test = torch.randn(batch_size, seq_len, input_size)

# Create an instance of the model
model = AirModel()

# Test the model with the generated data
output = model(x_test)

# Print the output shape to verify
print("Output shape:", output.shape)
