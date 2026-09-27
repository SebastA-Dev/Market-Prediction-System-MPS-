import os
from typing import Dict, List, Optional
import httpx
from pydantic import ValidationError
from fastapi import APIRouter, Depends, Query
from ...data_providers.schemas import FMPSchemas as FMP

# ==============================================================================
# Configuración y Autenticación Financial Modeling Prep (FMP)
# ==============================================================================

# TODO: Colocar la API KEY extraida de .env. Crear en .env example
FMP_API_KEY = os.getenv("FMP_API_KEY", "")
__BASE_URL = "https://financialmodelingprep.com"

router = APIRouter(prefix="/fmp", tags=["FMP"])


def _get_headers() -> Dict[str, str]:
    """Retorna las cabeceras HTTP estándar para FMP."""
    return {"accept": "application/json"}


def _add_apikey(params: Optional[dict] = None) -> dict:
    """Inyecta el query param 'apikey' requerido por FMP."""
    p = {k: v for k, v in (params or {}).items() if v is not None}
    if FMP_API_KEY:
        p["apikey"] = FMP_API_KEY
    return p


# ==============================================================================
# 1. Macro & Sectoral Endpoints
# ==============================================================================

def sector_performance() -> Optional[List[FMP.SectorPerformanceItem]]:
    """
    Endpoint: GET /api/v3/sector-performance
    Snapshot de rendimiento en tiempo real por sectores económicos.
    """
    try:
        url = f"{__BASE_URL}/api/v3/sector-performance"
        with httpx.Client(timeout=15.0) as client:
            response = client.get(url, headers=_get_headers(), params=_add_apikey())
            response.raise_for_status()
            raw = response.json()

        if not isinstance(raw, list):
            return None
        return [FMP.SectorPerformanceItem.model_validate(item) for item in raw]
    except (ValidationError, httpx.HTTPError, Exception):
        return None


def historical_sector_performance(limit: int = 50) -> Optional[List[FMP.HistoricalSectorPerformanceItem]]:
    """
    Endpoint: GET /api/v3/historical-sectors-performance
    Rendimiento histórico diario desagregado por sectores.
    """
    try:
        url = f"{__BASE_URL}/api/v3/historical-sectors-performance"
        with httpx.Client(timeout=15.0) as client:
            response = client.get(url, headers=_get_headers(), params=_add_apikey({"limit": limit}))
            response.raise_for_status()
            raw = response.json()

        if not isinstance(raw, list):
            return None
        return [FMP.HistoricalSectorPerformanceItem.model_validate(item) for item in raw]
    except (ValidationError, httpx.HTTPError, Exception):
        return None


def treasury_rates(p: FMP.TreasuryRatesParams) -> Optional[List[FMP.TreasuryRatesItem]]:
    """
    Endpoint: GET /api/v4/treasury
    Tasas de la curva de rendimientos del Tesoro de EE.UU. (1M a 30Y).
    """
    try:
        url = f"{__BASE_URL}/api/v4/treasury"
        query_params = {
            "from": p.from_date,
            "to": p.to_date,
        }
        with httpx.Client(timeout=15.0) as client:
            response = client.get(url, headers=_get_headers(), params=_add_apikey(query_params))
            response.raise_for_status()
            raw = response.json()

        if not isinstance(raw, list):
            return None
        return [FMP.TreasuryRatesItem.model_validate(item) for item in raw]
    except (ValidationError, httpx.HTTPError, Exception):
        return None


def company_screener(p: FMP.CompanyScreenerParams) -> Optional[List[FMP.CompanyScreenerItem]]:
    """
    Endpoint: GET /api/v3/stock-screener
    Filtro cuantitativo de empresas por sector, industria, capitalización y beta.
    """
    try:
        url = f"{__BASE_URL}/api/v3/stock-screener"
        query_params = {
            "sector": p.sector,
            "industry": p.industry,
            "marketCapMoreThan": p.market_cap_more_than,
            "marketCapLowerThan": p.market_cap_lower_than,
            "betaMoreThan": p.beta_more_than,
            "betaLowerThan": p.beta_lower_than,
            "limit": p.limit,
        }
        with httpx.Client(timeout=15.0) as client:
            response = client.get(url, headers=_get_headers(), params=_add_apikey(query_params))
            response.raise_for_status()
            raw = response.json()

        if not isinstance(raw, list):
            return None
        return [FMP.CompanyScreenerItem.model_validate(item) for item in raw]
    except (ValidationError, httpx.HTTPError, Exception):
        return None


# ==============================================================================
# 2. Company Fundamentals & Valuation
# ==============================================================================

def company_profile(p: FMP.SymbolParam) -> Optional[List[FMP.CompanyProfileItem]]:
    """
    Endpoint: GET /api/v3/profile/{symbol}
    Perfil integral, valoración intrínseca DCF, beta y capitalización bursátil.
    """
    try:
        url = f"{__BASE_URL}/api/v3/profile/{p.symbol}"
        with httpx.Client(timeout=15.0) as client:
            response = client.get(url, headers=_get_headers(), params=_add_apikey())
            response.raise_for_status()
            raw = response.json()

        if not isinstance(raw, list):
            return None
        return [FMP.CompanyProfileItem.model_validate(item) for item in raw]
    except (ValidationError, httpx.HTTPError, Exception):
        return None


def ratios_ttm(p: FMP.SymbolParam) -> Optional[List[FMP.FinancialRatiosTTMItem]]:
    """
    Endpoint: GET /api/v3/ratios-ttm/{symbol}
    Ratios financieros trailing twelve months (P/E, P/B, ROE, ROA, Debt/Equity).
    """
    try:
        url = f"{__BASE_URL}/api/v3/ratios-ttm/{p.symbol}"
        with httpx.Client(timeout=15.0) as client:
            response = client.get(url, headers=_get_headers(), params=_add_apikey())
            response.raise_for_status()
            raw = response.json()

        if not isinstance(raw, list):
            return None
        return [FMP.FinancialRatiosTTMItem.model_validate(item) for item in raw]
    except (ValidationError, httpx.HTTPError, Exception):
        return None


def key_metrics_ttm(p: FMP.SymbolParam) -> Optional[List[FMP.KeyMetricsTTMItem]]:
    """
    Endpoint: GET /api/v3/key-metrics-ttm/{symbol}
    Métricas de valoración empresarial TTM (EV, EV/EBITDA, Free Cash Flow, ROIC).
    """
    try:
        url = f"{__BASE_URL}/api/v3/key-metrics-ttm/{p.symbol}"
        with httpx.Client(timeout=15.0) as client:
            response = client.get(url, headers=_get_headers(), params=_add_apikey())
            response.raise_for_status()
            raw = response.json()

        if not isinstance(raw, list):
            return None
        return [FMP.KeyMetricsTTMItem.model_validate(item) for item in raw]
    except (ValidationError, httpx.HTTPError, Exception):
        return None


def price_target_consensus(p: FMP.SymbolParam) -> Optional[List[FMP.PriceTargetConsensusItem]]:
    """
    Endpoint: GET /api/v4/price-target-consensus
    Consenso de precios objetivo de analistas (high, low, median, consensus).
    """
    try:
        url = f"{__BASE_URL}/api/v4/price-target-consensus"
        with httpx.Client(timeout=15.0) as client:
            response = client.get(url, headers=_get_headers(), params=_add_apikey({"symbol": p.symbol}))
            response.raise_for_status()
            raw = response.json()

        if not isinstance(raw, list):
            return None
        return [FMP.PriceTargetConsensusItem.model_validate(item) for item in raw]
    except (ValidationError, httpx.HTTPError, Exception):
        return None


# ==============================================================================
# 3. Time Series & OHLCV Data
# ==============================================================================

def historical_price_full(p: FMP.HistoricalPriceFullParams) -> Optional[FMP.HistoricalPriceFullResponse]:
    """
    Endpoint: GET /api/v3/historical-price-full/{symbol}
    Serie de tiempo histórica diaria completa con precios ajustados y volumen para Galformer.
    """
    try:
        url = f"{__BASE_URL}/api/v3/historical-price-full/{p.symbol}"
        query_params = {
            "from": p.from_date,
            "to": p.to_date,
        }
        with httpx.Client(timeout=20.0) as client:
            response = client.get(url, headers=_get_headers(), params=_add_apikey(query_params))
            response.raise_for_status()
            raw = response.json()

        if not isinstance(raw, dict):
            return None
        return FMP.HistoricalPriceFullResponse.model_validate(raw)
    except (ValidationError, httpx.HTTPError, Exception):
        return None


# ==============================================================================
# FastAPI Router Endpoints
# ==============================================================================

@router.get("/sector-performance", response_model=Optional[List[FMP.SectorPerformanceItem]])
def get_sector_performance() -> Optional[List[FMP.SectorPerformanceItem]]:
    return sector_performance()


@router.get("/historical-sectors-performance", response_model=Optional[List[FMP.HistoricalSectorPerformanceItem]])
def get_historical_sectors_performance(limit: int = Query(50, ge=1, le=500)) -> Optional[List[FMP.HistoricalSectorPerformanceItem]]:
    return historical_sector_performance(limit=limit)


@router.get("/treasury", response_model=Optional[List[FMP.TreasuryRatesItem]])
def get_treasury_rates(p: FMP.TreasuryRatesParams = Depends()) -> Optional[List[FMP.TreasuryRatesItem]]:
    return treasury_rates(p)


@router.get("/stock-screener", response_model=Optional[List[FMP.CompanyScreenerItem]])
def get_company_screener(p: FMP.CompanyScreenerParams = Depends()) -> Optional[List[FMP.CompanyScreenerItem]]:
    return company_screener(p)


@router.get("/profile", response_model=Optional[List[FMP.CompanyProfileItem]])
def get_company_profile(p: FMP.SymbolParam = Depends()) -> Optional[List[FMP.CompanyProfileItem]]:
    return company_profile(p)


@router.get("/ratios-ttm", response_model=Optional[List[FMP.FinancialRatiosTTMItem]])
def get_ratios_ttm(p: FMP.SymbolParam = Depends()) -> Optional[List[FMP.FinancialRatiosTTMItem]]:
    return ratios_ttm(p)


@router.get("/key-metrics-ttm", response_model=Optional[List[FMP.KeyMetricsTTMItem]])
def get_key_metrics_ttm(p: FMP.SymbolParam = Depends()) -> Optional[List[FMP.KeyMetricsTTMItem]]:
    return key_metrics_ttm(p)


@router.get("/price-target-consensus", response_model=Optional[List[FMP.PriceTargetConsensusItem]])
def get_price_target_consensus(p: FMP.SymbolParam = Depends()) -> Optional[List[FMP.PriceTargetConsensusItem]]:
    return price_target_consensus(p)


@router.get("/historical-price-full", response_model=Optional[FMP.HistoricalPriceFullResponse])
def get_historical_price_full(p: FMP.HistoricalPriceFullParams = Depends()) -> Optional[FMP.HistoricalPriceFullResponse]:
    return historical_price_full(p)
