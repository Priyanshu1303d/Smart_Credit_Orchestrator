"""
Smart Credit Orchestrator – FastAPI entry point.

Run locally:
  uvicorn main:app --reload --port 8000

Then open: http://localhost:8000/docs
"""

import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Load .env before any LangChain/Groq imports so tracing picks up the keys
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

from src.Smart_Credit_Orchestrator.api.routes import router
from src.Smart_Credit_Orchestrator.graph.workflow import get_graph

app = FastAPI(
    title="Smart Credit Orchestrator",
    description="AI agent that generates escalating invoice follow-up emails using LangGraph + Groq.",
    version="1.0.0",
)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.include_router(router, prefix="/api/v1")


@app.on_event("startup")
def startup():
    """Pre-compile the LangGraph on startup so the first request isn't slow."""
    logging.info("LangSmith tracing: %s", os.getenv("LANGCHAIN_TRACING_V2", "false"))
    get_graph()
    logging.info("LangGraph ready. Docs → http://localhost:8000/docs")


@app.get("/", include_in_schema=False)
def root():
    return {"service": "Smart Credit Orchestrator", "docs": "/docs", "health": "/api/v1/health"}
