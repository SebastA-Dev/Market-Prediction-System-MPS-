"""
Servicio de conversión y volcado de datos a formato binario nativo de Microsoft Qlib.
Genera la jerarquía de directorios y archivos requeridos por Qlib:
- calendars/day.txt
- instruments/all.txt
- features/<instrument>/<feature>.day.bin
Permite el cálculo ultrarrápido de Alpha Factors (Alpha158, Alpha360) cumpliendo RF-05.
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional
import numpy as np
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class QlibBinaryDumpService:
    """
    Gestiona la exportación de series temporales de activos hacia el formato binario nativo de Qlib.
    """

    FEATURE_NAMES = ["open", "close", "high", "low", "volume", "factor"]

    def __init__(self, qlib_dir: Path):
        self.qlib_dir = Path(qlib_dir)
        self.calendars_dir = self.qlib_dir / "calendars"
        self.instruments_dir = self.qlib_dir / "instruments"
        self.features_dir = self.qlib_dir / "features"

    def prepare_directories(self):
        """Crea las carpetas base del dataset de Qlib."""
        self.calendars_dir.mkdir(parents=True, exist_ok=True)
        self.instruments_dir.mkdir(parents=True, exist_ok=True)
        self.features_dir.mkdir(parents=True, exist_ok=True)

    def dump_all(self, assets_data: Dict[str, pd.DataFrame]) -> bool:
        """
        Vuelca un diccionario de DataFrames de activos {ticker: df_qlib} a la estructura binaria.
        Cada DataFrame debe tener las columnas: [date, open, close, high, low, volume, factor].
        """
        try:
            self.prepare_directories()
            if not assets_data:
                logger.warning("[QlibBinDump] No se proporcionaron datos de activos para volcar.")
                return False

            # 1. Consolidar calendario global (todos los días de negociación únicos ordenados)
            all_dates = set()
            for ticker, df in assets_data.items():
                if "date" in df.columns:
                    all_dates.update(df["date"].astype(str).tolist())
            
            sorted_dates = sorted(list(all_dates))
            calendar_path = self.calendars_dir / "day.txt"
            with open(calendar_path, "w", encoding="utf-8") as f:
                f.write("\n".join(sorted_dates) + "\n")
            logger.info(f"[QlibBinDump] Calendario generado con {len(sorted_dates)} fechas en {calendar_path}")

            date_to_idx = {d: i for i, d in enumerate(sorted_dates)}
            n_dates = len(sorted_dates)

            # 2. Generar instruments/all.txt
            instruments_lines = []
            for ticker, df in assets_data.items():
                if df.empty:
                    continue
                clean_ticker = ticker.lower().replace("-", "_").replace(".", "_")
                start_date = df["date"].min()
                end_date = df["date"].max()
                instruments_lines.append(f"{clean_ticker}\t{start_date}\t{end_date}")

                # 3. Volcar features individuales en formato float32 binario
                ticker_feat_dir = self.features_dir / clean_ticker
                ticker_feat_dir.mkdir(parents=True, exist_ok=True)

                # Alinear datos con el calendario global
                df_indexed = df.set_index("date")

                for feat in self.FEATURE_NAMES:
                    col_data = np.full(n_dates, np.nan, dtype=np.float32)
                    if feat in df_indexed.columns:
                        for d, val in df_indexed[feat].items():
                            if d in date_to_idx and not pd.isna(val):
                                col_data[date_to_idx[d]] = float(val)

                    bin_path = ticker_feat_dir / f"{feat}.day.bin"
                    col_data.astype(np.float32).tofile(str(bin_path))

            all_inst_path = self.instruments_dir / "all.txt"
            with open(all_inst_path, "w", encoding="utf-8") as f:
                f.write("\n".join(instruments_lines) + "\n")
            logger.info(f"[QlibBinDump] Instrumentos registrados: {len(instruments_lines)} en {all_inst_path}")

            logger.info(f"[QlibBinDump] Volcado binario completado con éxito en {self.qlib_dir}")
            return True
        except Exception as e:
            logger.error(f"[QlibBinDump] Error durante el volcado binario de Qlib: {e}")
            return False
