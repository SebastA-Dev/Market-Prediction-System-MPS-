"""
Pipeline de entrenamiento y arquitectura para MASTER (Market-Guided Stock Transformer).
MASTER modela la correlación inter-sectorial y cross-asset condicionada por variables macroeconómicas.
Genera la proyección de tendencia multi-activo y score de correlación.
Cumple con RF-07 y HU-1.3.
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
import logging

logger = logging.getLogger(__name__)
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset


class MarketGuidedAttention(nn.Module):
    """
    Capa de atención guiada por el mercado.
    Pondera las características del activo individual con el vector de contexto sectorial/macro.
    """

    def __init__(self, d_model: int):
        super().__init__()
        self.query = nn.Linear(d_model, d_model)
        self.key = nn.Linear(d_model, d_model)
        self.value = nn.Linear(d_model, d_model)
        self.scale = np.sqrt(d_model)

    def forward(self, asset_feat: torch.Tensor, market_context: torch.Tensor) -> torch.Tensor:
        # asset_feat: [batch, d_model], market_context: [batch, d_model]
        q = self.query(asset_feat).unsqueeze(1)
        k = self.key(market_context).unsqueeze(1)
        v = self.value(market_context).unsqueeze(1)

        scores = torch.bmm(q, k.transpose(1, 2)) / self.scale
        attn = torch.softmax(scores, dim=-1)
        context = torch.bmm(attn, v).squeeze(1)
        return asset_feat + context


class PyTorchMASTER(nn.Module):
    """
    Arquitectura MASTER adaptada para el pipeline MPS.
    Salidas:
    - Logits de tendencia (BULLISH, BEARISH, NEUTRAL).
    - Representación latente de correlación inter-sectorial.
    """

    def __init__(self, num_factors: int = 15, d_model: int = 64, num_classes: int = 3):
        super().__init__()
        self.factor_proj = nn.Linear(num_factors, d_model)
        self.market_proj = nn.Linear(num_factors, d_model)
        self.market_guided_attn = MarketGuidedAttention(d_model)

        self.classifier = nn.Sequential(
            nn.Linear(d_model, 64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, num_classes),
        )

    def forward(self, factors: torch.Tensor, market_ctx: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        f_emb = torch.relu(self.factor_proj(factors))
        m_emb = torch.relu(self.market_proj(market_ctx))
        guided = self.market_guided_attn(f_emb, m_emb)
        logits = self.classifier(guided)
        return logits, guided


class MASTERTrainer:
    """
    Entrenador del modelo MASTER con soporte para Alpha Factors y contexto de mercado.
    """

    def __init__(self, checkpoints_dir: Path):
        self.checkpoints_dir = Path(checkpoints_dir)
        self.checkpoints_dir.mkdir(parents=True, exist_ok=True)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    def train(
        self,
        X_factors: np.ndarray,
        X_market: np.ndarray,
        Y_labels: np.ndarray,
        epochs: int = 20,
        batch_size: int = 32,
        lr: float = 0.001,
    ) -> Optional[Path]:
        """
        Entrena el modelo MASTER sobre factores técnicos y contexto de mercado.
        Labels: 0 = BEARISH, 1 = NEUTRAL, 2 = BULLISH.
        """
        try:
            dataset = TensorDataset(
                torch.from_numpy(X_factors.astype(np.float32)),
                torch.from_numpy(X_market.astype(np.float32)),
                torch.from_numpy(Y_labels.astype(np.int64)),
            )
            loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

            num_factors = X_factors.shape[1]
            model = PyTorchMASTER(num_factors=num_factors).to(self.device)
            criterion = nn.CrossEntropyLoss()
            optimizer = torch.optim.Adam(model.parameters(), lr=lr)

            checkpoint_path = self.checkpoints_dir / "master_global.pt"

            for epoch in range(epochs):
                model.train()
                total_loss = 0.0
                for f_batch, m_batch, y_batch in loader:
                    f_batch = f_batch.to(self.device)
                    m_batch = m_batch.to(self.device)
                    y_batch = y_batch.to(self.device)

                    optimizer.zero_grad()
                    logits, _ = model(f_batch, m_batch)
                    loss = criterion(logits, y_batch)
                    loss.backward()
                    optimizer.step()
                    total_loss += loss.item()

            torch.save(model.state_dict(), str(checkpoint_path))
            logger.info(f"[MASTERTrainer] Modelo MASTER guardado exitosamente en {checkpoint_path}")
            return checkpoint_path
        except Exception as e:
            logger.error(f"[MASTERTrainer] Error entrenando MASTER: {e}")
            return None
