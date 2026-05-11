import streamlit as st
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.Smart_Credit_Orchestrator.services import audit_service, escalation_service
import pandas as pd
from pathlib import Path


def render():
    st.markdown("""
    <div class="page-header">
      <h1>🏠 Dashboard</h1>
      <p>Live overview of your invoice collection pipeline</p>
    </div>""", unsafe_allow_html=True)

    # ── Stats row ─────────────────────────────────────────────────────────────
    stats = audit_service.get_stats()
    c1, c2, c3, c4, c5 = st.columns(5)
    for col, label, key, color in [
        (c1, "Total Processed", "total",     "#818cf8"),
        (c2, "Dry Run",        "dry_run",    "#38bdf8"),
        (c3, "Sent",           "sent",       "#34d399"),
        (c4, "Escalated",      "escalated",  "#fbbf24"),
        (c5, "Failed",         "failed",     "#f87171"),
    ]:
        col.markdown(f"""
        <div class="stat">
          <div class="n" style="color:{color}">{stats.get(key, 0)}</div>
          <div class="l">{label}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Invoice overview from CSV ──────────────────────────────────────────────
    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.markdown("#### 📊 Invoice Stage Distribution")
        csv = Path("./data/sample_invoices.csv")
        if csv.exists():
            df = pd.read_csv(csv)
            counts = {1: 0, 2: 0, 3: 0, 4: 0, 99: 0}
            for _, row in df.iterrows():
                stage, esc = escalation_service.resolve_stage(int(row["days_overdue"]))
                counts[99 if esc else stage] += 1

            chart_df = pd.DataFrame({
                "Stage": ["Stage 1\nWarm", "Stage 2\nFirm", "Stage 3\nSerious", "Stage 4\nUrgent", "Escalated"],
                "Count": [counts[1], counts[2], counts[3], counts[4], counts[99]],
            })
            st.bar_chart(chart_df.set_index("Stage"), color="#818cf8")
        else:
            st.info("No invoice CSV found at `data/sample_invoices.csv`")

    with col_right:
        st.markdown("#### 📌 Quick Facts")
        if csv.exists():
            df = pd.read_csv(csv)
            total_amount = df["amount"].sum()
            avg_overdue = df["days_overdue"].mean()
            st.markdown(f"""
            <div class="card">
              <h4>Total Receivables</h4>
              <div class="val">₹{total_amount:,.0f}</div>
            </div>
            <div class="card" style="border-color:#fbbf24">
              <h4>Avg Days Overdue</h4>
              <div class="val" style="color:#fbbf24">{avg_overdue:.1f} days</div>
            </div>
            <div class="card" style="border-color:#34d399">
              <h4>Total Invoices</h4>
              <div class="val" style="color:#34d399">{len(df)}</div>
            </div>
            """, unsafe_allow_html=True)
