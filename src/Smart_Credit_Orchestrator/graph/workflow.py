"""
LangGraph Workflow – builds and compiles the StateGraph.

Graph topology:
  classify_stage
    ├─(is_escalated)──► escalate_record ──► write_audit ──► END
    └─(else)──────────► generate_email
                            └──► validate_output
                                   ├─(valid)──────────────► send_email ──► write_audit ──► END
                                   ├─(retry < 2)──────────► regenerate_email ──► validate_output
                                   └─(retries exhausted)──► fail_invoice ──► write_audit ──► END
"""

import logging
from langgraph.graph import StateGraph, END

from src.Smart_Credit_Orchestrator.graph.state import AgentState
from src.Smart_Credit_Orchestrator.graph.nodes import (
    classify_stage, generate_email, validate_output,
    regenerate_email, send_email, escalate_record,
    fail_invoice, write_audit,
)
from src.Smart_Credit_Orchestrator.graph.edges import route_after_classify, route_after_validate

logger = logging.getLogger(__name__)

_graph = None  # singleton — compiled once, reused by FastAPI


def get_graph():
    """Build and cache the compiled LangGraph StateGraph."""
    global _graph
    if _graph is None:
        g = StateGraph(AgentState)

        # Add nodes
        for name, fn in [
            ("classify_stage",   classify_stage),
            ("generate_email",   generate_email),
            ("validate_output",  validate_output),
            ("regenerate_email", regenerate_email),
            ("send_email",       send_email),
            ("escalate_record",  escalate_record),
            ("fail_invoice",     fail_invoice),
            ("write_audit",      write_audit),
        ]:
            g.add_node(name, fn)

        # Entry point
        g.set_entry_point("classify_stage")

        # Conditional edge 1: classify → generate or escalate
        g.add_conditional_edges("classify_stage", route_after_classify,
                                {"generate_email": "generate_email", "escalate_record": "escalate_record"})

        # Static edge: generate → validate
        g.add_edge("generate_email", "validate_output")

        # Conditional edge 2: validate → send, retry, or fail
        g.add_conditional_edges("validate_output", route_after_validate,
                                {"send_email": "send_email", "regenerate_email": "regenerate_email", "fail_invoice": "fail_invoice"})

        # Retry loop
        g.add_edge("regenerate_email", "validate_output")

        # All terminal nodes → audit → END
        for terminal in ("send_email", "escalate_record", "fail_invoice"):
            g.add_edge(terminal, "write_audit")
        g.add_edge("write_audit", END)

        _graph = g.compile()
        logger.info("[workflow] LangGraph compiled OK")
    return _graph
