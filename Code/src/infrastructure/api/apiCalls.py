import finnhub
from fastapi import FastAPI
from fastapi import Request
import httpx
from .dependencies import lifespan
from .routers import CoinGecko, Finnhub, FMP, FRED, Polygon, YahooFinance

app = FastAPI(lifespan=lifespan)


def get_http_client(request: Request) -> httpx.AsyncClient:
    """Extrae el cliente HTTP instanciado en el ciclo de vida de la aplicación."""
    return request.app.state.http_client


app.include_router(CoinGecko.router)  #
app.include_router(Finnhub.router)
app.include_router(FMP.router)
app.include_router(FRED.router)
app.include_router(Polygon.router)
app.include_router(YahooFinance.router)


@app.get("/")
def root():
    return {"hola": "hola"}
