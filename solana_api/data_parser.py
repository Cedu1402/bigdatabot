import re


def extract_data(message):
    # Modified pattern to match 44-character string without requiring newline
    contract_pattern = r'([A-Za-z0-9]{44})'
    market_cap_pattern = r'MC:\s*([\d,]+\.\d+)'

    contract_match = re.search(contract_pattern, message)
    contract_address = contract_match.group(0) if contract_match else None

    market_cap_match = re.search(market_cap_pattern, message)
    market_cap = market_cap_match.group(1) if market_cap_match else None

    return contract_address, market_cap