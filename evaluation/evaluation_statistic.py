from typing import List

import numpy as np


def print_statistics(data: List[float], description: str):
    """
    Prints statistical information about a list of numerical data.

    :param data: List of numerical values.
    :param description: Description of the data (e.g., "Token Ages").
    """
    if not data:
        print(f"No data available for {description}.")
        return

    print(f"Statistics for {description}:")
    print(f"  Count: {len(data)}")
    print(f"  Mean: {np.mean(data):.2f}")
    print(f"  Median: {np.median(data):.2f}")
    print(f"  Standard Deviation: {np.std(data):.2f}")
    print(f"  Minimum: {np.min(data):.4f}")
    print(f"  Maximum: {np.max(data):.4f}")
    print()
