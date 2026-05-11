"""
LLM Service – calls Groq via LangChain to generate a follow-up email.

Picks the right stage prompt, fills in all invoice fields, and returns
the raw JSON string from the model. LangSmith traces this automatically
when LANGCHAIN_TRACING_V2=true is set in the environment.
"""

import logging
import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser

from src.Smart_Credit_Orchestrator.models.invoice import InvoiceRecord
from src.Smart_Credit_Orchestrator.prompts.stage1 import STAGE1_SYSTEM_PROMPT
from src.Smart_Credit_Orchestrator.prompts.stage2 import STAGE2_SYSTEM_PROMPT
from src.Smart_Credit_Orchestrator.prompts.stage3 import STAGE3_SYSTEM_PROMPT
from src.Smart_Credit_Orchestrator.prompts.stage4 import STAGE4_SYSTEM_PROMPT

load_dotenv()
logger = logging.getLogger(__name__)

STAGE_PROMPTS = {
    1: STAGE1_SYSTEM_PROMPT,
    2: STAGE2_SYSTEM_PROMPT,
    3: STAGE3_SYSTEM_PROMPT,
    4: STAGE4_SYSTEM_PROMPT,
}

TONE_LABELS = {
    1: "Warm & Friendly",
    2: "Polite but Firm",
    3: "Formal & Serious",
    4: "Stern & Urgent",
}


def _build_llm() -> ChatGroq:
    api_key = os.getenv("GROQ_API_KEY", "")
    if not api_key or api_key == "your_groq_api_key_here":
        raise EnvironmentError("GROQ_API_KEY is not set in your .env file.")
    return ChatGroq(
        model=os.getenv("GROQ_MODEL_NAME", "llama-3.3-70b-versatile"),
        temperature=0.2,
        max_tokens=1024,
        api_key=api_key,
    )


def generate_email(invoice: InvoiceRecord, tone_stage: int) -> str:
    """
    Call the Groq LLM and return the raw JSON string.
    Raises RuntimeError if the API call fails.
    """
    human_message = f"""Generate a {TONE_LABELS[tone_stage]} follow-up email using EXACTLY the data below.

INVOICE DATA:
  invoice_no      : {invoice.invoice_no}
  client_name     : {invoice.client_name}
  client_first    : {invoice.client_first_name}
  amount          : {invoice.amount}
  currency        : {invoice.currency}
  due_date        : {invoice.due_date}
  days_overdue    : {invoice.days_overdue}
  payment_link    : {invoice.payment_link}
  finance_email   : {invoice.finance_manager_email}
  follow_up_count : {invoice.follow_up_count}

Return ONLY a valid JSON object matching the schema in your instructions. No markdown, no extra text."""

    llm = _build_llm()
    messages = [
        SystemMessage(content=STAGE_PROMPTS[tone_stage]),
        HumanMessage(content=human_message),
    ]

    try:
        response = llm.invoke(messages)
        raw = StrOutputParser().invoke(response).strip()
        logger.info("[LLM] %s | stage=%d | OK", invoice.invoice_no, tone_stage)
        return raw
    except Exception as exc:
        raise RuntimeError(f"LLM call failed for {invoice.invoice_no}: {exc}") from exc
