"""
Punto de entrada de consola para la preparación y binarización de datos con Qlib.
Ejecuta la adquisición de activos representativos y genera la estructura binaria.
"""

import sys
import logging

logger = logging.getLogger(__name__)
from src.domain.services.Qlib.DataPreparation import QlibDataPreparationService


def main():
    logger.info("=== Iniciando Pipeline de Preparación de Datos Qlib ===")
    tickers = ["AAPL", "MSFT", "NVDA", "BTC-USD", "GSPC"]

    service = QlibDataPreparationService()
    success = service.prepare_and_dump_instruments(tickers=tickers, range_str="1y")

    if success:
        logger.info("Pipeline de datos Qlib completado satisfactoriamente.")
        sys.exit(0)
    else:
        logger.error("El pipeline de datos Qlib encontró errores.")
        sys.exit(1)


if __name__ == "__main__":
    main()
