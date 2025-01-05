WITH
    profitable AS (
        SELECT
            *,
            CASE
                WHEN profit_loss > 0 THEN 1
                ELSE 0
            END AS profitable,
            CASE
                WHEN profit_loss => (total_sol_spent * 2.1) THEN 1
                ELSE 0
            END as win_hit
        FROM
            query_4499255
        WHERE
            total_sol_spent > 0
    ),
    aggregated AS (
        SELECT
            trader_id,
            SUM(total_sol_spent) AS total_sol_spent,
            SUM(profit_loss) AS profit_loss,
            SUM(profitable) AS profitable_tokens,
            COUNT(*) AS totoal_tokens,
            SUM(total_trades) AS total_trades,
            CAST(SUM(profitable) AS DOUBLE) / COUNT(*) AS win_rate,
            (SUM(profit_loss) - SUM(total_sol_spent)) / SUM(total_sol_spent) * 100 as win_percentage,
            SUM(win_hit) as total_wins,
            COUNT(*) / NULLIF(SUM(win_hit), 0) as win_hit_percentage
        FROM
            profitable
        GROUP BY
            trader_id
    )
SELECT
    a.*
FROM
    aggregated as a
    JOIN solana_utils.latest_balances as lb ON lb.address = a.trader_id
WHERE
    a.win_rate < 0.9
    AND a.profit_loss > 0
    AND lb.sol_balance > 1
    AND a.win_percentage >= 100
ORDER BY
    a.win_hit_percentage DESC,
    a.profit_loss DESC
LIMIT
    50;