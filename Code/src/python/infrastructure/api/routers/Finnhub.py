import logging
import os
from typing import Any, Dict, List, Optional, Union
import httpx
from pydantic import ValidationError
from fastapi import APIRouter, Depends
from ..errors import UPSTREAM_ERROR_RESPONSES, raise_upstream_error

from ...data_providers.schemas import FinnhubSchema as FS

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# ==============================================================================
# Configuración y Autenticación Finnhub API
# ==============================================================================

__BASE_URL = "https://api.finnhub.io/api/v1"

router = APIRouter(prefix="/finnhub", tags=["Finnhub"])


def _get_api_key() -> str:
    """Obtiene la clave de Finnhub desde las variables de entorno."""
    return os.getenv("FINNHUB_APIKEY", "").strip()


def _get_headers() -> Dict[str, str]:
    """Retorna las cabeceras estándar para peticiones HTTP a Finnhub."""
    headers = {"accept": "application/json"}
    key = _get_api_key()
    if key:
        headers["X-Finnhub-Token"] = key
    return headers


def _build_params(extra_params: Dict[str, Any] = None) -> Dict[str, Any]:
    """Construye los query params incluyendo token si está disponible."""
    params: Dict[str, Any] = {}
    key = _get_api_key()
    if key:
        params["token"] = key
    if extra_params:
        for k, v in extra_params.items():
            if v is not None:
                params[k] = v
    return params


# ==============================================================================
# 1. Symbol Lookup (/search)
# ==============================================================================


def symbol_lookup_params(p: FS.SymbolLookupParams) -> FS.SymbolLookupResponse:
    """Busca símbolos y empresas por término de búsqueda y filtro opcional de exchange."""
    try:
        url = f"{__BASE_URL}/search"
        extra: Dict[str, Any] = {"q": p.q}
        if p.exchange:
            extra["exchange"] = p.exchange

        with httpx.Client(timeout=20.0, follow_redirects=True) as client:
            response = client.get(
                url, headers=_get_headers(), params=_build_params(extra)
            )
            response.raise_for_status()
            raw = response.json()

        return FS.SymbolLookupResponse.model_validate(raw)
    except (ValidationError, httpx.HTTPError, ValueError) as exc:
        raise_upstream_error(exc)


# ==============================================================================
# 2. Stock Symbols (/stock/symbol)
# ==============================================================================


def stock_symbols(p: FS.StockSymbolsParams) -> List[FS.StockSymbolItem]:
    """Obtiene la lista de símbolos soportados para un exchange específico."""
    try:
        url = f"{__BASE_URL}/stock/symbol"
        extra: Dict[str, Any] = {"exchange": p.exchange}
        if p.mic:
            extra["mic"] = p.mic
        if p.security_type:
            extra["securityType"] = p.security_type

        with httpx.Client(timeout=20.0, follow_redirects=True) as client:
            response = client.get(
                url, headers=_get_headers(), params=_build_params(extra)
            )
            response.raise_for_status()
            raw = response.json()

        if not isinstance(raw, list):
            raise_upstream_error(ValueError("Unexpected upstream response shape"))
        return [FS.StockSymbolItem.model_validate(item) for item in raw]
    except (ValidationError, httpx.HTTPError, ValueError) as exc:
        raise_upstream_error(exc)


# Alias para compatibilidad
stock_symbol = stock_symbols


# ==============================================================================
# 3. Market Status (/stock/market-status)
# ==============================================================================


def market_status(p: FS.MarketStatusParams) -> FS.MarketStatusResponse:
    """Consulta el estado operativo actual de un mercado bursátil (abierto/cerrado/sesión)."""
    try:
        url = f"{__BASE_URL}/stock/market-status"
        extra: Dict[str, Any] = {"exchange": p.exchange}

        with httpx.Client(timeout=20.0, follow_redirects=True) as client:
            response = client.get(
                url, headers=_get_headers(), params=_build_params(extra)
            )
            response.raise_for_status()
            raw = response.json()

        return FS.MarketStatusResponse.model_validate(raw)
    except (ValidationError, httpx.HTTPError, ValueError) as exc:
        raise_upstream_error(exc)


# ==============================================================================
# 4. Market News (/news)
# ==============================================================================


def market_news(p: FS.MarketNewsParams) -> List[FS.NewsArticle]:
    """Obtiene noticias generales del mercado según categoría (general, forex, crypto, merger)."""
    try:
        url = f"{__BASE_URL}/news"
        extra: Dict[str, Any] = {
            "category": p.category,
            "minId": p.min_id if p.min_id is not None else 0,
        }

        with httpx.Client(timeout=20.0, follow_redirects=True) as client:
            response = client.get(
                url, headers=_get_headers(), params=_build_params(extra)
            )
            response.raise_for_status()
            raw = response.json()

        if not isinstance(raw, list):
            raise_upstream_error(ValueError("Unexpected upstream response shape"))
        return [FS.NewsArticle.model_validate(item) for item in raw]
    except (ValidationError, httpx.HTTPError, ValueError) as exc:
        raise_upstream_error(exc)


# ==============================================================================
# 5. Company News (/company-news)
# ==============================================================================


def company_news(p: FS.CompanyNewsParams) -> List[FS.NewsArticle]:
    """Obtiene noticias de una empresa en un rango de fechas determinado."""
    try:
        url = f"{__BASE_URL}/company-news"
        extra: Dict[str, Any] = {
            "symbol": p.symbol,
            "from": str(p.from_date),
            "to": str(p.to_date),
        }

        with httpx.Client(timeout=20.0, follow_redirects=True) as client:
            response = client.get(
                url, headers=_get_headers(), params=_build_params(extra)
            )
            response.raise_for_status()
            raw = response.json()

        if not isinstance(raw, list):
            raise_upstream_error(ValueError("Unexpected upstream response shape"))
        return [FS.NewsArticle.model_validate(item) for item in raw]
    except (ValidationError, httpx.HTTPError, ValueError) as exc:
        raise_upstream_error(exc)


# ==============================================================================
# 6. Insider Sentiment (/stock/insider-sentiment)
# ==============================================================================


def insider_sentiment(
    p: FS.InsiderSentimentParams,
) -> FS.InsiderSentimentResponse:
    """Consulta el sentimiento mensual de insiders (compras/ventas y puntuación MSPR)."""
    try:
        url = f"{__BASE_URL}/stock/insider-sentiment"
        extra: Dict[str, Any] = {"symbol": p.symbol}
        if p.from_date:
            extra["from"] = str(p.from_date)
        if p.to_date:
            extra["to"] = str(p.to_date)

        with httpx.Client(timeout=20.0, follow_redirects=True) as client:
            response = client.get(
                url, headers=_get_headers(), params=_build_params(extra)
            )
            response.raise_for_status()
            raw = response.json()

        return FS.InsiderSentimentResponse.model_validate(raw)
    except (ValidationError, httpx.HTTPError, ValueError) as exc:
        raise_upstream_error(exc)


# ==============================================================================
# 7. Trades (WebSocket & Historical Tick Data)
# ==============================================================================


def historical_ticks(p: FS.HistoricalTickParams) -> FS.HistoricalTickResponse:
    """Obtiene ticks y datos históricos de operaciones para una fecha determinada."""
    try:
        url = f"{__BASE_URL}/stock/tick"
        extra: Dict[str, Any] = {
            "symbol": p.symbol,
            "date": str(p.date),
            "limit": p.limit if p.limit is not None else 500,
            "skip": p.skip if p.skip is not None else 0,
        }

        with httpx.Client(timeout=20.0, follow_redirects=True) as client:
            response = client.get(
                url, headers=_get_headers(), params=_build_params(extra)
            )
            response.raise_for_status()
            raw = response.json()

        return FS.HistoricalTickResponse.model_validate(raw)
    except (ValidationError, httpx.HTTPError, ValueError) as exc:
        raise_upstream_error(exc)


# Alias
stock_tick = historical_ticks


def create_trade_subscription(
    symbol: str, action: str = "subscribe"
) -> FS.WebSocketTradeSubscription:
    """Crea un mensaje estructurado para suscripción/desuscripción a streams WebSocket."""
    return FS.WebSocketTradeSubscription(type=action, symbol=symbol)


def parse_trade_message(
    message: Union[str, dict],
) -> Optional[FS.WebSocketTradeMessage]:
    """Valida y parsea un mensaje entrante del WebSocket de trades en tiempo real."""
    try:
        if isinstance(message, str):
            return FS.WebSocketTradeMessage.model_validate_json(message)
        return FS.WebSocketTradeMessage.model_validate(message)
    except (ValidationError, Exception) as e:
        logger.error(f"[Finnhub] Error al parsear mensaje de trade: {e}")
        return None


# ==============================================================================
# FastAPI Router Endpoints
# ==============================================================================


@router.get(
    "/search",
    response_model=FS.SymbolLookupResponse,
    responses=UPSTREAM_ERROR_RESPONSES,
)
def get_symbol_lookup(
    p: FS.SymbolLookupParams = Depends(),
) -> FS.SymbolLookupResponse:
    return symbol_lookup_params(p)


@router.get(
    "/stock/symbols",
    response_model=List[FS.StockSymbolItem],
    responses=UPSTREAM_ERROR_RESPONSES,
)
def get_stock_symbols(
    p: FS.StockSymbolsParams = Depends(),
) -> List[FS.StockSymbolItem]:
    return stock_symbols(p)


@router.get(
    "/market-status",
    response_model=FS.MarketStatusResponse,
    responses=UPSTREAM_ERROR_RESPONSES,
)
def get_market_status(
    p: FS.MarketStatusParams = Depends(),
) -> FS.MarketStatusResponse:
    return market_status(p)


@router.get(
    "/news",
    response_model=List[FS.NewsArticle],
    responses=UPSTREAM_ERROR_RESPONSES,
)
def get_market_news(
    p: FS.MarketNewsParams = Depends(),
) -> List[FS.NewsArticle]:
    return market_news(p)


@router.get(
    "/company-news",
    response_model=List[FS.NewsArticle],
    responses=UPSTREAM_ERROR_RESPONSES,
)
def get_company_news(
    p: FS.CompanyNewsParams = Depends(),
) -> List[FS.NewsArticle]:
    return company_news(p)


@router.get(
    "/insider-sentiment",
    response_model=FS.InsiderSentimentResponse,
    responses=UPSTREAM_ERROR_RESPONSES,
)
def get_insider_sentiment(
    p: FS.InsiderSentimentParams = Depends(),
) -> FS.InsiderSentimentResponse:
    return insider_sentiment(p)


@router.get(
    "/tick",
    response_model=FS.HistoricalTickResponse,
    responses=UPSTREAM_ERROR_RESPONSES,
)
def get_historical_ticks(
    p: FS.HistoricalTickParams = Depends(),
) -> FS.HistoricalTickResponse:
    return historical_ticks(p)
