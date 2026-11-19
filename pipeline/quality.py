"""Data quality checks the pipeline runs after every batch (task 3).

check_quality(conn) returns a list of problems found in claims_latest and daily_summary;
an empty list means the data is fine to publish.
"""
import sqlite3


def check_quality(conn: sqlite3.Connection) -> list[str]:
    problems: list[str] = []
    # TODO (task 3): add the checks that would have caught this incident.
    return problems
