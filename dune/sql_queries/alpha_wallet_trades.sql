WITH
    date_range AS (
        SELECT
            NOW() - INTERVAL '1' month AS start_time,
            NOW() - INTERVAL '7' day AS end_time
    ),
    filtered_calls AS (
        SELECT
            fc.account_mint,
            fc.call_block_time,
            fc.account_user
        FROM
            pumpdotfun_solana.pump_call_create fc
            JOIN date_range dr ON fc.call_block_time BETWEEN dr.start_time AND dr.end_time
    ),
    pre_filtered_trades AS (
        SELECT
            t.trader_id,
            t.token_bought_mint_address,
            t.block_time,
            fc.call_block_time,
            t.amount_usd / (t.token_bought_amount_raw / 1e6) as token_price
        FROM
            dex_solana.trades t
            JOIN date_range dr ON t.block_time BETWEEN dr.start_time AND dr.end_time
            JOIN filtered_calls fc ON t.token_bought_mint_address = fc.account_mint
            LEFT JOIN dune.testnet3232.result_solana_bots b ON t.trader_id = b.identifier
        WHERE
            t.token_sold_mint_address = 'So11111111111111111111111111111111111111112'
            AND t.token_sold_amount >= 1
            AND t.token_bought_amount_raw > 0
            AND t.block_time <= fc.call_block_time + INTERVAL '10' hour
            AND b.identifier IS NULL
    ),
    price_stats AS (
        SELECT
            token_bought_mint_address,
            APPROX_PERCENTILE(token_price, 0.25) AS q1,
            APPROX_PERCENTILE(token_price, 0.75) AS q3
        FROM
            pre_filtered_trades
        GROUP BY
            token_bought_mint_address
    ),
    filtered_trades AS (
        SELECT
            t.*
        FROM
            pre_filtered_trades t
            JOIN price_stats ps ON t.token_bought_mint_address = ps.token_bought_mint_address
        WHERE
            t.token_price BETWEEN (ps.q1 - 0 * (ps.q3 - ps.q1)) AND (ps.q3 + 0 * (ps.q3 - ps.q1))
    ),
    buy_trades AS (
        SELECT
            t.token_bought_mint_address,
            t.trader_id,
            t.token_price,
            t.block_time,
            ROW_NUMBER() OVER (
                PARTITION BY
                    t.trader_id,
                    t.token_bought_mint_address
                ORDER BY
                    t.block_time DESC
            ) AS rn
        FROM
            filtered_trades t
        WHERE t.block_time <= t.call_block_time + INTERVAL '5' hour
    ),
    buy_summary AS (
        SELECT
            token_bought_mint_address,
            trader_id,
            token_price AS buy_price,
            block_time
        FROM
            buy_trades
        WHERE
            rn = 1
    ),
    min_buy_time AS (
        SELECT
            token_bought_mint_address,
            MIN(block_time) AS min_block_time
        FROM
            buy_summary
        GROUP BY
            token_bought_mint_address
    ),
    filtered_price_transaction AS (
        SELECT
            date_trunc('minute', t.block_time) AS min_tick,
            token_price,
            t.token_bought_mint_address
        FROM
            filtered_trades t
            JOIN min_buy_time mb ON t.token_bought_mint_address = mb.token_bought_mint_address
            JOIN filtered_calls tc ON t.token_bought_mint_address = tc.account_mint
        WHERE
            t.block_time > mb.min_block_time
            AND t.block_time < tc.call_block_time + INTERVAL '10' hour
    ),
    token_prices AS (
        SELECT
            token_bought_mint_address,
            min_tick,
            APPROX_PERCENTILE(token_price, 0.95) AS token_price
        FROM
            filtered_price_transaction
        GROUP BY
            token_bought_mint_address,
            min_tick
    )
SELECT
    b.*,
    tp.token_price as max_price,
    ((tp.token_price - b.buy_price) / b.buy_price) * 100 AS percentage_return
FROM
    buy_summary b
    JOIN token_prices tp ON tp.min_tick <= b.block_time
    AND tp.min_tick + INTERVAL '1' minute > b.block_time
                                AND tp.token_bought_mint_address = b.token_bought_mint_address
ORDER BY percentage_return DESC