from pathlib import Path
from dotenv import load_dotenv
import sqlite3
import os
from src.Smart_Credit_Orchestrator.app.models import AuditLogEntry

curr_dir = Path(__file__).resolve().parent
root_dir = curr_dir.parents[2]

load_dotenv(root_dir / ".env")

AUDIT_DB_PATH=os.getenv("AUDIT_DB_PATH")
if not AUDIT_DB_PATH:
    raise ValueError("AUDIT DB PATH not present")


def create_db() -> None:
    """Create the SQLite database and audit table."""

    try:
        con = sqlite3.connect(AUDIT_DB_PATH)
        print("connected to the DB ... ")
        con.execute(
            """ CREATE TABLE IF NOT EXISTS query_audit(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_no TEXT NOT NULL,
            client_name TEXT NOT NULL,
            contact_email_masked TEXT NOT NULL,
            amount REAL NOT NULL,
            currency TEXT NOT NULL,
            days_overdue INTEGER NOT NULL,
            tone_stage INTEGER NOT NULL,
            tone_label TEXT NOT NULL,
            subject TEXT NOT NULL,
            body_preview TEXT NOT NULL,
            send_status TEXT NOT NULL,
            is_escalated INTEGER NOT NULL,
            timestamp TEXT NOT NULL
            )
        """)
        con.commit()
        con.close()
    except Exception as e:
        raise ValueError(f"Not able to create db due to {e} ")


def write_db(entry : AuditLogEntry) -> None:
    """Write one audit entry to the database."""

    try:
        con = sqlite3.connect(AUDIT_DB_PATH)
        print("Successfully connected to the db ... ")

        con.execute("""
            INSERT INTO query_audit (
                    invoice_no,
                    client_name,
                    contact_email_masked,
                    amount,
                    currency,
                    days_overdue,
                    tone_stage,
                    tone_label,
                    subject,
                    body_preview,
                    send_status,
                    is_escalated,
                    timestamp
                )
            VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,(
            entry.invoice_no,
            entry.client_name,
            entry.contact_email_masked,
            entry.amount,
            entry.currency,
            entry.days_overdue,
            entry.tone_stage,
            entry.tone_label,
            entry.subject,
            entry.body_preview,
            entry.send_status,
            entry.is_escalated,
            entry.timestamp
        ))

        con.commit()
        con.close()
    except Exception as e:
      raise ValueError(f"Not able to write in db due to {e} ")
