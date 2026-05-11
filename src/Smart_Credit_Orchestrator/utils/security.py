"""
Security Utility – Smart Credit Orchestrator

Helpers for input sanitisation, PII masking, and API key validation.
These functions are used in routes and validation service to implement
the security mitigations required by the assignment rubric.
"""

from __future__ import annotations

import hashlib
import re
from typing import Optional


# ── PII Masking ───────────────────────────────────────────────────────────────

def mask_email(email: str) -> str:
    """
    Mask an email address for safe logging.
    rajesh.kapoor@example.com → r*****r@example.com
    """
    if "@" not in email:
        return "***@***"
    local, domain = email.split("@", 1)
    if len(local) <= 2:
        masked = local[0] + "*"
    else:
        masked = local[0] + "*" * (len(local) - 2) + local[-1]
    return f"{masked}@{domain}"


def mask_name(name: str) -> str:
    """
    Partially mask a client name for logs.
    Rajesh Kapoor → R***** K*****
    """
    parts = name.split()
    return " ".join(p[0] + "*" * (len(p) - 1) for p in parts)


# ── Input Sanitisation ───────────────────────────────────────────────────────

# Patterns that suggest prompt injection attempts in user-supplied fields
_INJECTION_PATTERNS = [
    r"ignore (previous|prior|earlier|all) instructions",
    r"you are now",
    r"new persona",
    r"system prompt",
    r"jailbreak",
    r"act as",
    r"<\|.*?\|>",          # LLM special tokens
    r"\[INST\]",            # Llama injection markers
    r"disregard.*instructions",
]

_INJECTION_RX = [re.compile(p, re.IGNORECASE) for p in _INJECTION_PATTERNS]


def sanitise_text_field(value: str, field_name: str = "field") -> str:
    """
    Check a user-supplied text field for prompt injection patterns.

    Raises:
        ValueError: If an injection pattern is detected.

    Returns:
        The original value if clean.
    """
    for rx in _INJECTION_RX:
        if rx.search(value):
            raise ValueError(
                f"Potential prompt injection detected in '{field_name}': "
                f"pattern '{rx.pattern}' matched."
            )
    return value


def sanitise_invoice_fields(data: dict) -> dict:
    """
    Sanitise all string fields of an incoming invoice payload.
    Raises ValueError on injection detection.
    """
    text_fields = ["invoice_no", "client_name", "client_first_name"]
    for field in text_fields:
        if field in data and isinstance(data[field], str):
            sanitise_text_field(data[field], field_name=field)
    return data


# ── API Key Utilities ─────────────────────────────────────────────────────────

def hash_api_key(raw_key: str) -> str:
    """Return a SHA-256 hash of an API key (for storage comparison)."""
    return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()


def constant_time_compare(val1: str, val2: str) -> bool:
    """
    Compare two strings in constant time to prevent timing attacks.
    Use this when comparing API keys or secrets.
    """
    import hmac
    return hmac.compare_digest(val1.encode("utf-8"), val2.encode("utf-8"))
