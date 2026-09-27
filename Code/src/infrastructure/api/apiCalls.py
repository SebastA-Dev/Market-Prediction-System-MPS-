from fastapi import FastAPI
from fastapi import Request
import httpx
from .dependencies import lifespan


app = FastAPI(lifespan=lifespan)


def get_http_client(request: Request) -> httpx.AsyncClient:
    """Extrae el cliente HTTP instanciado en el ciclo de vida de la aplicación."""
    return request.app.state.http_client
