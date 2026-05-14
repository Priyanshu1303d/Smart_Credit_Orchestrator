<div align="center">
  <img src="https://img.icons8.com/nolan/128/invoice.png" alt="Smart Credit Orchestrator Logo" width="100"/>
  <h1>Smart Credit Orchestrator 💼⚡</h1>
  <p><strong>An AI-powered Finance Credit Follow-Up Email Agent with Tone Escalation Orchestration</strong></p>

  <p>
    <img src="https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi" alt="FastAPI" />
    <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit" />
    <img src="https://img.shields.io/badge/LangGraph-FF4F00?style=for-the-badge" alt="LangGraph" />
    <img src="https://img.shields.io/badge/LangChain-1C3C3C?style=for-the-badge&logo=langchain" alt="LangChain" />
    <img src="https://img.shields.io/badge/Groq-000000?style=for-the-badge" alt="Groq" />
    <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  </p>

  <p>
    <img src="https://img.shields.io/badge/LangSmith-Observability-blueviolet?style=flat-square" />
    <img src="https://img.shields.io/badge/Tests-20%20Passing-brightgreen?style=flat-square" />
    <img src="https://img.shields.io/badge/License-MIT-blue?style=flat-square" />
  </p>
</div>

---

## 🌟 Overview

**Smart Credit Orchestrator** is an end-to-end AI agent for automating invoice follow-up communications in a finance collection pipeline. It ingests overdue invoice records, classifies each account into an escalation stage based on days overdue, generates a professionally-toned follow-up email using a large language model, validates the output for hallucinations and prompt injections, and logs every action to a persistent audit trail — **all without a single manual email.**

Powered by **LangGraph** for robust stateful agent orchestration and **Groq (`llama-3.3-70b-versatile`)** for lightning-fast LLM inference, the system enforces a strict 4-stage tone escalation matrix while automatically flagging critical accounts (30+ days) for legal review.

---

## ✨ Key Features

- **🧠 LangGraph State-Machine Orchestration** — A full `StateGraph` with 8 nodes, 2 conditional edges, and an automatic retry loop (up to 2 attempts on validation failure).
- **📈 4-Stage Tone Escalation** — Deterministic routing from *Warm & Friendly* → *Polite but Firm* → *Formal & Serious* → *Stern & Urgent* based on days overdue.
- **🔐 Multi-Layer Security** — Prompt injection scanning, Pydantic cross-validation to catch hallucinated invoice fields, and PII masking in all audit logs.
- **🔭 LangSmith Observability** — Every LLM call is automatically traced and visible in the LangSmith dashboard for debugging and performance analysis.
- **📜 Immutable Audit Trail** — Every processed invoice (sent / dry-run / escalated / failed) is appended to a JSON audit log with masked PII.
- **⚡ FastAPI Backend** — REST API with Swagger UI for single and batch invoice processing, audit retrieval, and live stats.
- **🎨 Streamlit Dashboard** — A sleek dark-mode UI with 5 pages: Dashboard, Invoice Queue, Run Agent, Audit Log, and About.

---

## 🗂️ Project Structure

```
Smart_Credit_Orchestrator/
│
├── data/
│   ├── sample_invoices.csv        # 20 synthetic Indian client invoices
│   └── generated_logs.json        # Persistent JSON audit trail
│
├── src/Smart_Credit_Orchestrator/
│   ├── graph/
│   │   ├── state.py               # AgentState TypedDict
│   │   ├── nodes.py               # 8 workflow nodes
│   │   ├── edges.py               # 2 conditional routing functions
│   │   └── workflow.py            # StateGraph compilation (singleton)
│   │
│   ├── services/
│   │   ├── llm_service.py         # Groq + LangChain integration
│   │   ├── escalation_service.py  # Days-overdue → tone stage resolver
│   │   ├── validation_service.py  # 4-layer LLM output validator
│   │   ├── email_service.py       # Dry-run email dispatcher + PII masking
│   │   └── audit_service.py       # JSON audit log reader/writer
│   │
│   ├── api/
│   │   ├── models.py              # FastAPI request/response schemas
│   │   └── routes.py              # 6 REST API endpoints
│   │
│   ├── models/
│   │   ├── invoice.py             # InvoiceRecord + EmailOutput Pydantic models
│   │   └── email_log.py           # Audit log Pydantic model
│   │
│   └── prompts/
│       ├── stage1.py … stage4.py  # Tone-specific system prompts
│
├── streamlit/ui/
│   ├── app.py                     # Main Streamlit app (dark theme)
│   ├── page_dashboard.py          # Stats + bar chart
│   ├── page_invoices.py           # Filterable invoice queue
│   ├── page_agent.py              # Live agent runner
│   ├── page_audit.py              # Searchable audit log
│   └── page_about.py              # Project info + tech stack
│
├── tests/
│   ├── test_escalation.py         # 13 parameterized boundary tests
│   └── test_validation.py         # 7 validation pipeline tests
│
├── main.py                        # FastAPI app entry point
├── Dockerfile
├── requirements.txt
└── .env.example
```

---

## 🛠️ Tech Stack

| Component | Technologies |
| :--- | :--- |
| **Agent Framework** | LangGraph (StateGraph), LangChain |
| **LLM Inference** | Groq · `llama-3.3-70b-versatile` |
| **Backend API** | FastAPI, Uvicorn, Python 3.12 |
| **Frontend UI** | Streamlit (Dark Mode) |
| **Data Validation** | Pydantic v2 |
| **Data Processing** | Pandas, CSV |
| **Observability** | LangSmith |
| **Audit Storage** | JSON flat file |
| **Testing** | pytest (20 tests) |
| **Containerisation** | Docker |

---

## 🔄 Agent Workflow (LangGraph)

```
                    ┌─────────────────┐
                    │  classify_stage │  ← Entry Point
                    └────────┬────────┘
                             │
               ┌─────────────┴──────────────┐
        (>30d) │                            │ (≤30d)
               ▼                            ▼
     ┌──────────────────┐        ┌──────────────────┐
     │  escalate_record │        │  generate_email  │ ← Groq LLM
     └────────┬─────────┘        └────────┬─────────┘
              │                           │
              │                  ┌────────▼─────────┐
              │                  │  validate_output  │ ← 4-layer check
              │                  └────────┬──────────┘
              │            ┌──────────────┤
              │       valid │             │ invalid
              │             ▼             ▼
              │      ┌──────────┐  ┌──────────────────┐
              │      │send_email│  │ regenerate_email  │ ← retry ≤ 2
              │      └────┬─────┘  └────────┬─────────┘
              │           │              (exhausted)
              │           │         ┌────────▼─────────┐
              │           │         │   fail_invoice   │
              │           │         └────────┬─────────┘
              └───────────┴──────────────────┘
                                    │
                           ┌────────▼─────────┐
                           │   write_audit    │ ← JSON log
                           └────────┬─────────┘
                                    │
                                   END
```

### Escalation Matrix

| Days Overdue | Stage | Tone |
|:---:|:---:|:---|
| 1 – 7 days | Stage 1 | 😊 Warm & Friendly |
| 8 – 14 days | Stage 2 | 🤝 Polite but Firm |
| 15 – 21 days | Stage 3 | 📋 Formal & Serious |
| 22 – 30 days | Stage 4 | ⚠️ Stern & Urgent |
| **30+ days** | **Legal** | ⚖️ **Escalation Flag — No email sent** |

---

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/Priyanshu1303d/Smart_Credit_Orchestrator.git
cd Smart_Credit_Orchestrator

pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and add your keys:

```env
# LLM — get your key at console.groq.com
GROQ_API_KEY=gsk_your_groq_key_here
GROQ_MODEL_NAME=llama-3.3-70b-versatile

# Observability — get your key at smith.langchain.com
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=lsv2_your_langsmith_key_here
LANGCHAIN_PROJECT=smart-credit-orchestrator
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
```

### 3. Run the FastAPI Backend

```bash
uvicorn main:app --reload --port 8000
```

📖 Swagger UI → **http://localhost:8000/docs**

### 4. Run the Streamlit Dashboard

```bash
streamlit run streamlit/ui/app.py
```

🎨 Dashboard → **http://localhost:8501**

### 5. Run Tests

```bash
pytest tests/ -v
# 20 passed ✅
```

---

## 🌐 API Endpoints

| Method | Endpoint | Description |
|:---:|:---|:---|
| `GET` | `/api/v1/health` | Service status + LangSmith tracing flag |
| `POST` | `/api/v1/process/single` | Run agent on one invoice |
| `POST` | `/api/v1/process/batch` | Run agent on all CSV invoices |
| `GET` | `/api/v1/audit` | Full audit log (all entries) |
| `GET` | `/api/v1/audit/stats` | Aggregate counters for dashboard |
| `GET` | `/api/v1/invoices` | CSV preview with computed escalation stage |

---

## 🔒 Security Design

| Concern | Mitigation |
|:---|:---|
| **Prompt Injection** | Regex scan of LLM output before JSON parse |
| **Hallucination** | Pydantic cross-checks `invoice_no`, `amount`, `tone_stage` against source |
| **PII Leakage** | Email addresses masked (`r****@domain.com`) in all audit records |
| **Key Exposure** | API keys only in `.env` (gitignored) — never hardcoded |
| **Accidental Email** | Default `dry_run` mode — no real emails sent during development |

---

## 📊 Live Test — Invoice ID 4

> **Arjun Desai · INV-2024-007 · ₹92,000 · 23 days overdue · Stage 4 (Stern & Urgent)**

```
SUBJECT: FINAL NOTICE: Overdue Invoice INV-2024-007 for INR 92,000

BODY: Dear Mr. Desai, this is the FINAL automated reminder for invoice
INV-2024-007, which is now 23 days overdue. The amount of INR 92,000
was due on 2026-04-19. We urge you to settle this immediately or
contact our finance department at finance@smartcredit.in within 24
hours to avoid escalation to our recovery process.
Please make the payment at https://pay.smartcredit.in/INV-2024-007.

Tone Stage : 4 — Stern & Urgent ✅
Validation : PASSED ✅
```

---

## 🖥️ Streamlit Dashboard Pages

| Page | What It Shows |
|:---|:---|
| 🏠 **Dashboard** | Stats, invoice stage distribution bar chart, total receivables |
| 📋 **Invoice Queue** | All 20 invoices with filter by stage, sort, and search |
| ⚡ **Run Agent** | Live LangGraph pipeline — pick invoice → get generated email |
| 📜 **Audit Log** | Full searchable audit trail, expandable per-entry view |
| ℹ️ **About** | Project description, escalation matrix, tech stack, security |

---

<div align="center">
  <i>Architected & Built by Priyanshu · 2026</i>
</div>
