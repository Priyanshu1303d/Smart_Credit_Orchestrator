"""
Email Service – just logs the email to console (dry-run mode).
No SMTP, no SendGrid, no external dependencies.
"""

import logging
from src.Smart_Credit_Orchestrator.utils.security import mask_email

logger = logging.getLogger(__name__)

def send_email(to_email: str, subject: str, body: str, invoice_no: str) -> str:
    """
    Log the email and return 'dry_run'.
    In a real deployment, swap this function body with SMTP/SendGrid code.
    """
    logger.info(
        "\n[DRY-RUN EMAIL]\n"
        "  Invoice : %s\n"
        "  To      : %s\n"
        "  Subject : %s\n"
        "  Body    : %s\n",
        invoice_no,
        mask_email(to_email),
        subject,
        body[:300],
    )
    return "dry_run"
