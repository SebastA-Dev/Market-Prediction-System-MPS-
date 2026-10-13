"""
Pipeline de entrenamiento y ajuste fino para Galformer.
Galformer: Transformer con decodificación generativa y función de pérdida híbrida
(Hybrid Loss: MSE + penalización por error de dirección de tendencia) para predicción multi-step.
Cumple con RF-08 y HU-1.4.
"""

from pathlib import Path
from typing import Dict, Optional, Tuple
import numpy as np
import pandas as pd
import logging

logger = logging.getLogger(__name__)
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset


class PyTorchGalformer(nn.Module):
    """
    Arquitectura Galformer optimizada en PyTorch para inferencia y entrenamiento ágil.
    Incorpora Encoder Transformer multi-cabeza y decodificador generativo para series de tiempo.
    """

    def __init__(
        self,
        input_dim: int = 1,
        d_model: int = 64,
        nhead: int = 4,
        num_layers: int = 3,
        dim_feedforward: int = 256,
        dropout: float = 0.1,
        horizon: int = 5,
    ):
        super().__init__()
        self.horizon = horizon
        self.input_proj = nn.Linear(input_dim, d_model)
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=dim_feedforward,
            dropout=dropout,
            batch_first=True,
        )
        self.transformer_encoder = nn.TransformerEncoder(
            encoder_layer, num_layers=num_layers
        )
        self.fc_out = nn.Sequential(
            nn.Linear(d_model, 64),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(64, horizon),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: [batch, seq_len, input_dim]
        proj = self.input_proj(x)
        encoded = self.transformer_encoder(proj)
        # Pooling sobre la dimensión temporal (último estado o media)
        last_state = encoded[:, -1, :]
        out = self.fc_out(last_state)
        return out


class HybridLoss(nn.Module):
    """
    Función de pérdida híbrida de Galformer:
    Combina el error cuadrático medio (MSE) con la precisión direccional (Up/Down Trend accuracy).
    Loss = MSE + lambda_dir * (1 - DirectionalAccuracy)
    """

    def __init__(self, lambda_dir: float = 0.5):
        super().__init__()
        self.mse = nn.MSELoss()
        self.lambda_dir = lambda_dir

    def forward(self, pred: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        mse_loss = self.mse(pred, target)
        # Signos del cambio proyectado
        pred_sign = torch.sign(pred)
        target_sign = torch.sign(target)
        directional_acc = torch.mean((pred_sign == target_sign).float())
        dir_loss = 1.0 - directional_acc
        return mse_loss + self.lambda_dir * dir_loss


class GalformerTrainer:
    """
    Entrenador de series de tiempo para Galformer.
    Gestiona la preparación de ventanas deslizantes, normalización y guardado de pesos.
    """

    def __init__(self, checkpoints_dir: Path):
        self.checkpoints_dir = Path(checkpoints_dir)
        self.checkpoints_dir.mkdir(parents=True, exist_ok=True)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    def prepare_sliding_windows(
        self,
        prices: np.ndarray,
        window_size: int = 20,
        horizon: int = 5,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Genera secuencias X (precios pasados) e Y (retornos futuros multi-step).
        """
        # Calcular retornos relativos para estacionariedad
        returns = np.diff(prices) / (prices[:-1] + 1e-8)
        X, Y = [], []
        for i in range(len(returns) - window_size - horizon + 1):
            x_seq = returns[i : i + window_size]
            y_seq = returns[i + window_size : i + window_size + horizon]
            X.append(x_seq.reshape(-1, 1))
            Y.append(y_seq)
        return np.array(X, dtype=np.float32), np.array(Y, dtype=np.float32)

    def train(
        self,
        ticker: str,
        df_clean: pd.DataFrame,
        epochs: int = 15,
        batch_size: int = 32,
        lr: float = 0.001,
        window_size: int = 20,
        horizon: int = 5,
    ) -> Optional[Path]:
        """
        Ejecuta el ciclo de entrenamiento para un activo dado y guarda el checkpoint.
        """
        try:
            prices = df_clean["Adj Close"].values
            if len(prices) < window_size + horizon + 10:
                logger.warning(
                    f"[GalformerTrainer] Datos insuficientes para entrenar {ticker}"
                )
                return None

            X, Y = self.prepare_sliding_windows(prices, window_size, horizon)
            split_idx = int(len(X) * 0.8)
            X_train, Y_train = X[:split_idx], Y[:split_idx]
            X_val, Y_val = X[split_idx:], Y[split_idx:]

            train_dataset = TensorDataset(
                torch.from_numpy(X_train), torch.from_numpy(Y_train)
            )
            val_dataset = TensorDataset(
                torch.from_numpy(X_val), torch.from_numpy(Y_val)
            )

            train_loader = DataLoader(
                train_dataset, batch_size=batch_size, shuffle=True
            )
            val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)

            model = PyTorchGalformer(input_dim=1, horizon=horizon).to(self.device)
            criterion = HybridLoss(lambda_dir=0.3)
            optimizer = torch.optim.Adam(model.parameters(), lr=lr)

            best_val_loss = float("inf")
            checkpoint_path = self.checkpoints_dir / f"galformer_{ticker.lower()}.pt"

            for _ in range(epochs):
                model.train()
                # train_loss = 0.0
                for batch_x, batch_y in train_loader:
                    batch_x, batch_y = batch_x.to(self.device), batch_y.to(self.device)
                    optimizer.zero_grad()
                    out = model(batch_x)
                    loss = criterion(out, batch_y)
                    loss.backward()
                    optimizer.step()
                    # train_loss += loss.item()

                model.eval()
                val_loss = 0.0
                with torch.no_grad():
                    for batch_x, batch_y in val_loader:
                        batch_x, batch_y = batch_x.to(self.device), batch_y.to(
                            self.device
                        )
                        out = model(batch_x)
                        val_loss += criterion(out, batch_y).item()

                val_loss /= max(len(val_loader), 1)
                if val_loss < best_val_loss:
                    best_val_loss = val_loss
                    torch.save(model.state_dict(), str(checkpoint_path))

            logger.info(
                f"[GalformerTrainer] Entrenamiento finalizado para {ticker}. Checkpoint: {checkpoint_path}"
            )
            return checkpoint_path
        except Exception as e:
            logger.error(
                f"[GalformerTrainer] Error entrenando Galformer para {ticker}: {e}"
            )
            return None
