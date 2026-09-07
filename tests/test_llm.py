import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import os
sys.path.insert(0, os.path.abspath("."))

from dotenv import load_dotenv
load_dotenv()

from src.Smart_Credit_Orchestrator.models.invoice import InvoiceRecord
from src.Smart_Credit_Orchestrator.services import llm_service, validation_service, escalation_service

# Invoice matching generated_logs.json id=4
invoice = InvoiceRecord(
    invoice_no="INV-2024-007",
    client_name="Arjun Desai",
    client_first_name="Arjun",
    amount=92000.0,
    currency="INR",
    due_date="2026-04-19",
    contact_email="arjun.desai@cloudworks.in",
    follow_up_count=3,
    days_overdue=23,
    payment_link="https://pay.smartcredit.in/INV-2024-007",
    finance_manager_email="finance@smartcredit.in",
)

stage, is_escalated = escalation_service.resolve_stage(invoice.days_overdue)
print(f"\n{'='*60}")
print(f"  INVOICE   : {invoice.invoice_no}")
print(f"  CLIENT    : {invoice.client_name}")
print(f"  AMOUNT    : ₹{invoice.amount:,.0f}")
print(f"  OVERDUE   : {invoice.days_overdue} days")
print(f"  STAGE     : {stage} — {escalation_service.TONE_LABELS[stage]}")
print(f"  ESCALATED : {is_escalated}")
print(f"{'='*60}\n")

print("Calling Groq LLM...")
raw = llm_service.generate_email(invoice, tone_stage=stage)
print(f"\n--- RAW LLM OUTPUT ---\n{raw}\n")

result = validation_service.validate_llm_output(raw, invoice, expected_stage=stage)
print(f"--- VALIDATION ---")
print(f"  Passed : {result.is_valid}")
if not result.is_valid:
    print(f"  Errors : {result.errors}")
else:
    out = result.email_output
    print(f"\n  SUBJECT :\n  {out.subject}")
    print(f"\n  BODY :\n{'-'*60}")
    print(out.body)
    print(f"{'-'*60}")
    print(f"\n  Tone Stage : {out.tone_stage} — {out.tone_label}")
    print(f"  Invoice No : {out.invoice_no}")
    print(f"  Amount     : ₹{out.amount:,.0f}")
