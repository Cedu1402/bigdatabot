import numpy as np
import pandas as pd

from constants import PRICE_PCT_CHANGE, CURRENT_ASSET_PRICE_COLUMN


def jump_diffusion(current_price, mu=0.05, sigma=0.2, lam=0.3,
                   jump_mean=0.1, jump_std=0.2, timesteps=100):
    """
    Generate price movements using the Merton jump-diffusion model.

    Parameters:
    - current_price: Current token price
    - mu: Drift (expected return)
    - sigma: Volatility
    - lam: Jump intensity (frequency)
    - jump_mean: Mean of jump sizes (log-normal scale)
    - jump_std: Std deviation of jump sizes
    - timesteps: Number of movements to generate

    Returns:
    - Pandas DataFrame with columns 'change' and 'new_price'
    """
    prices = [current_price]
    changes = []
    dt = 1 / timesteps

    for _ in range(timesteps):
        # Brownian motion
        brownian_motion = np.random.normal(mu * dt, sigma * np.sqrt(dt))

        # Jump component
        jump = 0
        if np.random.poisson(lam * dt) > 0:
            jump = np.random.normal(jump_mean, jump_std)

        # Update price
        change = brownian_motion + jump
        new_price = prices[-1] * np.exp(change)

        changes.append(change)
        prices.append(new_price)

    return pd.DataFrame({PRICE_PCT_CHANGE: changes, CURRENT_ASSET_PRICE_COLUMN: prices[1:]})

# # # Example usage
# current_price = 1.0  # Current token price in USDC
# plt.figure(figsize=(12, 6))
# sampled_futures = []
# for i in range(300):
#     movements = jump_diffusion(current_price, timesteps=300)
#     sampled_futures.append(movements)
#     plt.plot(movements, linewidth=1)
#
# print(len(sampled_futures))
#
# plt.title("Possible Price Movements (Jump-Diffusion Model)")
# plt.xlabel("Timesteps")
# plt.ylabel("Price (USDC)")
# plt.show()
