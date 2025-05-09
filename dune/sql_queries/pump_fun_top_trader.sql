WITH profitable AS (SELECT *,
                           CASE
                               WHEN (profit_loss - total_sol_spent) / (total_sol_spent * 100) > 1 THEN 1
                               ELSE 0 END                              AS win_hit,
                           CASE WHEN profit_loss > 0 THEN 1 ELSE 0 END AS profitable
                    FROM query_4284948),
     aggregated AS (SELECT trader_id,
                           SUM(total_sol_spent)                                                   AS total_sol_spent,
                           SUM(profit_loss)                                                       AS profit_loss,
                           SUM(profitable)                                                        AS profitable_trades,
                           SUM(total_trades)                                                      AS total_trades,
                           CAST(SUM(profitable) AS DOUBLE) / CAST(COUNT(*) AS DOUBLE)             AS win_rate,
                           (SUM(profit_loss) - SUM(total_sol_spent)) / SUM(total_sol_spent) * 100 as win_percentage,
                           SUM(win_hit)                                                           as total_wins,
                           COUNT(*) / SUM(win_hit)                                                as win_hit_percentage
                    FROM profitable
                    GROUP BY trader_id)
SELECT a.*
FROM aggregated as a
         JOIN solana_utils.latest_balances as lb on lb.address = a.trader_id
WHERE a.win_rate < 0.9
  AND a.profit_loss > 0
  AND a.total_trades >= 30
  AND a.total_trades <= 1500
  AND lb.sol_balance > 1
  AND win_percentage >= 100
ORDER BY a.win_rate DESC, a.profit_loss DESC
LIMIT 50