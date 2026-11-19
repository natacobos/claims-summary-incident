import sqlite3
import unittest
from pathlib import Path

from pipeline.run import run_batch

DATA = Path(__file__).parent.parent / "data"


def summary(conn):
    return {(d, s): (c, t) for d, s, c, t in conn.execute(
        "SELECT loss_date, state, claim_count, total_incurred FROM daily_summary")}


class PipelineTests(unittest.TestCase):
    def test_first_batch_summary(self):
        conn = sqlite3.connect(":memory:")
        run_batch(conn, DATA / "claims_2025-01-03.csv")
        self.assertEqual(summary(conn)[("2025-01-02", "CA")], (1, 8000.0))
        self.assertEqual(summary(conn)[("2025-01-02", "TX")], (2, 16500.5))

    def test_negative_amounts_are_excluded(self):
        conn = sqlite3.connect(":memory:")
        run_batch(conn, DATA / "claims_2025-01-03.csv")
        self.assertNotIn(-50.0, [t for _, t in summary(conn).values()])


if __name__ == "__main__":
    unittest.main()
