import streamlit as st
import pandas as pd
from pathlib import Path
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from dotenv import load_dotenv
load_dotenv()

from src.Smart_Credit_Orchestrator.models.invoice import InvoiceRecord
from src.Smart_Credit_Orchestrator.services import escalation_service
from src.Smart_Credit_Orchestrator.graph.workflow import get_graph

TONE_COLORS = {1: "#34d399", 2: "#38bdf8", 3: "#fbbf24", 4: "#f87171"}

API_URL=os.getenv("API_URL")

if not API_URL:
    raise ValueError("API URL not found")

def render():
    st.markdown("""
    <div class="page-header">
      <h1>⚡ Run Agent</h1>
      <p>Select an invoice and fire the LangGraph agent to generate a follow-up email</p>
    </div>""", unsafe_allow_html=True)

    csv_source = st.radio("Choose Data Source:", ["Demo CSV", "Upload CSV"], horizontal=True)

    if csv_source == "Upload CSV":
        uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])
        if uploaded_file is not None:
            if st.button("Confirm & Upload to Backend", use_container_width=True):
                import requests
                
                # Save it locally on Streamlit's server so Streamlit can read it for the dropdown
                Path("./data").mkdir(exist_ok=True)
                with open("./data/uploaded_invoices.csv", "wb") as f:
                    f.write(uploaded_file.getvalue())

                with st.spinner("Uploading to backend..."):
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")}
                    try:
                        api_url = os.getenv("API_URL", "http://localhost:8000")
                        res = requests.post(f"{api_url}/api/v1/upload", files=files)
                        if res.status_code == 200:
                            st.success("File uploaded successfully!")
                        else:
                            st.error(f"Upload failed: {res.text}")
                    except Exception as e:
                        st.error(f"Connection error to FastAPI backend: {e}")
        
        csv = Path("./data/uploaded_invoices.csv")
        if not csv.exists() and uploaded_file is None:
            st.info("Please upload a CSV file to continue.")
            return
        elif not csv.exists():
            st.warning("Please click 'Confirm & Upload to Backend' to save the file.")
            return
    else:
        csv = Path("./data/sample_invoices.csv")

    if not csv.exists():
        st.error("Invoice CSV not found.")
        return

    df = pd.read_csv(csv).fillna("")
    options = {f"{r['invoice_no']} — {r['client_name']} ({int(r['days_overdue'])}d overdue)": i
               for i, r in df.iterrows()}
    chosen_label = st.selectbox("Pick an invoice", list(options.keys()))
    row = df.iloc[options[chosen_label]]

    # ── Invoice preview ───────────────────────────────────────────────────────
    stage, is_esc = escalation_service.resolve_stage(int(row["days_overdue"]))
    tone_label = escalation_service.TONE_LABELS.get(stage, "N/A")
    color = TONE_COLORS.get(stage, "#818cf8")

    with st.expander("📄 Invoice Details", expanded=True):
        c1, c2, c3 = st.columns(3)
        c1.metric("Invoice No", row["invoice_no"])
        c1.metric("Client", row["client_name"])
        c2.metric("Amount (INR)", f"₹{float(row['amount']):,.0f}")
        c2.metric("Days Overdue", int(row["days_overdue"]))
        c3.metric("Follow-Ups Sent", int(row["follow_up_count"]))
        c3.markdown(f"""
        <div style="margin-top:.5rem;padding:.6rem 1rem;
                    background:#0f172a;border-left:4px solid {color};border-radius:8px;">
          <span style="color:{color};font-weight:600">Stage {stage} — {tone_label}</span>
          {"<br><span style='color:#c084fc;font-size:.85rem'>⚖️ Will be escalated (30+ days)</span>" if is_esc else ""}
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚀  Run Agent", use_container_width=True, type="primary"):
        if is_esc:
            st.warning("This invoice (30+ days) will be **escalated** — no email generated.")

        with st.spinner("Calling Groq LLM via LangGraph…"):
            try:
                invoice = InvoiceRecord(
                    invoice_no=str(row["invoice_no"]),
                    client_name=str(row["client_name"]),
                    client_first_name=str(row["client_first_name"]),
                    amount=float(row["amount"]),
                    currency=str(row.get("currency", "INR")),
                    due_date=str(row["due_date"]),
                    contact_email=str(row["contact_email"]),
                    follow_up_count=int(row["follow_up_count"]),
                    days_overdue=int(row["days_overdue"]),
                    payment_link=str(row["payment_link"]),
                    finance_manager_email=str(row.get("finance_manager_email", "finance@smartcredit.in")),
                )
                state = get_graph().invoke({
                    "invoice": invoice, "retry_count": 0,
                    "validation_errors": [], "is_escalated": False, "validation_passed": False,
                })
            except Exception as exc:
                st.error(f"Agent error: {exc}")
                return

        out = state.get("email_output")
        status = state.get("send_status", "unknown")
        status_icon = {"dry_run": "📧", "escalated": "⚖️", "failed": "❌", "sent": "✅"}.get(status, "ℹ️")
        st.success(f"{status_icon} Agent completed — Status: **{status.upper()}**")

        if out:
            st.markdown(f"""
            <div style="background:#1e293b;border-radius:12px;padding:1.4rem 1.6rem;
                        border-left:5px solid {color};margin-top:.5rem;">
              <div style="font-size:.78rem;color:#64748b;margin-bottom:.5rem;letter-spacing:.05em">
                STAGE {stage} · {tone_label.upper()}
              </div>
              <div style="font-weight:700;font-size:1.05rem;color:#e2e8f0;margin-bottom:.8rem">
                {out.subject}
              </div>
              <div style="line-height:1.75;white-space:pre-wrap;font-size:.92rem;color:#cbd5e1">
                {out.body}
              </div>
            </div>""", unsafe_allow_html=True)

            with st.expander("🔍 Raw JSON from LLM"):
                import json
                st.code(json.dumps({
                    "subject": out.subject, "body": out.body,
                    "tone_stage": out.tone_stage, "tone_label": out.tone_label,
                    "invoice_no": out.invoice_no, "client_name": out.client_name, "amount": out.amount,
                }, indent=2, ensure_ascii=False), language="json")

        if state.get("audit_id"):
            st.caption(f"✔ Logged to audit trail — entry #{state['audit_id']}")
