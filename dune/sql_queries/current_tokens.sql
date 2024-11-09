WITH filtered_pcc AS (
    SELECT account_mint, call_block_time
    FROM pumpdotfun_solana.pump_call_create
    WHERE call_block_time BETWEEN cast('{{time_from}}' as timestamp) AND cast('{{time_to}}' as timestamp)
),
filtered_trades AS (
    SELECT token_bought_mint_address, block_time, t.trader_id
    FROM dex_solana.trades as t
    JOIN query_4217799 AS q4 ON t.trader_id = q4.trader_id
    WHERE block_time BETWEEN cast('{{time_from}}' as timestamp) AND cast('{{time_to}}' as timestamp)
    AND token_sold_mint_address = 'So11111111111111111111111111111111111111112'
)

SELECT f_pcc.account_mint
FROM filtered_pcc AS f_pcc
JOIN filtered_trades AS f_t ON f_pcc.account_mint = f_t.token_bought_mint_address
WHERE f_t.block_time BETWEEN f_pcc.call_block_time
      AND f_pcc.call_block_time + INTERVAL '{{min_token_age_h}}' hour
GROUP BY f_pcc.account_mint