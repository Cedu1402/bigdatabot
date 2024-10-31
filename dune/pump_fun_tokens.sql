WITH profitable_traders AS (
    SELECT trader_id
    FROM dune.testnet32.result_top_pump_dot_fun_trader
),
trades as (
    SELECT t.account_mint
    FROM query_4208224 as t
    JOIN profitable_traders as pt  on pt.trader_id = t.trader_id
)

SELECT * from trades
GROUP BY account_mint
