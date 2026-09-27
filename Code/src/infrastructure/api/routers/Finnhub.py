import os
from typing import List, Optional, Union
from pydantic import ValidationError
import finnhub
from fastapi import APIRouter, Depends
from ...data_providers.schemas import FinnhubSchema as FS

# API Key extraída de las variables de entorno (.env)
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY", "")
__BASE_URL = "https://api.finnhub.io/api/v1"

finnhub_client = finnhub.Client(api_key=FINNHUB_API_KEY)
router = APIRouter(prefix="/finnhub", tags=["Finnhub"])


# ==============================================================================
# 1. Symbol Lookup (/search)
# ==============================================================================


def symbol_lookup_params(p: FS.SymbolLookupParams) -> Optional[FS.SymbolLookupResponse]:
    """Busca símbolos y empresas por término de búsqueda y filtro opcional de exchange."""
    try:
        if p.exchange:
            raw = finnhub_client._get(
                "/search", params={"q": p.q, "exchange": p.exchange}
            )
        else:
            raw = finnhub_client.symbol_lookup(p.q)
        return FS.SymbolLookupResponse.model_validate(raw)
    except (ValidationError, Exception):
        return None


# ==============================================================================
# 2. Stock Symbols (/stock/symbol)
# ==============================================================================


def stock_symbols(p: FS.StockSymbolsParams) -> Optional[List[FS.StockSymbolItem]]:
    """Obtiene la lista de símbolos soportados para un exchange específico."""
    try:
        raw = finnhub_client.stock_symbols(
            exchange=p.exchange,
            mic=p.mic,
            security_type=p.security_type,
        )
        if not isinstance(raw, list):
            return None
        return [FS.StockSymbolItem.model_validate(item) for item in raw]
    except (ValidationError, Exception):
        return None


# Alias para compatibilidad
stock_symbol = stock_symbols


# ==============================================================================
# 3. Market Status (/stock/market-status)
# ==============================================================================


def market_status(p: FS.MarketStatusParams) -> Optional[FS.MarketStatusResponse]:
    """Consulta el estado operativo actual de un mercado bursátil (abierto/cerrado/sesión)."""
    try:
        raw = finnhub_client.market_status(exchange=p.exchange)
        return FS.MarketStatusResponse.model_validate(raw)
    except (ValidationError, Exception):
        return None


# ==============================================================================
# 4. Market News (/news)
# ==============================================================================


def market_news(p: FS.MarketNewsParams) -> Optional[List[FS.NewsArticle]]:
    """Obtiene noticias generales del mercado según categoría (general, forex, crypto, merger)."""
    try:
        raw = finnhub_client.general_news(
            category=p.category,
            min_id=p.min_id if p.min_id is not None else 0,
        )
        if not isinstance(raw, list):
            return None
        return [FS.NewsArticle.model_validate(item) for item in raw]
    except (ValidationError, Exception):
        return None


# ==============================================================================
# 5. Company News (/company-news)
# ==============================================================================

# TODO: Este va directo a la parte de limpieza para el entrenamiento de AI


def company_news(p: FS.CompanyNewsParams) -> Optional[List[FS.NewsArticle]]:
    """Obtiene noticias de una empresa en un rango de fechas determinado."""
    try:
        raw = finnhub_client.company_news(
            symbol=p.symbol,
            _from=str(p.from_date),
            to=str(p.to_date),
        )
        if not isinstance(raw, list):
            return None
        return [FS.NewsArticle.model_validate(item) for item in raw]
    except (ValidationError, Exception):
        return None


# ==============================================================================
# 6. Insider Sentiment (/stock/insider-sentiment)
# ==============================================================================

# TODO: Este va directo a la parte de limpieza para el entrenamiento de AI


def insider_sentiment(
    p: FS.InsiderSentimentParams,
) -> Optional[FS.InsiderSentimentResponse]:
    """Consulta el sentimiento mensual de insiders (compras/ventas y puntuación MSPR)."""
    try:
        raw = finnhub_client.stock_insider_sentiment(
            symbol=p.symbol,
            _from=p.from_date,
            to=p.to_date,
        )
        return FS.InsiderSentimentResponse.model_validate(raw)
    except (ValidationError, Exception):
        return None


# ==============================================================================
# 7. Trades (WebSocket & Historical Tick Data)
# ==============================================================================

# TODO: Este va directo a la parte de limpieza para el entrenamiento de AI


def historical_ticks(p: FS.HistoricalTickParams) -> Optional[FS.HistoricalTickResponse]:
    """Obtiene ticks y datos históricos de operaciones para una fecha determinada."""
    try:
        raw = finnhub_client.stock_tick(
            symbol=p.symbol,
            date=str(p.date),
            limit=p.limit if p.limit is not None else 500,
            skip=p.skip if p.skip is not None else 0,
        )
        return FS.HistoricalTickResponse.model_validate(raw)
    except (ValidationError, Exception):
        return None


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
    except (ValidationError, Exception):
        return None


# ==============================================================================
# FastAPI Router Endpoints
# ==============================================================================


@router.get("/search", response_model=Optional[FS.SymbolLookupResponse])
def get_symbol_lookup(
    p: FS.SymbolLookupParams = Depends(),
) -> Optional[FS.SymbolLookupResponse]:
    return symbol_lookup_params(p)


@router.get("/stock/symbols", response_model=Optional[List[FS.StockSymbolItem]])
def get_stock_symbols(
    p: FS.StockSymbolsParams = Depends(),
) -> Optional[List[FS.StockSymbolItem]]:
    return stock_symbols(p)


@router.get("/market-status", response_model=Optional[FS.MarketStatusResponse])
def get_market_status(
    p: FS.MarketStatusParams = Depends(),
) -> Optional[FS.MarketStatusResponse]:
    return market_status(p)


@router.get("/news", response_model=Optional[List[FS.NewsArticle]])
def get_market_news(
    p: FS.MarketNewsParams = Depends(),
) -> Optional[List[FS.NewsArticle]]:
    return market_news(p)


@router.get("/company-news", response_model=Optional[List[FS.NewsArticle]])
def get_company_news(
    p: FS.CompanyNewsParams = Depends(),
) -> Optional[List[FS.NewsArticle]]:
    return company_news(p)


@router.get("/insider-sentiment", response_model=Optional[FS.InsiderSentimentResponse])
def get_insider_sentiment(
    p: FS.InsiderSentimentParams = Depends(),
) -> Optional[FS.InsiderSentimentResponse]:
    return insider_sentiment(p)


@router.get("/tick", response_model=Optional[FS.HistoricalTickResponse])
def get_historical_ticks(
    p: FS.HistoricalTickParams = Depends(),
) -> Optional[FS.HistoricalTickResponse]:
    return historical_ticks(p)
