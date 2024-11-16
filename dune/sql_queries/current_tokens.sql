WITH filtered_pcc AS (
    SELECT account_mint, call_block_time
    FROM pumpdotfun_solana.pump_call_create
    WHERE call_block_time BETWEEN TIMESTAMP '2024-11-01 00:00:00' AND TIMESTAMP '2024-11-09 23:59:59'
),
filtered_trades AS (
    SELECT token_bought_mint_address, block_time, t.trader_id
    FROM dex_solana.trades AS t
    JOIN dune.testnet3232.result_solana_pump_dot_fun_top_trader AS q4 ON t.trader_id = q4.trader_id
    WHERE block_time BETWEEN TIMESTAMP '2024-11-01 00:00:00' AND TIMESTAMP '2024-11-09 23:59:59'
    AND token_sold_mint_address = 'So11111111111111111111111111111111111111112'
)

SELECT f_pcc.account_mint, MIN(f_pcc.call_block_time) AS call_block_time
FROM filtered_pcc AS f_pcc
JOIN filtered_trades AS f_t ON f_pcc.account_mint = f_t.token_bought_mint_address
WHERE f_t.block_time BETWEEN f_pcc.call_block_time
      AND f_pcc.call_block_time + INTERVAL '4' HOUR
GROUP BY f_pcc.account_mint;
