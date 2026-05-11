import streamlit as st
import pandas as pd
from pathlib import Path
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.Smart_Credit_Orchestrator.services import escalation_service

BADGE = {1: "badge-1", 2: "badge-2", 3: "badge-3", 4: "badge-4", 99: "badge-e"}
LABEL = {1: "Stage 1 – Warm", 2: "Stage 2 – Firm", 3: "Stage 3 – Serious", 4: "Stage 4 – Urgent", 99: "⚖️ Escalated"}


def render():
    st.markdown("""
    <div class="page-header">
      <h1>📋 Invoice Queue</h1>
      <p>All overdue invoices with computed escalation stage</p>
    </div>""", unsafe_allow_html=True)

    csv = Path("./data/sample_invoices.csv")
    if not csv.exists():
        st.error("Invoice CSV not found at `data/sample_invoices.csv`")
        return

    df = pd.read_csv(csv).fillna("")

    # ── Filters ───────────────────────────────────────────────────────────────
    col1, col2, col3 = st.columns(3)
    with col1:
        stage_filter = st.selectbox("Filter by Stage", ["All", "Stage 1", "Stage 2", "Stage 3", "Stage 4", "Escalated"])
    with col2:
        sort_by = st.selectbox("Sort by", ["days_overdue ↓", "amount ↓", "client_name ↑"])
    with col3:
        search = st.text_input("Search client name", placeholder="e.g. Rajesh")

    # ── Enrich with stage info ────────────────────────────────────────────────
    rows = []
    for _, row in df.iterrows():
        days = int(row["days_overdue"])
        stage, esc = escalation_service.resolve_stage(days)
        stage_key = 99 if esc else stage
        rows.append({**row.to_dict(), "_stage_key": stage_key, "_stage_label": LABEL[stage_key]})

    enriched = pd.DataFrame(rows)

    # Apply filters
    if stage_filter != "All":
        target = {"Stage 1": 1, "Stage 2": 2, "Stage 3": 3, "Stage 4": 4, "Escalated": 99}[stage_filter]
        enriched = enriched[enriched["_stage_key"] == target]
    if search:
        enriched = enriched[enriched["client_name"].str.contains(search, case=False)]

    # Sort
    if sort_by == "days_overdue ↓":
        enriched = enriched.sort_values("days_overdue", ascending=False)
    elif sort_by == "amount ↓":
        enriched = enriched.sort_values("amount", ascending=False)
    else:
        enriched = enriched.sort_values("client_name")

    st.markdown(f"**{len(enriched)} invoices** matching filters")
    st.markdown("---")

    # ── Render each invoice as a card ─────────────────────────────────────────
    for _, row in enriched.iterrows():
        key = int(row["_stage_key"])
        badge_cls = BADGE[key]
        with st.container():
            c1, c2, c3, c4 = st.columns([2, 1.5, 1.5, 1])
            with c1:
                st.markdown(f"**{row['client_name']}**  \n`{row['invoice_no']}`")
            with c2:
                st.markdown(f"₹{float(row['amount']):,.0f}  \n*{row['currency']}*")
            with c3:
                st.markdown(f"**{int(row['days_overdue'])} days** overdue  \nDue: {row['due_date']}")
            with c4:
                st.markdown(f'<span class="badge {badge_cls}">{row["_stage_label"]}</span>', unsafe_allow_html=True)
            st.divider()
