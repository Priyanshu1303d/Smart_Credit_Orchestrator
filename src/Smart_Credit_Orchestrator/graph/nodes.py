"""
LangGraph Nodes – one function per step in the agent workflow.

Flow:
  classify_stage → generate_email → validate_output → send_email → write_audit
                ↘ escalate_record ↗                ↘ regenerate_email (retry) ↗
                                                    ↘ fail_invoice ↗
"""

import logging
from src.Smart_Credit_Orchestrator.graph.state import AgentState
from src.Smart_Credit_Orchestrator.models.invoice import InvoiceRecord, EmailOutput
from src.Smart_Credit_Orchestrator.services import (
    llm_service,
    email_service,
    escalation_service,
    validation_service,
    audit_service,
)

logger = logging.getLogger(__name__)


# ── Node 1: Classify stage ────────────────────────────────────────────────────
def classify_stage(state: AgentState) -> dict:
    invoice: InvoiceRecord = state["invoice"]
    stage, is_escalated = escalation_service.resolve_stage(invoice.days_overdue)
    logger.info("[classify] %s → stage=%d escalated=%s", invoice.invoice_no, stage, is_escalated)
    return {"tone_stage": stage, "is_escalated": is_escalated, "retry_count": 0, "validation_errors": []}


# ── Node 2: Generate email via LLM ────────────────────────────────────────────
def generate_email(state: AgentState) -> dict:
    invoice: InvoiceRecord = state["invoice"]
    try:
        raw = llm_service.generate_email(invoice, state["tone_stage"])
        return {"raw_llm_response": raw, "email_output": None}
    except Exception as exc:
        logger.error("[generate] %s failed: %s", invoice.invoice_no, exc)
        return {"raw_llm_response": None, "validation_passed": False,
                "validation_errors": [str(exc)], "error_message": str(exc)}


# ── Node 3: Validate LLM output ───────────────────────────────────────────────
def validate_output(state: AgentState) -> dict:
    invoice: InvoiceRecord = state["invoice"]
    raw = state.get("raw_llm_response")
    retries = state.get("retry_count", 0)

    if not raw:
        return {"validation_passed": False, "validation_errors": ["No LLM response"], "retry_count": retries + 1}

    result = validation_service.validate_llm_output(raw, invoice, state["tone_stage"])

    if result.is_valid:
        logger.info("[validate] %s PASSED", invoice.invoice_no)
        return {"validation_passed": True, "email_output": result.email_output, "validation_errors": [], "retry_count": retries}
    else:
        logger.warning("[validate] %s FAILED (attempt %d): %s", invoice.invoice_no, retries + 1, result.errors)
        return {"validation_passed": False, "validation_errors": result.errors, "retry_count": retries + 1}


# ── Node 4: Retry — just re-runs generate_email ───────────────────────────────
def regenerate_email(state: AgentState) -> dict:
    logger.info("[regenerate] %s retry #%d", state["invoice"].invoice_no, state.get("retry_count", 0))
    return generate_email(state)


# ── Node 5: Send (dry-run log) ────────────────────────────────────────────────
def send_email(state: AgentState) -> dict:
    invoice: InvoiceRecord = state["invoice"]
    out: EmailOutput = state["email_output"]
    status = email_service.send_email(
        to_email=str(invoice.contact_email),
        subject=out.subject,
        body=out.body,
        invoice_no=invoice.invoice_no,
    )
    return {"send_status": status}


# ── Node 6: Escalate — flag for legal review, no email sent ──────────────────
def escalate_record(state: AgentState) -> dict:
    invoice: InvoiceRecord = state["invoice"]
    logger.warning("[escalate] %s flagged — %d days overdue", invoice.invoice_no, invoice.days_overdue)
    note = EmailOutput(
        subject=f"[ESCALATED] Invoice {invoice.invoice_no} – Legal Review Required",
        body=(
            f"Invoice {invoice.invoice_no} for {invoice.client_name} "
            f"({invoice.currency} {invoice.amount:,.2f}) is {invoice.days_overdue} days overdue. "
            f"Automated follow-ups suspended. Finance manager notified: {invoice.finance_manager_email}"
        ),
        tone_stage=4, tone_label="Stern & Urgent",
        invoice_no=invoice.invoice_no, client_name=invoice.client_name, amount=invoice.amount,
    )
    return {"email_output": note, "send_status": "escalated", "is_escalated": True, "validation_passed": True}


# ── Node 7: Hard fail after retries exhausted ─────────────────────────────────
def fail_invoice(state: AgentState) -> dict:
    invoice: InvoiceRecord = state["invoice"]
    errors = state.get("validation_errors", ["Unknown error"])
    logger.error("[fail] %s gave up after %d retries: %s", invoice.invoice_no, state.get("retry_count", 0), errors)
    stub = EmailOutput(
        subject=f"[FAILED] Invoice {invoice.invoice_no}",
        body=f"Email generation failed for {invoice.invoice_no}. Errors: {'; '.join(errors)}",
        tone_stage=state.get("tone_stage", 1), tone_label="Warm & Friendly",
        invoice_no=invoice.invoice_no, client_name=invoice.client_name, amount=invoice.amount,
    )
    return {"email_output": stub, "send_status": "failed", "error_message": "; ".join(errors)}


# ── Node 8: Write audit log ───────────────────────────────────────────────────
def write_audit(state: AgentState) -> dict:
    invoice: InvoiceRecord = state["invoice"]
    audit_id = audit_service.log_email(
        invoice=invoice,
        email_output=state.get("email_output"),
        send_status=state.get("send_status", "failed"),
        is_escalated=state.get("is_escalated", False),
    )
    return {"audit_id": audit_id}
