"""
LangGraph Conditional Edges – route the agent between nodes.
"""

from src.Smart_Credit_Orchestrator.graph.state import AgentState


def route_after_classify(state: AgentState) -> str:
    """After classify_stage: go to escalate if 30+ days overdue, else generate email."""
    return "escalate_record" if state.get("is_escalated") else "generate_email"


def route_after_validate(state: AgentState) -> str:
    """After validate_output: send if valid, retry up to 2x, then fail."""
    if state.get("validation_passed"):
        return "send_email"
    if state.get("retry_count", 0) < 2:
        return "regenerate_email"
    return "fail_invoice"
