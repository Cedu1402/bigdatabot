WITH
  buy_volume AS (
    SELECT
      DATE_TRUNC('minute', block_time) AS trading_minute,
      MAX(block_time) AS block_time,
      SUM(token_sold_amount) AS volume,
      token_bought_mint_address AS token
    FROM
      dex_solana.trades AS t
    WHERE
      t.token_bought_mint_address IN (
    SELECT token
    FROM unnest(split('{{tokens}}', ',')) AS c(token)
)
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
    WHERE
      t.token_sold_mint_address IN (
    SELECT token
    FROM unnest(split('{{tokens}}', ',')) AS c(token)
)
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
    WHERE
      t.token_bought_mint_address IN (
    SELECT token
    FROM unnest(split('{{tokens}}', ',')) AS c(token)
)
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
    WHERE
      t.token_sold_mint_address IN (
    SELECT token
    FROM unnest(split('{{tokens}}', ',')) AS c(token)
)
  )
SELECT
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
  END AS latest_price,
  1 as test
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