"""
Pydantic Schemas for Financial Modeling Prep (FMP) API Data Fetching.

Organized for the Market Prediction System (MPS) Pipeline:
1. Macro & Sectoral Endpoints (INTENT_MACRO & INTENT_SECTORIAL):
   - Sector Performance Snapshot & Historical Sector Performance
   - Treasury Rates / Yield Curve
   - Company / Stock Screener by Sector & Industry

2. Quantitative Fundamentals & Valuation (INTENT_ACTIVO & Qlib Fundamental Alphas):
   - Company Profile (Market Cap, Beta, DCF, Range)
   - Financial Ratios TTM (P/E, P/B, Debt/Equity, Margins, ROE, ROA)
   - Key Metrics TTM (EV, EV/EBITDA, Free Cash Flow, ROIC)
   - Analyst Price Target Consensus

3. Time Series & OHLCV Data (Galformer & Qlib Technical Alpha Factors):
   - Historical Daily Price Full (Open, High, Low, Close, AdjClose, Volume, VWAP)
"""

import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class BaseFMPModel(BaseModel):
    """Base model with configuration allowing field aliases and ignoring extra fields."""
    model_config = ConfigDict(
        populate_by_name=True,
        extra="ignore"
    )


# ==============================================================================
# 1. Macro & Sectoral Schemas (INTENT_MACRO & INTENT_SECTORIAL)
# ==============================================================================

class SectorPerformanceItem(BaseFMPModel):
    """Real-time performance snapshot for a market sector."""
    sector: str = Field(..., description="Name of the economic sector (e.g. Technology)")
    changes_percentage: str = Field(..., alias="changesPercentage", description="Percentage change formatted string (e.g. '0.85%')")


class HistoricalSectorPerformanceItem(BaseFMPModel):
    """Historical daily performance per market sector."""
    date: datetime.date = Field(..., description="Date of observation")
    basic_materials: Optional[float] = Field(None, alias="basicMaterialsChangesPercentage")
    communication_services: Optional[float] = Field(None, alias="communicationServicesChangesPercentage")
    consumer_cyclical: Optional[float] = Field(None, alias="consumerCyclicalChangesPercentage")
    consumer_defensive: Optional[float] = Field(None, alias="consumerDefensiveChangesPercentage")
    energy: Optional[float] = Field(None, alias="energyChangesPercentage")
    financial: Optional[float] = Field(None, alias="financialChangesPercentage")
    healthcare: Optional[float] = Field(None, alias="healthcareChangesPercentage")
    industrials: Optional[float] = Field(None, alias="industrialsChangesPercentage")
    real_estate: Optional[float] = Field(None, alias="realEstateChangesPercentage")
    technology: Optional[float] = Field(None, alias="technologyChangesPercentage")
    utilities: Optional[float] = Field(None, alias="utilitiesChangesPercentage")


class TreasuryRatesParams(BaseFMPModel):
    """Query parameters for US Treasury rates endpoint."""
    from_date: Optional[str] = Field(None, alias="from", description="Start date (YYYY-MM-DD)")
    to_date: Optional[str] = Field(None, alias="to", description="End date (YYYY-MM-DD)")


class TreasuryRatesItem(BaseFMPModel):
    """US Treasury yield curve rates for macro capital distribution."""
    date: datetime.date = Field(..., description="Date of yield curve rates")
    month1: Optional[float] = Field(None, description="1-Month Treasury yield rate (%)")
    month3: Optional[float] = Field(None, description="3-Month Treasury yield rate (%)")
    month6: Optional[float] = Field(None, description="6-Month Treasury yield rate (%)")
    year1: Optional[float] = Field(None, description="1-Year Treasury yield rate (%)")
    year2: Optional[float] = Field(None, description="2-Year Treasury yield rate (%)")
    year5: Optional[float] = Field(None, description="5-Year Treasury yield rate (%)")
    year7: Optional[float] = Field(None, description="7-Year Treasury yield rate (%)")
    year10: Optional[float] = Field(None, description="10-Year Treasury yield rate (%)")
    year20: Optional[float] = Field(None, description="20-Year Treasury yield rate (%)")
    year30: Optional[float] = Field(None, description="30-Year Treasury yield rate (%)")


class CompanyScreenerParams(BaseFMPModel):
    """Query parameters to filter businesses by sector, industry, and size."""
    sector: Optional[str] = Field(None, description="Economic sector (e.g. 'Technology', 'Healthcare')")
    industry: Optional[str] = Field(None, description="Specific industry classification")
    market_cap_more_than: Optional[float] = Field(None, alias="marketCapMoreThan", description="Minimum market cap")
    market_cap_lower_than: Optional[float] = Field(None, alias="marketCapLowerThan", description="Maximum market cap")
    beta_more_than: Optional[float] = Field(None, alias="betaMoreThan", description="Minimum beta")
    beta_lower_than: Optional[float] = Field(None, alias="betaLowerThan", description="Maximum beta")
    limit: Optional[int] = Field(100, description="Max number of screening results")


class CompanyScreenerItem(BaseFMPModel):
    """Screened asset matching sectorial or quantitative criteria."""
    symbol: str = Field(..., description="Stock ticker symbol")
    company_name: str = Field(..., alias="companyName", description="Full company name")
    market_cap: Optional[float] = Field(None, alias="marketCap", description="Market capitalization")
    sector: Optional[str] = Field(None, description="Sector name")
    industry: Optional[str] = Field(None, description="Industry name")
    beta: Optional[float] = Field(None, description="Stock beta")
    price: Optional[float] = Field(None, description="Current price")
    last_annual_dividend: Optional[float] = Field(None, alias="lastAnnualDividend", description="Last annual dividend")
    volume: Optional[float] = Field(None, description="Daily trading volume")
    exchange: Optional[str] = Field(None, description="Exchange code")
    country: Optional[str] = Field(None, description="Country of origin")


# ==============================================================================
# 2. Company Fundamentals & Valuation (INTENT_ACTIVO & Qlib Alphas)
# ==============================================================================

class SymbolParam(BaseFMPModel):
    """Single stock symbol parameter."""
    symbol: str = Field(..., description="Stock ticker symbol (e.g. 'AAPL')")


class CompanyProfileItem(BaseFMPModel):
    """Comprehensive company profile and core valuation metrics."""
    symbol: str = Field(..., description="Stock ticker symbol")
    price: float = Field(..., description="Current stock price")
    beta: Optional[float] = Field(None, description="Beta coefficient")
    vol_avg: Optional[float] = Field(None, alias="volAvg", description="Average daily trading volume")
    mkt_cap: Optional[float] = Field(None, alias="mktCap", description="Market capitalization")
    last_div: Optional[float] = Field(None, alias="lastDiv", description="Last dividend paid")
    range: Optional[str] = Field(None, description="52-week price range")
    changes: Optional[float] = Field(None, description="Daily price change")
    company_name: str = Field(..., alias="companyName", description="Company legal name")
    currency: Optional[str] = Field(None, description="Trading currency")
    exchange: Optional[str] = Field(None, description="Exchange name")
    industry: Optional[str] = Field(None, description="Industry classification")
    sector: Optional[str] = Field(None, description="Sector classification")
    description: Optional[str] = Field(None, description="Business description")
    dcf: Optional[float] = Field(None, description="Discounted Cash Flow intrinsic valuation")


class FinancialRatiosTTMItem(BaseFMPModel):
    """Trailing twelve months financial ratios for quantitative scoring."""
    symbol: Optional[str] = Field(None, description="Ticker symbol")
    dividend_yield_ttm: Optional[float] = Field(None, alias="dividendYielTTM", description="Dividend yield TTM")
    current_ratio_ttm: Optional[float] = Field(None, alias="currentRatioTTM", description="Current liquidity ratio")
    quick_ratio_ttm: Optional[float] = Field(None, alias="quickRatioTTM", description="Quick liquidity ratio")
    cash_ratio_ttm: Optional[float] = Field(None, alias="cashRatioTTM", description="Cash ratio")
    gross_profit_margin_ttm: Optional[float] = Field(None, alias="grossProfitMarginTTM", description="Gross profit margin")
    operating_profit_margin_ttm: Optional[float] = Field(None, alias="operatingProfitMarginTTM", description="Operating profit margin")
    net_profit_margin_ttm: Optional[float] = Field(None, alias="netProfitMarginTTM", description="Net profit margin")
    return_on_equity_ttm: Optional[float] = Field(None, alias="returnOnEquityTTM", description="ROE (Return on Equity)")
    return_on_assets_ttm: Optional[float] = Field(None, alias="returnOnAssetsTTM", description="ROA (Return on Assets)")
    debt_to_equity_ttm: Optional[float] = Field(None, alias="debtToEquityTTM", description="Debt to Equity ratio")
    price_to_earnings_ttm: Optional[float] = Field(None, alias="priceToEarningsTTM", description="P/E ratio TTM")
    price_to_sales_ttm: Optional[float] = Field(None, alias="priceToSalesTTM", description="P/S ratio TTM")
    price_to_book_ttm: Optional[float] = Field(None, alias="priceToBookRatioTTM", description="P/B ratio TTM")


class KeyMetricsTTMItem(BaseFMPModel):
    """Key enterprise metrics TTM for advanced multi-factor valuation."""
    symbol: Optional[str] = Field(None, description="Ticker symbol")
    revenue_per_share_ttm: Optional[float] = Field(None, alias="revenuePerShareTTM")
    net_income_per_share_ttm: Optional[float] = Field(None, alias="netIncomePerShareTTM")
    operating_cash_flow_per_share_ttm: Optional[float] = Field(None, alias="operatingCashFlowPerShareTTM")
    free_cash_flow_per_share_ttm: Optional[float] = Field(None, alias="freeCashFlowPerShareTTM")
    cash_per_share_ttm: Optional[float] = Field(None, alias="cashPerShareTTM")
    pe_ratio_ttm: Optional[float] = Field(None, alias="peRatioTTM")
    pocfratio_ttm: Optional[float] = Field(None, alias="pocfratioTTM", description="Price to Operating Cash Flow")
    pfcf_ratio_ttm: Optional[float] = Field(None, alias="pfcfRatioTTM", description="Price to Free Cash Flow")
    book_value_per_share_ttm: Optional[float] = Field(None, alias="bookValuePerShareTTM")
    enterprise_value_ttm: Optional[float] = Field(None, alias="enterpriseValueTTM", description="Enterprise Value")
    enterprise_value_multiple_ttm: Optional[float] = Field(None, alias="enterpriseValueMultipleTTM", description="EV / EBITDA")
    roic_ttm: Optional[float] = Field(None, alias="roicTTM", description="Return on Invested Capital")


class PriceTargetConsensusItem(BaseFMPModel):
    """Analyst price target consensus and sentiment outlook."""
    symbol: str = Field(..., description="Stock ticker symbol")
    target_high: Optional[float] = Field(None, alias="targetHigh", description="Highest analyst price target")
    target_low: Optional[float] = Field(None, alias="targetLow", description="Lowest analyst price target")
    target_consensus: Optional[float] = Field(None, alias="targetConsensus", description="Consensus average price target")
    target_median: Optional[float] = Field(None, alias="targetMedian", description="Median price target")
    last_updated: Optional[datetime.date] = Field(None, alias="lastUpdated", description="Date of last consensus update")


# ==============================================================================
# 3. Time Series & OHLCV Data (Galformer & Qlib Technical Alpha Factors)
# ==============================================================================

class HistoricalPriceFullParams(BaseFMPModel):
    """Query parameters for full historical price time series."""
    symbol: str = Field(..., description="Stock ticker symbol (e.g. 'AAPL')")
    from_date: Optional[str] = Field(None, alias="from", description="Start date (YYYY-MM-DD)")
    to_date: Optional[str] = Field(None, alias="to", description="End date (YYYY-MM-DD)")


class HistoricalDailyPriceRecord(BaseFMPModel):
    """Daily OHLCV trading candle required by Galformer and Qlib feature extractors."""
    date: datetime.date = Field(..., description="Trading date (YYYY-MM-DD)")
    open: float = Field(..., description="Opening price")
    high: float = Field(..., description="Highest price of the session")
    low: float = Field(..., description="Lowest price of the session")
    close: float = Field(..., description="Closing price")
    adj_close: float = Field(..., alias="adjClose", description="Split and dividend adjusted closing price")
    volume: float = Field(..., description="Trading volume")
    unadjusted_volume: Optional[float] = Field(None, alias="unadjustedVolume", description="Raw trading volume")
    change: Optional[float] = Field(None, description="Absolute price change")
    change_percent: Optional[float] = Field(None, alias="changePercent", description="Percentage price change")
    vwap: Optional[float] = Field(None, description="Volume Weighted Average Price")
    label: Optional[str] = Field(None, description="Readable date label")
    change_over_time: Optional[float] = Field(None, alias="changeOverTime", description="Cumulative change over period")


class HistoricalPriceFullResponse(BaseFMPModel):
    """Full historical price payload containing the continuous time series for Galformer."""
    symbol: str = Field(..., description="Stock ticker symbol")
    historical: List[HistoricalDailyPriceRecord] = Field(default_factory=list, description="List of daily candles")
