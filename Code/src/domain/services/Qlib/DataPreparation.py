"""
Servicio de Preparación y Binarización de Datos con Microsoft Qlib.
Adquiere los datos desde infraestructura, realiza la limpieza (RF-06, RF-12),
los transforma al formato canónico de Qlib y ejecuta el volcado binario
(calendars/day.txt, instruments/all.txt, features/<ticker>/*.bin).
"""

from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd
import logging

logger = logging.getLogger(__name__)

from src.domain.services.data_cleaning.data_acquisition import DataAcquisitionService
from src.domain.services.data_cleaning.clean_market_data import DataCleaningService
from src.domain.services.data_binarization.qlib_bin_dump import QlibBinaryDumpService


class QlibDataPreparationService:
    """
    Coordina el flujo de ingestión, depuración y conversión binaria para Qlib.
    """

    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or Path(__file__).resolve().parent / "qlib_data"
        self.dump_service = QlibBinaryDumpService(qlib_dir=self.output_dir)

    def prepare_and_dump_instruments(
        self,
        tickers: List[str],
        range_str: str = "2y",
        interval: str = "1d",
    ) -> bool:
        """
        Descarga, limpia y binariza un conjunto de tickers hacia la estructura Qlib.
        """
        logger.info(f"[QlibDataPreparation] Iniciando preparación para tickers: {tickers}")
        cleaned_datasets: Dict[str, pd.DataFrame] = {}

        for ticker in tickers:
            logger.info(f"[QlibDataPreparation] Descargando datos para {ticker}...")
            df_raw = DataAcquisitionService.fetch_yahoo_ohlcv(ticker, range_str=range_str, interval=interval)
            if df_raw is None or df_raw.empty:
                logger.info(f"[QlibDataPreparation] Reintentando con Polygon para {ticker}...")
                df_raw = DataAcquisitionService.fetch_polygon_ohlcv(ticker)

            if df_raw is None or df_raw.empty:
                logger.warning(f"[QlibDataPreparation] Imposible adquirir datos para {ticker}")
                continue

            is_valid, df_clean, msg = DataCleaningService.clean_ohlcv_dataframe(df_raw, ticker=ticker)
            if not is_valid:
                logger.warning(f"[QlibDataPreparation] {ticker} descartado: {msg}")
                continue

            # Formatear a columnas requeridas por Qlib
            df_qlib = DataCleaningService.format_for_qlib(df_clean)
            cleaned_datasets[ticker] = df_qlib
            logger.info(f"[QlibDataPreparation] {ticker} listo con {len(df_qlib)} registros diarios.")

        if not cleaned_datasets:
            logger.error("[QlibDataPreparation] No se preparó ningún dataset válido.")
            return False

        # Volcado binario
        success = self.dump_service.dump_all(cleaned_datasets)
        if success:
            logger.info(f"[QlibDataPreparation] Volcado completado en {self.output_dir}")
        return success
