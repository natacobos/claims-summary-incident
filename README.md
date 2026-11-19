# Claims summary incident

You lead the data platform of an insurance company. This morning finance reported that the daily
claims summary does not match the claims system (`INCIDENT.md`). The pipeline was written by an
engineer on your team and its tests pass. Find out why, fix it, and make sure it cannot happen again.

Python 3.10 or newer, standard library only (SQLite in memory). Nothing to install.
You may use your AI tool; we will watch how you use it.

## Files

- `INCIDENT.md`: what finance reported and the **data rules**.
- `pipeline/run.py`: loads a daily file and builds the tables (`run_batch` is what the orchestrator calls).
- `pipeline/models/`: the SQL models (`claims_latest`, `daily_summary`).
- `pipeline/quality.py`: data quality checks, to write (task 3).
- `data/`: the two daily files. `tests/`: the team's tests (`python3 -m unittest`).
- `NOTES.md`: your notes.

## Tasks: 15 minutes in total

1. **Diagnose (about 4 minutes).** Why are the numbers wrong? Write the causes in `NOTES.md`.
2. **Fix (about 6 minutes).** Change the pipeline so it follows the data rules in `INCIDENT.md`.
   Keep `run_batch(conn, path)` and the table names.
3. **Prevent (about 3 minutes).** Write `check_quality` in `pipeline/quality.py`: the checks that
   would have caught this before finance did. They must not report problems on correct data.
4. **Communicate (about 2 minutes).** Finish `NOTES.md`: what you changed, and your message to finance and the team.

If you are still on one task two minutes after its time, move to the next one.
Do not change the `check/` folder: the interviewer uses it at the end.
