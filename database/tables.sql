CREATE TABLE IF NOT EXISTS trades
(
    id                  SERIAL PRIMARY KEY,
    trader              VARCHAR(255) NOT NULL,
    token               VARCHAR(255) NOT NULL,
    token_amount        BIGINT       NOT NULL,
    sol_amount          BIGINT       NOT NULL,
    buy                 BOOLEAN      NOT NULL,
    token_holding_after BIGINT       NOT NULL,
    trade_time          TIMESTAMP    NOT NULL,
    tx_signature        VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS token_dataset
(
    id             SERIAL PRIMARY KEY,
    token          VARCHAR(255) NOT NULL,
    trading_minute TIMESTAMP    NOT NULL,
    raw_data       BYTEA        NOT NULL
);

CREATE TABLE IF NOT EXISTS token_watch
(
    id         SERIAL PRIMARY KEY,
    token      VARCHAR(255) NOT NULL,
    start_time TIMESTAMP    NOT NULL,
    end_time   TIMESTAMP    NULL
);

CREATE TABLE IF NOT EXISTS token_trade_history
(
    id         SERIAL PRIMARY KEY,
    token      VARCHAR(255)   NOT NULL,
    buy_time   TIMESTAMP      NOT NULL,
    sell_time  TIMESTAMP      NULL,
    buy_price  DECIMAL(18, 8) NOT NULL,
    sell_price DECIMAL(18, 8) NULL
);

CREATE TABLE IF NOT EXISTS event
(
    id        SERIAL PRIMARY KEY,
    wallet    VARCHAR(255) NOT NULL,
    time      TIMESTAMP    NOT NULL,
    signature VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS token_creation_info
(
    id        SERIAL PRIMARY KEY,
    token     VARCHAR(255) NOT NULL,
    creator   VARCHAR(255) NOT NULL,
    timestamp TIMESTAMP    NOT NULL
);
