"""
Modelos de dominio para el sistema cuantitativo de inversión predictiva (MPS).
Define las entidades fundamentales del pipeline analítico y persistencia.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field


class SignalType(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class MarketTrend(str, Enum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"


class IntentType(str, Enum):
    INTENT_MACRO = "INTENT_MACRO"
    INTENT_SECTORIAL = "INTENT_SECTORIAL"
    INTENT_ACTIVO = "INTENT_ACTIVO"


class RawMarketData(BaseModel):
    """Datos de mercado en bruto extraídos del tick o vela OHLCV."""
    price: float = Field(..., description="Precio de cierre o último trade")
    volume: float = Field(..., description="Volumen negociado")
    open_price: Optional[float] = None
    high_price: Optional[float] = None
    low_price: Optional[float] = None


class QlibFeatures(BaseModel):
    """Vectores de Alpha Factors generados por Qlib."""
    feature_vector: bytes = Field(..., description="Serialización binaria de los factores")
    factor_names: Optional[List[str]] = Field(default_factory=list)


class MasterInference(BaseModel):
    """Resultados de inferencia del modelo MASTER (inter-sectorial y cross-asset)."""
    raw_tensors: bytes = Field(..., description="Serialización binaria de los tensores latentes")
    trend: str = Field(..., description="Tendencia proyectada (BULLISH, BEARISH, NEUTRAL)")
    sector_correlations: Optional[Dict[str, float]] = Field(default_factory=dict)


class GalformerInference(BaseModel):
    """Resultados de inferencia del modelo Galformer (trayectoria multi-step)."""
    raw_tensors: bytes = Field(..., description="Serialización binaria de los tensores de predicción")
    projected_horizon: float = Field(..., description="Horizonte proyectado en pasos de tiempo")
    predicted_prices: Optional[List[float]] = Field(default_factory=list)


class StatisticalValidation(BaseModel):
    """Validación estadística mediante prueba de hipótesis Z-test (alpha = 0.05)."""
    z_score: float = Field(..., description="Puntaje Z calculado")
    p_value: float = Field(..., description="p-value resultante")
    is_significant: bool = Field(..., description="True si |z| > 1.96 y p < 0.05")
    final_signal: SignalType = Field(..., description="Señal final validada: BUY, SELL o HOLD")


class MarketTickDocument(BaseModel):
    """
    Documento completo de MongoDB para la colección 'market_ticks_and_features'.
    Estructura inmutable (append-only) según UMLBaseDeDatos.drawio.
    """
    ticker: str = Field(..., description="Símbolo del activo (ej: AAPL, BTC-USD)")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    raw_data: RawMarketData
    qlib_features: Optional[QlibFeatures] = None
    master_inference: Optional[MasterInference] = None
    galformer_inference: Optional[GalformerInference] = None
    statistical_validation: StatisticalValidation


class IntentPredictionLog(BaseModel):
    """
    Documento de MongoDB para la colección 'INTENT_PREDICTION_LOG'.
    Registra consultas en lenguaje natural y su clasificación.
    """
    user_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    raw_prompt: str
    classified_intent: IntentType
    parsed_amount: Optional[float] = None
    parsed_sector: Optional[str] = None
    parsed_ticker: Optional[str] = None
    execution_time_ms: int = 0


class MarketSignalPayload(BaseModel):
    """
    Payload publicado al canal Redis 'market_signals'.
    Cumple con el RNF-02 y RF-13 para consumo del microservicio en Java.
    """
    ticker: str
    price: float
    signal: SignalType
    p_value: float
    timestamp: str
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
