import pandas as pd

from constants import TOKEN_COlUMN, TRADING_MINUTE_COLUMN, PRICE_COLUMN, PRICE_PCT_CHANGE, \
    SOL_PRICE, MARKET_CAP_USD, PERCENTAGE_OF_1_MILLION_MARKET_CAP, BUY_VOLUME_COLUMN, \
    SELL_VOLUME_COLUMN, TOTAL_VOLUME_COLUMN, BUY_VOLUME_PCT_CHANGE, SELL_VOLUME_PCT_CHANGE, TOTAL_VOLUME_PCT_CHANGE


def get_token_price_in_usd(tokens_per_sol, sol_price_usd):
    """
    Calculate the price of one token in USD.

    :param tokens_per_sol: Amount of tokens you get per 1 SOL (tokens/SOL)
    :param sol_price_usd: Current price of SOL in USD
    :return: Price of one token in USD
    """

    if tokens_per_sol == 0 or sol_price_usd == 0:
        return 0

    # Calculate token price in USD
    token_price_usd = sol_price_usd / tokens_per_sol
    return token_price_usd


def calculate_market_cap_in_usd(token_price_usd, total_supply=1_000_000_000):
    """
    Calculate the market cap of a token in USD.

    :param token_price_usd: Price of one token in USD
    :param total_supply: Total supply of the token (default is 1 billion)
    :return: Market cap in USD
    """
    # Calculate market cap in USD
    market_cap_usd = token_price_usd * total_supply
    return market_cap_usd


def get_market_cap_from_tokens_per_sol_and_sol_price(tokens_per_sol, sol_price_usd, total_supply=1_000_000_000):
    """
    Calculate the market cap of a token in USD using tokens per SOL and the price of SOL.

    :param tokens_per_sol: Amount of tokens per SOL
    :param sol_price_usd: Current price of SOL in USD
    :param total_supply: Total supply of the token (default is 1 billion)
    :return: Market cap in USD
    """
    # Calculate token price in USD
    token_price_usd = get_token_price_in_usd(tokens_per_sol, sol_price_usd)
    # Calculate market cap using the token price
    market_cap_usd = calculate_market_cap_in_usd(token_price_usd, total_supply)
    return market_cap_usd


def add_features(data: pd.DataFrame) -> pd.DataFrame:
    data = data.sort_values(by=[TOKEN_COlUMN, TRADING_MINUTE_COLUMN])  # Sort by token and then by time

    data[PRICE_COLUMN] = pd.to_numeric(data[PRICE_COLUMN], errors='coerce')
    data[BUY_VOLUME_COLUMN] = pd.to_numeric(data[BUY_VOLUME_COLUMN], errors='coerce')
    data[SELL_VOLUME_COLUMN] = pd.to_numeric(data[SELL_VOLUME_COLUMN], errors='coerce')

    data[MARKET_CAP_USD] = data.apply(
        lambda row: get_market_cap_from_tokens_per_sol_and_sol_price(float(row[PRICE_COLUMN]), SOL_PRICE),
        axis=1
    )
    data[TOTAL_VOLUME_COLUMN] = data[BUY_VOLUME_COLUMN] + data[SELL_VOLUME_COLUMN]

    for token in data[TOKEN_COlUMN].unique():
        token_mask = (data[TOKEN_COlUMN] == token)
        data.loc[token_mask, PRICE_PCT_CHANGE] = data.loc[token_mask, PRICE_COLUMN].pct_change(fill_method=None).fillna(0)

        data.loc[token_mask, BUY_VOLUME_PCT_CHANGE] = data.loc[token_mask, BUY_VOLUME_COLUMN].pct_change(fill_method=None).fillna(0)
        data.loc[token_mask, SELL_VOLUME_PCT_CHANGE] = data.loc[token_mask, SELL_VOLUME_COLUMN].pct_change(fill_method=None).fillna(0)
        data.loc[token_mask, TOTAL_VOLUME_PCT_CHANGE] = data.loc[token_mask, TOTAL_VOLUME_COLUMN].pct_change(fill_method=None).fillna(0)

        data.loc[token_mask, PERCENTAGE_OF_1_MILLION_MARKET_CAP] = data[MARKET_CAP_USD] / 1_000_000

    return data
