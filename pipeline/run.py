"""Daily claims pipeline. The orchestrator calls run_batch(conn, path) once per daily file
(and retries it if the run times out)."""
import csv
import sqlite3
from pathlib import Path

MODELS = Path(__file__).parent / "models"


def create_tables(conn: sqlite3.Connection) -> None:
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS raw_claims (
            event_id INTEGER, claim_id TEXT, policy_id TEXT, loss_date TEXT,
            state TEXT, incurred_amount REAL, updated_at TEXT
        );
        CREATE TABLE IF NOT EXISTS daily_summary (
            loss_date TEXT, state TEXT, claim_count INTEGER, total_incurred REAL
        );
    """)


def load_batch(conn: sqlite3.Connection, path) -> list[dict]:
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    conn.executemany(
        "INSERT INTO raw_claims VALUES (:event_id, :claim_id, :policy_id, :loss_date, :state, :incurred_amount, :updated_at)",
        rows,
    )
    return rows


def run_batch(conn: sqlite3.Connection, path) -> None:
    create_tables(conn)
    rows = load_batch(conn, path)
    conn.executescript((MODELS / "claims_latest.sql").read_text())
    for day in sorted({r["loss_date"] for r in rows}):
        conn.execute((MODELS / "daily_summary.sql").read_text(), {"day": day})
    conn.commit()
