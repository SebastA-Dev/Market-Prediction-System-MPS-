"""
Pydantic Schemas for CoinGecko Free / Public Demo API Data Fetching.

Accessible globally (including Colombia) without geographic restrictions.
Crucial for Galformer ('BTC-USD' prediction) and Qlib crypto feature extraction:
- Simple Price (/simple/price)
- Coins Markets (/coins/markets)
- Coin Market Chart (/coins/{id}/market_chart)
- Coin OHLC Candlesticks (/coins/{id}/ohlc)
- Global Market Macro Data (/global)
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class BaseCoinGeckoModel(BaseModel):
    """Base model with configuration allowing field aliases and ignoring extra fields."""
    model_config = ConfigDict(
        populate_by_name=True,
        extra="ignore"
    )


# ==============================================================================
# 1. Simple Price - /api/v3/simple/price
# ==============================================================================

class SimplePriceParams(BaseCoinGeckoModel):
    """Query parameters for Simple Price endpoint (/simple/price)."""
    ids: str = Field(..., description="Comma-separated cryptocurrency IDs (e.g. 'bitcoin,ethereum')")
    vs_currencies: str = Field("usd", description="Comma-separated target fiat/crypto currencies (e.g. 'usd')")
    include_market_cap: Optional[bool] = Field(True, description="Include market cap")
    include_24hr_vol: Optional[bool] = Field(True, description="Include 24-hour volume")
    include_24hr_change: Optional[bool] = Field(True, description="Include 24-hour price change percentage")
    include_last_updated_at: Optional[bool] = Field(True, description="Include last updated timestamp")


class SimplePriceItem(BaseCoinGeckoModel):
    """Current price and 24h statistics for a cryptocurrency."""
    usd: float = Field(..., description="Current price in USD")
    usd_market_cap: Optional[float] = Field(None, description="Market cap in USD")
    usd_24h_vol: Optional[float] = Field(None, description="24-hour volume in USD")
    usd_24h_change: Optional[float] = Field(None, description="24-hour price change percentage")
    last_updated_at: Optional[int] = Field(None, description="Unix timestamp of last update")


# Simple price returns a dictionary mapping coin_id -> SimplePriceItem, e.g. {"bitcoin": {...}}
SimplePriceResponse = Dict[str, SimplePriceItem]


# ==============================================================================
# 2. Coins Markets - /api/v3/coins/markets
# ==============================================================================

class CoinMarketsParams(BaseCoinGeckoModel):
    """Query parameters for Coins Markets endpoint (/coins/markets)."""
    vs_currency: str = Field("usd", description="Target currency (e.g. 'usd')")
    ids: Optional[str] = Field(None, description="Comma-separated coin IDs (e.g. 'bitcoin,ethereum')")
    category: Optional[str] = Field(None, description="Filter by category")
    order: Optional[str] = Field("market_cap_desc", description="Sort order: 'market_cap_desc', 'volume_desc', etc.")
    per_page: Optional[int] = Field(100, ge=1, le=250, description="Results per page (1-250)")
    page: Optional[int] = Field(1, ge=1, description="Page number")
    sparkline: Optional[bool] = Field(False, description="Include sparkline 7d data")
    price_change_percentage: Optional[str] = Field(None, description="Periods for price change percentage (e.g. '1h,24h,7d')")


class CoinMarketItem(BaseCoinGeckoModel):
    """Ranked cryptocurrency market overview and statistics."""
    id: str = Field(..., description="Unique coin ID (e.g. 'bitcoin')")
    symbol: str = Field(..., description="Symbol (e.g. 'btc')")
    name: str = Field(..., description="Name of the cryptocurrency (e.g. 'Bitcoin')")
    image: Optional[str] = Field(None, description="Icon thumbnail URL")
    current_price: float = Field(..., description="Current price in target currency")
    market_cap: float = Field(..., description="Current market capitalization")
    market_cap_rank: Optional[int] = Field(None, description="Rank by market cap")
    fully_diluted_valuation: Optional[float] = Field(None, description="FDV based on max supply")
    total_volume: float = Field(..., description="24-hour trading volume")
    high_24h: Optional[float] = Field(None, description="Highest price in 24 hours")
    low_24h: Optional[float] = Field(None, description="Lowest price in 24 hours")
    price_change_24h: Optional[float] = Field(None, description="Absolute price change in 24h")
    price_change_percentage_24h: Optional[float] = Field(None, description="Percentage price change in 24h")
    circulating_supply: Optional[float] = Field(None, description="Tokens currently in circulation")
    total_supply: Optional[float] = Field(None, description="Total tokens created so far")
    max_supply: Optional[float] = Field(None, description="Maximum possible token supply")
    ath: Optional[float] = Field(None, description="All-time high price")
    ath_change_percentage: Optional[float] = Field(None, description="Percentage distance from ATH")
    ath_date: Optional[str] = Field(None, description="Date when ATH occurred")
    atl: Optional[float] = Field(None, description="All-time low price")
    last_updated: Optional[str] = Field(None, description="Timestamp of last update")


# ==============================================================================
# 3. Market Chart (Historical Time Series) - /api/v3/coins/{id}/market_chart
# ==============================================================================

class MarketChartParams(BaseCoinGeckoModel):
    """Query parameters for Market Chart endpoint (/coins/{id}/market_chart)."""
    id: str = Field(..., description="Unique coin ID (e.g. 'bitcoin')")
    vs_currency: str = Field("usd", description="Target currency (e.g. 'usd')")
    days: str = Field("1", description="Data range in days: 1, 14, 30, 90, 180, 365, max")
    interval: Optional[str] = Field(None, description="Data interval (e.g. 'daily')")


class TimeSeriesPoint(BaseCoinGeckoModel):
    """Timestamped value point [unix_timestamp_ms, value]."""
    timestamp: int = Field(..., description="Unix millisecond timestamp")
    value: float = Field(..., description="Metric value (price, volume, or market cap)")


class MarketChartResponse(BaseCoinGeckoModel):
    """Historical time series data for Galformer multi-step forecasting."""
    prices: List[List[float]] = Field(default_factory=list, description="Array of [timestamp_ms, price]")
    market_caps: List[List[float]] = Field(default_factory=list, description="Array of [timestamp_ms, market_cap]")
    total_volumes: List[List[float]] = Field(default_factory=list, description="Array of [timestamp_ms, total_volume]")

    def to_points(self) -> List[TimeSeriesPoint]:
        """Utility to convert raw price pairs into structured objects."""
        return [TimeSeriesPoint(timestamp=int(p[0]), value=float(p[1])) for p in self.prices]


# ==============================================================================
# 4. OHLC Candlestick Series - /api/v3/coins/{id}/ohlc
# ==============================================================================

class CoinOHLCParams(BaseCoinGeckoModel):
    """Query parameters for OHLC Candlestick endpoint (/coins/{id}/ohlc)."""
    id: str = Field(..., description="Unique coin ID (e.g. 'bitcoin')")
    vs_currency: str = Field("usd", description="Target currency (e.g. 'usd')")
    days: str = Field("1", description="Data range in days: 1, 7, 14, 30, 90, 180, 365")


class CoinOHLCCandle(BaseCoinGeckoModel):
    """Individual OHLC candle parsed from [time_ms, open, high, low, close]."""
    time: int = Field(..., description="Unix millisecond timestamp")
    open: float = Field(..., description="Open price")
    high: float = Field(..., description="High price")
    low: float = Field(..., description="Low price")
    close: float = Field(..., description="Close price")


# ==============================================================================
# 5. Global Market Data (Crypto Macro Context) - /api/v3/global
# ==============================================================================

class GlobalCryptoData(BaseCoinGeckoModel):
    """Macro indicators for the aggregate cryptocurrency market."""
    active_cryptocurrencies: int = Field(..., description="Count of actively tracked coins")
    upcoming_icos: Optional[int] = Field(0)
    ongoing_icos: Optional[int] = Field(0)
    ended_icos: Optional[int] = Field(0)
    markets: int = Field(..., description="Number of trading markets")
    total_market_cap: Dict[str, float] = Field(default_factory=dict, description="Market cap by fiat currency")
    total_volume: Dict[str, float] = Field(default_factory=dict, description="Volume by fiat currency")
    market_cap_percentage: Dict[str, float] = Field(default_factory=dict, description="Dominance % (e.g. btc, eth)")
    market_cap_change_percentage_24h_usd: float = Field(..., description="24h market cap percentage change")
    updated_at: int = Field(..., description="Unix timestamp of update")


class GlobalMarketResponse(BaseCoinGeckoModel):
    """Response envelope for CoinGecko global market data."""
    data: GlobalCryptoData = Field(...)
