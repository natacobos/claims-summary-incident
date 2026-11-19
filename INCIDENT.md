# Incident: daily claims summary does not match the claims system

**Reported by:** Priya, finance (with the actuarial team), Monday 2025-01-06, 08:15.

> The daily claims summary we used for this morning's reserve review does not match the claims
> system. For loss date 2025-01-02 in Texas the summary says 9 claims and $72,501.50; the claims
> system says 2 open claims and $19,000.00. California and New York look too high as well.
> We need to know which numbers we can trust and when it will be fixed.

What the on-call engineer found so far:

- The orchestrator ran the 2025-01-03 file twice: the first run timed out after loading and was retried.
- The 2025-01-04 file included a late update to claim C100 (loss date 2025-01-02), which had already been
  reported in the 2025-01-03 summary.
- `daily_summary` now has several rows for some loss dates and states. Finance adds them up.
- The team's tests pass.

## Data rules (agreed with finance)

1. A claim counts once, with its **latest version**: the greatest `updated_at`; if two versions have the
   same `updated_at`, the one with the greater `event_id`.
2. Claims with a negative `incurred_amount` are excluded from the summary.
3. `daily_summary` has **exactly one row per `loss_date` and `state`**, and it always reflects the latest
   version of every claim, including updates that arrive days later.
4. Running the same file again must not change the result.
