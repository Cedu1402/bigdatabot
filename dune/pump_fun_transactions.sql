WITH buy_trades AS (SELECT t.trader_id,
                           token_sold_amount,
                           token_bought_amount,
                           token_bought_mint_address as token,
                           block_time,
                           1 as buy
                    FROM dex_solana.trades as t
                             JOIN dune.testnet32.result_traded_tokens as rtt
                                  on rtt.account_mint = t.token_bought_mint_address
                             JOIN dune.testnet32.result_top_pump_dot_fun_trader as tt on tt.trader_id = t.trader_id
                    WHERE token_sold_mint_address = 'So11111111111111111111111111111111111111112'
                      AND token_sold_amount >= 1
                      AND block_time >= NOW() - INTERVAL '1' month),
     sell_trades AS (SELECT t.trader_id,
                            token_sold_amount,
                            token_bought_amount,
                            token_sold_mint_address as token,
                            block_time,
                            0 as buy
                     FROM dex_solana.trades as t
                              JOIN dune.testnet32.result_traded_tokens as rtt
                                   on rtt.account_mint = t.token_sold_mint_address
                              JOIN dune.testnet32.result_top_pump_dot_fun_trader as tt on tt.trader_id = t.trader_id
                     WHERE token_bought_mint_address = 'So11111111111111111111111111111111111111112'
                       AND block_time >= NOW() - INTERVAL '1' month)

SELECT * FROM buy_trades
UNION ALL
SELECT * FROM sell_trades