from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class ProcessInvoiceResponse(BaseModel):
    """Response returned after processing a single invoice."""
    invoice_no: str = Field(...,min_length=3,max_length=10,description="Processed invoice number")
    status: Literal["processed","escalated","error"] = Field(...,description="Invoice processing status")
    tone_stage: Optional[int] = Field(default=None, ge=1, le=4,  description="Escalation tone stage")
    tone_label: Optional[str] = Field(default=None, min_length=3, max_length=50, description="Human readable tone label")
    send_status: Optional[Literal[ "sent","dry_run","escalated", "failed"]] = Field(default=None,description="Email delivery status")
    is_escalated: bool = Field(default=False,description="Whether invoice was escalated")
    error: Optional[str] = Field(default=None, min_length=3,max_length=500,description="Error message if processing failed")


class BatchProcessResponse(BaseModel):
    """Response returned after processing multiple invoices in batch.
    """
    total: int = Field(...,ge=0,le=1_000_000,description="Total invoices received")
    processed: int = Field(..., ge=0,le=1_000_000, description="Successfully processed invoices")
    escalated: int = Field(...,ge=0,le=1_000_000, description="Escalated invoices")
    failed: int = Field(...,ge=0,le=1_000_000, description="Failed invoices")
    results: List[ProcessInvoiceResponse] = Field(...,description="List of processed invoice responses")


class AuditLogResponse(BaseModel):
    """Response containing audit logs."""
    total: int = Field(...,ge=0,le=1_000_000, description="Total audit log records")
    logs: List[EmailLog] = Field(...,description="Audit log entries")


class HealthResponse(BaseModel):
    """Health check response model."""
    status: Literal["ok"] = Field(default="ok", description="Application health status")
    db: Literal["connected","disconnected"] = Field(default="connected", description="Database connection status")
    llm: Literal["reachable","unreachable"] = Field(default="reachable", description="LLM service availability")