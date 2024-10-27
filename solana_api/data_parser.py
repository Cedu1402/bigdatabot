import re


def extract_data(message):
    # Define a regex pattern to match the contract address and market cap
    contract_pattern = r'(?<=\n)([A-Za-z0-9]{44})'  # 44-character alphanumeric contract address
    market_cap_pattern = r'MC:\s*([\d,]+\.\d+)'  # Market cap format

    # Extract the contract address
    contract_match = re.search(contract_pattern, message)
    contract_address = contract_match.group(0) if contract_match else None

    # Extract the market cap
    market_cap_match = re.search(market_cap_pattern, message)
    market_cap = market_cap_match.group(1) if market_cap_match else None

    return contract_address, market_cap
