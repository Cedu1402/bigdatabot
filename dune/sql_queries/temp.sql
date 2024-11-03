WITH filtered_calls AS (SELECT account_mint,
                               call_block_time,
                               account_user
                        FROM pumpdotfun_solana.pump_call_create
                        WHERE call_block_time BETWEEN cast('{{time_from}}' as timestamp) AND cast('{{time_to}}' as timestamp)),
     buy_trades AS (SELECT t.trader_id,
                           token_sold_amount,
                           token_bought_amount,
                           token_bought_mint_address as token,
                           t.block_time,
                           1                         as buy
                    FROM dex_solana.trades as t
                             JOIN filtered_calls as fc on fc.account_mint = t.token_bought_mint_address
                             JOIN dune.testnet32.result_traded_tokens as rtt
                                  on rtt.account_mint = t.token_bought_mint_address
                    WHERE token_sold_mint_address = 'So11111111111111111111111111111111111111112'
                      AND token_sold_amount >= 1
                      AND t.trader_id = 'GfTTcN1ie45MjtuBgUCwMmM4YVJ81KhQ1ZFH92YTG6Yz'
                      AND t.block_time >= fc.call_block_time
                      AND t.block_time <= fc.call_block_time + INTERVAL '{{min_token_age_h}}' hour
                      AND t.block_time BETWEEN cast('{{time_from}}' as timestamp) AND cast('{{time_to}}' as timestamp)),
     sell_trades AS (SELECT t.trader_id,
                            token_sold_amount,
                            token_bought_amount,
                            token_sold_mint_address as token,
                            t.block_time,
                            0                       as buy
                     FROM dex_solana.trades as t
                              JOIN filtered_calls as fc on fc.account_mint = t.token_bought_mint_address
                              JOIN dune.testnet32.result_traded_tokens as rtt
                                   on rtt.account_mint = t.token_sold_mint_address
                     WHERE token_bought_mint_address = 'So11111111111111111111111111111111111111112'
                       AND t.block_time >= fc.call_block_time
                       AND t.trader_id = 'GfTTcN1ie45MjtuBgUCwMmM4YVJ81KhQ1ZFH92YTG6Yz'
                       AND t.block_time <= fc.call_block_time + INTERVAL '{{min_token_age_h}}' hour
                       AND t.block_time BETWEEN cast('{{time_from}}' as timestamp) AND cast('{{time_to}}' as timestamp))

SELECT *
FROM buy_trades
UNION ALL
SELECT *
FROM sell_trades