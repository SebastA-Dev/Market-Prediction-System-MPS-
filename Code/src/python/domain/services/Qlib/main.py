"""
Punto de entrada de consola para la preparación y binarización de datos con Qlib.
Ejecuta la adquisición de activos representativos y genera la estructura binaria.
"""

import sys
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Asegurar que las rutas raíz estén en sys.path
_CURRENT_DIR = Path(__file__).resolve().parent
_PYTHON_ROOT = _CURRENT_DIR.parent.parent.parent
for _p in [str(_PYTHON_ROOT), str(_PYTHON_ROOT.parent), str(_PYTHON_ROOT.parent.parent)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

try:
    from .DataPreparation import QlibDataPreparationService
except (ImportError, ValueError):
    from domain.services.Qlib.DataPreparation import QlibDataPreparationService


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
