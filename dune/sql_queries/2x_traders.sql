WITH
max_values AS (
    SELECT
        MAX(total_tokens) as max_tokens,
        MAX(profit_loss) as max_profit_loss
    FROM dune.testnet3232.result_bot_filtered_pnl_1_week
)
SELECT
    a.*,
    -- Composite Score Calculation
    (0.3 * a.win_rate) as composit_win_rate,
    (0.3 * (a.total_tokens / mv.max_tokens)) as composit_total_tokens,
    (0.3 * (a.profit_loss / mv.max_profit_loss)) as composit_profit_loss,
    (0.3 * a.win_hit_percentage) as composit_hit_percentage,
    (0.3 * a.win_rate) +
    (0.3 * (a.total_tokens / mv.max_tokens)) +
    (0.3 * (a.profit_loss / mv.max_profit_loss)) +
    (0.3 * a.win_hit_percentage) AS composite_score
FROM
    dune.testnet3232.result_bot_filtered_pnl_1_week as a
    CROSS JOIN max_values mv
    JOIN solana_utils.latest_balances lb ON lb.address = a.trader_id
WHERE a.profit_loss > 0
    AND lb.sol_balance > 1
    AND a.win_percentage >= 100
    AND a.win_hit_percentage >= 0.5
ORDER BY
    total_wins DESC
LIMIT
    100;