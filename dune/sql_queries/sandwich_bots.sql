WITH tokens AS (SELECT account_mint
                FROM pumpdotfun_solana.pump_call_create
                WHERE call_block_time BETWEEN cast('{{time_from}}' as timestamp) AND cast('{{time_to}}' as timestamp)
                  AND call_block_time <= NOW() - INTERVAL '{{min_token_age_h}}' hour),
     unique_traders as (SELECT t.trader_id
                        FROM dex_solana.trades as t
                        WHERE t.token_sold_mint_address IN (SELECT * FROM tokens)
                          AND block_time BETWEEN cast('{{time_from}}' as timestamp) AND cast('{{time_to}}' as timestamp)
                        GROUP BY t.trader_id

                        UNION ALL

                        SELECT t.trader_id
                        FROM dex_solana.trades as t
                        WHERE t.token_bought_mint_address IN (SELECT * FROM tokens)
                          AND block_time BETWEEN cast('{{time_from}}' as timestamp) AND cast('{{time_to}}' as timestamp)
                        GROUP BY t.trader_id),
     filtered_trades AS (SELECT t.trader_id,
                                t.token_sold_mint_address AS token_address,
                                t.block_time              AS trade_time,
                                'sell'                    AS trade_type
                         FROM dex_solana.trades AS t
                         WHERE t.trader_id IN (SELECT trader_id FROM unique_traders)
                           AND t.token_sold_mint_address IN (SELECT * FROM tokens)
                           AND block_time BETWEEN cast('{{time_from}}' as timestamp) AND cast('{{time_to}}' as timestamp)
                         UNION ALL

                         SELECT t.trader_id,
                                t.token_bought_mint_address AS token_address,
                                t.block_time                AS trade_time,
                                'buy'                       AS trade_type
                         FROM dex_solana.trades AS t
                         WHERE t.trader_id IN (SELECT trader_id FROM unique_traders)
                           AND t.token_bought_mint_address IN (SELECT * FROM tokens)
                           AND block_time BETWEEN cast('{{time_from}}' as timestamp) AND cast('{{time_to}}' as timestamp)),
     paired_trades AS (SELECT ft1.trader_id,
                              ft1.token_address,
                              ft1.trade_time                                      AS buy_time,
                              ft2.trade_time                                      AS sell_time,
                              date_diff('second', ft1.trade_time, ft2.trade_time) AS time_diff
                       FROM filtered_trades ft1
                                JOIN filtered_trades ft2
                                     ON ft1.trader_id = ft2.trader_id
                                         AND ft1.token_address = ft2.token_address
                                         AND ft1.trade_type = 'buy'
                                         AND ft2.trade_type = 'sell'
                                         AND ft2.trade_time > ft1.trade_time
                                         AND date_diff('second', ft1.trade_time, ft2.trade_time) <=
                                             60 -- Change to X minutes (e.g., 60*X for X minutes)
     )
SELECT trader_id,
       COUNT(*)       AS bot_like_trades,
       MIN(time_diff) AS fastest_trade_time,
       AVG(time_diff) AS avg_trade_time
FROM paired_trades
GROUP BY trader_id
ORDER BY bot_like_trades DESC;