from typing import Dict, Optional, Tuple
import httpx
from pydantic import ValidationError
from fastapi import APIRouter, Depends
from ...data_providers.schemas import YahooFinanceSchemas as YF

# ==============================================================================
# Configuración Yahoo Finance API v8 / v7 / v10 / v1
# ==============================================================================

__BASE_URL = "https://query2.finance.yahoo.com"
__USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

router = APIRouter(prefix="/yahoo", tags=["YahooFinance"])

_cached_crumb: Optional[str] = None
_cached_cookies: Optional[httpx.Cookies] = None


def _get_headers() -> Dict[str, str]:
    """Retorna las cabeceras requeridas para evitar bloqueos por parte de Yahoo Finance."""
    return {
        "User-Agent": __USER_AGENT,
        "Accept": "application/json",
    }


def _get_session_and_crumb() -> Tuple[httpx.Client, Optional[str]]:
    """
    Obtiene o reutiliza la cookie de sesión y el token 'crumb' requeridos
    por los endpoints v7 (quote) y v10 (quoteSummary) de Yahoo Finance.
    """
    global _cached_crumb, _cached_cookies

    client = httpx.Client(headers=_get_headers(), timeout=15.0, cookies=_cached_cookies)

    if _cached_crumb is not None:
        return client, _cached_crumb

    try:
        # 1. Obtener cookie de sesión desde fc.yahoo.com
        client.get("https://fc.yahoo.com")
        # 2. Obtener crumb de autenticación
        crumb_resp = client.get(f"{__BASE_URL}/v1/test/getcrumb")
        if crumb_resp.status_code == 200 and crumb_resp.text:
            _cached_crumb = crumb_resp.text.strip()
            _cached_cookies = client.cookies
            return client, _cached_crumb
    except Exception:
        pass

    return client, None


# ==============================================================================
# 1. Chart v8 API - GET /v8/finance/chart/{symbol}
# ==============================================================================

def chart(p: YF.YahooChartParams) -> Optional[YF.YahooChartResponse]:
    """
    Endpoint: GET /v8/finance/chart/{symbol}
    Obtiene series de tiempo continuas OHLCV y precio de cierre ajustado (Galformer & Qlib).
    """
    try:
        url = f"{__BASE_URL}/v8/finance/chart/{p.symbol}"
        params = {
            "range": p.range,
            "interval": p.interval,
            "includePrePost": str(p.include_pre_post).lower() if p.include_pre_post is not None else "false",
        }
        clean_params = {k: v for k, v in params.items() if v is not None}

        with httpx.Client(headers=_get_headers(), timeout=15.0) as client:
            response = client.get(url, params=clean_params)
            response.raise_for_status()
            raw = response.json()

        if not isinstance(raw, dict):
            return None

        return YF.YahooChartResponse.model_validate(raw)
    except (ValidationError, httpx.HTTPError, Exception):
        return None


# ==============================================================================
# 2. Quote v7 API - GET /v7/finance/quote?symbols=...
# ==============================================================================

def quote(p: YF.YahooQuoteParams) -> Optional[YF.YahooQuoteResponse]:
    """
    Endpoint: GET /v7/finance/quote
    Cotizaciones multi-activo en tiempo real, múltiplos P/E, estadísticas de 52 semanas y estado del mercado.
    """
    try:
        client, crumb = _get_session_and_crumb()
        url = f"{__BASE_URL}/v7/finance/quote"
        params = {"symbols": p.symbols}
        if crumb:
            params["crumb"] = crumb

        with client:
            response = client.get(url, params=params)
            response.raise_for_status()
            raw = response.json()

        if not isinstance(raw, dict):
            return None

        return YF.YahooQuoteResponse.model_validate(raw)
    except (ValidationError, httpx.HTTPError, Exception):
        return None


# ==============================================================================
# 3. QuoteSummary v10 API - GET /v10/finance/quoteSummary/{symbol}?modules=...
# ==============================================================================

def quote_summary(p: YF.YahooQuoteSummaryParams) -> Optional[YF.YahooQuoteSummaryResponse]:
    """
    Endpoint: GET /v10/finance/quoteSummary/{symbol}
    Módulos de información financiera, perfil corporativo y estadísticas de valoración.
    """
    try:
        client, crumb = _get_session_and_crumb()
        url = f"{__BASE_URL}/v10/finance/quoteSummary/{p.symbol}"
        params = {"modules": p.modules or "assetProfile,financialData,defaultKeyStatistics"}
        if crumb:
            params["crumb"] = crumb

        with client:
            response = client.get(url, params=params)
            response.raise_for_status()
            raw = response.json()

        if not isinstance(raw, dict):
            return None

        return YF.YahooQuoteSummaryResponse.model_validate(raw)
    except (ValidationError, httpx.HTTPError, Exception):
        return None


# ==============================================================================
# 4. Search v1 API - GET /v1/finance/search?q=...
# ==============================================================================

def search(p: YF.YahooSearchParams) -> Optional[YF.YahooSearchResponse]:
    """
    Endpoint: GET /v1/finance/search
    Búsqueda de tickers, empresas coincidentes y noticias financieras relevantes.
    """
    try:
        url = f"{__BASE_URL}/v1/finance/search"
        params = {
            "q": p.q,
            "quotesCount": p.quotes_count,
            "newsCount": p.news_count,
        }
        clean_params = {k: v for k, v in params.items() if v is not None}

        with httpx.Client(headers=_get_headers(), timeout=15.0) as client:
            response = client.get(url, params=clean_params)
            response.raise_for_status()
            raw = response.json()

        if not isinstance(raw, dict):
            return None

        return YF.YahooSearchResponse.model_validate(raw)
    except (ValidationError, httpx.HTTPError, Exception):
        return None


# ==============================================================================
# FastAPI Router Endpoints
# ==============================================================================

@router.get("/chart", response_model=Optional[YF.YahooChartResponse])
def get_chart(p: YF.YahooChartParams = Depends()) -> Optional[YF.YahooChartResponse]:
    return chart(p)


@router.get("/quote", response_model=Optional[YF.YahooQuoteResponse])
def get_quote(p: YF.YahooQuoteParams = Depends()) -> Optional[YF.YahooQuoteResponse]:
    return quote(p)


@router.get("/quote-summary", response_model=Optional[YF.YahooQuoteSummaryResponse])
def get_quote_summary(p: YF.YahooQuoteSummaryParams = Depends()) -> Optional[YF.YahooQuoteSummaryResponse]:
    return quote_summary(p)


@router.get("/search", response_model=Optional[YF.YahooSearchResponse])
def get_search(p: YF.YahooSearchParams = Depends()) -> Optional[YF.YahooSearchResponse]:
    return search(p)
