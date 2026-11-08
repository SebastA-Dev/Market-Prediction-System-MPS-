"""Normalize investment prompts and classify their requested investment scope."""

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
import re
import unicodedata
from typing import Optional


@dataclass(frozen=True)
class IntentClassification:
    normalized_prompt: str
    classified_intent: Optional[str]
    parsed_amount: Optional[float] = None
    parsed_sector: Optional[str] = None
    parsed_ticker: Optional[str] = None
    candidate_sectors: tuple[str, ...] = ()
    clarification: Optional[str] = None

    @property
    def needs_clarification(self) -> bool:
        return self.classified_intent is None or self.clarification is not None


def normalize_prompt(prompt: str) -> str:
    """Lowercase, remove accents and punctuation noise, and collapse whitespace."""
    text = unicodedata.normalize("NFKD", prompt.casefold())
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = text.replace("&", " ")
    text = re.sub(r"[^\w\s.$=^-]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _matches_phrase(text: str, phrase: str) -> bool:
    return re.search(rf"(?<![\w-]){re.escape(phrase)}(?![\w-])", text) is not None


def _parse_amount(prompt: str) -> Optional[float]:
    match = re.search(r"(?<!\w)\$?\s*(\d[\d.,]*)(?!\w)", prompt)
    if not match:
        return None

    value = match.group(1)
    dot, comma = value.rfind("."), value.rfind(",")
    decimal_separator = None
    if dot >= 0 and comma >= 0:
        decimal_separator = "." if dot > comma else ","
    elif dot >= 0 or comma >= 0:
        separator = "." if dot >= 0 else ","
        digits_after = len(value) - value.rfind(separator) - 1
        if digits_after not in (0, 3):
            decimal_separator = separator

    if decimal_separator:
        thousands_separator = "," if decimal_separator == "." else "."
        value = value.replace(thousands_separator, "")
        value = value.replace(decimal_separator, ".")
    else:
        value = value.replace(".", "").replace(",", "")

    try:
        return float(Decimal(value))
    except (InvalidOperation, ValueError):
        return None


_ASSET_ALIASES = {
    "apple": "AAPL",
    "aapl": "AAPL",
    "microsoft": "MSFT",
    "msft": "MSFT",
    "nvidia": "NVDA",
    "nvda": "NVDA",
    "bitcoin": "BTC-USD",
    "btc": "BTC-USD",
    "btc-usd": "BTC-USD",
    "ethereum": "ETH-USD",
    "ether": "ETH-USD",
    "eth": "ETH-USD",
    "eth-usd": "ETH-USD",
    "tesla": "TSLA",
    "tsla": "TSLA",
    "amazon": "AMZN",
    "amzn": "AMZN",
    "google": "GOOGL",
    "alphabet": "GOOGL",
    "googl": "GOOGL",
    "meta": "META",
    "facebook": "META",
    "sp500": "GSPC",
    "s p500": "GSPC",
    "s p 500": "GSPC",
    "s and p 500": "GSPC",
    "gspc": "GSPC",
    "nasdaq": "IXIC",
    "ixic": "IXIC",
    "dow jones": "DJI",
    "dji": "DJI",
}

_SECTOR_ALIASES = {
    "Technology": (
        "tecnologia",
        "tecnologico",
        "tecnologica",
        "tecnologicos",
        "tecnologicas",
        "tech",
        "technology",
        "information technology",
    ),
    "Energy": (
        "energia",
        "energetico",
        "energetica",
        "energeticos",
        "energeticas",
        "energy",
        "petroleo",
        "oil and gas",
    ),
    "Financial Services": (
        "finanzas",
        "financiero",
        "financiera",
        "financieros",
        "financieras",
        "financial",
        "financial services",
        "banca",
        "bancario",
        "bancaria",
    ),
    "Healthcare": (
        "salud",
        "sanitario",
        "sanitaria",
        "sanitarios",
        "sanitarias",
        "health",
        "healthcare",
        "atencion medica",
    ),
    "Consumer Cyclical": (
        "consumo ciclico",
        "consumo discrecional",
        "consumer cyclical",
        "consumer discretionary",
        "retail",
    ),
    "Consumer Defensive": (
        "consumo defensivo",
        "consumo basico",
        "consumer defensive",
        "consumer staples",
    ),
    "Industrials": ("industria", "industrial", "industriales", "industrials"),
    "Basic Materials": (
        "materiales basicos",
        "materiales",
        "basic materials",
        "materials",
    ),
    "Communication Services": (
        "comunicaciones",
        "telecomunicaciones",
        "communication services",
    ),
    "Real Estate": ("bienes raices", "inmobiliario", "inmobiliaria", "real estate"),
    "Utilities": ("servicios publicos", "utilities"),
}

_GLOBAL_ALIASES = (
    "global",
    "globalmente",
    "mercado en general",
    "mercado general",
    "mercado completo",
    "panorama general",
    "economia",
    "macroeconomico",
    "macroeconomica",
    "macro",
    "portafolio",
    "cartera",
    "diversificar",
    "diversificacion",
    "acciones en general",
    "inversion general",
    "inversion global",
)
_INVESTMENT_ACTIONS = (
    "invertir",
    "inversion",
    "inversiones",
    "invierte",
    "invierteme",
    "diversificar",
    "investir",
    "invest",
    "comprar",
    "compra",
    "adquirir",
    "buy",
    "purchase",
)


def classify_investment_prompt(prompt: str) -> IntentClassification:
    """Classify a cleaned prompt as global, sectoral, asset-specific, or unclear."""
    normalized = normalize_prompt(prompt)
    amount = _parse_amount(prompt)

    for alias, ticker in sorted(_ASSET_ALIASES.items(), key=lambda item: -len(item[0])):
        if _matches_phrase(normalized, alias):
            return IntentClassification(
                normalized_prompt=normalized,
                classified_intent="INTENT_ACTIVO",
                parsed_amount=amount,
                parsed_ticker=ticker,
            )

    explicit_ticker = re.search(
        r"(?i:\bticker\b|\bsimbolo\b|\bsymbol\b)\s*[:=]?\s*\$?([A-Z][A-Z0-9.^=_-]{0,9})\b",
        prompt,
    ) or re.search(r"(?<!\w)\$([A-Z][A-Z0-9.^=_-]{0,9})(?!\w)", prompt)
    if explicit_ticker:
        return IntentClassification(
            normalized_prompt=normalized,
            classified_intent="INTENT_ACTIVO",
            parsed_amount=amount,
            parsed_ticker=explicit_ticker.group(1).upper(),
        )

    found_sectors = sorted(
        sector
        for sector, aliases in _SECTOR_ALIASES.items()
        if any(_matches_phrase(normalized, normalize_prompt(alias)) for alias in aliases)
    )
    if len(found_sectors) == 1:
        return IntentClassification(
            normalized_prompt=normalized,
            classified_intent="INTENT_SECTORIAL",
            parsed_amount=amount,
            parsed_sector=found_sectors[0],
            candidate_sectors=tuple(found_sectors),
        )
    if len(found_sectors) > 1:
        return IntentClassification(
            normalized_prompt=normalized,
            classified_intent="INTENT_SECTORIAL",
            parsed_amount=amount,
            candidate_sectors=tuple(found_sectors),
            clarification="Mencionaste varios sectores. Elige uno para continuar.",
        )

    if any(_matches_phrase(normalized, phrase) for phrase in _GLOBAL_ALIASES):
        return IntentClassification(
            normalized_prompt=normalized,
            classified_intent="INTENT_MACRO",
            parsed_amount=amount,
        )

    if amount is not None or any(
        _matches_phrase(normalized, action) for action in _INVESTMENT_ACTIONS
    ):
        return IntentClassification(
            normalized_prompt=normalized,
            classified_intent="INTENT_MACRO",
            parsed_amount=amount,
        )

    return IntentClassification(
        normalized_prompt=normalized,
        classified_intent=None,
        parsed_amount=amount,
        clarification="Indica si buscas una inversión global, un sector o un activo específico.",
    )
