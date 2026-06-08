"""Transformer model implementation."""
import torch
import torch.nn as nn

class TransformerModel(nn.Module):
    def __init__(self, d_model=512, nhead=8, num_layers=6):
        super().__init__()
        self.encoder = nn.TransformerEncoder(
            nn.TransformerEncoderLayer(d_model, nhead),
            num_layers
        )

    def forward(self, src):
        return self.encoder(src)
