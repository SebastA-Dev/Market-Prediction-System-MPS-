"""
Módulo de limpieza, saneamiento y validación de datos de mercado.
Asegura la calidad estadística y consistencia requerida por los requerimientos:
- RF-06: Mínimo 30 observaciones históricas.
- RF-12 & RNF-11: Detección de varianza cero y división por cero.
- Estandarización de columnas OHLCV para Qlib y Galformer.
"""

from typing import Tuple
import numpy as np
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class DataCleaningService:
    """
    Realiza saneamiento, validación estadística y formateo de series financieras.
    """

    MIN_REQUIRED_OBSERVATIONS = 30

    @classmethod
    def clean_ohlcv_dataframe(
        cls,
        df: pd.DataFrame,
        ticker: str = "ASSET",
    ) -> Tuple[bool, pd.DataFrame, str]:
        """
        Limpia y valida un DataFrame OHLCV crudo.

        Retorna:
            (es_valido, df_limpio, mensaje)
        """
        if df is None or df.empty:
            return False, pd.DataFrame(), f"[{ticker}] DataFrame vacío o nulo."

        # 1. Normalizar nombres de columnas a minúsculas o estándar
        df_clean = df.copy()
        col_map = {col: col.strip().title() for col in df_clean.columns}
        df_clean = df_clean.rename(columns=col_map)

        # Mapeo de variantes comunes
        rename_dict = {}
        for col in df_clean.columns:
            lower = col.lower()
            if "date" in lower or "timestamp" in lower or "time" in lower:
                rename_dict[col] = "Date"
            elif lower == "open":
                rename_dict[col] = "Open"
            elif lower == "high":
                rename_dict[col] = "High"
            elif lower == "low":
                rename_dict[col] = "Low"
            elif lower == "close":
                rename_dict[col] = "Close"
            elif "adj" in lower:
                rename_dict[col] = "Adj Close"
            elif lower == "volume" or lower == "vol":
                rename_dict[col] = "Volume"
        df_clean = df_clean.rename(columns=rename_dict)

        required_cols = ["Date", "Open", "High", "Low", "Close", "Volume"]
        missing = [col for col in required_cols if col not in df_clean.columns]
        if missing:
            return (
                False,
                pd.DataFrame(),
                f"[{ticker}] Faltan columnas esenciales: {missing}",
            )

        if "Adj Close" not in df_clean.columns:
            df_clean["Adj Close"] = df_clean["Close"]

        # 2. Conversión de tipos
        df_clean["Date"] = pd.to_datetime(df_clean["Date"], errors="coerce")
        for col in ["Open", "High", "Low", "Close", "Adj Close", "Volume"]:
            df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce")

        # 3. Eliminar fechas nulas y ordenar
        df_clean = (
            df_clean.dropna(subset=["Date"])
            .sort_values("Date")
            .drop_duplicates(subset=["Date"])
        )
        df_clean = df_clean.reset_index(drop=True)

        # 4. Verificación RF-06: Mínimo 30 observaciones históricas
        if len(df_clean) < cls.MIN_REQUIRED_OBSERVATIONS:
            return (
                False,
                df_clean,
                f"[{ticker}] Datos insuficientes: posee {len(df_clean)} observaciones (mínimo requerido: {cls.MIN_REQUIRED_OBSERVATIONS}).",
            )

        # 5. Tratamiento de NaNs en valores numéricos (forward-fill y luego backward-fill)
        numeric_cols = ["Open", "High", "Low", "Close", "Adj Close", "Volume"]
        df_clean[numeric_cols] = df_clean[numeric_cols].ffill().bfill()

        # Si aún quedan NaNs, descartar
        df_clean = df_clean.dropna(subset=numeric_cols).reset_index(drop=True)

        # 6. Verificación RF-12 & RNF-11: Desviación estándar igual a cero
        close_std = df_clean["Close"].std()
        if pd.isna(close_std) or close_std == 0:
            return (
                False,
                df_clean,
                f"[{ticker}] Desviación estándar nula (precio plano). Inhibición estadística aplicada.",
            )

        # 7. Consistencia física de velas (High debe ser max, Low debe ser min)
        df_clean["High"] = df_clean[["Open", "High", "Close"]].max(axis=1)
        df_clean["Low"] = df_clean[["Open", "Low", "Close"]].min(axis=1)
        df_clean["Volume"] = df_clean["Volume"].clip(lower=0)

        # 8. Calcular retornos y factor de ajuste (para compatibilidad Qlib)
        df_clean["factor"] = df_clean["Adj Close"] / df_clean["Close"].replace(
            0, np.nan
        )
        df_clean["factor"] = df_clean["factor"].fillna(1.0)
        df_clean["returns"] = df_clean["Adj Close"].pct_change().fillna(0.0)

        logger.info(
            f"[{ticker}] Limpieza completada exitosamente: {len(df_clean)} observaciones válidas."
        )
        return True, df_clean, "OK"

    @classmethod
    def format_for_qlib(cls, df: pd.DataFrame) -> pd.DataFrame:
        """
        Formatea el DataFrame al esquema canónico requerido por el dump binario de Qlib:
        columnas en minúscula: date, open, close, high, low, volume, factor
        """
        df_qlib = pd.DataFrame(
            {
                "date": pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%d"),
                "open": df["Open"].astype(float),
                "close": df["Close"].astype(float),
                "high": df["High"].astype(float),
                "low": df["Low"].astype(float),
                "volume": df["Volume"].astype(float),
                "factor": df["factor"].astype(float) if "factor" in df.columns else 1.0,
            }
        )
        return df_qlib.sort_values("date").reset_index(drop=True)

    @classmethod
    def format_for_galformer(cls, df: pd.DataFrame) -> pd.DataFrame:
        """
        Formatea el DataFrame al esquema esperado por Galformer:
        Date, Open, High, Low, Close, Adj Close, Volume
        """
        cols = ["Date", "Open", "High", "Low", "Close", "Adj Close", "Volume"]
        return df[cols].copy()
