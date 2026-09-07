"""
Audit Service – appends one JSON record per processed invoice.
No SQLite, no database, just a plain JSON list in generated_logs.json.
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from src.Smart_Credit_Orchestrator.models.invoice import InvoiceRecord, EmailOutput
from src.Smart_Credit_Orchestrator.utils.security import mask_email

logger = logging.getLogger(__name__)

LOG_FILE = Path("./data/generated_logs.json")


def log_email(
    invoice: InvoiceRecord,
    email_output: Optional[EmailOutput],
    send_status: str,
    is_escalated: bool,
) -> int:
    """
    Append one audit entry to generated_logs.json.
    Returns the new record's index (1-based).
    """
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Load existing logs or start fresh
    if LOG_FILE.exists() and LOG_FILE.stat().st_size > 0:
        logs = json.loads(LOG_FILE.read_text(encoding="utf-8"))
    else:
        logs = []

    entry = {
        "id": len(logs) + 1,
        "invoice_no": invoice.invoice_no,
        "client_name": invoice.client_name,
        "contact_email_masked": mask_email(str(invoice.contact_email)),
        "amount": invoice.amount,
        "currency": invoice.currency,
        "days_overdue": invoice.days_overdue,
        "tone_stage": email_output.tone_stage if email_output else 0,
        "tone_label": email_output.tone_label if email_output else "N/A",
        "subject": email_output.subject if email_output else "[none]",
        "body_preview": (email_output.body[:300] if email_output else "[none]"),
        "send_status": send_status,
        "is_escalated": is_escalated,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    logs.append(entry)
    LOG_FILE.write_text(json.dumps(logs, indent=2, ensure_ascii=False), encoding="utf-8")

    logger.info("[AUDIT] #%d | %s | %s", entry["id"], invoice.invoice_no, send_status)
    return entry["id"]


def get_all_logs() -> list:
    """Read all audit entries from the JSON file. Handles both list and dict formats."""
    if not LOG_FILE.exists():
        return []
    try:
        data = json.loads(LOG_FILE.read_text(encoding="utf-8"))
        # Handle old seed format: {"audit_logs": [...], "metadata": {...}}
        if isinstance(data, dict) and "audit_logs" in data:
            return data["audit_logs"]
        if isinstance(data, list):
            return data
        return []
    except Exception:
        return []


def get_stats() -> dict:
    """Compute simple counters from the JSON log file."""
    logs = [l for l in get_all_logs() if isinstance(l, dict)]  # guard against stale format
    return {
        "total":     len(logs),
        "dry_run":   sum(1 for l in logs if l.get("send_status") == "dry_run"),
        "escalated": sum(1 for l in logs if l.get("is_escalated")),
        "failed":    sum(1 for l in logs if l.get("send_status") == "failed"),
        "sent":      sum(1 for l in logs if l.get("send_status") == "sent"),
    }
