import httpx
from fastapi import HTTPException
from pydantic import BaseModel, ValidationError


class APIErrorResponse(BaseModel):
    """Public error shape shared by provider and pipeline endpoints."""

    detail: str


UPSTREAM_ERROR_RESPONSES = {
    code: {"model": APIErrorResponse, "description": description}
    for code, description in {
        300: "Provider redirection could not be completed",
        322: "Provider returned HTTP 322",
        400: "Provider rejected the request",
        401: "Provider authentication failed",
        402: "Provider subscription does not allow this endpoint",
        403: "Provider access is forbidden",
        404: "Provider resource was not found",
        429: "Provider rate limit exceeded",
        500: "Provider failed to process the request",
        502: "Provider returned an invalid response or gateway failure",
        503: "Provider is temporarily unavailable",
        504: "Provider request timed out",
    }.items()
}
UPSTREAM_ERROR_RESPONSES["default"] = {
    "model": APIErrorResponse,
    "description": "Other upstream HTTP error",
}


def raise_upstream_error(exc: Exception) -> None:
    """Expose provider failures as HTTP errors instead of returning HTTP 200/null."""
    if isinstance(exc, HTTPException):
        raise exc
    if isinstance(exc, httpx.HTTPStatusError):
        status = exc.response.status_code
        # Preserve non-2xx provider statuses so clients can identify the failure.
        if 300 <= status <= 599:
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
