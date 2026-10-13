"""
Servicio Principal del Dominio Analítico y Cuantitativo (MPS).
Orquesta:
1. Adquisición de datos desde APIs de infraestructura (Yahoo, Polygon, FMP, FRED, Finnhub, CoinGecko).
2. Limpieza y validación (RF-06: min 30 observaciones, RF-12: detección std=0).
3. Volcado binario (Qlib .bin nativo y serialización de tensores).
4. Inferencia con modelos de Machine Learning (MASTER + Galformer + Qlib Alphas).
5. Validación estadística de hipótesis Z-test (RF-09, RF-10, RF-11, RF-12).
6. Persistencia append-only en MongoDB 'market_ticks_and_features' y 'INTENT_PREDICTION_LOG' (RF-15, RF-16).
7. Publicación reactiva de señales en Redis 'market_signals' (RF-13, RF-14).
8. Endpoint conversacional /api/v1/predict/intent (RF-17 a RF-20, UC-01, UC-02).
"""

from contextlib import asynccontextmanager
from datetime import datetime, timezone
import os
from pathlib import Path
import re
import time
from typing import Any, Dict, List, Optional

import logging
from fastapi import BackgroundTasks, FastAPI, HTTPException, Query, status
from pydantic import BaseModel, Field
import uvicorn

logger = logging.getLogger(__name__)

# Modelos y servicios del dominio
from src.domain.models.market import (
    IntentPredictionLog,
    IntentType,
    MarketSignalPayload,
    MarketTickDocument,
    SignalType,
)
from src.domain.services.data_binarization.qlib_bin_dump import QlibBinaryDumpService
from src.domain.services.data_cleaning.clean_market_data import DataCleaningService
from src.domain.services.data_cleaning.data_acquisition import DataAcquisitionService
from src.domain.services.inference.risk_management import RiskManagementService
from src.domain.services.inference.signal_generator import SignalGenerationEngine
from src.domain.services.inference.statistical_validator import StatisticalValidator
from src.domain.services.models_training.train_galformer import GalformerTrainer
from src.domain.services.models_training.train_master import MASTERTrainer
from src.domain.services.models_training.train_qlib_alpha import QlibAlphaTrainer
from src.domain.services.storage.mongo_repository import MongoMarketRepository
from src.domain.services.storage.redis_publisher import RedisSignalPublisher

# Configuración de rutas
BASE_DIR = Path(__file__).resolve().parent
CHECKPOINTS_DIR = BASE_DIR / "models_training" / "checkpoints"
QLIB_DATA_DIR = BASE_DIR / "Qlib" / "qlib_data"

# Instanciación de componentes
mongo_repo = MongoMarketRepository()
redis_pub = RedisSignalPublisher()
signal_engine = SignalGenerationEngine(checkpoints_dir=CHECKPOINTS_DIR)
qlib_dump_service = QlibBinaryDumpService(qlib_dir=QLIB_DATA_DIR)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ciclo de vida de la aplicación: inicialización de persistencia y brokers."""
    logger.info("[MPS Domain Service] Iniciando servicio analítico cuantitativo...")
    mongo_repo.connect()
    redis_pub.connect()
    CHECKPOINTS_DIR.mkdir(parents=True, exist_ok=True)
    QLIB_DATA_DIR.mkdir(parents=True, exist_ok=True)
    yield
    logger.info(
        "[MPS Domain Service] Apagando servicio de forma ordenada (Graceful Shutdown)."
    )


app = FastAPI(
    title="MPS Quantitative Analytical Service",
    description="Servicio de IA cuantitativa, inferencia de modelos (MASTER & Galformer), ingesta y validación estadística",
    version="1.0.0",
    lifespan=lifespan,
)


# ==============================================================================
# Modelos de Entrada / Salida para la API Conversacional y Pipeline
# ==============================================================================


class IntentRequest(BaseModel):
    prompt: str = Field(..., example="Invertir 20000 en el sector de tecnología")
    user_id: Optional[str] = Field(None, example="3fa85f64-5717-4562-b3fc-2c963f66afa6")


class AssetRecommendation(BaseModel):
    ticker: str
    price: float
    signal: SignalType
    z_score: float
    p_value: float
    weight_pct: float
    stop_loss: float
    take_profit: float
    explanation: str


class IntentResponse(BaseModel):
    classified_intent: IntentType
    confidence_statement: str
    macro_context: Optional[str] = None
    allocation_chart: Dict[str, float]
    recommendations: List[AssetRecommendation]
    execution_time_ms: int


class PipelineRunRequest(BaseModel):
    tickers: List[str] = Field(default=["AAPL", "MSFT", "NVDA", "BTC-USD"])
    range_str: str = Field(default="1y")


# ==============================================================================
# Utilidades de Clasificación de Lenguaje Natural (RF-17 a RF-20)
# ==============================================================================


def parse_and_classify_intent(
    prompt: str,
) -> Tuple[IntentType, Optional[float], Optional[str], Optional[str]]:
    """
    Clasifica la consulta del usuario en INTENT_MACRO, INTENT_SECTORIAL o INTENT_ACTIVO
    y extrae el monto, sector o ticker correspondiente.
    """
    clean_p = prompt.strip().lower()

    # Extraer monto
    amount_match = re.search(r"(\$?\s*\d+[\d,]*(\.\d+)?)", clean_p)
    amount = None
    if amount_match:
        try:
            raw_amt = amount_match.group(1).replace("$", "").replace(",", "").strip()
            amount = float(raw_amt)
        except Exception:
            amount = None

    # Detectar activos individuales específicos
    known_tickers = {
        "apple": "AAPL",
        "aapl": "AAPL",
        "microsoft": "MSFT",
        "msft": "MSFT",
        "nvidia": "NVDA",
        "nvda": "NVDA",
        "bitcoin": "BTC-USD",
        "btc": "BTC-USD",
        "sp500": "GSPC",
        "s&p500": "GSPC",
        "nasdaq": "IXIC",
        "ixic": "IXIC",
    }
    for name, sym in known_tickers.items():
        if name in clean_p:
            return IntentType.INTENT_ACTIVO, amount, None, sym

    # Detectar sectores específicos
    known_sectors = [
        "tecnología",
        "technology",
        "tech",
        "energía",
        "energy",
        "finanzas",
        "financial",
        "banca",
        "salud",
        "healthcare",
        "consumo",
        "consumer",
    ]
    for sec in known_sectors:
        if sec in clean_p:
            return IntentType.INTENT_SECTORIAL, amount, sec.capitalize(), None

    # Por descarte: Si contiene monto general o palabras macro
    if (
        amount is not None
        or "invertir" in clean_p
        or "portafolio" in clean_p
        or "diversificar" in clean_p
    ):
        return IntentType.INTENT_MACRO, amount, None, None

    # No clasificado
    raise ValueError(
        "Prompt no interpretable en las categorías de intención soportadas."
    )


# ==============================================================================
# Endpoints de la API
# ==============================================================================


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "mps-analytical-domain",
        "timestamp": datetime.now(timezone.utc),
    }


@app.post("/api/v1/predict/intent", response_model=IntentResponse)
def predict_intent(req: IntentRequest):
    """
    RF-17 a RF-20 & UC-01/UC-02:
    Clasifica un prompt en lenguaje natural, ejecuta el pipeline predictivo real
    y retorna la estructura de recomendación con descargo estadístico legal.
    """
    start_time = time.time()
    try:
        intent_type, parsed_amount, parsed_sector, parsed_ticker = (
            parse_and_classify_intent(req.prompt)
        )
    except ValueError:
        # RF-20: Solicitar aclaración sin generar error 500
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No pudimos interpretar su intención de inversión. Por favor especifique un monto (ej: 10000), un sector (ej: Tecnología) o un activo concreto (ej: Apple).",
        )

    # Determinar universo de activos a evaluar
    if intent_type == IntentType.INTENT_ACTIVO and parsed_ticker:
        target_tickers = [parsed_ticker]
    elif intent_type == IntentType.INTENT_SECTORIAL:
        target_tickers = ["NVDA", "AAPL", "MSFT"]
    else:  # INTENT_MACRO
        target_tickers = ["AAPL", "MSFT", "NVDA", "BTC-USD"]

    recommendations: List[AssetRecommendation] = []
    allocation_chart: Dict[str, float] = {}
    n_assets = len(target_tickers)
    weight_each = round(100.0 / n_assets, 2)

    for sym in target_tickers:
        # 1. Adquisición desde infraestructura
        df_raw = DataAcquisitionService.fetch_yahoo_ohlcv(
            sym, range_str="6mo", interval="1d"
        )
        if df_raw is None or df_raw.empty:
            # Fallback en caso de activo de respaldo
            df_raw = DataAcquisitionService.fetch_polygon_ohlcv(sym)

        # 2. Limpieza y validación (RF-06, RF-12)
        is_valid, df_clean, msg = DataCleaningService.clean_ohlcv_dataframe(
            df_raw, ticker=sym
        )
        if not is_valid:
            continue

        # 3. Inferencia de modelos cuantitativos
        doc, signal_payload = signal_engine.process_tick(
            ticker=sym, df_clean=df_clean, sector=parsed_sector
        )

        # 4. Persistencia append-only en MongoDB (RF-15, RF-16)
        mongo_repo.insert_tick_document(doc)

        # 5. Publicar en Redis si la señal es significativa (RF-13)
        if signal_payload:
            redis_pub.publish_signal(signal_payload)

        # Stop-loss y take-profit
        stop_l, take_p, explanation = RiskManagementService.calculate_risk_levels(
            current_price=doc.raw_data.price,
            df_clean=df_clean,
            signal=doc.statistical_validation.final_signal,
        )

        recommendations.append(
            AssetRecommendation(
                ticker=sym,
                price=doc.raw_data.price,
                signal=doc.statistical_validation.final_signal,
                z_score=doc.statistical_validation.z_score,
                p_value=doc.statistical_validation.p_value,
                weight_pct=weight_each,
                stop_loss=stop_l,
                take_profit=take_p,
                explanation=explanation,
            )
        )
        allocation_chart[sym] = weight_each

    # Si la suma no es exactamente 100%, ajustar el último
    if allocation_chart:
        total_w = sum(allocation_chart.values())
        diff = round(100.0 - total_w, 2)
        first_key = list(allocation_chart.keys())[0]
        allocation_chart[first_key] = round(allocation_chart[first_key] + diff, 2)

    exec_time = int((time.time() - start_time) * 1000)

    # Registrar en INTENT_PREDICTION_LOG
    log_entry = IntentPredictionLog(
        user_id=req.user_id,
        raw_prompt=req.prompt,
        classified_intent=intent_type,
        parsed_amount=parsed_amount,
        parsed_sector=parsed_sector,
        parsed_ticker=parsed_ticker,
        execution_time_ms=exec_time,
    )
    mongo_repo.insert_intent_log(log_entry)

    # Texto legal obligatorio (RF-36 & RNF-20)
    confidence_statement = (
        "El indicador de confianza representa exclusivamente la consistencia y solidez "
        "de la evidencia estadística matemática (nivel de significancia p < 0.05 en Z-test) "
        "y NO constituye una garantía ni probabilidad de rentabilidad monetaria futura."
    )

    macro_context = (
        "El entorno macroeconómico actual refleja estabilidad en los índices de volatilidad "
        "con dinámicas sectoriales condicionadas por tasas de interés y retornos tecnológicos."
        if intent_type in (IntentType.INTENT_MACRO, IntentType.INTENT_SECTORIAL)
        else None
    )

    return IntentResponse(
        classified_intent=intent_type,
        confidence_statement=confidence_statement,
        macro_context=macro_context,
        allocation_chart=allocation_chart,
        recommendations=recommendations,
        execution_time_ms=exec_time,
    )


@app.post("/api/v1/pipeline/acquire-and-process")
def acquire_and_process_pipeline(
    req: PipelineRunRequest, background_tasks: BackgroundTasks
):
    """
    Ejecuta el ciclo integral:
    - Adquisición desde APIs
    - Limpieza
    - Volcado binario (Qlib)
    - Inferencia y validación estadística
    - Persistencia en MongoDB y notificación en Redis
    """
    results = {}
    cleaned_datasets = {}

    for ticker in req.tickers:
        logger.info(f"[Pipeline] Adquiriendo datos para {ticker}...")
        df_raw = DataAcquisitionService.fetch_yahoo_ohlcv(
            ticker, range_str=req.range_str, interval="1d"
        )
        if df_raw is None or df_raw.empty:
            df_raw = DataAcquisitionService.fetch_polygon_ohlcv(ticker)

        is_valid, df_clean, msg = DataCleaningService.clean_ohlcv_dataframe(
            df_raw, ticker=ticker
        )
        if not is_valid:
            results[ticker] = {"status": "SKIPPED", "reason": msg}
            continue

        # Formato para Qlib
        df_qlib = DataCleaningService.format_for_qlib(df_clean)
        cleaned_datasets[ticker] = df_qlib

        # Inferencia y validación
        doc, sig_payload = signal_engine.process_tick(ticker=ticker, df_clean=df_clean)
        mongo_repo.insert_tick_document(doc)

        if sig_payload:
            redis_pub.publish_signal(sig_payload)

        results[ticker] = {
            "status": "PROCESSED",
            "price": doc.raw_data.price,
            "signal": doc.statistical_validation.final_signal,
            "z_score": doc.statistical_validation.z_score,
            "p_value": doc.statistical_validation.p_value,
            "is_significant": doc.statistical_validation.is_significant,
        }

    # Volcado binario en segundo plano a Qlib
    if cleaned_datasets:
        background_tasks.add_task(qlib_dump_service.dump_all, cleaned_datasets)

    return {
        "status": "SUCCESS",
        "processed_count": len(
            [r for r in results.values() if r.get("status") == "PROCESSED"]
        ),
        "results": results,
    }


def main():
    """Punto de entrada de consola para iniciar el servidor de servicios analíticos."""
    port = int(os.getenv("PORT", "8000"))
    logger.info(f"Iniciando servidor MPS en http://0.0.0.0:{port}")
    uvicorn.run("src.domain.services.main:app", host="0.0.0.0", port=port, reload=True)


if __name__ == "__main__":
    main()
