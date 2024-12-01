import asyncio

import aiohttp

from loguru import logger


async def make_http_request(method: str, url: str, **kwargs):
    """Generic function to handle HTTP requests with error handling."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, **kwargs) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error("Request failed, status code: %d, response: %s", response.status, await response.text())
                    return None
    except aiohttp.ClientError as e:
        logger.error("Network error occurred: %s", str(e))
        return None
    except Exception as e:
        logger.error("An unexpected error occurred: %s", str(e))
        return None


async def make_http_request_with_retry(retries: int, delay: float, method: str, url: str, **kwargs):
    """Retries make_http_request up to `retries` times with a delay on failure."""
    for attempt in range(1, retries + 1):
        logger.info("Attempt %d of %d for %s request to %s", attempt, retries, method, url)
        result = await make_http_request(method, url, **kwargs)

        if result is not None:
            logger.info("Request succeeded on attempt %d", attempt)
            return result

        logger.warning("Attempt %d failed; retrying in %.2f seconds...", attempt, delay)
        await asyncio.sleep(delay)

    logger.error("All %d attempts failed for %s request to %s", retries, method, url)
    return None