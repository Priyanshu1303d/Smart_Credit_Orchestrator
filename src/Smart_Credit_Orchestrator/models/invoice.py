from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional, Literal, List
from datetime import datetime


class InvoiceRecord(BaseModel):
    """Represents a single invoice / credit record from the data source."""

    invoice_no: str = Field(...,min_length=3,max_length=10,description="Unique invoice number")
    client_name: str = Field(...,min_length=2,max_length=30,description="Full client/company name")
    client_first_name: str = Field(...,min_length=2,max_length=20,description="Client first name")
    amount: float = Field(...,gt=0,le=1_000_000_000,description="Invoice amount")
    currency: str = Field(default="INR",min_length=3,max_length=5,description="Currency code")
    due_date: str = Field(...,description="Invoice due date in ISO format")
    contact_email: EmailStr = Field( ...,description="Client contact email")
    follow_up_count: int = Field( ...,ge=0, le=10, description="Number of reminders already sent")
    days_overdue: int = Field( ..., ge=0, le=3650,description="Days overdue")
    payment_link: str = Field(..., min_length=10,max_length=500,description="Payment URL")
    finance_manager_email: EmailStr = Field(default="finance@company.com",description="Finance escalation email")

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

    @field_validator("due_date")
    @classmethod
    def validate_due_date(cls, value: str):

        try:
            datetime.fromisoformat(value)
        except Exception:
            raise ValueError(
                "due_date must be valid ISO format YYYY-MM-DD"
            )

        return value

    @field_validator("payment_link")
    @classmethod
    def validate_payment_link(cls, value: str):

        if not (
            value.startswith("http://")
            or value.startswith("https://")
        ):
            raise ValueError(
                "Payment link must start with http:// or https://"
            )

        return value


class EmailOutput(BaseModel):
    """Structured LLM output. Every field must be populated."""
    subject: str = Field( ..., min_length=5, max_length=200,description="Generated email subject")
    body: str = Field( ..., min_length=50,max_length=5000,description="Generated email body")
    tone_stage: int = Field(...,ge=1,le=4,description="Escalation tone stage")
    tone_label: str = Field( ..., min_length=3,max_length=50,description="Human readable tone label")
    invoice_no: str = Field(...,min_length=3,max_length=10,description="Invoice number" )
    client_name: str = Field(...,min_length=2,max_length=30, description="Client name" )
    amount: float = Field(..., gt=0, le=1_000_000_000,description="Invoice amount")

    @field_validator("tone_label")
    @classmethod
    def validate_tone_label(cls, value: str):

        allowed = [
            "Warm & Friendly",
            "Polite but Firm",
            "Formal & Serious",
            "Stern & Urgent"
        ]

        if value not in allowed:
            raise ValueError(
                f"tone_label must be one of {allowed}"
            )

        return value

    @field_validator("body")
    @classmethod
    def validate_body(cls, value: str):

        if "invoice" not in value.lower():
            raise ValueError(
                "Generated email must reference invoice"
            )

        return value