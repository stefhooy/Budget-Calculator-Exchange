"""
utils.py — shared helper functions: currency conversion, formatting, image loading, parsing.
"""
import re
import os
import base64
import streamlit as st

from config import CURRENCIES

IMAGES_DIR = os.path.join(os.path.dirname(__file__), "..", "images")


def _image_b64(filename: str) -> str | None:
    path = os.path.join(IMAGES_DIR, filename)
    if os.path.exists(path):
        with open(path, "rb") as f:
            ext = filename.rsplit(".", 1)[-1].lower()
            mime = "image/jpeg" if ext in ("jpg", "jpeg") else f"image/{ext}"
            return f"data:{mime};base64,{base64.b64encode(f.read()).decode()}"
    return None


def convert_amount(amount: float, from_cur: str, to_cur: str) -> float:
    if from_cur == to_cur:
        return amount
    eur = amount / CURRENCIES.get(from_cur, CURRENCIES["EUR"])["rate_to_eur"]
    return eur * CURRENCIES.get(to_cur, CURRENCIES["EUR"])["rate_to_eur"]


def fmt(amount: float, currency: str = None) -> str:
    cur = currency or st.session_state.get("display_currency", "EUR")
    sym = CURRENCIES[cur]["symbol"]
    return f"{sym}{amount:,.2f}"


def to_display(amount: float, original_currency: str) -> float:
    dc = st.session_state.get("display_currency", "EUR")
    return convert_amount(amount, original_currency, dc)


def _detect_currency(raw: str) -> str:
    s = str(raw).strip()
    if "Ft" in s or "ft" in s:
        return "HUF"
    if "€" in s:
        return "EUR"
    if "₺" in s:
        return "TRY"
    if "kr" in s.lower():
        return "SEK"
    if "$" in s:
        return "CAD"
    return "EUR"


def _parse_amount(raw: str) -> float:
    cleaned = re.sub(r"[^\d.,]", "", str(raw).strip())
    cleaned = re.sub(r",(\d{3})(?=\.)", r"\1", cleaned)
    cleaned = cleaned.replace(",", "")
    try:
        return float(cleaned)
    except ValueError:
        return 0.0
