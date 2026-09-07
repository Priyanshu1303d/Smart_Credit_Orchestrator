"""
FastAPI Request / Response Models - Smart Credit Orchestrator

Pydantic models for API input validation and response serialisation.
Separate from domain models (src/models/) to keep API contracts explicit.
"""

from __future__ import annotations

from typing import List, Literal, Optional
from pydantic import BaseModel, Field, EmailStr


# ─────────────────────────────────────────────────────────────────────────────
# Request Models
# ─────────────────────────────────────────────────────────────────────────────

class ProcessSingleRequest(BaseModel):
    """Request body for processing a single invoice."""
    invoice_no: str = Field(..., min_length=3, max_length=50, example="INV-2024-001")
    client_name: str = Field(..., min_length=2, max_length=100, example="Rajesh Kapoor")
    client_first_name: str = Field(..., min_length=2, max_length=50, example="Rajesh")
    amount: float = Field(..., gt=0, example=45000.0)
    currency: str = Field(default="INR", example="INR")
    due_date: str = Field(..., example="2026-05-04")
    contact_email: EmailStr = Field(..., example="rajesh.kapoor@example.com")
    follow_up_count: int = Field(..., ge=0, example=0)
    days_overdue: int = Field(..., ge=0, example=7)
    payment_link: str = Field(..., example="https://pay.smartcredit.in/INV-2024-001")
    finance_manager_email: EmailStr = Field(
        default="finance@smartcredit.in",
        example="finance@smartcredit.in",
    )


class ProcessBatchRequest(BaseModel):
    """Request body for processing all overdue invoices from the CSV."""
    csv_path: Optional[str] = Field(
        default=None,
        description="Override CSV path. Defaults to INVOICES_CSV_PATH env var.",
    )
    dry_run: bool = Field(
        default=True,
        description="If true, no emails are actually sent.",
    )


# ─────────────────────────────────────────────────────────────────────────────
# Response Models
# ─────────────────────────────────────────────────────────────────────────────

class EmailGeneratedResponse(BaseModel):
    """Response for a successfully processed invoice."""
    invoice_no: str
    client_name: str
    tone_stage: int
    tone_label: str
    subject: str
    body: str
    send_status: Literal["sent", "dry_run", "escalated", "failed"]
    is_escalated: bool
    audit_id: Optional[int]
    days_overdue: int
    amount: float
    currency: str


class BatchProcessResponse(BaseModel):
    """Response for a batch invoice processing run."""
    total_processed: int
    sent: int
    dry_run: int
    escalated: int
    failed: int
    results: List[EmailGeneratedResponse]


class AuditLogEntry(BaseModel):
    """Single audit log record as returned by the /audit endpoint."""
    id: Optional[int]
    invoice_no: str
    client_name: str
    contact_email_masked: str
    amount: float
    currency: str
    days_overdue: int
    tone_stage: int
    tone_label: str
    subject: str
    body_preview: str
    send_status: str
    is_escalated: bool
    timestamp: str


class AuditStatsResponse(BaseModel):
    """Aggregate statistics for the dashboard."""
    total: int
    sent: int
    dry_run: int
    escalated: int
    failed: int


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    env: str
    langsmith_tracing: bool
