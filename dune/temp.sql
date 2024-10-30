
WITH filtered_calls AS (
    SELECT account_mint,
           call_block_time
    FROM pumpdotfun_solana.pump_call_create
    WHERE call_block_time >= NOW() - INTERVAL '1' day
      AND call_block_time <= NOW() - INTERVAL '4' hour
),
filtered_transactions as (
    SELECT fc.account_mint,
           ft.token_bought_amount,
           ft.token_sold_amount,
           ROW_NUMBER() OVER (PARTITION BY ft.token_sold_mint_address ORDER BY ft.block_time ASC) AS rn
    FROM filtered_calls AS fc
    JOIN dex_solana.trades AS ft  ON ft.token_sold_mint_address = fc.account_mint
    WHERE ft.block_time > fc.call_block_time + INTERVAL '4' hour
      AND ft.block_time < fc.call_block_time + INTERVAL '8' hour
),
    closest_transactions AS (
    SELECT account_mint,
           COALESCE(token_bought_amount / NULLIF(token_sold_amount, 0), 0) AS price
    FROM filtered_transactions
    WHERE rn = 1
)


SELECT *
FROM closest_transactions;
