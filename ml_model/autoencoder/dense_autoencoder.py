import torch.nn.functional as F
from torch import nn


class DenseAutoencoder(nn.Module):

    def __init__(self, input_size, min_size, shrink_factor):
        super(DenseAutoencoder, self).__init__()

        self.encoder = nn.ModuleList()
        current_size = input_size
        while current_size > min_size:
            out_size = max(min_size, current_size // shrink_factor)
            self.encoder.append(nn.Linear(current_size, out_size))
            current_size = out_size

        self.decoder = nn.ModuleList()
        while current_size < input_size:
            out_size = min(input_size, current_size * shrink_factor)
            self.decoder.append(nn.Linear(current_size, out_size))
            current_size = out_size

        self.out_layer = nn.Linear(current_size, input_size)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        # Forward pass through encoder
        for layer in self.encoder:
            x = F.relu(layer(x))

        # Forward pass through decoder
        for layer in self.decoder:
            x = F.relu(layer(x))

        x = self.sigmoid(self.out_layer(x))
        return x
