import logging
from datetime import datetime
from typing import Optional, Tuple

from birdeye_api.token_creation_endpoint import get_token_create_info_bird_eye
from constants import PUMP_DOT_FUN_AUTHORITY
from database.token_creation_info_table import select_token_creation_info, insert_token_creation_info

logger = logging.getLogger(__name__)


async def load_token_create_info(token: str) -> Optional[Tuple[datetime, str]]:
    try:
        token_create_time, owner = await get_token_create_info_bird_eye(token)
        return token_create_time, owner
    except Exception as e:
        logger.exception(f"Failed to get token create time")
        return None


async def get_token_create_info(token) -> Optional[Tuple[Optional[datetime], Optional[str]]]:
    token_create_info = select_token_creation_info(token)
    if token_create_info is None:
        token_create_info = await load_token_create_info(token)
        if token_create_info is None:
            logger.info("Failed to load token create info")
            return None, None

        token_create_time, owner = token_create_info
        insert_token_creation_info(token, owner, token_create_time)

    token_create_time, owner = token_create_info
    return token_create_time, owner


async def check_token_create_info_age_now(token: str) -> bool:
    token_create_time, owner = await get_token_create_info(token)
    if token_create_time is None:
        return False

    if not check_pump_fun_token(owner, token):
        return False

    if (datetime.utcnow() - token_create_time).total_seconds() > 120 * 60:
        logger.info("Token older than two horus, skip", extra={'token': token})
        return False

    return True


def check_pump_fun_token(owner: str, token: str) -> bool:
    if owner != PUMP_DOT_FUN_AUTHORITY:
        logger.info("Not a pump fun token", extra={'token': token, 'owner': owner})
        return False
    return True


async def check_token_create_info_date_range(token: str, start_date: datetime, end_date: datetime) -> Tuple[
    bool, Optional[datetime]]:
    token_create_time, owner = await get_token_create_info(token)
    if token_create_time is None:
        return False, None

    if not check_pump_fun_token(owner, token):
        return False, None

    if not (start_date <= token_create_time <= end_date):
        logger.info(
            "Token creation time is outside the specified date range, skip",
            extra={'token': token, 'token_create_time': token_create_time}
        )
        return False, None

    return True, start_date
