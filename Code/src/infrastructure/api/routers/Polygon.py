import os
from typing import Dict, Optional
import httpx
from pydantic import ValidationError
from fastapi import APIRouter, Depends
from ...data_providers.schemas import PolygonSchemas as PG

# ==============================================================================
# Configuración y Autenticación Polygon.io API
# ==============================================================================

# TODO: Colocar la API KEY extraida de .env. Crear en .env example
POLYGON_API_KEY = os.getenv("POLYGON_API_KEY", "")
__BASE_URL = "https://api.polygon.io"

router = APIRouter(prefix="/polygon", tags=["Polygon"])


def _get_headers() -> Dict[str, str]:
    """
    Retorna cabeceras HTTP para Polygon.io:
    - accept: application/json
    - Authorization: Bearer <API_KEY>
    """
    headers = {"accept": "application/json"}
    if POLYGON_API_KEY:
        headers["Authorization"] = f"Bearer {POLYGON_API_KEY}"
    return headers


# ==============================================================================
# 1. Aggregates (Bars / OHLCV) - GET /v2/aggs/ticker/...
# ==============================================================================

def aggregates(p: PG.AggregatesParams) -> Optional[PG.AggregatesResponse]:
    """
    Endpoint: GET /v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{from}/{to}
    Obtiene velas OHLCV históricas para secuencias continuas en Galformer y factores Qlib.
    """
    try:
        url = (
            f"{__BASE_URL}/v2/aggs/ticker/{p.ticker}/range/"
            f"{p.multiplier}/{p.timespan}/{p.from_date}/{p.to_date}"
        )
        params = {
            "adjusted": str(p.adjusted).lower() if p.adjusted is not None else "true",
            "sort": p.sort,
            "limit": p.limit,
        }
        clean_params = {k: v for k, v in params.items() if v is not None}

        with httpx.Client(timeout=15.0) as client:
            response = client.get(url, headers=_get_headers(), params=clean_params)
            response.raise_for_status()
            raw = response.json()

        if not isinstance(raw, dict):
            return None

        return PG.AggregatesResponse.model_validate(raw)
    except (ValidationError, httpx.HTTPError, Exception):
        return None


# ==============================================================================
# 2. Grouped Daily (Full Market Snapshot) - GET /v2/aggs/grouped/locale/us/market/stocks/{date}
# ==============================================================================

def grouped_daily(p: PG.GroupedDailyParams) -> Optional[PG.GroupedDailyResponse]:
    """
    Endpoint: GET /v2/aggs/grouped/locale/us/market/stocks/{date}
    Obtiene el rendimiento diario de todo el mercado de acciones de EE.UU. para una fecha específica.
    """
    try:
        url = f"{__BASE_URL}/v2/aggs/grouped/locale/us/market/stocks/{p.date}"
        params = {
            "adjusted": str(p.adjusted).lower() if p.adjusted is not None else "true",
        }
        with httpx.Client(timeout=20.0) as client:
            response = client.get(url, headers=_get_headers(), params=params)
            response.raise_for_status()
            raw = response.json()

        if not isinstance(raw, dict):
            return None

        return PG.GroupedDailyResponse.model_validate(raw)
    except (ValidationError, httpx.HTTPError, Exception):
        return None


# ==============================================================================
# 3. Daily Open / Close - GET /v1/open-close/{ticker}/{date}
# ==============================================================================

def daily_open_close(p: PG.DailyOpenCloseParams) -> Optional[PG.DailyOpenCloseResponse]:
    """
    Endpoint: GET /v1/open-close/{ticker}/{date}
    Obtiene el resumen de precios de la sesión (open, high, low, close, pre/after market).
    """
    try:
        url = f"{__BASE_URL}/v1/open-close/{p.ticker}/{p.date}"
        params = {
            "adjusted": str(p.adjusted).lower() if p.adjusted is not None else "true",
        }
        with httpx.Client(timeout=15.0) as client:
            response = client.get(url, headers=_get_headers(), params=params)
            response.raise_for_status()
            raw = response.json()

        if not isinstance(raw, dict):
            return None

        return PG.DailyOpenCloseResponse.model_validate(raw)
    except (ValidationError, httpx.HTTPError, Exception):
        return None


# ==============================================================================
# 4. Ticker Details v3 - GET /v3/reference/tickers/{ticker}
# ==============================================================================

def ticker_details(p: PG.TickerDetailsParams) -> Optional[PG.TickerDetailsResponse]:
    """
    Endpoint: GET /v3/reference/tickers/{ticker}
    Obtiene metadatos fundamentales, descripción, clasificación SIC y empleados de la compañía.
    """
    try:
        url = f"{__BASE_URL}/v3/reference/tickers/{p.ticker}"
        params = {"date": p.date} if p.date else {}

        with httpx.Client(timeout=15.0) as client:
            response = client.get(url, headers=_get_headers(), params=params)
            response.raise_for_status()
            raw = response.json()

        if not isinstance(raw, dict):
            return None

        return PG.TickerDetailsResponse.model_validate(raw)
    except (ValidationError, httpx.HTTPError, Exception):
        return None


# ==============================================================================
# 5. Market Status - GET /v1/marketstatus/now
# ==============================================================================

def market_status() -> Optional[PG.PolygonMarketStatusResponse]:
    """
    Endpoint: GET /v1/marketstatus/now
    Consulta el estado operativo en tiempo real de las bolsas y divisas (open/closed/extended).
    """
    try:
        url = f"{__BASE_URL}/v1/marketstatus/now"
        with httpx.Client(timeout=15.0) as client:
            response = client.get(url, headers=_get_headers())
            response.raise_for_status()
            raw = response.json()

        if not isinstance(raw, dict):
            return None

        return PG.PolygonMarketStatusResponse.model_validate(raw)
    except (ValidationError, httpx.HTTPError, Exception):
        return None


# ==============================================================================
# FastAPI Router Endpoints
# ==============================================================================

@router.get("/aggs", response_model=Optional[PG.AggregatesResponse])
def get_aggregates(p: PG.AggregatesParams = Depends()) -> Optional[PG.AggregatesResponse]:
    return aggregates(p)


@router.get("/grouped-daily", response_model=Optional[PG.GroupedDailyResponse])
def get_grouped_daily(p: PG.GroupedDailyParams = Depends()) -> Optional[PG.GroupedDailyResponse]:
    return grouped_daily(p)


@router.get("/open-close", response_model=Optional[PG.DailyOpenCloseResponse])
def get_daily_open_close(p: PG.DailyOpenCloseParams = Depends()) -> Optional[PG.DailyOpenCloseResponse]:
    return daily_open_close(p)


@router.get("/ticker-details", response_model=Optional[PG.TickerDetailsResponse])
def get_ticker_details(p: PG.TickerDetailsParams = Depends()) -> Optional[PG.TickerDetailsResponse]:
    return ticker_details(p)


@router.get("/market-status", response_model=Optional[PG.PolygonMarketStatusResponse])
def get_market_status() -> Optional[PG.PolygonMarketStatusResponse]:
    return market_status()
