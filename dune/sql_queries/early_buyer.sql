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
            amount_usd,
            trader_id
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
            call_block_time as launch_date,
            trader_id
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
            token_bought_mint_address as token,
            MAX(launch_date) as launch_time,
            APPROX_PERCENTILE(moving_avg, 0.95) AS token_price,
            APPROX_PERCENTILE(moving_avg, 0.95) * 1000000000 AS max_mc
        FROM
            rolling_avg as t
        GROUP BY
            token_bought_mint_address
    ),
    tokens as (
        SELECT
            token
        FROM
            market_caps
        WHERE
            max_mc > 1000000
    ),
    mc_reached_time as (
        SELECT
            token_bought_mint_address,
            MIN(block_time) as first_time_reached
        FROM
            pre_filterd_trades
        WHERE
            token_price > 1000000
        GROUP BY
            token_bought_mint_address
    ),
    trader_trades as (
        SELECT
            t.trader_id,
            t.token_bought_mint_address
        FROM
            pre_filterd_trades as t
            JOIN filtered_calls as fc on t.token_bought_mint_address = fc.account_mint
            JOIN mc_reached_time as mc_time on mc_time.token_bought_mint_address = t.token_bought_mint_address
        WHERE
            t.token_bought_mint_address in (
                SELECT
                    *
                FROM
                    tokens
            )
            AND t.block_time <= fc.call_block_time + INTERVAL '1' HOUR
            AND t.block_time <= mc_time.first_time_reached
    ),
    trader_coins as (
        SELECT
            trader_id,
            token_bought_mint_address
        FROM
            trader_trades
        GROUP BY
            trader_id,
            token_bought_mint_address
    )
SELECT
    trader_id,
    COUNT(*) as early_tokens
FROM
    trader_coins
GROUP BY
    trader_id