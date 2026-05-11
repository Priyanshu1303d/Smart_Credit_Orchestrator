"""
LangGraph State – the shared dictionary that flows through every node.
"""

from typing import Optional, List
from typing_extensions import TypedDict
from src.Smart_Credit_Orchestrator.models.invoice import InvoiceRecord, EmailOutput


class AgentState(TypedDict, total=False):
    # Input
    invoice: InvoiceRecord

    # Set by classify_stage
    tone_stage: int
    is_escalated: bool

    # Set by generate/regenerate
    raw_llm_response: Optional[str]

    # Set by validate_output
    email_output: Optional[EmailOutput]
    validation_passed: bool
    validation_errors: List[str]
    retry_count: int

    # Set by send/escalate/fail
    send_status: str

    # Set by write_audit
    audit_id: Optional[int]

    # Error info
    error_message: Optional[str]
