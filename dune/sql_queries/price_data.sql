  WITH tokens  as (
      SELECT q4.account_mint, pcc.call_block_time
        FROM pumpdotfun_solana.pump_call_create as pcc
          JOIN query_4229122 as q4 on q4.account_mint = pcc.account_mint
  ),
  buy_volume AS (
    SELECT
      DATE_TRUNC('minute', block_time) AS trading_minute,
      MAX(block_time) AS block_time,
      SUM(token_sold_amount) AS volume,
      token_bought_mint_address AS token
    FROM
      dex_solana.trades AS t
    JOIN tokens as tk on t.token_bought_mint_address = tk.account_mint
    WHERE token_sold_mint_address = 'So11111111111111111111111111111111111111112' AND t.block_time BETWEEN tk.call_block_time AND tk.call_block_time + INTERVAL '{{min_token_age_h}}' hour
    GROUP BY
      token_bought_mint_address,
      DATE_TRUNC('minute', block_time)
  ),
  sell_volume AS (
    SELECT
      DATE_TRUNC('minute', block_time) AS trading_minute,
      MAX(block_time) AS block_time,
      SUM(token_bought_amount) AS volume,
      token_sold_mint_address AS token
    FROM
      dex_solana.trades AS t
    JOIN tokens as tk on t.token_sold_mint_address = tk.account_mint
    WHERE token_bought_mint_address = 'So11111111111111111111111111111111111111112' AND t.block_time BETWEEN tk.call_block_time AND tk.call_block_time + INTERVAL '{{min_token_age_h}}' hour
    GROUP BY
      token_sold_mint_address,
      DATE_TRUNC('minute', block_time)
  ),
  last_buy_price AS (
    SELECT
      token_bought_amount / token_sold_amount AS price,
      t.block_time,
      ROW_NUMBER() OVER (
        PARTITION BY
          t.token_bought_mint_address,
          DATE_TRUNC('minute', block_time)
        ORDER BY
          t.block_slot DESC
      ) AS rn,
      t.token_bought_mint_address AS token,
      t.block_slot,
      DATE_TRUNC('minute', block_time) as trading_minute
    FROM
      dex_solana.trades AS t
    JOIN tokens as tk on t.token_bought_mint_address = tk.account_mint
    WHERE token_sold_mint_address = 'So11111111111111111111111111111111111111112' AND t.block_time BETWEEN tk.call_block_time AND tk.call_block_time + INTERVAL '{{min_token_age_h}}' hour
  ),
  last_sell_price AS (
    SELECT
      token_sold_amount / token_bought_amount AS price,
      t.block_time,
      ROW_NUMBER() OVER (
        PARTITION BY
          t.token_sold_mint_address,
          DATE_TRUNC('minute', block_time)
        ORDER BY
          t.block_slot DESC
      ) AS rn,
      t.token_sold_mint_address AS token,
      t.block_slot,
      DATE_TRUNC('minute', block_time) as trading_minute
    FROM
      dex_solana.trades AS t
    JOIN tokens as tk on t.token_sold_mint_address = tk.account_mint
    WHERE token_bought_mint_address = 'So11111111111111111111111111111111111111112' AND t.block_time BETWEEN tk.call_block_time AND tk.call_block_time + INTERVAL '{{min_token_age_h}}' hour
  )
SELECT
  sv.token,
  bv.trading_minute,
  bv.volume AS buy_volume,
  sv.volume AS sell_volume,
  CASE
    WHEN lbp.block_time > lsp.block_time
    OR (
      lbp.block_time = lsp.block_time
      AND lbp.block_slot >= lsp.block_slot
    ) THEN lbp.price
    ELSE lsp.price
  END AS latest_price
FROM
  buy_volume AS bv
  JOIN sell_volume AS sv ON sv.token = bv.token
  AND sv.trading_minute = bv.trading_minute
  LEFT JOIN last_buy_price AS lbp ON lbp.token = bv.token
  AND lbp.trading_minute = bv.trading_minute
  AND lbp.rn = 1
  LEFT JOIN last_sell_price AS lsp ON lsp.token = bv.token
  AND lsp.trading_minute = bv.trading_minute
  AND lsp.rn = 1
ORDER BY
  bv.trading_minute ASC;