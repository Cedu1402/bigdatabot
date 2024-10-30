WITH filtered_trades AS (SELECT trader_id,
                                token_sold_amount,
                                token_bought_amount,
                                token_bought_mint_address,
                                block_time
                         FROM dex_solana.trades
                         WHERE token_sold_mint_address = 'So11111111111111111111111111111111111111112'
                           AND token_sold_amount >= 1
                           AND block_time >= NOW() - INTERVAL '1' month),
     filtered_calls AS (SELECT account_mint,
                               call_block_time,
                               account_user
                        FROM pumpdotfun_solana.pump_call_create
                        WHERE call_block_time >= NOW() - INTERVAL '1' month
                          AND call_block_time <= NOW() - INTERVAL '4' hour),
     joined_data AS (SELECT fc.account_mint,
                            ft.trader_id,
                            ft.token_sold_amount,
                            ft.token_bought_amount
                     FROM filtered_calls AS fc
                              JOIN filtered_trades AS ft ON ft.token_bought_mint_address = fc.account_mint AND fc.account_user != ft.trader_id
                         AND ft.block_time <= fc.call_block_time + INTERVAL '4' hour),
     interesting_traders AS (SELECT trader_id
                             FROM joined_data
                             GROUP BY trader_id),
     filtered_sell_trades AS (SELECT trader_id,
                                     token_sold_amount,
                                     token_bought_amount,
                                     token_sold_mint_address
                              FROM dex_solana.trades
                              WHERE token_bought_mint_address = 'So11111111111111111111111111111111111111112'
                                AND block_time >= NOW() - INTERVAL '1' month),
     sell_tx AS (SELECT fc.account_mint,
                        fst.trader_id,
                        fst.token_sold_amount,
                        fst.token_bought_amount
                 FROM interesting_traders AS it
                          JOIN filtered_sell_trades AS fst on it.trader_id = fst.trader_id
                          JOIN filtered_calls as fc on fc.account_mint = fst.token_sold_mint_address),
     buy_summary as (SELECT account_mint,
                            trader_id,
                            SUM(token_sold_amount)   AS sol_spent,
                            SUM(token_bought_amount) as token_received
                     FROM joined_data
                     GROUP BY account_mint,
                              trader_id),
     sell_summary as (SELECT account_mint,
                             trader_id,
                             SUM(token_sold_amount)   AS token_spent,
                             SUM(token_bought_amount) as sol_received
                      FROM sell_tx
                      GROUP BY account_mint,
                               trader_id
),
filtered_last_price_transactions as (
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
    FROM filtered_last_price_transactions
    WHERE rn = 1
)

SELECT
    bs.account_mint,
    bs.trader_id,
    bs.sol_spent AS total_sol_spent,
    COALESCE(ss.sol_received, 0) AS total_sol_received,
    COALESCE(ss.token_spent, 0) AS total_token_sold,
    GREATEST(COALESCE(bs.token_received, 0) - COALESCE(ss.token_spent, 0), 0) AS unsold_tokens,
    COALESCE(GREATEST((COALESCE(bs.token_received, 0) - COALESCE(ss.token_spent, 0)) * COALESCE(ct.price, 0), 0), 0) AS unsold_value,
    COALESCE((COALESCE(ss.sol_received, 0) +
               GREATEST((COALESCE(bs.token_received, 0) - COALESCE(ss.token_spent, 0)) * COALESCE(ct.price, 0), 0)) -
               COALESCE(bs.sol_spent, 0), 0) AS profit_loss
FROM
    buy_summary AS bs
LEFT JOIN
    sell_summary AS ss ON ss.account_mint = bs.account_mint AND ss.trader_id = bs.trader_id
LEFT JOIN
    closest_transactions AS ct ON ct.account_mint = bs.account_mint;
