from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional, Literal, List
from datetime import datetime


class EmailLog(BaseModel):
    """Audit record written to SQLite for every processed invoice."""

    id: Optional[int] = Field(default=None, ge=1, description="Unique database ID")
    invoice_no: str = Field(..., min_length=3, max_length=50, description="Unique invoice number")
    client_name: str = Field(..., min_length=2, max_length=30, description="Client or company name")
    contact_email_masked: str = Field( ..., min_length=5, max_length=120, description="Masked client email")
    amount: float = Field(..., gt=0, le=1_000_000_000, description="Invoice amount")
    currency: str = Field( default="INR", min_length=3, max_length=5, description="Currency code")
    days_overdue: int = Field( ..., ge=0, le=3650, description="Number of overdue days" )
    tone_stage: int = Field(..., ge=1, le=4, description="Escalation stage")
    tone_label: str = Field(  ..., min_length=3, max_length=50, description="Human readable tone label")
    subject: str = Field(..., min_length=5,max_length=200, description="Generated email subject")
    body_preview: str = Field( ..., min_length=20, max_length=1000, description="Short preview of email body")
    send_status: Literal[ "sent", "dry_run", "escalated","failed"] = Field( ..., description="Email delivery status")
    is_escalated: bool = Field(default=False, description="Whether invoice was escalated")
    timestamp: str = Field( default_factory=lambda: datetime.utcnow().isoformat(),description="ISO formatted timestamp")

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, value: str):

        value = value.upper()

        allowed = ["INR", "USD", "EUR", "GBP"]

        if value not in allowed:
            raise ValueError(
                f"Currency must be one of {allowed}"
            )

        return value

    @field_validator("contact_email_masked")
    @classmethod
    def validate_masked_email(cls, value: str):

        if "@" not in value:
            raise ValueError(
                "Masked email must contain @"
            )

        return value

    @field_validator("timestamp")
    @classmethod
    def validate_timestamp(cls, value: str):

        try:
            datetime.fromisoformat(value)
        except Exception:
            raise ValueError(
                "Timestamp must be valid ISO format"
            )

        return value