import os
from datetime import date
from typing import Dict, List, Optional
import httpx
from pydantic import ValidationError
from fastapi import APIRouter, Depends, Query
from ...data_providers.schemas import FMPSchemas as FMP
from ..errors import raise_upstream_error

# ==============================================================================
# Configuración y Autenticación Financial Modeling Prep (FMP)
# ==============================================================================

FMP_API_KEY = os.getenv("FMP_APIKEY", "")
__BASE_URL = "https://financialmodelingprep.com/stable"

router = APIRouter(prefix="/fmp", tags=["FMP"])


def _get_headers() -> Dict[str, str]:
    """Autentica por cabecera para no exponer la clave en URLs y logs."""
    headers = {"accept": "application/json"}
    if FMP_API_KEY:
        headers["apikey"] = FMP_API_KEY
    return headers


def _add_apikey(params: Optional[dict] = None) -> dict:
    """Elimina parámetros nulos; la clave viaja en el encabezado apikey."""
    return {k: v for k, v in (params or {}).items() if v is not None}


# ==============================================================================
# 1. Macro & Sectoral Endpoints
# ==============================================================================


def sector_performance(snapshot_date: Optional[str] = None) -> Optional[List[FMP.SectorPerformanceItem]]:
    """
    Endpoint: GET /stable/sector-performance-snapshot?date=...
    Snapshot diario de rendimiento por sectores económicos.
    """
    try:
        url = f"{__BASE_URL}/sector-performance-snapshot"
        params = {"date": snapshot_date or date.today().isoformat()}
        with httpx.Client(timeout=15.0) as client:
            response = client.get(url, headers=_get_headers(), params=_add_apikey(params))
            response.raise_for_status()
            raw = response.json()

        if not isinstance(raw, list):
            return None
        return [FMP.SectorPerformanceItem.model_validate(item) for item in raw]
    except (ValidationError, httpx.HTTPError, ValueError) as exc:
        raise_upstream_error(exc)


def historical_sector_performance(
    p: FMP.HistoricalSectorPerformanceParams,
) -> Optional[List[FMP.HistoricalSectorPerformanceItem]]:
    """
    Endpoint: GET /stable/historical-sector-performance?sector=...
    Rendimiento histórico diario para el sector seleccionado.
    """
    try:
        url = f"{__BASE_URL}/historical-sector-performance"
        query_params = {
            "sector": p.sector,
            "from": p.from_date,
            "to": p.to_date,
            "exchange": p.exchange,
        }
        with httpx.Client(timeout=15.0) as client:
            response = client.get(
                url, headers=_get_headers(), params=_add_apikey(query_params)
            )
            response.raise_for_status()
            raw = response.json()

        if not isinstance(raw, list):
            return None
        return [
            FMP.HistoricalSectorPerformanceItem.model_validate(item) for item in raw
        ]
    except (ValidationError, httpx.HTTPError, ValueError) as exc:
        raise_upstream_error(exc)


def treasury_rates(p: FMP.TreasuryRatesParams) -> Optional[List[FMP.TreasuryRatesItem]]:
    """
    Endpoint: GET /stable/treasury-rates
    Tasas de la curva de rendimientos del Tesoro de EE.UU. (1M a 30Y).
    """
    try:
        url = f"{__BASE_URL}/treasury-rates"
        query_params = {
            "from": p.from_date,
            "to": p.to_date,
        }
        with httpx.Client(timeout=15.0) as client:
            response = client.get(
                url, headers=_get_headers(), params=_add_apikey(query_params)
            )
            response.raise_for_status()
            raw = response.json()

        if not isinstance(raw, list):
            return None
        return [FMP.TreasuryRatesItem.model_validate(item) for item in raw]
    except (ValidationError, httpx.HTTPError, ValueError) as exc:
        raise_upstream_error(exc)


def company_screener(
    p: FMP.CompanyScreenerParams,
) -> Optional[List[FMP.CompanyScreenerItem]]:
    """
    Endpoint: GET /stable/company-screener
    Filtro cuantitativo de empresas por sector, industria, capitalización y beta.
    """
    try:
        url = f"{__BASE_URL}/company-screener"
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
            response = client.get(
                url, headers=_get_headers(), params=_add_apikey(query_params)
            )
            response.raise_for_status()
            raw = response.json()

        if not isinstance(raw, list):
            return None
        return [FMP.CompanyScreenerItem.model_validate(item) for item in raw]
    except (ValidationError, httpx.HTTPError, ValueError) as exc:
        raise_upstream_error(exc)


# ==============================================================================
# 2. Company Fundamentals & Valuation
# ==============================================================================


def company_profile(p: FMP.SymbolParam) -> Optional[List[FMP.CompanyProfileItem]]:
    """
    Endpoint: GET /stable/profile?symbol=...
    Perfil integral, valoración intrínseca DCF, beta y capitalización bursátil.
    """
    try:
        url = f"{__BASE_URL}/profile"
        with httpx.Client(timeout=15.0) as client:
            response = client.get(url, headers=_get_headers(), params=_add_apikey({"symbol": p.symbol}))
            response.raise_for_status()
            raw = response.json()

        if not isinstance(raw, list):
            return None
        return [FMP.CompanyProfileItem.model_validate(item) for item in raw]
    except (ValidationError, httpx.HTTPError, ValueError) as exc:
        raise_upstream_error(exc)


def ratios_ttm(p: FMP.SymbolParam) -> Optional[List[FMP.FinancialRatiosTTMItem]]:
    """
    Endpoint: GET /stable/ratios-ttm?symbol=...
    Ratios financieros trailing twelve months (P/E, P/B, ROE, ROA, Debt/Equity).
    """
    try:
        url = f"{__BASE_URL}/ratios-ttm"
        with httpx.Client(timeout=15.0) as client:
            response = client.get(url, headers=_get_headers(), params=_add_apikey({"symbol": p.symbol}))
            response.raise_for_status()
            raw = response.json()

        if not isinstance(raw, list):
            return None
        return [FMP.FinancialRatiosTTMItem.model_validate(item) for item in raw]
    except (ValidationError, httpx.HTTPError, ValueError) as exc:
        raise_upstream_error(exc)


def key_metrics_ttm(p: FMP.SymbolParam) -> Optional[List[FMP.KeyMetricsTTMItem]]:
    """
    Endpoint: GET /stable/key-metrics-ttm?symbol=...
    Métricas de valoración empresarial TTM (EV, EV/EBITDA, Free Cash Flow, ROIC).
    """
    try:
        url = f"{__BASE_URL}/key-metrics-ttm"
        with httpx.Client(timeout=15.0) as client:
            response = client.get(url, headers=_get_headers(), params=_add_apikey({"symbol": p.symbol}))
            response.raise_for_status()
            raw = response.json()

        if not isinstance(raw, list):
            return None
        return [FMP.KeyMetricsTTMItem.model_validate(item) for item in raw]
    except (ValidationError, httpx.HTTPError, ValueError) as exc:
        raise_upstream_error(exc)


def price_target_consensus(
    p: FMP.SymbolParam,
) -> Optional[List[FMP.PriceTargetConsensusItem]]:
    """
    Endpoint: GET /stable/price-target-consensus?symbol=...
    Consenso de precios objetivo de analistas (high, low, median, consensus).
    """
    try:
        url = f"{__BASE_URL}/price-target-consensus"
        with httpx.Client(timeout=15.0) as client:
            response = client.get(
                url, headers=_get_headers(), params=_add_apikey({"symbol": p.symbol})
            )
            response.raise_for_status()
            raw = response.json()

        if not isinstance(raw, list):
            return None
        return [FMP.PriceTargetConsensusItem.model_validate(item) for item in raw]
    except (ValidationError, httpx.HTTPError, ValueError) as exc:
        raise_upstream_error(exc)


# ==============================================================================
# 3. Time Series & OHLCV Data
# ==============================================================================


def historical_price_full(
    p: FMP.HistoricalPriceFullParams,
) -> Optional[FMP.HistoricalPriceFullResponse]:
    """
    Endpoint: GET /stable/historical-price-eod/full?symbol=...
    Serie de tiempo histórica diaria completa con precios ajustados y volumen para Galformer.
    """
    try:
        url = f"{__BASE_URL}/historical-price-eod/full"
        query_params = {
            "symbol": p.symbol,
            "from": p.from_date,
            "to": p.to_date,
        }
        with httpx.Client(timeout=20.0) as client:
            response = client.get(
                url, headers=_get_headers(), params=_add_apikey(query_params)
            )
            response.raise_for_status()
            raw = response.json()

        if not isinstance(raw, list):
            return None
        records = [FMP.HistoricalDailyPriceRecord.model_validate(item) for item in raw]
        return FMP.HistoricalPriceFullResponse(symbol=p.symbol, historical=records)
    except (ValidationError, httpx.HTTPError, ValueError) as exc:
        raise_upstream_error(exc)


# ==============================================================================
# FastAPI Router Endpoints
# ==============================================================================


@router.get(
    "/sector-performance", response_model=Optional[List[FMP.SectorPerformanceItem]]
)
def get_sector_performance(
    snapshot_date: Optional[str] = Query(None, alias="date"),
) -> Optional[List[FMP.SectorPerformanceItem]]:
    return sector_performance(snapshot_date=snapshot_date)


@router.get(
    "/historical-sectors-performance",
    response_model=Optional[List[FMP.HistoricalSectorPerformanceItem]],
)
def get_historical_sectors_performance(
    p: FMP.HistoricalSectorPerformanceParams = Depends(),
) -> Optional[List[FMP.HistoricalSectorPerformanceItem]]:
    return historical_sector_performance(p)


@router.get("/treasury", response_model=Optional[List[FMP.TreasuryRatesItem]])
def get_treasury_rates(
    p: FMP.TreasuryRatesParams = Depends(),
) -> Optional[List[FMP.TreasuryRatesItem]]:
    return treasury_rates(p)


@router.get("/profile", response_model=Optional[List[FMP.CompanyProfileItem]])
def get_company_profile(
    p: FMP.SymbolParam = Depends(),
) -> Optional[List[FMP.CompanyProfileItem]]:
    return company_profile(p)


@router.get("/ratios-ttm", response_model=Optional[List[FMP.FinancialRatiosTTMItem]])
def get_ratios_ttm(
    p: FMP.SymbolParam = Depends(),
) -> Optional[List[FMP.FinancialRatiosTTMItem]]:
    return ratios_ttm(p)


@router.get("/key-metrics-ttm", response_model=Optional[List[FMP.KeyMetricsTTMItem]])
def get_key_metrics_ttm(
    p: FMP.SymbolParam = Depends(),
) -> Optional[List[FMP.KeyMetricsTTMItem]]:
    return key_metrics_ttm(p)


@router.get(
    "/price-target-consensus",
    response_model=Optional[List[FMP.PriceTargetConsensusItem]],
)
def get_price_target_consensus(
    p: FMP.SymbolParam = Depends(),
) -> Optional[List[FMP.PriceTargetConsensusItem]]:
    return price_target_consensus(p)


@router.get(
    "/historical-price-full", response_model=Optional[FMP.HistoricalPriceFullResponse]
)
def get_historical_price_full(
    p: FMP.HistoricalPriceFullParams = Depends(),
) -> Optional[FMP.HistoricalPriceFullResponse]:
    return historical_price_full(p)
