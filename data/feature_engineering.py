import logging
from typing import List, Dict

import numpy as np
import pandas as pd

from constants import TOKEN_COlUMN, TRADING_MINUTE_COLUMN, PRICE_COLUMN, PRICE_PCT_CHANGE, \
    SOL_PRICE, MARKET_CAP_USD, PERCENTAGE_OF_1_MILLION_MARKET_CAP, TOTAL_VOLUME_COLUMN, TOTAL_VOLUME_PCT_CHANGE

logger = logging.getLogger(__name__)


def bin_data(data: List[pd.DataFrame], columns: List[str], bin_edges: Dict[str, List[float]]) -> List[pd.DataFrame]:
    # Step 1: Add an identifier to each DataFrame and concatenate them
    concatenated = pd.concat([df.assign(_df_index=i) for i, df in enumerate(data)], ignore_index=True)

    # Step 2: Apply binning for each specified column in the concatenated DataFrame
    for column in columns:
        if column in concatenated.columns and column in bin_edges:
            concatenated[column] = np.digitize(concatenated[column],
                                               bins=bin_edges[column],
                                               right=False).clip(1, len(bin_edges[column]))

    # Step 3: Split concatenated DataFrame back into the original list of DataFrames
    result = [concatenated[concatenated["_df_index"] == i].drop(columns="_df_index").reset_index(drop=True) for i in
              range(len(data))]

    return result


def compute_bin_edges(combined_data: pd.DataFrame, columns: List[str], n_bins: int) -> Dict:
    bin_edges = dict()
    """Compute bin edges based on full dataset"""
    for column in columns:
        if column in combined_data.columns:
            # Calculate bin edges for each specified column
            try:
                # Attempt to use qcut
                bin_edges[column] = pd.qcut(combined_data[column], n_bins, retbins=True, duplicates='drop')[1]
            except ValueError as e:
                logger.error(f"Warning: Falling back to pd.cut for column '{column}' due to error: {e}")

                # Fallback to pd.cut if qcut fails
                bin_edges[column] = pd.cut(combined_data[column], bins=n_bins, retbins=True, duplicates='drop')[1]

    return bin_edges


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


def calculate_pct_change(data, column, token_mask):
    """Calculate percentage change for a column, handle infinities, and fill NaNs."""
    pct_change = data.loc[token_mask, column].replace(0, np.nan).pct_change(fill_method=None)
    if pct_change.isin([np.inf, -np.inf]).all():
        logger.error("All values are inf or -inf")

    return pct_change.replace([np.inf, -np.inf], np.nan).fillna(0.0).astype('float64')


def add_features(data: pd.DataFrame) -> pd.DataFrame:
    data = data.sort_values(by=[TOKEN_COlUMN, TRADING_MINUTE_COLUMN])  # Sort by token and then by time

    data[MARKET_CAP_USD] = data.apply(
        lambda row: get_market_cap_from_tokens_per_sol_and_sol_price(float(row[PRICE_COLUMN]), SOL_PRICE),
        axis=1
    )

    for token in data[TOKEN_COlUMN].unique():
        token_mask = (data[TOKEN_COlUMN] == token)
        data.loc[token_mask, PRICE_PCT_CHANGE] = calculate_pct_change(data, PRICE_COLUMN, token_mask)
        data.loc[token_mask, TOTAL_VOLUME_PCT_CHANGE] = calculate_pct_change(data, TOTAL_VOLUME_COLUMN, token_mask)

        data.loc[token_mask, PERCENTAGE_OF_1_MILLION_MARKET_CAP] = data[MARKET_CAP_USD] / 1_000_000

    return data
