WITH profitable_traders AS (
    SELECT trader_id
    FROM dune.testnet3232.result_solana_pump_dot_fun_top_trader
),
trades as (
    SELECT t.account_mint
    FROM query_4284948 as t
    JOIN profitable_traders as pt  on pt.trader_id = t.trader_id
)
SELECT * from trades
GROUP BY account_mint
