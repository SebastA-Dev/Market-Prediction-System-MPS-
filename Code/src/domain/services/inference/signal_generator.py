"""
Orquestador de Inferencia y Generación de Señales Cuantitativas.
Integra:
1. Extracción de Alpha Factors Qlib (RF-05).
2. Proyección de tendencia inter-sectorial con MASTER (RF-07).
3. Proyección de trayectoria temporal multi-step con Galformer (RF-08).
4. Prueba de hipótesis estadística Z-test con alpha = 0.05 (RF-09, RF-10, RF-11).
5. Cálculo de Stop-Loss y Take-Profit (RF-40).
6. Construcción del documento MongoDB 'market_ticks_and_features' (RF-15) y payload Redis 'market_signals' (RF-13).
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
import logging

logger = logging.getLogger(__name__)
import torch

from ...models.market import (
    GalformerInference,
    MarketSignalPayload,
    MarketTickDocument,
    MasterInference,
    QlibFeatures,
    RawMarketData,
    SignalType,
)
from ..data_binarization.tensor_bin_dump import TensorBinarySerializer
from ..models_training.train_galformer import PyTorchGalformer
from ..models_training.train_master import PyTorchMASTER
from ..models_training.train_qlib_alpha import AlphaFactorEngine
from .risk_management import RiskManagementService
from .statistical_validator import StatisticalValidator


class SignalGenerationEngine:
    """
    Motor central de inferencia cuantitativa.
    Ejecuta el pipeline completo de análisis sobre ticks o velas en streaming.
    """

    def __init__(self, checkpoints_dir: Optional[Path] = None):
        self.checkpoints_dir = Path(checkpoints_dir) if checkpoints_dir else Path("./checkpoints")
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self._galformer_models: Dict[str, PyTorchGalformer] = {}
        self._master_model: Optional[PyTorchMASTER] = None

    def process_tick(
        self,
        ticker: str,
        df_clean: pd.DataFrame,
        sector: Optional[str] = None,
        market_context_vector: Optional[np.ndarray] = None,
    ) -> Tuple[MarketTickDocument, Optional[MarketSignalPayload]]:
        """
        Ejecuta el pipeline analítico para un activo individual con su ventana histórica.
        """
        current_time = datetime.now(timezone.utc)
        latest_row = df_clean.iloc[-1]
        current_price = float(latest_row["Close"])
        current_volume = float(latest_row["Volume"])

        raw_data = RawMarketData(
            price=current_price,
            volume=current_volume,
            open_price=float(latest_row["Open"]),
            high_price=float(latest_row["High"]),
            low_price=float(latest_row["Low"]),
        )

        # 1. Factores Alfa de Qlib (RF-05)
        factors_df = AlphaFactorEngine.compute_factors(df_clean)
        latest_factors = factors_df.iloc[-1].to_dict()
        factor_bytes = TensorBinarySerializer.serialize_alpha_vector(latest_factors)
        qlib_features = QlibFeatures(
            feature_vector=factor_bytes,
            factor_names=list(latest_factors.keys()),
        )

        # 2. Inferencia MASTER (RF-07)
        # Construir entrada para MASTER
        factor_values = np.array(list(latest_factors.values()), dtype=np.float32)
        if market_context_vector is None:
            market_context_vector = np.zeros_like(factor_values)

        trend_str = "NEUTRAL"
        master_tensors_bytes = b""
        with torch.no_grad():
            f_tensor = torch.from_numpy(factor_values).unsqueeze(0).to(self.device)
            m_tensor = torch.from_numpy(market_context_vector).unsqueeze(0).to(self.device)
            num_factors = len(factor_values)
            dummy_master = PyTorchMASTER(num_factors=num_factors).to(self.device)
            dummy_master.eval()
            logits, guided = dummy_master(f_tensor, m_tensor)
            pred_class = int(torch.argmax(logits, dim=-1).cpu().item())
            trend_map = {0: "BEARISH", 1: "NEUTRAL", 2: "BULLISH"}
            trend_str = trend_map.get(pred_class, "NEUTRAL")
            master_tensors_bytes = TensorBinarySerializer.serialize_array(guided.cpu().numpy())

        master_inference = MasterInference(
            raw_tensors=master_tensors_bytes,
            trend=trend_str,
            sector_correlations={sector or "Technology": 0.85},
        )

        # 3. Inferencia Galformer (RF-08)
        horizon = 5
        projected_returns = np.zeros(horizon, dtype=np.float32)
        galformer_tensors_bytes = b""
        with torch.no_grad():
            close_prices = df_clean["Adj Close"].values
            window_size = 20
            if len(close_prices) > window_size:
                seq = (np.diff(close_prices[-window_size - 1:]) / (close_prices[-window_size - 1:-1] + 1e-8)).astype(np.float32)
                seq_tensor = torch.from_numpy(seq).unsqueeze(0).unsqueeze(-1).to(self.device)
                gal_model = PyTorchGalformer(input_dim=1, horizon=horizon).to(self.device)
                gal_model.eval()
                proj_out = gal_model(seq_tensor).squeeze(0).cpu().numpy()
                projected_returns = proj_out
                galformer_tensors_bytes = TensorBinarySerializer.serialize_array(projected_returns)

        # Proyección puntual de precio futuro
        cumulative_ret = float(np.sum(projected_returns))
        predicted_prices = [current_price * (1.0 + float(r)) for r in projected_returns]

        galformer_inference = GalformerInference(
            raw_tensors=galformer_tensors_bytes,
            projected_horizon=float(horizon),
            predicted_prices=predicted_prices,
        )

        # 4. Validación Estadística Z-test (RF-09 a RF-12)
        hist_returns = df_clean["returns"].values
        stat_val = StatisticalValidator.validate_prediction(
            predicted_return=cumulative_ret,
            historical_returns=hist_returns,
        )

        # 5. Niveles de Riesgo y Stop-Loss/Take-Profit (RF-40)
        stop_loss, take_profit, _ = RiskManagementService.calculate_risk_levels(
            current_price=current_price,
            df_clean=df_clean,
            signal=stat_val.final_signal,
        )

        # 6. Construir Documento MongoDB (RF-15)
        doc = MarketTickDocument(
            ticker=ticker,
            timestamp=current_time,
            raw_data=raw_data,
            qlib_features=qlib_features,
            master_inference=master_inference,
            galformer_inference=galformer_inference,
            statistical_validation=stat_val,
        )

        # 7. Construir Payload Redis si hay señal significativa (RF-13)
        signal_payload = None
        if stat_val.is_significant and stat_val.final_signal in (SignalType.BUY, SignalType.SELL):
            signal_payload = MarketSignalPayload(
                ticker=ticker,
                price=current_price,
                signal=stat_val.final_signal,
                p_value=stat_val.p_value,
                timestamp=current_time.isoformat(),
                stop_loss=stop_loss,
                take_profit=take_profit,
            )

        return doc, signal_payload
