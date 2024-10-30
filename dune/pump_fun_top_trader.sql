WITH profitable AS (
    SELECT *,
           CASE WHEN profit_loss > 0 THEN 1 ELSE 0 END AS profitable
    FROM query_4208224
),
aggregated AS (
    SELECT
        trader_id,
        SUM(total_sol_spent) AS total_sol_spent,
        SUM(profit_loss) AS profit_loss,
        SUM(profitable) AS profitable_trades,
        COUNT(*) AS total_trades,
        CAST(SUM(profitable) AS DOUBLE) / CAST(COUNT(*) AS DOUBLE) AS win_rate
    FROM profitable
    WHERE profit_loss > 0
    GROUP BY trader_id
)

SELECT *
FROM aggregated
WHERE win_rate < 1
ORDER BY win_rate DESC, profit_loss DESC
LIMIT 500
