"""
Pipeline de generación y entrenamiento de Alpha Factors mediante Qlib.
Calcula un conjunto representativo de factores alfa (Momentum, Volatilidad, Reversión a la media, RSI, MACD)
y entrena un modelo predictivo tabular para alimentar las inferencias.
Cumple con RF-05 y HU-1.2.
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class AlphaFactorEngine:
    """
    Calcula factores cuantitativos sobre series de tiempo OHLCV limpias.
    Inspirado en la especificación Alpha158 de Qlib.
    """

    @classmethod
    def compute_factors(cls, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula un vector de Alpha Factors sobre un DataFrame con columnas:
        [Date, Open, High, Low, Close, Volume]
        """
        df_out = pd.DataFrame(index=df.index)
        close = df["Close"]
        high = df["High"]
        low = df["Low"]
        open_p = df["Open"]
        volume = df["Volume"]

        # 1. Factores de Retorno y Momentum
        df_out["return_1d"] = close.pct_change(1)
        df_out["return_5d"] = close.pct_change(5)
        df_out["return_10d"] = close.pct_change(10)
        df_out["return_20d"] = close.pct_change(20)

        # 2. Medias Móviles y Distancia (Mean Reversion)
        ma5 = close.rolling(5).mean()
        ma20 = close.rolling(20).mean()
        ma60 = close.rolling(60).mean()
        df_out["ma_ratio_5_20"] = (ma5 / (ma20 + 1e-8)) - 1.0
        df_out["dist_ma20"] = (close / (ma20 + 1e-8)) - 1.0
        df_out["dist_ma60"] = (close / (ma60 + 1e-8)) - 1.0

        # 3. Volatilidad Histórica
        df_out["volatility_5d"] = close.pct_change().rolling(5).std()
        df_out["volatility_20d"] = close.pct_change().rolling(20).std()

        # 4. Rango Verdadero Promedio (ATR proxy)
        tr = np.maximum(high - low, np.maximum(abs(high - close.shift(1)), abs(low - close.shift(1))))
        df_out["atr_14"] = tr.rolling(14).mean() / (close + 1e-8)

        # 5. RSI proxy (14 periodos)
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / (loss + 1e-8)
        df_out["rsi_14"] = 100 - (100 / (1 + rs))

        # 6. Dinámica de Volumen
        vol_ma5 = volume.rolling(5).mean()
        vol_ma20 = volume.rolling(20).mean()
        df_out["vol_ratio_5_20"] = (vol_ma5 / (vol_ma20 + 1e-8)) - 1.0

        # 7. Posición Intradía
        df_out["intraday_range"] = (high - low) / (open_p + 1e-8)
        df_out["close_pos"] = (close - low) / (high - low + 1e-8)

        return df_out.ffill().bfill().fillna(0.0)


class QlibAlphaTrainer:
    """
    Entrenador de modelos sobre Alpha Factors calculados.
    """

    def __init__(self, checkpoints_dir: Path):
        self.checkpoints_dir = Path(checkpoints_dir)
        self.checkpoints_dir.mkdir(parents=True, exist_ok=True)

    def extract_and_align(self, df_clean: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """
        Extrae la matriz de factores X y el objetivo Y (retorno futuro a 5 días).
        """
        factors_df = AlphaFactorEngine.compute_factors(df_clean)
        target = df_clean["Close"].pct_change(5).shift(-5)

        valid_mask = ~target.isna()
        X = factors_df[valid_mask].values
        Y = target[valid_mask].values
        feature_names = list(factors_df.columns)
        return X, Y, feature_names
