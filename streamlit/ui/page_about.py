import streamlit as st


def render():
    st.markdown("""
    <div class="page-header">
      <h1>ℹ️ About This Project</h1>
      <p>Smart Credit Orchestrator · Capstone Assignment 2 · AI Agent for Invoice Collections</p>
    </div>""", unsafe_allow_html=True)

    # ── Hero ──────────────────────────────────────────────────────────────────
    st.markdown("""
    <div style="background:#1e293b;border-radius:14px;padding:2rem;
                border:1px solid #334155;margin-bottom:1.5rem;">
      <h2 style="margin:0 0 .6rem;color:#e2e8f0">💼 Finance Credit Follow-Up Email Agent</h2>
      <p style="color:#94a3b8;font-size:1rem;line-height:1.75;margin:0">
        An AI agent that automates invoice follow-up emails for the Finance team.
        It reads overdue invoice records, determines the correct escalation tone based on how many
        days past due the invoice is, generates a personalised email using a large language model,
        logs every action to an audit trail, and flags critical accounts for legal review —
        all without a single manual email.
      </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Escalation Matrix ─────────────────────────────────────────────────────
    st.markdown("### 📈 Tone Escalation Matrix")
    cols = st.columns(5)
    stages = [
        ("1–7 days",  "Stage 1",  "Warm & Friendly",  "#34d399",
         "Gentle reminder. Assume oversight. Include payment link."),
        ("8–14 days", "Stage 2",  "Polite but Firm",  "#38bdf8",
         "Previous reminder acknowledged. Request confirmation."),
        ("15–21 days","Stage 3",  "Formal & Serious", "#fbbf24",
         "Escalating concern. Mention credit impact. 48hr response."),
        ("22–30 days","Stage 4",  "Stern & Urgent",   "#f87171",
         "Final automated notice. Pay in 24hrs or face escalation."),
        ("30+ days",  "Legal",    "Escalation Flag",  "#c084fc",
         "No email sent. Flagged for manual legal/finance review."),
    ]
    for col, (days, stage, tone, color, desc) in zip(cols, stages):
        col.markdown(f"""
        <div style="background:#1e293b;border-top:4px solid {color};
                    border-radius:12px;padding:1rem;border:1px solid #334155;
                    border-top-width:4px;">
          <div style="font-size:.75rem;color:{color};font-weight:700;margin-bottom:.3rem">{days}</div>
          <div style="font-weight:700;font-size:.95rem;color:#e2e8f0;margin-bottom:.2rem">{stage}</div>
          <div style="font-size:.8rem;color:{color};margin-bottom:.5rem">{tone}</div>
          <div style="font-size:.78rem;color:#64748b">{desc}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Tech stack + Workflow ─────────────────────────────────────────────────
    st.markdown("### 🛠️ Tech Stack")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        | Layer | Technology |
        |-------|-----------|
        | LLM | Groq · `llama-3.3-70b-versatile` |
        | Agent Framework | LangGraph (StateGraph) |
        | Tracing | LangSmith |
        | API | FastAPI + Uvicorn |
        | UI | Streamlit |
        | Data | Pandas + CSV |
        | Audit | JSON flat file |
        """)
    with c2:
        st.markdown("""
        **Agent Workflow (LangGraph)**
        ```
        classify_stage
          ├─ escalate_record  (30+ days)
          └─ generate_email
               └─ validate_output
                    ├─ send_email    (valid)
                    ├─ regenerate    (retry ≤ 2)
                    └─ fail_invoice
                         └─ write_audit → END
        ```
        """)

    # ── Security ──────────────────────────────────────────────────────────────
    st.markdown("### 🔒 Security Measures")
    items = [
        ("🛡️", "Prompt Injection Guard",   "LLM output is scanned for injection patterns before parsing"),
        ("🔍", "Hallucination Check",       "Pydantic cross-checks invoice_no, amount, and tone_stage against source data"),
        ("🔑", "API Key Safety",            "Keys only in `.env` (gitignored). Never hardcoded in source files"),
        ("✉️", "PII Masking",              "Email addresses masked in all logs: `r****@domain.com`"),
        ("🔄", "Dry-Run Default",          "No real emails sent during development — all actions logged only"),
    ]
    for icon, title, desc in items:
        st.markdown(f"""
        <div style="display:flex;align-items:flex-start;gap:.9rem;
                    background:#1e293b;border-radius:10px;padding:.85rem 1.1rem;
                    margin-bottom:.5rem;border:1px solid #334155;">
          <div style="font-size:1.2rem;margin-top:.05rem">{icon}</div>
          <div>
            <div style="font-weight:600;color:#e2e8f0;font-size:.9rem">{title}</div>
            <div style="font-size:.82rem;color:#64748b;margin-top:.15rem">{desc}</div>
          </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.caption("Built by Priyanshu · Capstone Project · Assignment 2 · 2026")
