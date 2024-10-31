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
        CAST(SUM(profitable) AS DOUBLE) / CAST(COUNT(*) AS DOUBLE) AS win_rate,
        (SUM(profit_loss) - SUM(total_sol_spent)) / SUM(total_sol_spent) * 100 as win_percentage
    FROM profitable
    GROUP BY trader_id
)

SELECT *
FROM aggregated as a
JOIN solana_utils.latest_balances as lb on lb.address = a.trader_id
WHERE a.win_rate < 0.9 AND a.profit_loss > 0
  AND a.total_trades >= 15 AND a.total_trades <= 300
  AND lb.sol_balance > 1 AND win_percentage >= 100
ORDER BY a.win_rate DESC, a.profit_loss DESC
LIMIT 50
