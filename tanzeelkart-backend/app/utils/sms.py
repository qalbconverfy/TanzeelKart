from loguru import logger
import httpx


async def send_sms(phone: str, message: str) -> bool:
    try:
        logger.info(f"SMS to {phone}: {message}")
        return True
    except Exception as e:
        logger.error(f"SMS error: {e}")
        return False
