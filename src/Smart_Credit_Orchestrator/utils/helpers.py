"""
Helper Utilities – Smart Credit Orchestrator
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Optional


def days_since(due_date_str: str) -> int:
    """
    Calculate how many calendar days have elapsed since the due date.

    Args:
        due_date_str: ISO date string "YYYY-MM-DD".

    Returns:
        Number of days overdue (0 if not yet overdue).
    """
    try:
        due = datetime.fromisoformat(due_date_str).date()
    except ValueError:
        return 0
    delta = date.today() - due
    return max(0, delta.days)


def format_currency(amount: float, currency: str = "INR") -> str:
    """Return a human-readable currency string. e.g. ₹45,000.00"""
    symbols = {"INR": "₹", "USD": "$", "EUR": "€", "GBP": "£"}
    symbol = symbols.get(currency.upper(), currency)
    return f"{symbol}{amount:,.2f}"


def truncate(text: str, max_len: int = 300) -> str:
    """Truncate a string to max_len characters, appending '…' if needed."""
    if len(text) <= max_len:
        return text
    return text[: max_len - 1] + "…"
