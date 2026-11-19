-- One row per claim: the latest version of each claim.
-- updated_at is unique per claim (guaranteed by the claims system),
-- so rank() keeps exactly one row per claim.
DROP TABLE IF EXISTS claims_latest;
CREATE TABLE claims_latest AS
SELECT event_id, claim_id, policy_id, loss_date, state, incurred_amount, updated_at
FROM (
    SELECT r.*,
           rank() OVER (PARTITION BY claim_id ORDER BY updated_at DESC) AS rn
    FROM raw_claims r
)
WHERE rn = 1;
