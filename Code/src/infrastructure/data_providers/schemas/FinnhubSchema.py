"""
Pydantic Schemas for Finnhub API Data Fetching.

Covers:
1. Symbol Lookup (/search)
2. Stock Symbols (/stock/symbol)
3. Market Status (/stock/market-status)
4. Market News (/news)
5. Company News (/company-news)
6. Insider Sentiment (/stock/insider-sentiment)
7. Trades (WebSocket real-time trade messages and Historical Tick Data)
"""

import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class BaseFinnhubModel(BaseModel):
    """Base model with configuration allowing field aliases and ignoring extra fields."""
    model_config = ConfigDict(
        populate_by_name=True,
        extra="ignore"
    )


# ==============================================================================
# 1. Symbol Lookup (/search)
# ==============================================================================

class SymbolLookupParams(BaseFinnhubModel):
    """Query parameters for Symbol Lookup."""
    q: str = Field(..., description="Query text to search for (symbol, name, ISIN, CUSIP)")
    exchange: Optional[str] = Field(None, description="Optional exchange filter (e.g. US)")


class SymbolLookupItem(BaseFinnhubModel):
    """Individual match result in symbol search."""
    description: str = Field(..., description="Name or description of the security")
    display_symbol: str = Field(..., alias="displaySymbol", description="Display symbol")
    symbol: str = Field(..., description="Unique symbol identifier used by Finnhub")
    type: str = Field(..., description="Security type (e.g. Common Stock, ETF)")


class SymbolLookupResponse(BaseFinnhubModel):
    """Response model for Symbol Lookup endpoint."""
    count: int = Field(..., description="Number of results found")
    result: List[SymbolLookupItem] = Field(default_factory=list, description="Array of matching symbols")


# ==============================================================================
# 2. Stock Symbols (/stock/symbol)
# ==============================================================================

class StockSymbolsParams(BaseFinnhubModel):
    """Query parameters for Stock Symbols."""
    exchange: str = Field(..., description="Exchange code (e.g. 'US')")
    mic: Optional[str] = Field(None, description="Market Identifier Code (e.g. 'XNAS')")
    security_type: Optional[str] = Field(None, alias="securityType", description="Filter by security type")


class StockSymbolItem(BaseFinnhubModel):
    """Individual supported stock symbol metadata."""
    symbol: str = Field(..., description="Unique symbol for the security")
    display_symbol: str = Field(..., alias="displaySymbol", description="Display symbol")
    description: Optional[str] = Field(None, description="Company or security description")
    currency: Optional[str] = Field(None, description="Currency of price quote (e.g. USD)")
    type: Optional[str] = Field(None, description="Security type (e.g. Common Stock, ADR)")
    mic: Optional[str] = Field(None, description="Primary exchange Market Identifier Code")
    figi: Optional[str] = Field(None, description="OpenFIGI global identifier")
    share_class_figi: Optional[str] = Field(None, alias="shareClassFIGI", description="Share class FIGI")
    isin: Optional[str] = Field(None, description="ISIN code")


# ==============================================================================
# 3. Market Status (/stock/market-status)
# ==============================================================================

class MarketStatusParams(BaseFinnhubModel):
    """Query parameters for Market Status."""
    exchange: str = Field(..., description="Exchange code (e.g. 'US', 'L')")


class MarketStatusResponse(BaseFinnhubModel):
    """Response model indicating current market operating status."""
    exchange: str = Field(..., description="Exchange code")
    is_open: bool = Field(..., alias="isOpen", description="True if market is currently open")
    session: Optional[str] = Field(None, description="Current session: 'pre-market', 'regular', 'post-market', or None")
    holiday: Optional[str] = Field(None, description="Holiday details if market is closed for holiday")
    timezone: Optional[str] = Field(None, description="Exchange timezone (e.g. 'America/New_York')")
    t: Optional[int] = Field(None, description="Current epoch timestamp (seconds)")


# ==============================================================================
# 4. Market News (/news)
# ==============================================================================

class MarketNewsParams(BaseFinnhubModel):
    """Query parameters for general Market News."""
    category: str = Field("general", description="News category: 'general', 'forex', 'crypto', 'merger'")
    min_id: Optional[int] = Field(0, alias="minId", description="Fetch only news with ID strictly greater than this value")


class NewsArticle(BaseFinnhubModel):
    """Common news article model used for both Market and Company News."""
    id: int = Field(..., description="Unique news ID")
    category: str = Field(..., description="News category")
    datetime: int = Field(..., description="Published time (UNIX timestamp)")
    headline: str = Field(..., description="News article headline / title")
    image: Optional[str] = Field(None, description="Thumbnail image URL")
    related: Optional[str] = Field(None, description="Related ticker symbols")
    source: str = Field(..., description="Publisher / source name (e.g. CNBC, Reuters)")
    summary: str = Field(..., description="Article snippet / summary")
    url: str = Field(..., description="Direct link to original article")


# ==============================================================================
# 5. Company News (/company-news)
# ==============================================================================

class CompanyNewsParams(BaseFinnhubModel):
    """Query parameters for Company News."""
    symbol: str = Field(..., description="Company symbol (e.g. 'AAPL')")
    from_date: datetime.date = Field(..., alias="from", description="Start date (YYYY-MM-DD)")
    to_date: datetime.date = Field(..., alias="to", description="End date (YYYY-MM-DD)")


# ==============================================================================
# 6. Insider Sentiment (/stock/insider-sentiment)
# ==============================================================================

class InsiderSentimentParams(BaseFinnhubModel):
    """Query parameters for Insider Sentiment."""
    symbol: str = Field(..., description="Company ticker symbol (e.g. 'AAPL')")
    from_date: Optional[str] = Field(None, alias="from", description="Start date (YYYY-MM-DD)")
    to_date: Optional[str] = Field(None, alias="to", description="End date (YYYY-MM-DD)")


class InsiderSentimentItem(BaseFinnhubModel):
    """Monthly aggregate insider sentiment entry."""
    symbol: str = Field(..., description="Ticker symbol")
    year: int = Field(..., description="Filing year")
    month: int = Field(..., description="Filing month (1-12)")
    change: int = Field(..., description="Net number of shares changed (purchases - sales)")
    mspr: float = Field(..., description="Monthly Sentiment Proprietary Rating [-100 to 100]")
    filing_date: Optional[str] = Field(None, alias="filingDate", description="Filing date string (YYYY-MM-DD)")


class InsiderSentimentResponse(BaseFinnhubModel):
    """Response model for Insider Sentiment."""
    symbol: str = Field(..., description="Ticker symbol")
    data: List[InsiderSentimentItem] = Field(default_factory=list, description="List of monthly sentiment points")


# ==============================================================================
# 7. Trades (WebSocket Streaming & Historical Ticks)
# ==============================================================================

class WebSocketTradeSubscription(BaseFinnhubModel):
    """Subscription / unsubscription message sent to WebSocket server."""
    type: str = Field("subscribe", description="Action type: 'subscribe' or 'unsubscribe'")
    symbol: str = Field(..., description="Ticker symbol to track (e.g. 'AAPL', 'BINANCE:BTCUSDT')")


class TradeDataPoint(BaseFinnhubModel):
    """Individual trade execution event received via WebSocket stream."""
    s: str = Field(..., description="Symbol")
    p: float = Field(..., description="Execution price")
    t: int = Field(..., description="UNIX millisecond timestamp")
    v: float = Field(..., description="Volume / size of the trade")
    c: Optional[List[str]] = Field(default=None, description="Trade condition codes")


class WebSocketTradeMessage(BaseFinnhubModel):
    """Incoming WebSocket trade message packet from Finnhub."""
    type: str = Field("trade", description="Message type indicator (e.g. 'trade', 'ping')")
    data: List[TradeDataPoint] = Field(default_factory=list, description="Array of trade executions")


class HistoricalTickParams(BaseFinnhubModel):
    """Query parameters for historical tick / trade data endpoint (/stock/tick)."""
    symbol: str = Field(..., description="Ticker symbol (e.g. 'AAPL')")
    date: datetime.date = Field(..., description="Trading date (YYYY-MM-DD)")
    limit: Optional[int] = Field(500, description="Number of ticks to return (max 25000)")
    skip: Optional[int] = Field(0, description="Offset for pagination")


class HistoricalTickResponse(BaseFinnhubModel):
    """Response model for historical trade tick data."""
    s: str = Field(..., description="Symbol")
    skip: Optional[int] = Field(0, description="Current offset")
    count: Optional[int] = Field(0, description="Count of ticks in this response")
    total: Optional[int] = Field(0, description="Total ticks available for this date")
    v: List[float] = Field(default_factory=list, description="List of trade volumes")
    p: List[float] = Field(default_factory=list, description="List of trade prices")
    t: List[int] = Field(default_factory=list, description="List of UNIX millisecond timestamps")
    c: Optional[List[List[str]]] = Field(default=None, description="List of trade condition codes")
