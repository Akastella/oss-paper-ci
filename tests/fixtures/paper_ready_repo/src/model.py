"""Model definition."""
import torch.nn as nn

class ScienceModel(nn.Module):
    def __init__(self, input_size=10, hidden_size=128):
        super().__init__()
        self.fc = nn.Linear(input_size, hidden_size)
