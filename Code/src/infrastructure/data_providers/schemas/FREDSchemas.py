"""
Pydantic Schemas for Federal Reserve Economic Data (FRED) API.

Accessible globally (including Colombia) via free API key from the St. Louis Fed.
Crucial for INTENT_MACRO in MPS:
- Series Observations (/fred/series/observations)
- Series Metadata (/fred/series)
- Predefined Macro Indicators (GDP, CPI, Unemployment, Fed Funds, Yield Curve 10Y-2Y, VIX)
"""

import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class BaseFREDModel(BaseModel):
    """Base model with configuration allowing field aliases and ignoring extra fields."""
    model_config = ConfigDict(
        populate_by_name=True,
        extra="ignore"
    )


# ==============================================================================
# Common FRED Macro Series Identifiers
# ==============================================================================

class MacroSeriesID(str, Enum):
    """Canonical economic indicators for macro asset allocation."""
    GDP = "GDP"                           # Gross Domestic Product
    INFLATION_CPI = "CPIAUCSL"            # Consumer Price Index (All Urban Consumers)
    UNEMPLOYMENT_RATE = "UNRATE"          # Civilian Unemployment Rate
    FED_FUNDS_RATE = "FEDFUNDS"           # Federal Funds Effective Rate
    TREASURY_10Y = "DGS10"                # 10-Year Treasury Constant Maturity
    TREASURY_2Y = "DGS2"                  # 2-Year Treasury Constant Maturity
    YIELD_SPREAD_10Y_2Y = "T10Y2Y"        # 10-Year Minus 2-Year Treasury Spread (Yield Curve Inversion)
    VIX_VOLATILITY = "VIXCLS"             # CBOE Volatility Index (VIX)
    M2_MONEY_SUPPLY = "M2SL"              # M2 Money Stock


# ==============================================================================
# 1. Series Observations - /fred/series/observations
# ==============================================================================

class FREDObservationsParams(BaseFREDModel):
    """Query parameters for FRED series observations."""
    series_id: str = Field(..., description="FRED series code (e.g. 'DGS10', 'CPIAUCSL')")
    observation_start: Optional[str] = Field(None, description="Start date (YYYY-MM-DD)")
    observation_end: Optional[str] = Field(None, description="End date (YYYY-MM-DD)")
    limit: Optional[int] = Field(100000, description="Max number of observations (max 100000)")
    offset: Optional[int] = Field(0, description="Offset for pagination")
    sort_order: Optional[str] = Field("asc", description="Sort order: 'asc' or 'desc'")
    units: Optional[str] = Field("lin", description="Data units: 'lin', 'chg', 'ch1', 'pch', 'pc1', 'pca', 'cch', 'cca', 'log'")
    frequency: Optional[str] = Field(None, description="Frequency aggregation (e.g. 'd', 'w', 'm', 'q', 'sa', 'a')")


class FREDObservation(BaseFREDModel):
    """Individual economic time series observation point."""
    date: datetime.date = Field(..., description="Date of observation (YYYY-MM-DD)")
    value_raw: str = Field(..., alias="value", description="Raw string value from FRED (may be '.' for holidays)")
    realtime_start: Optional[str] = None
    realtime_end: Optional[str] = None

    @property
    def value(self) -> Optional[float]:
        """Parsed numeric float value, returning None if FRED reported a missing '.' value."""
        if self.value_raw == "." or not self.value_raw.strip():
            return None
        try:
            return float(self.value_raw)
        except ValueError:
            return None


class FREDObservationsResponse(BaseFREDModel):
    """Container response for series observations query."""
    realtime_start: Optional[str] = None
    realtime_end: Optional[str] = None
    observation_start: Optional[str] = None
    observation_end: Optional[str] = None
    units: Optional[str] = None
    output_type: Optional[int] = None
    file_type: Optional[str] = None
    order_by: Optional[str] = None
    sort_order: Optional[str] = None
    count: Optional[int] = None
    offset: Optional[int] = None
    limit: Optional[int] = None
    observations: List[FREDObservation] = Field(default_factory=list, description="Array of historical observations")

    def to_clean_series(self) -> List[tuple[datetime.date, float]]:
        """Returns non-null (date, float_value) tuples ready for econometric analysis or Qlib features."""
        cleaned = []
        for obs in self.observations:
            val = obs.value
            if val is not None:
                cleaned.append((obs.date, val))
        return cleaned


# ==============================================================================
# 2. Series Metadata - /fred/series
# ==============================================================================

class FREDSeriesParams(BaseFREDModel):
    """Query parameters for FRED series metadata."""
    series_id: str = Field(..., description="FRED series code (e.g. 'DGS10', 'CPIAUCSL')")


class FREDSeriesInfo(BaseFREDModel):
    """Descriptive metadata for an economic series."""
    id: str = Field(..., description="FRED series code (e.g. 'DGS10', 'CPIAUCSL')")
    title: str = Field(..., description="Full descriptive title of the series")
    observation_start: Optional[str] = None
    observation_end: Optional[str] = None
    frequency: Optional[str] = Field(None, description="Observation frequency (e.g. Daily, Monthly, Quarterly)")
    units: Optional[str] = Field(None, description="Units of measurement (e.g. Percent, Billions of Dollars)")
    seasonal_adjustment: Optional[str] = Field(None, description="Seasonal adjustment description")
    last_updated: Optional[str] = None
    notes: Optional[str] = None


class FREDSeriesResponse(BaseFREDModel):
    """Response envelope for series info request."""
    realtime_start: Optional[str] = None
    realtime_end: Optional[str] = None
    seriess: List[FREDSeriesInfo] = Field(default_factory=list, description="Array of series metadata objects")
