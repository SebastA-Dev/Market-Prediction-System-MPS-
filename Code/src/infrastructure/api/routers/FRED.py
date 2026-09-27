import os
from typing import Dict, Optional
import httpx
from pydantic import ValidationError
from fastapi import APIRouter, Depends
from ...data_providers.schemas import FREDSchemas as FRED

# ==============================================================================
# Configuración y Autenticación Federal Reserve Economic Data (FRED)
# ==============================================================================

# TODO: Colocar la API KEY extraida de .env. Crear en .env example
FRED_API_KEY = os.getenv("FRED_API_KEY", "")
__BASE_URL = "https://api.stlouisfed.org/fred"

router = APIRouter(prefix="/fred", tags=["FRED"])


def _get_headers() -> Dict[str, str]:
    """Retorna las cabeceras HTTP estándar para FRED."""
    return {"accept": "application/json"}


def _add_fred_params(params: Optional[dict] = None) -> dict:
    """Inyecta 'api_key' y 'file_type=json' requeridos por FRED API."""
    p = {k: v for k, v in (params or {}).items() if v is not None}
    p["file_type"] = "json"
    if FRED_API_KEY:
        p["api_key"] = FRED_API_KEY
    return p


# ==============================================================================
# 1. Series Observations - GET /fred/series/observations
# ==============================================================================

def series_observations(p: FRED.FREDObservationsParams) -> Optional[FRED.FREDObservationsResponse]:
    """
    Endpoint: GET /fred/series/observations
    Obtiene observaciones históricas de series macroeconómicas (GDP, CPI, UNRATE, DGS10, VIX, etc.).
    """
    try:
        url = f"{__BASE_URL}/series/observations"
        query_params = {
            "series_id": p.series_id,
            "observation_start": p.observation_start,
            "observation_end": p.observation_end,
            "limit": p.limit,
            "offset": p.offset,
            "sort_order": p.sort_order,
            "units": p.units,
            "frequency": p.frequency,
        }
        with httpx.Client(timeout=15.0) as client:
            response = client.get(url, headers=_get_headers(), params=_add_fred_params(query_params))
            response.raise_for_status()
            raw = response.json()

        if not isinstance(raw, dict):
            return None

        return FRED.FREDObservationsResponse.model_validate(raw)
    except (ValidationError, httpx.HTTPError, Exception):
        return None


# ==============================================================================
# 2. Series Metadata - GET /fred/series
# ==============================================================================

def series_metadata(p: FRED.FREDSeriesParams) -> Optional[FRED.FREDSeriesResponse]:
    """
    Endpoint: GET /fred/series
    Obtiene metadatos y descripción detallada de una serie macroeconómica de la Reserva Federal.
    """
    try:
        url = f"{__BASE_URL}/series"
        query_params = {
            "series_id": p.series_id,
        }
        with httpx.Client(timeout=15.0) as client:
            response = client.get(url, headers=_get_headers(), params=_add_fred_params(query_params))
            response.raise_for_status()
            raw = response.json()

        if not isinstance(raw, dict):
            return None

        return FRED.FREDSeriesResponse.model_validate(raw)
    except (ValidationError, httpx.HTTPError, Exception):
        return None


# ==============================================================================
# FastAPI Router Endpoints
# ==============================================================================

@router.get("/series/observations", response_model=Optional[FRED.FREDObservationsResponse])
def get_series_observations(p: FRED.FREDObservationsParams = Depends()) -> Optional[FRED.FREDObservationsResponse]:
    return series_observations(p)


@router.get("/series", response_model=Optional[FRED.FREDSeriesResponse])
def get_series_metadata(p: FRED.FREDSeriesParams = Depends()) -> Optional[FRED.FREDSeriesResponse]:
    return series_metadata(p)
