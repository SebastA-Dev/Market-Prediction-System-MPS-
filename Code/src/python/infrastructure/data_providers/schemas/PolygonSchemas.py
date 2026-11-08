"""
Pydantic Schemas for Polygon.io Free API Data Fetching.

Accessible globally (including Colombia) via free API key (5 calls/min).
Useful for MPS Pipeline:
- Aggregates (Bars / Candlesticks) for Galformer continuous sequences & Qlib features.
- Grouped Daily Bars for cross-asset ranking and market screening.
- Daily Open/Close and Previous Day Close for pricing.
- Ticker Details for fundamental metadata.
- Market Status for operational session checks.
"""

from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class BasePolygonModel(BaseModel):
    """Base model with configuration allowing field aliases and ignoring extra fields."""
    model_config = ConfigDict(
        populate_by_name=True,
        extra="ignore"
    )


# ==============================================================================
# 1. Aggregates (Bars / OHLCV) - /v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{from}/{to}
# ==============================================================================

class AggregatesParams(BasePolygonModel):
    """Query parameters for Aggregates Bars endpoint."""
    ticker: str = Field(..., description="Stock ticker symbol (e.g. 'AAPL')")
    multiplier: int = Field(1, description="Size of the timespan multiplier")
    timespan: str = Field("day", description="Size of the time window: minute, hour, day, week, month, quarter, year")
    from_date: str = Field(..., alias="from", description="Start of aggregate time window (YYYY-MM-DD)")
    to_date: str = Field(..., alias="to", description="End of aggregate time window (YYYY-MM-DD)")
    adjusted: Optional[bool] = Field(True, description="Whether results are split-adjusted")
    sort: Optional[str] = Field("asc", description="Sort order: 'asc' or 'desc'")
    limit: Optional[int] = Field(5000, description="Limits the number of base aggregates (max 50000)")


class AggregateBar(BasePolygonModel):
    """Individual OHLCV candlestick bar."""
    o: float = Field(..., description="Open price")
    h: float = Field(..., description="High price")
    l: float = Field(..., description="Low price")
    c: float = Field(..., description="Close price")
    v: float = Field(..., description="Trading volume")
    vw: Optional[float] = Field(None, description="Volume Weighted Average Price (VWAP)")
    t: int = Field(..., description="Unix millisecond timestamp")
    n: Optional[int] = Field(None, description="Number of transactions in bar")


class AggregatesResponse(BasePolygonModel):
    """Response containing time series bars for Galformer and Qlib feature extraction."""
    ticker: Optional[str] = Field(None, description="Ticker symbol")
    status: str = Field(..., description="Response status (e.g. 'OK')")
    query_count: Optional[int] = Field(None, alias="queryCount", description="Number of aggregates matched")
    results_count: Optional[int] = Field(None, alias="resultsCount", description="Number of aggregates returned")
    adjusted: Optional[bool] = Field(True, description="Whether results are split-adjusted")
    results: List[AggregateBar] = Field(default_factory=list, description="Array of OHLCV bars")


# ==============================================================================
# 2. Grouped Daily (Full Market Snapshot) - /v2/aggs/grouped/locale/us/market/stocks/{date}
# ==============================================================================

class GroupedDailyParams(BasePolygonModel):
    """Query parameters for Grouped Daily Market Snapshot."""
    date: str = Field(..., description="Trading date (YYYY-MM-DD)")
    adjusted: Optional[bool] = Field(True, description="Whether results are split-adjusted")


class GroupedDailyBar(BasePolygonModel):
    """Daily bar for an individual ticker in the grouped market snapshot."""
    t: Optional[int] = Field(None, description="Unix millisecond timestamp")
    ticker: str = Field(..., alias="T", description="Ticker symbol")
    v: float = Field(..., description="Trading volume")
    vw: Optional[float] = Field(None, description="Volume weighted average price")
    o: float = Field(..., description="Open price")
    c: float = Field(..., description="Close price")
    h: float = Field(..., description="High price")
    l: float = Field(..., description="Low price")
    n: Optional[int] = Field(None, description="Number of trades")


class GroupedDailyResponse(BasePolygonModel):
    """Entire US market daily performance across all tickers for a specific date."""
    status: str = Field(..., description="Response status")
    query_count: Optional[int] = Field(None, alias="queryCount")
    results_count: Optional[int] = Field(None, alias="resultsCount")
    adjusted: Optional[bool] = Field(True)
    results: List[GroupedDailyBar] = Field(default_factory=list, description="All traded equities for the day")


# ==============================================================================
# 3. Daily Open / Close - /v1/open-close/{ticker}/{date}
# ==============================================================================

class DailyOpenCloseParams(BasePolygonModel):
    """Query parameters for Daily Open/Close summary."""
    ticker: str = Field(..., description="Stock ticker symbol (e.g. 'AAPL')")
    date: str = Field(..., description="Trading date (YYYY-MM-DD)")
    adjusted: Optional[bool] = Field(True, description="Whether results are split-adjusted")


class DailyOpenCloseResponse(BasePolygonModel):
    """Official session summary including pre-market and after-hours prices."""
    status: str = Field(...)
    from_date: str = Field(..., alias="from", description="Date string YYYY-MM-DD")
    symbol: str = Field(..., description="Ticker symbol")
    open: float = Field(..., description="Open price")
    high: float = Field(..., description="High price")
    low: float = Field(..., description="Low price")
    close: float = Field(..., description="Close price")
    volume: float = Field(..., description="Trading volume")
    after_hours: Optional[float] = Field(None, alias="afterHours", description="After-hours trading price")
    pre_market: Optional[float] = Field(None, alias="preMarket", description="Pre-market trading price")


# ==============================================================================
# 4. Ticker Details v3 - /v3/reference/tickers/{ticker}
# ==============================================================================

class TickerDetailsParams(BasePolygonModel):
    """Query parameters for Ticker Details endpoint."""
    ticker: str = Field(..., description="Stock ticker symbol (e.g. 'AAPL')")
    date: Optional[str] = Field(None, description="Specify a point in time for ticker details (YYYY-MM-DD)")


class TickerAddress(BasePolygonModel):
    """Company headquarters address."""
    address1: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None


class TickerDetails(BasePolygonModel):
    """Reference metadata and classification for a company."""
    ticker: str = Field(..., description="Ticker symbol")
    name: str = Field(..., description="Company name")
    market: Optional[str] = Field(None, description="Market type (e.g. 'stocks', 'crypto')")
    locale: Optional[str] = Field(None, description="Locale (e.g. 'us', 'global')")
    primary_exchange: Optional[str] = Field(None, alias="primary_exchange", description="Primary stock exchange")
    type: Optional[str] = Field(None, description="Security type (e.g. 'CS' for Common Stock)")
    active: bool = Field(True, description="Whether ticker is actively traded")
    currency_name: Optional[str] = Field(None, alias="currency_name", description="Currency (e.g. 'usd')")
    market_cap: Optional[float] = Field(None, alias="market_cap", description="Market capitalization")
    description: Optional[str] = Field(None, description="Business description")
    sic_code: Optional[str] = Field(None, alias="sic_code", description="Standard Industrial Classification code")
    sic_description: Optional[str] = Field(None, alias="sic_description", description="SIC industry description")
    total_employees: Optional[int] = Field(None, alias="total_employees", description="Number of employees")
    share_class_shares_outstanding: Optional[int] = Field(None, alias="share_class_shares_outstanding")
    weighted_shares_outstanding: Optional[int] = Field(None, alias="weighted_shares_outstanding")
    address: Optional[TickerAddress] = None


class TickerDetailsResponse(BasePolygonModel):
    """Response envelope for Ticker Details endpoint."""
    status: str = Field(...)
    request_id: Optional[str] = Field(None, alias="request_id")
    results: TickerDetails = Field(...)


# ==============================================================================
# 5. Market Status - /v1/marketstatus/now
# ==============================================================================

class MarketCurrencies(BasePolygonModel):
    """Current operating status of major currency and crypto markets."""
    fx: Optional[str] = None
    crypto: Optional[str] = None


class MarketExchanges(BasePolygonModel):
    """Operating status of US equity exchanges."""
    nyse: Optional[str] = None
    nasdaq: Optional[str] = None
    otc: Optional[str] = None


class PolygonMarketStatusResponse(BasePolygonModel):
    """Real-time market open/closed status across exchanges."""
    market: str = Field(..., description="Overall market status (e.g. 'open', 'closed', 'extended-hours')")
    server_time: str = Field(..., alias="serverTime", description="Current server timestamp")
    exchanges: Optional[MarketExchanges] = None
    currencies: Optional[MarketCurrencies] = None
