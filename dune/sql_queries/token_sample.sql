WITH
    filtered_calls AS (
        SELECT
            account_mint,
            call_block_time,
            account_user
        FROM
            pumpdotfun_solana.pump_call_create
        WHERE
            call_block_time BETWEEN NOW() - INTERVAL '12' MONTH AND NOW()
    ),
    interresting_trades as (
        SELECT
            token_bought_mint_address,
            block_time,
            token_sold_amount_raw,
            token_bought_amount_raw,
            amount_usd
        FROM
            dex_solana.trades AS t
        WHERE
            token_sold_mint_address = 'So11111111111111111111111111111111111111112'
            AND token_bought_mint_address IN (
                SELECT
                    account_mint
                FROM
                    filtered_calls
            )
            AND token_sold_amount >= 1
            AND block_time BETWEEN NOW() - INTERVAL '12' MONTH AND NOW()
            AND token_bought_amount > 1
    ),
    pre_filterd_trades as (
        SELECT
            token_bought_mint_address,
            block_time,
            amount_usd / (token_bought_amount_raw / 1e6) AS token_price,
            call_block_time as launch_date
        FROM
            interresting_trades AS t
            JOIN filtered_calls as fc on t.token_bought_mint_address = fc.account_mint
        WHERE
            block_time BETWEEN fc.call_block_time AND fc.call_block_time  + INTERVAL '10' hour
    ),
    price_stats AS (
        SELECT
            token_bought_mint_address,
            APPROX_PERCENTILE(token_price, 0.25) AS q1,
            APPROX_PERCENTILE(token_price, 0.75) AS q3
        FROM
            pre_filterd_trades
        GROUP BY
            token_bought_mint_address
    ),
    filtered_trades AS (
        SELECT
            t.*
        FROM
            pre_filterd_trades t
            JOIN price_stats ps ON t.token_bought_mint_address = ps.token_bought_mint_address
        WHERE
            t.token_price BETWEEN (ps.q1 - 0 * (ps.q3 - ps.q1)) AND (ps.q3 + 0 * (ps.q3 - ps.q1))
    ),
    rolling_avg AS (
        SELECT
            token_bought_mint_address,
            block_time,
            token_price,
            launch_date,
            AVG(token_price) OVER (
                PARTITION BY
                    token_bought_mint_address
                ORDER BY
                    block_time ROWS BETWEEN 20 PRECEDING
                    AND CURRENT ROW
            ) AS moving_avg
        FROM
            filtered_trades
    ),
    market_caps as (
        SELECT
            token_bought_mint_address,
            MAX(launch_date) as launch_date,
            APPROX_PERCENTILE(moving_avg, 0.95) AS token_price,
            APPROX_PERCENTILE(moving_avg, 0.95) * 1000000000 AS max_mc
        FROM
            rolling_avg as t
        GROUP BY
            token_bought_mint_address
    ),
    market_caps_buckets AS (
        SELECT
            *,
            CASE
                WHEN max_mc BETWEEN 1000 AND 10000 THEN 1
                WHEN max_mc BETWEEN 10001 AND 25000 THEN 2
                WHEN max_mc BETWEEN 25001 AND 50000 THEN 3
                WHEN max_mc BETWEEN 50001 AND 100000 THEN 4
                WHEN max_mc BETWEEN 100001 AND 200000 THEN 5
                WHEN max_mc BETWEEN 200001 AND 500000 THEN 6
                WHEN max_mc BETWEEN 500001 AND 750000 THEN 7
                WHEN max_mc BETWEEN 750001 AND 1000000 THEN 8
                WHEN max_mc BETWEEN 1000001 AND 2000000 THEN 9
                WHEN max_mc BETWEEN 2000001 AND 5000000 THEN 10
                WHEN max_mc BETWEEN 5000001 AND 10000000 THEN 11
                WHEN max_mc BETWEEN 10000001 AND 20000000 THEN 12
                WHEN max_mc BETWEEN 20000001 AND 50000000 THEN 13
                WHEN max_mc BETWEEN 50000001 AND 75000000 THEN 14
                WHEN max_mc BETWEEN 75000001 AND 100000000 THEN 15
                WHEN max_mc BETWEEN 100000001 AND 200000000 THEN 16
                WHEN max_mc BETWEEN 200000001 AND 500000000 THEN 17
                WHEN max_mc > 500000001 THEN 18
            END AS bucket
        FROM
            market_caps
        where max_mc > 1000
    ),
    numbered AS (
        SELECT
            *,
            ROW_NUMBER() OVER (
                PARTITION BY
                    bucket
                ORDER BY
                    token_bought_mint_address DESC
            ) AS rn
        FROM
            market_caps_buckets
    )
SELECT
    token_bought_mint_address as token,
    -- token_price,
    -- max_mc,
    -- bucket,
    launch_date as launch_time
FROM
    numbered
WHERE
    rn <= CASE
        WHEN bucket = 18 THEN 10000
        ELSE 3000
    END
ORDER BY
    bucket DESC,
    token_bought_mint_address DESC;