"""
FastAPI Routes – Smart Credit Orchestrator

Endpoints:
  GET  /health          → API status
  POST /process/single  → Run one invoice through the agent
  POST /process/batch   → Run all invoices from the CSV
  GET  /audit           → All audit log entries
  GET  /audit/stats     → Counts (total, dry_run, escalated, failed, sent)
  GET  /invoices        → Preview CSV with computed escalation stage
"""

import logging
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException

from src.Smart_Credit_Orchestrator.api.models import (
    ProcessSingleRequest, ProcessBatchRequest,
    EmailGeneratedResponse, BatchProcessResponse,
    AuditLogEntry, AuditStatsResponse, HealthResponse,
)
from fastapi import File, UploadFile
import shutil
from src.Smart_Credit_Orchestrator.graph.workflow import get_graph
from src.Smart_Credit_Orchestrator.models.invoice import InvoiceRecord
from src.Smart_Credit_Orchestrator.services import audit_service, escalation_service

load_dotenv()
logger = logging.getLogger(__name__)
router = APIRouter()

CSV_PATH = "./data/sample_invoices.csv"
UPLOADED_FILE_PATH = "./data/uploaded_invoices.csv"


def _run_agent(invoice: InvoiceRecord) -> dict:
    """Run the LangGraph agent for a single invoice and return final state."""
    return get_graph().invoke({
        "invoice": invoice,
        "retry_count": 0,
        "validation_errors": [],
        "is_escalated": False,
        "validation_passed": False,
    })


def _state_to_response(state: dict, invoice: InvoiceRecord) -> EmailGeneratedResponse:
    out = state.get("email_output")
    return EmailGeneratedResponse(
        invoice_no=invoice.invoice_no,
        client_name=invoice.client_name,
        tone_stage=state.get("tone_stage", 0),
        tone_label=out.tone_label if out else "N/A",
        subject=out.subject if out else "",
        body=out.body if out else "",
        send_status=state.get("send_status", "failed"),
        is_escalated=state.get("is_escalated", False),
        audit_id=state.get("audit_id"),
        days_overdue=invoice.days_overdue,
        amount=invoice.amount,
        currency=invoice.currency,
    )


# ── Health ────────────────────────────────────────────────────────────────────
@router.get("/health", response_model=HealthResponse, tags=["System"])
def health():
    return HealthResponse(
        status="ok", version="1.0.0",
        env=os.getenv("APP_ENV", "development"),
        langsmith_tracing=os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true",
    )


# ── Upload CSV ────────────────────────────────────────────────────────────────
@router.post("/upload", tags=["Data"])
async def upload_csv(file: UploadFile = File(...)):
    """Upload a new CSV file to run the agent on."""
    try:
        with open(UPLOADED_FILE_PATH, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return {"message": "File uploaded successfully", "file_path": UPLOADED_FILE_PATH}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))



# ── Process single invoice ────────────────────────────────────────────────────
@router.post("/process/single", response_model=EmailGeneratedResponse, tags=["Agent"])
def process_single(req: ProcessSingleRequest):
    try:
        invoice = InvoiceRecord(**req.model_dump())
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    try:
        state = _run_agent(invoice)
    except EnvironmentError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    return _state_to_response(state, invoice)


# ── Batch process all CSV invoices ────────────────────────────────────────────
@router.post("/process/batch", response_model=BatchProcessResponse, tags=["Agent"])
def process_batch(req: ProcessBatchRequest):
    csv_file = Path(req.csv_path or CSV_PATH)
    if not csv_file.exists():
        raise HTTPException(status_code=404, detail=f"CSV not found: {csv_file}")
    try:
        df = pd.read_csv(csv_file).fillna("")
        df = df[df["days_overdue"].astype(int) > 0]
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    results, counters = [], {"sent": 0, "dry_run": 0, "escalated": 0, "failed": 0}

    for _, row in df.iterrows():
        try:
            invoice = InvoiceRecord(**{
                "invoice_no": str(row["invoice_no"]),
                "client_name": str(row["client_name"]),
                "client_first_name": str(row["client_first_name"]),
                "amount": float(row["amount"]),
                "currency": str(row.get("currency", "INR")),
                "due_date": str(row["due_date"]),
                "contact_email": str(row["contact_email"]),
                "follow_up_count": int(row["follow_up_count"]),
                "days_overdue": int(row["days_overdue"]),
                "payment_link": str(row["payment_link"]),
                "finance_manager_email": str(row.get("finance_manager_email", "finance@smartcredit.in")),
            })
            state = _run_agent(invoice)
            resp = _state_to_response(state, invoice)
            results.append(resp)
            if resp.send_status in counters:
                counters[resp.send_status] += 1
        except Exception as exc:
            logger.warning("Skipped row: %s", exc)
            counters["failed"] += 1

    return BatchProcessResponse(total_processed=len(results), results=results, **counters)


# ── Audit ─────────────────────────────────────────────────────────────────────
@router.get("/audit", response_model=list[AuditLogEntry], tags=["Audit"])
def get_audit():
    return audit_service.get_all_logs()


@router.get("/audit/stats", response_model=AuditStatsResponse, tags=["Audit"])
def get_stats():
    return audit_service.get_stats()


# ── Invoice preview ───────────────────────────────────────────────────────────
@router.get("/invoices", tags=["Data"])
def list_invoices():
    """Return CSV rows annotated with computed tone_stage (no LLM call)."""
    csv_file = Path(CSV_PATH)
    if not csv_file.exists():
        raise HTTPException(status_code=404, detail="Invoice CSV not found.")
    df = pd.read_csv(csv_file).fillna("")
    result = []
    for _, row in df.iterrows():
        days = int(row.get("days_overdue", 0))
        stage, escalated = escalation_service.resolve_stage(days)
        result.append({
            "invoice_no": row["invoice_no"],
            "client_name": row["client_name"],
            "amount": row["amount"],
            "days_overdue": days,
            "tone_stage": stage,
            "tone_label": escalation_service.TONE_LABELS.get(stage, "N/A"),
            "is_escalated": escalated,
        })
    return result
