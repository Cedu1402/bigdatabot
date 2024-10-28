SELECT
  pcb.call_block_time,
  pcb.account_user,
  pcb.account_mint,
  (
    SELECT
      pre_token_balance
    FROM
      solana.account_activity as aa
    WHERE
      aa.block_time = pcb.call_block_time
      AND aa.address = pcb.account_user
      AND aa.tx_id = pcb.call_tx_id
    LIMIT
      1
  )
FROM
  pumpdotfun_solana.pump_call_buy as pcb
WHERE
  pcb.account_mint = 'BawCWuZp9U33FwNMTXdcryWj4zsUBRGLfuw9dA7rXCSc'