"""
Pydantic Schemas for Yahoo Finance API Data Fetching.

Accessible globally without API keys (via Yahoo Finance v8/v7/v10 endpoints or yfinance library).
Fundamental for MPS:
- Chart v8 API: Continuous OHLCV and Adjusted Close series (matches Galformer input and Qlib datasets).
- Quote v7 API: Real-time multi-asset quotes, valuation multiples, 52-week statistics, and market states.
- QuoteSummary v10 API: Financial data, key statistics, sector/industry profile, and analyst recommendations.
- Search v1 API: Symbol lookup and relevant news for investment tips.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class BaseYahooModel(BaseModel):
    """Base model with configuration allowing field aliases and ignoring extra fields."""
    model_config = ConfigDict(
        populate_by_name=True,
        extra="ignore"
    )


# ==============================================================================
# 1. Chart v8 API (/v8/finance/chart/{symbol}) - Galformer & Qlib Engine
# ==============================================================================

class YahooChartParams(BaseYahooModel):
    """Query parameters for Yahoo Finance chart endpoint."""
    symbol: str = Field(..., description="Asset ticker symbol (e.g. 'AAPL', 'BTC-USD', '^GSPC')")
    range: Optional[str] = Field("1mo", description="Time range (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)")
    interval: Optional[str] = Field("1d", description="Candle interval (1m, 2m, 5m, 15m, 30m, 60m, 1h, 1d, 5d, 1wk, 1mo)")
    include_pre_post: Optional[bool] = Field(False, alias="includePrePost", description="Include pre and post market data")


class YahooChartMeta(BaseYahooModel):
    """Metadata regarding symbol, trading periods, exchange and precision."""
    currency: Optional[str] = None
    symbol: str = Field(..., description="Asset ticker symbol (e.g. 'AAPL', 'BTC-USD', '^GSPC')")
    exchange_name: Optional[str] = Field(None, alias="exchangeName")
    instrument_type: Optional[str] = Field(None, alias="instrumentType")
    first_trade_date: Optional[int] = Field(None, alias="firstTradeDate")
    regular_market_time: Optional[int] = Field(None, alias="regularMarketTime")
    gmtoffset: Optional[int] = None
    timezone: Optional[str] = None
    regular_market_price: Optional[float] = Field(None, alias="regularMarketPrice")
    chart_previous_close: Optional[float] = Field(None, alias="chartPreviousClose")
    previous_close: Optional[float] = Field(None, alias="previousClose")
    data_granularity: Optional[str] = Field(None, alias="dataGranularity")


class YahooQuoteCandles(BaseYahooModel):
    """Raw parallel arrays for OHLCV series."""
    open: List[Optional[float]] = Field(default_factory=list)
    high: List[Optional[float]] = Field(default_factory=list)
    low: List[Optional[float]] = Field(default_factory=list)
    close: List[Optional[float]] = Field(default_factory=list)
    volume: List[Optional[float]] = Field(default_factory=list)


class YahooAdjCloseItem(BaseYahooModel):
    """Adjusted close array."""
    adjclose: List[Optional[float]] = Field(default_factory=list)


class YahooChartIndicators(BaseYahooModel):
    """Container for quote arrays and dividend/split adjusted close."""
    quote: List[YahooQuoteCandles] = Field(default_factory=list)
    adjclose: Optional[List[YahooAdjCloseItem]] = Field(default_factory=list)


class YahooHistoricalBar(BaseYahooModel):
    """Clean standardized OHLCV bar aligned by timestamp for Galformer & Qlib."""
    timestamp: int = Field(..., description="Unix timestamp (seconds)")
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    close: Optional[float] = None
    adj_close: Optional[float] = None
    volume: Optional[float] = None


class YahooChartResultItem(BaseYahooModel):
    """Single chart query result containing time series."""
    meta: YahooChartMeta
    timestamp: List[int] = Field(default_factory=list, description="Array of Unix timestamps")
    indicators: YahooChartIndicators

    def to_historical_bars(self) -> List[YahooHistoricalBar]:
        """Aligns timestamps, OHLCV, and adjclose into clean sequential bars."""
        bars: List[YahooHistoricalBar] = []
        if not self.timestamp or not self.indicators.quote:
            return bars

        quote = self.indicators.quote[0]
        adjclose_list = (
            self.indicators.adjclose[0].adjclose
            if self.indicators.adjclose and len(self.indicators.adjclose) > 0
            else []
        )

        num_points = len(self.timestamp)
        for i in range(num_points):
            t = self.timestamp[i]
            o = quote.open[i] if i < len(quote.open) else None
            h = quote.high[i] if i < len(quote.high) else None
            l = quote.low[i] if i < len(quote.low) else None
            c = quote.close[i] if i < len(quote.close) else None
            v = quote.volume[i] if i < len(quote.volume) else None
            ac = adjclose_list[i] if i < len(adjclose_list) else c

            # Filter out points where close is missing (e.g. market holidays)
            if c is not None:
                bars.append(YahooHistoricalBar(
                    timestamp=t,
                    open=o,
                    high=h,
                    low=l,
                    close=c,
                    adj_close=ac if ac is not None else c,
                    volume=v
                ))
        return bars


class YahooChartEnvelope(BaseYahooModel):
    """Result envelope for chart queries."""
    result: Optional[List[YahooChartResultItem]] = None
    error: Optional[Any] = None


class YahooChartResponse(BaseYahooModel):
    """Root response for Yahoo Finance v8 chart API."""
    chart: YahooChartEnvelope


# ==============================================================================
# 2. Quote v7 API (/v7/finance/quote?symbols=...)
# ==============================================================================

class YahooQuoteParams(BaseYahooModel):
    """Query parameters for Yahoo Finance quote endpoint."""
    symbols: str = Field(..., description="Comma-separated ticker symbols (e.g. 'AAPL,MSFT,BTC-USD')")


class YahooQuoteItem(BaseYahooModel):
    """Real-time market quote, 52-week stats, and valuation metrics."""
    symbol: str = Field(..., description="Asset ticker symbol")
    short_name: Optional[str] = Field(None, alias="shortName")
    long_name: Optional[str] = Field(None, alias="longName")
    currency: Optional[str] = None
    exchange: Optional[str] = None
    market_state: Optional[str] = Field(None, alias="marketState", description="REGULAR, PRE, POST, or CLOSED")
    regular_market_price: Optional[float] = Field(None, alias="regularMarketPrice")
    regular_market_change: Optional[float] = Field(None, alias="regularMarketChange")
    regular_market_change_percent: Optional[float] = Field(None, alias="regularMarketChangePercent")
    regular_market_time: Optional[int] = Field(None, alias="regularMarketTime")
    regular_market_day_high: Optional[float] = Field(None, alias="regularMarketDayHigh")
    regular_market_day_low: Optional[float] = Field(None, alias="regularMarketDayLow")
    regular_market_volume: Optional[float] = Field(None, alias="regularMarketVolume")
    regular_market_previous_close: Optional[float] = Field(None, alias="regularMarketPreviousClose")
    market_cap: Optional[float] = Field(None, alias="marketCap")
    trailing_pe: Optional[float] = Field(None, alias="trailingPE")
    forward_pe: Optional[float] = Field(None, alias="forwardPE")
    eps_trailing_twelve_months: Optional[float] = Field(None, alias="epsTrailingTwelveMonths")
    fifty_two_week_low: Optional[float] = Field(None, alias="fiftyTwoWeekLow")
    fifty_two_week_high: Optional[float] = Field(None, alias="fiftyTwoWeekHigh")
    fifty_two_week_change_percent: Optional[float] = Field(None, alias="fiftyTwoWeekChangePercent")
    fifty_day_average: Optional[float] = Field(None, alias="fiftyDayAverage")
    two_hundred_day_average: Optional[float] = Field(None, alias="twoHundredDayAverage")


class YahooQuoteResponseEnvelope(BaseYahooModel):
    """Enclosure for quote responses."""
    result: List[YahooQuoteItem] = Field(default_factory=list)
    error: Optional[Any] = None


class YahooQuoteResponse(BaseYahooModel):
    """Root response for Yahoo Finance v7 quote endpoint."""
    quote_response: YahooQuoteResponseEnvelope = Field(..., alias="quoteResponse")


# ==============================================================================
# 3. QuoteSummary v10 API (/v10/finance/quoteSummary/{symbol}?modules=...)
# ==============================================================================

class YahooQuoteSummaryParams(BaseYahooModel):
    """Query parameters for Yahoo Finance quote summary endpoint."""
    symbol: str = Field(..., description="Asset ticker symbol (e.g. 'AAPL')")
    modules: Optional[str] = Field("assetProfile,financialData,defaultKeyStatistics", description="Comma-separated module names")


class YahooAssetProfile(BaseYahooModel):
    """Company sector, industry, and corporate overview."""
    sector: Optional[str] = None
    industry: Optional[str] = None
    full_time_employees: Optional[int] = Field(None, alias="fullTimeEmployees")
    long_business_summary: Optional[str] = Field(None, alias="longBusinessSummary")
    country: Optional[str] = None
    website: Optional[str] = None


class YahooFinancialData(BaseYahooModel):
    """Key financial performance, margins, and target prices."""
    current_price: Optional[Dict[str, Any]] = Field(None, alias="currentPrice")
    target_high_price: Optional[Dict[str, Any]] = Field(None, alias="targetHighPrice")
    target_low_price: Optional[Dict[str, Any]] = Field(None, alias="targetLowPrice")
    target_mean_price: Optional[Dict[str, Any]] = Field(None, alias="targetMeanPrice")
    recommendation_mean: Optional[Dict[str, Any]] = Field(None, alias="recommendationMean")
    recommendation_key: Optional[str] = Field(None, alias="recommendationKey")
    total_cash: Optional[Dict[str, Any]] = Field(None, alias="totalCash")
    total_debt: Optional[Dict[str, Any]] = Field(None, alias="totalDebt")
    total_revenue: Optional[Dict[str, Any]] = Field(None, alias="totalRevenue")
    gross_margins: Optional[Dict[str, Any]] = Field(None, alias="grossMargins")
    operating_margins: Optional[Dict[str, Any]] = Field(None, alias="operatingMargins")
    profit_margins: Optional[Dict[str, Any]] = Field(None, alias="profitMargins")


class YahooDefaultKeyStatistics(BaseYahooModel):
    """Enterprise valuation, shares float, and beta."""
    enterprise_value: Optional[Dict[str, Any]] = Field(None, alias="enterpriseValue")
    forward_pe: Optional[Dict[str, Any]] = Field(None, alias="forwardPE")
    profit_margins: Optional[Dict[str, Any]] = Field(None, alias="profitMargins")
    float_shares: Optional[Dict[str, Any]] = Field(None, alias="floatShares")
    shares_outstanding: Optional[Dict[str, Any]] = Field(None, alias="sharesOutstanding")
    beta: Optional[Dict[str, Any]] = None
    book_value: Optional[Dict[str, Any]] = Field(None, alias="bookValue")
    price_to_book: Optional[Dict[str, Any]] = Field(None, alias="priceToBook")


class YahooQuoteSummaryItem(BaseYahooModel):
    """Aggregated modules for an asset."""
    asset_profile: Optional[YahooAssetProfile] = Field(None, alias="assetProfile")
    financial_data: Optional[YahooFinancialData] = Field(None, alias="financialData")
    default_key_statistics: Optional[YahooDefaultKeyStatistics] = Field(None, alias="defaultKeyStatistics")


class YahooQuoteSummaryEnvelope(BaseYahooModel):
    """Enclosure for quote summary results."""
    result: Optional[List[YahooQuoteSummaryItem]] = None
    error: Optional[Any] = None


class YahooQuoteSummaryResponse(BaseYahooModel):
    """Root response for Yahoo Finance v10 quoteSummary endpoint."""
    quote_summary: YahooQuoteSummaryEnvelope = Field(..., alias="quoteSummary")


# ==============================================================================
# 4. Search v1 API (/v1/finance/search?q=...)
# ==============================================================================

class YahooSearchParams(BaseYahooModel):
    """Query parameters for Yahoo Finance search endpoint."""
    q: str = Field(..., description="Search query string (symbol or company name)")
    quotes_count: Optional[int] = Field(10, alias="quotesCount", description="Max number of quotes to return")
    news_count: Optional[int] = Field(5, alias="newsCount", description="Max number of news to return")


class YahooSearchQuoteItem(BaseYahooModel):
    """Ticker match found in search."""
    symbol: str
    shortname: Optional[str] = None
    longname: Optional[str] = None
    exchange: Optional[str] = None
    quote_type: Optional[str] = Field(None, alias="quoteType")
    industry: Optional[str] = None
    sector: Optional[str] = None


class YahooSearchNewsItem(BaseYahooModel):
    """Related news article returned in search."""
    uuid: str
    title: str
    publisher: Optional[str] = None
    link: Optional[str] = None
    provider_publish_time: Optional[int] = Field(None, alias="providerPublishTime")
    type: Optional[str] = None


class YahooSearchResponse(BaseYahooModel):
    """Search endpoint response with matching tickers and news."""
    count: int = Field(0)
    quotes: List[YahooSearchQuoteItem] = Field(default_factory=list)
    news: List[YahooSearchNewsItem] = Field(default_factory=list)
