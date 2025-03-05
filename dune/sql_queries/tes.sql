WITH
    buy_transactions as (
        SELECT
            t.trader_id,
            t.token_bought_mint_address as token,
            t.block_time,
            t.amount_usd / (t.token_bought_amount_raw / 1e6) as price
        FROM
            dex_solana.trades t
            JOIN pumpdotfun_solana.pump_call_create fc on t.token_bought_mint_address = fc.account_mint
            JOIN query_4758167 as q on q.trader_id = t.trader_id
        WHERE
            t.token_sold_mint_address = 'So11111111111111111111111111111111111111112'
            AND t.token_sold_amount >= 1
            AND t.amount_usd / (t.token_bought_amount_raw / 1e6) >= 0.00005
            AND fc.call_block_time BETWEEN NOW() - INTERVAL '7' day AND NOW()  - INTERVAL '5' hour
            AND t.block_time BETWEEN fc.call_block_time AND fc.call_block_time  + INTERVAL '5' hour
    ),
    tokens as (
        SELECT
            token
        from
            buy_transactions
        GROUP BY
            token
    ),
    first_buy AS (
        SELECT
            trader_id,
            token,
            MIN(block_time) AS first_buy_time
        FROM
            buy_transactions
        GROUP BY
            trader_id,
            token
    ),
    buy_prices AS (
        SELECT
            bt.trader_id,
            bt.token,
            bt.price AS first_buy_price,
            fb.first_buy_time
        FROM
            buy_transactions bt
            JOIN first_buy fb ON bt.trader_id = fb.trader_id
            AND bt.token = fb.token
            AND bt.block_time = fb.first_buy_time
    ),
    max_price_after as (
        SELECT
            MAX(t.amount_usd / (t.token_bought_amount_raw / 1e6)) as max_price,
            t.trader_id,
            t.token_bought_mint_address as token
        FROM
            dex_solana.trades t
            JOIN query_4758167 as q on q.trader_id = t.trader_id
            JOIN tokens as tok on t.token_bought_mint_address = tok.token
            JOIN pumpdotfun_solana.pump_call_create fc on t.token_bought_mint_address = fc.account_mint
            JOIN buy_prices as bp on bp.trader_id = t.trader_id
            and t.token_bought_mint_address = bp.token
        WHERE
            t.token_sold_mint_address = 'So11111111111111111111111111111111111111112'
            AND t.token_sold_amount >= 1
            AND t.block_time > bp.first_buy_time + INTERVAL '5' MINUTE
            AND t.block_time < fc.call_block_time + INTERVAL '10' HOUR
        GROUP BY
            t.token_bought_mint_address,
            t.trader_id
    ),
    trader_returns as (
        SELECT
            bp.*,
            (
                (bp.first_buy_price - mp.max_price) / mp.max_price
            ) * 100 AS percentage_return
        FROM
            max_price_after as mp
            JOIN buy_prices as bp on bp.token = mp.token
            and bp.trader_id = mp.trader_id
    ),
    hit_rate as (
        SELECT
            *,
            CASE
                WHEN percentage_return > 50 THEN 1
                ELSE 0
            END AS sucess
        FROM
            trader_returns
    )
SELECT
    SUM(percentage_return) as max_possible_profit,
    COUNT(*) as tokens,
    SUM(sucess) as success_tokens,
    CAST(SUM(sucess) AS DOUBLE) / COUNT(*) as hit_rate
FROM
    hit_rate
GROUP BY
    trader_id
ORDER BY
    hit_rate DESC