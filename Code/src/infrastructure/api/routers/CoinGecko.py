import os
from typing import Dict, List, Optional
import httpx
from pydantic import ValidationError
from fastapi import APIRouter, Depends
from ...data_providers.schemas import CoinGeckoSchemas as CG

# ==============================================================================
# Configuración y Autenticación CoinGecko API v3
# ==============================================================================

# TODO: Colocar la API KEY extraida de .env. Crear en .env example
COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY", "")
COINGECKO_IS_PRO = os.getenv("COINGECKO_IS_PRO", "false").lower() in ("true", "1", "yes")

__BASE_URL = (
    "https://pro-api.coingecko.com/api/v3"
    if COINGECKO_IS_PRO
    else "https://api.coingecko.com/api/v3"
)

router = APIRouter(prefix="/coingecko", tags=["CoinGecko"])


def _get_headers() -> Dict[str, str]:
    """
    Retorna las cabeceras HTTP para CoinGecko API v3:
    - accept: application/json
    - x-cg-demo-api-key: para cuentas Demo/Free
    - x-cg-pro-api-key: para cuentas Pro
    """
    headers = {"accept": "application/json"}
    if COINGECKO_API_KEY:
        if COINGECKO_IS_PRO:
            headers["x-cg-pro-api-key"] = COINGECKO_API_KEY
        else:
            headers["x-cg-demo-api-key"] = COINGECKO_API_KEY
    return headers


# ==============================================================================
# 1. Simple Price - GET /api/v3/simple/price
# ==============================================================================

def simple_price(p: CG.SimplePriceParams) -> Optional[CG.SimplePriceResponse]:
    """
    Endpoint: GET /simple/price
    Obtiene el precio actual, capitalización, volumen y variación en 24h.
    Retorna un diccionario mapeado con SimplePriceItem para cada coin_id.
    """
    try:
        url = f"{__BASE_URL}/simple/price"
        params = {
            "ids": p.ids,
            "vs_currencies": p.vs_currencies,
            "include_market_cap": str(p.include_market_cap).lower(),
            "include_24hr_vol": str(p.include_24hr_vol).lower(),
            "include_24hr_change": str(p.include_24hr_change).lower(),
            "include_last_updated_at": str(p.include_last_updated_at).lower(),
        }
        with httpx.Client(timeout=15.0) as client:
            response = client.get(url, headers=_get_headers(), params=params)
            response.raise_for_status()
            raw = response.json()

        if not isinstance(raw, dict):
            return None

        return {
            coin_id: CG.SimplePriceItem.model_validate(item_data)
            for coin_id, item_data in raw.items()
        }
    except (ValidationError, httpx.HTTPError, Exception):
        return None


# ==============================================================================
# 2. Coins Markets - GET /api/v3/coins/markets
# ==============================================================================

def coins_markets(p: CG.CoinMarketsParams) -> Optional[List[CG.CoinMarketItem]]:
    """
    Endpoint: GET /coins/markets
    Obtiene la lista clasificada de criptomonedas con métricas de mercado.
    Retorna una lista de CoinMarketItem.
    """
    try:
        url = f"{__BASE_URL}/coins/markets"
        params = {
            "vs_currency": p.vs_currency,
            "ids": p.ids,
            "category": p.category,
            "order": p.order,
            "per_page": p.per_page,
            "page": p.page,
            "sparkline": str(p.sparkline).lower(),
            "price_change_percentage": p.price_change_percentage,
        }
        clean_params = {k: v for k, v in params.items() if v is not None}

        with httpx.Client(timeout=15.0) as client:
            response = client.get(url, headers=_get_headers(), params=clean_params)
            response.raise_for_status()
            raw = response.json()

        if not isinstance(raw, list):
            return None

        return [CG.CoinMarketItem.model_validate(item) for item in raw]
    except (ValidationError, httpx.HTTPError, Exception):
        return None


# ==============================================================================
# 3. Market Chart (Historical Time Series) - GET /api/v3/coins/{id}/market_chart
# ==============================================================================

def market_chart(p: CG.MarketChartParams) -> Optional[CG.MarketChartResponse]:
    """
    Endpoint: GET /coins/{id}/market_chart
    Obtiene la serie temporal histórica (precios, market cap, volumen).
    Retorna MarketChartResponse para modelos predictivos (Galformer).
    """
    try:
        url = f"{__BASE_URL}/coins/{p.id}/market_chart"
        params = {
            "vs_currency": p.vs_currency,
            "days": p.days,
            "interval": p.interval,
        }
        clean_params = {k: v for k, v in params.items() if v is not None}

        with httpx.Client(timeout=15.0) as client:
            response = client.get(url, headers=_get_headers(), params=clean_params)
            response.raise_for_status()
            raw = response.json()

        if not isinstance(raw, dict):
            return None

        return CG.MarketChartResponse.model_validate(raw)
    except (ValidationError, httpx.HTTPError, Exception):
        return None


# ==============================================================================
# 4. OHLC Candlestick Series - GET /api/v3/coins/{id}/ohlc
# ==============================================================================

def coin_ohlc(p: CG.CoinOHLCParams) -> Optional[List[CG.CoinOHLCCandle]]:
    """
    Endpoint: GET /coins/{id}/ohlc
    Obtiene velas OHLC (Open, High, Low, Close) por rango de días.
    Retorna una lista de CoinOHLCCandle.
    """
    try:
        url = f"{__BASE_URL}/coins/{p.id}/ohlc"
        params = {
            "vs_currency": p.vs_currency,
            "days": p.days,
        }
        with httpx.Client(timeout=15.0) as client:
            response = client.get(url, headers=_get_headers(), params=params)
            response.raise_for_status()
            raw = response.json()

        if not isinstance(raw, list):
            return None

        return [
            CG.CoinOHLCCandle(
                time=int(c[0]),
                open=float(c[1]),
                high=float(c[2]),
                low=float(c[3]),
                close=float(c[4]),
            )
            for c in raw
            if isinstance(c, (list, tuple)) and len(c) >= 5
        ]
    except (ValidationError, httpx.HTTPError, Exception):
        return None


# ==============================================================================
# 5. Global Market Data (Crypto Macro Context) - GET /api/v3/global
# ==============================================================================

def global_market() -> Optional[CG.GlobalMarketResponse]:
    """
    Endpoint: GET /global
    Obtiene los datos macroeconómicos agregados del mercado de criptomonedas.
    Retorna GlobalMarketResponse.
    """
    try:
        url = f"{__BASE_URL}/global"
        with httpx.Client(timeout=15.0) as client:
            response = client.get(url, headers=_get_headers())
            response.raise_for_status()
            raw = response.json()

        if not isinstance(raw, dict):
            return None

        return CG.GlobalMarketResponse.model_validate(raw)
    except (ValidationError, httpx.HTTPError, Exception):
        return None


# ==============================================================================
# FastAPI Router Endpoints
# ==============================================================================

@router.get("/simple/price", response_model=Optional[CG.SimplePriceResponse])
def get_simple_price(p: CG.SimplePriceParams = Depends()) -> Optional[CG.SimplePriceResponse]:
    return simple_price(p)


@router.get("/coins/markets", response_model=Optional[List[CG.CoinMarketItem]])
def get_coins_markets(p: CG.CoinMarketsParams = Depends()) -> Optional[List[CG.CoinMarketItem]]:
    return coins_markets(p)


@router.get("/coins/{id}/market_chart", response_model=Optional[CG.MarketChartResponse])
def get_market_chart(p: CG.MarketChartParams = Depends()) -> Optional[CG.MarketChartResponse]:
    return market_chart(p)


@router.get("/coins/{id}/ohlc", response_model=Optional[List[CG.CoinOHLCCandle]])
def get_coin_ohlc(p: CG.CoinOHLCParams = Depends()) -> Optional[List[CG.CoinOHLCCandle]]:
    return coin_ohlc(p)


@router.get("/global", response_model=Optional[CG.GlobalMarketResponse])
def get_global_market() -> Optional[CG.GlobalMarketResponse]:
    return global_market()
