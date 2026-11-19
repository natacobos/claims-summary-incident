-- Daily summary for one loss date: one row per state.
-- Finance and actuarial read this table every morning.
INSERT INTO daily_summary (loss_date, state, claim_count, total_incurred)
SELECT loss_date, state, count(*), round(sum(incurred_amount), 2)
FROM claims_latest
WHERE loss_date = :day
  AND incurred_amount >= 0
GROUP BY loss_date, state;
