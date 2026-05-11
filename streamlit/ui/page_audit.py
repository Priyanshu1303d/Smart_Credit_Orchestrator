import streamlit as st
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.Smart_Credit_Orchestrator.services import audit_service

STATUS_COLOR = {
    "dry_run":   "#38bdf8",
    "sent":      "#34d399",
    "escalated": "#fbbf24",
    "failed":    "#f87171",
}
STAGE_LABEL = {1: "Warm", 2: "Firm", 3: "Serious", 4: "Urgent"}


def render():
    st.markdown("""
    <div class="page-header">
      <h1>📜 Audit Log</h1>
      <p>Every invoice the agent has processed — immutable, timestamped record</p>
    </div>""", unsafe_allow_html=True)

    logs = audit_service.get_all_logs()

    if not logs:
        st.info("No audit entries yet. Run the agent on some invoices first.")
        return

    # ── Stats strip ───────────────────────────────────────────────────────────
    stats = audit_service.get_stats()
    c1, c2, c3, c4 = st.columns(4)
    for col, label, key, color in [
        (c1, "Total",     "total",     "#818cf8"),
        (c2, "Dry Run",   "dry_run",   "#38bdf8"),
        (c3, "Escalated", "escalated", "#fbbf24"),
        (c4, "Failed",    "failed",    "#f87171"),
    ]:
        col.markdown(f"""
        <div class="stat">
          <div class="n" style="color:{color}">{stats.get(key,0)}</div>
          <div class="l">{label}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Filters ───────────────────────────────────────────────────────────────
    col1, col2 = st.columns([2, 1])
    with col1:
        search = st.text_input("Search invoice / client", placeholder="INV-2024-007 or Arjun")
    with col2:
        status_filter = st.selectbox("Status", ["All", "dry_run", "sent", "escalated", "failed"])

    filtered = logs
    if search:
        s = search.lower()
        filtered = [l for l in filtered if s in l.get("invoice_no","").lower() or s in l.get("client_name","").lower()]
    if status_filter != "All":
        filtered = [l for l in filtered if l.get("send_status") == status_filter]

    st.markdown(f"**{len(filtered)} entries**")
    st.markdown("---")

    # ── Log entries ───────────────────────────────────────────────────────────
    for entry in reversed(filtered):
        status = entry.get("send_status", "unknown")
        color  = STATUS_COLOR.get(status, "#64748b")
        stage  = entry.get("tone_stage", 0)

        with st.expander(
            f"#{entry.get('id','?')}  ·  {entry.get('invoice_no')}  ·  "
            f"{entry.get('client_name')}  ·  ₹{float(entry.get('amount',0)):,.0f}  ·  {status.upper()}"
        ):
            c1, c2 = st.columns([3, 1])
            with c1:
                st.markdown(f"**Subject:** {entry.get('subject','–')}")
                st.markdown(f"**Preview:** {entry.get('body_preview','–')}")
                st.caption(f"📅 {entry.get('timestamp','–')}  ·  📧 {entry.get('contact_email_masked','–')}")
            with c2:
                st.markdown(f"""
                <div style="text-align:center;padding:.8rem;background:#0f172a;
                            border-radius:10px;border:1px solid {color}55;">
                  <div style="font-size:1.4rem;font-weight:700;color:{color}">
                    Stage {stage}
                  </div>
                  <div style="font-size:.75rem;color:{color};margin-top:.2rem">
                    {STAGE_LABEL.get(stage,'–')}
                  </div>
                  <div style="margin-top:.5rem;font-weight:600;font-size:.8rem;color:{color}">
                    {status.upper()}
                  </div>
                </div>""", unsafe_allow_html=True)
                if entry.get("is_escalated"):
                    st.warning("⚖️ Escalated")
