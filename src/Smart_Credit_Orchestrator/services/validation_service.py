"""
Validation Service – parses raw LLM JSON and checks it against the EmailOutput schema.

Layers:
  1. Strip markdown fences (LLMs sometimes wrap output in ```json ... ```)
  2. JSON parse
  3. Pydantic schema validation
  4. Cross-check: invoice_no, amount, and tone_stage must match the source data
  5. Prompt injection scan on the body text
"""

import json
import logging
import re
from dataclasses import dataclass, field
from typing import List, Optional

from pydantic import ValidationError

from src.Smart_Credit_Orchestrator.models.invoice import InvoiceRecord, EmailOutput

logger = logging.getLogger(__name__)

# Patterns that hint at prompt injection in the LLM output
_INJECTION_PATTERNS = [
    r"ignore (previous|prior|all) instructions",
    r"you are now",
    r"new (role|persona)",
    r"system prompt",
    r"jailbreak",
    r"\[INST\]",
]
_INJECTION_RX = [re.compile(p, re.IGNORECASE) for p in _INJECTION_PATTERNS]


@dataclass
class ValidationResult:
    is_valid: bool
    email_output: Optional[EmailOutput] = None
    errors: List[str] = field(default_factory=list)


def _strip_fences(raw: str) -> str:
    """Remove ```json ... ``` wrappers and extract the first JSON object."""
    raw = re.sub(r"```(?:json)?", "", raw, flags=re.IGNORECASE).replace("```", "")
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    return match.group() if match else raw.strip()


def validate_llm_output(
    raw_json: str,
    invoice: InvoiceRecord,
    expected_stage: int,
) -> ValidationResult:
    """
    Parse and validate LLM output. Returns a ValidationResult with
    is_valid=True and a populated email_output on success.
    """
    # 1. Injection scan
    for rx in _INJECTION_RX:
        if rx.search(raw_json):
            return ValidationResult(
                is_valid=False,
                errors=[f"Security: prompt injection pattern detected ({rx.pattern})"],
            )

    # 2. JSON parse
    try:
        data = json.loads(_strip_fences(raw_json))
    except json.JSONDecodeError as exc:
        logger.warning("[Validation] JSON parse failed: %s", exc)
        return ValidationResult(is_valid=False, errors=[f"JSON parse error: {exc}"])

    # 3. Pydantic schema
    try:
        output = EmailOutput(**data)
    except ValidationError as exc:
        errs = [f"{e['loc'][0]}: {e['msg']}" for e in exc.errors()]
        return ValidationResult(is_valid=False, errors=errs)

    # 4. Cross-checks (anti-hallucination)
    errors = []
    if output.invoice_no != invoice.invoice_no:
        errors.append(f"invoice_no mismatch: got '{output.invoice_no}'")
    if abs(output.amount - invoice.amount) > 0.01:
        errors.append(f"amount mismatch: got {output.amount}")
    if output.tone_stage != expected_stage:
        errors.append(f"tone_stage mismatch: expected {expected_stage}, got {output.tone_stage}")
    if invoice.invoice_no not in output.body:
        errors.append("body does not mention the invoice number")

    if errors:
        return ValidationResult(is_valid=False, errors=errors)

    return ValidationResult(is_valid=True, email_output=output)
