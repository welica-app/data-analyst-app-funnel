.mode csv
.import project_eligible.csv eligible
.import count_template.csv count_grid
.headers on

SELECT
    CAST(g.step_position AS INTEGER) AS step_position,
    COUNT(DISTINCT e.user_id) AS reached_users
FROM count_grid AS g
LEFT JOIN eligible AS e
    ON CAST(e.step_position AS INTEGER) = CAST(g.step_position AS INTEGER)
WHERE g."group" = 'overall'
GROUP BY CAST(g.step_position AS INTEGER)
ORDER BY step_position;

-- TODO: count each segment by joining e.segment to the chosen segment on the grid.
-- TODO: add previous counts and calculate drop-off with count_template.csv.
