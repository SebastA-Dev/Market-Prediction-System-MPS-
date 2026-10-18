import httpx
from fastapi import HTTPException
from pydantic import ValidationError


def raise_upstream_error(exc: Exception) -> None:
    """Expose provider failures as HTTP errors instead of returning HTTP 200/null."""
    if isinstance(exc, httpx.HTTPStatusError):
        status = exc.response.status_code
        # The local API is a gateway; provider 4xx/5xx statuses are useful to callers,
        # while malformed upstream statuses are normalized to 502.
        if 400 <= status <= 599:
            raise HTTPException(
                status_code=status,
                detail=f"Upstream provider returned HTTP {status}",
            ) from exc
    if isinstance(exc, httpx.TimeoutException):
        raise HTTPException(status_code=504, detail="Upstream provider timed out") from exc
    if isinstance(exc, (httpx.HTTPError, ValidationError, ValueError)):
        raise HTTPException(
            status_code=502,
            detail="Upstream provider request failed or returned an invalid response",
        ) from exc
    raise HTTPException(status_code=502, detail="Upstream provider request failed") from exc
