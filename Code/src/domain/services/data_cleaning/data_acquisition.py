"""
Servicio de adquisición de datos financieros.
Consume los routers y clientes de infrastructure (YahooFinance, Polygon, Finnhub, FMP, FRED, CoinGecko)
para descargar series históricas y datos macroeconómicos requeridos por el pipeline analítico.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
import pandas as pd

logger = logging.getLogger(__name__)

# Importación de infraestructura
from infrastructure.api.routers import (
    YahooFinance as YF_router,
    Polygon as PG_router,
    Finnhub as FH_router,
    FMP as FMP_router,
    FRED as FRED_router,
    CoinGecko as CG_router,
)
from infrastructure.data_providers.schemas import (
    YahooFinanceSchemas as YF_schemas,
    PolygonSchemas as PG_schemas,
    FinnhubSchema as FH_schemas,
    FMPSchemas as FMP_schemas,
    FREDSchemas as FRED_schemas,
    CoinGeckoSchemas as CG_schemas,
)


class DataAcquisitionService:
    """
    Coordina la obtención de datos brutos desde múltiples fuentes de mercado.
    Mapea las respuestas estructuradas a DataFrames estandarizados.
    """

    @staticmethod
    def fetch_yahoo_ohlcv(symbol: str, range_str: str = "2y", interval: str = "1d") -> Optional[pd.DataFrame]:
        """
        Descarga velas OHLCV desde Yahoo Finance.
        Retorna DataFrame con columnas: [Date, Open, High, Low, Close, Adj Close, Volume]
        """
        try:
            params = YF_schemas.YahooChartParams(
                symbol=symbol,
                range=range_str,
                interval=interval,
                include_pre_post=False,
            )
            resp = YF_router.chart(params)
            if not resp or not resp.chart or not resp.chart.result:
                logger.warning(f"[DataAcquisition] No se obtuvieron datos de Yahoo Finance para {symbol}")
                return None

            result = resp.chart.result[0]
            timestamps = result.timestamp
            indicators = result.indicators.quote[0]
            adj_close_list = None
            if result.indicators.adjclose and len(result.indicators.adjclose) > 0:
                adj_close_list = result.indicators.adjclose[0].adjclose

            df = pd.DataFrame({
                "Date": pd.to_datetime(timestamps, unit="s"),
                "Open": indicators.open,
                "High": indicators.high,
                "Low": indicators.low,
                "Close": indicators.close,
                "Adj Close": adj_close_list if adj_close_list else indicators.close,
                "Volume": indicators.volume,
            })
            df = df.dropna(subset=["Close"]).reset_index(drop=True)
            logger.info(f"[DataAcquisition] Yahoo Finance: {len(df)} registros descargados para {symbol}")
            return df
        except Exception as e:
            logger.error(f"[DataAcquisition] Error consultando Yahoo Finance para {symbol}: {e}")
            return None

    @staticmethod
    def fetch_polygon_ohlcv(
        ticker: str,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        multiplier: int = 1,
        timespan: str = "day",
    ) -> Optional[pd.DataFrame]:
        """
        Descarga barras OHLCV agregadas desde Polygon.io.
        """
        try:
            if not to_date:
                to_date = datetime.now().strftime("%Y-%m-%d")
            if not from_date:
                from_date = (datetime.now() - timedelta(days=365 * 2)).strftime("%Y-%m-%d")

            params = PG_schemas.AggregatesParams(
                ticker=ticker,
                multiplier=multiplier,
                timespan=timespan,
                from_date=from_date,
                to_date=to_date,
                adjusted=True,
                sort="asc",
                limit=5000,
            )
            resp = PG_router.aggregates(params)
            if not resp or not resp.results:
                logger.warning(f"[DataAcquisition] No se obtuvieron datos de Polygon para {ticker}")
                return None

            records = []
            for bar in resp.results:
                records.append({
                    "Date": pd.to_datetime(bar.t, unit="ms"),
                    "Open": bar.o,
                    "High": bar.h,
                    "Low": bar.l,
                    "Close": bar.c,
                    "Adj Close": bar.c,
                    "Volume": bar.v,
                })
            df = pd.DataFrame(records)
            logger.info(f"[DataAcquisition] Polygon.io: {len(df)} registros descargados para {ticker}")
            return df
        except Exception as e:
            logger.error(f"[DataAcquisition] Error consultando Polygon para {ticker}: {e}")
            return None

    @staticmethod
    def fetch_sector_performance() -> Optional[List[Dict]]:
        """
        Descarga el rendimiento sectorial en tiempo real desde FMP para análisis de contexto y correlación.
        """
        try:
            items = FMP_router.sector_performance()
            if items:
                return [item.model_dump() for item in items]
            return None
        except Exception as e:
            logger.error(f"[DataAcquisition] Error consultando FMP sector_performance: {e}")
            return None

    @staticmethod
    def fetch_macro_series(series_id: str = "GDP", limit: int = 100) -> Optional[pd.DataFrame]:
        """
        Descarga indicadores macroeconómicos desde FRED (ej: VIX, DGS10, GDP, CPI).
        """
        try:
            params = FRED_schemas.FREDObservationsParams(
                series_id=series_id,
                limit=limit,
                sort_order="desc",
            )
            resp = FRED_router.series_observations(params)
            if not resp or not resp.observations:
                return None

            records = [
                {"Date": pd.to_datetime(obs.date), "Value": pd.to_numeric(obs.value, errors="coerce")}
                for obs in resp.observations
            ]
            df = pd.DataFrame(records).dropna().sort_values("Date").reset_index(drop=True)
            return df
        except Exception as e:
            logger.error(f"[DataAcquisition] Error consultando FRED series {series_id}: {e}")
            return None
