from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()

from .dependencies import lifespan as client_lifespan
from .routers import FMP, FRED, Polygon, YahooFinance


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with client_lifespan(app):
        yield


app = FastAPI(
    title="Market Prediction System API",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(YahooFinance.router, prefix="/api/v1")
app.include_router(Polygon.router, prefix="/api/v1")
app.include_router(FRED.router, prefix="/api/v1")
app.include_router(FMP.router, prefix="/api/v1")


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok"}
