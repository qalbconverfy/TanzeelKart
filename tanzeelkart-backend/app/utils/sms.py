from app.core.config import settings
from loguru import logger
import httpx


async def send_sms(phone: str, message: str) -> bool:
    try:
        # Fast2SMS API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://www.fast2sms.com/dev/bulkV2",
                headers={
                    "authorization": settings.SMS_API_KEY,
                    "Content-Type": "application/json"
                },
                json={
                    "route": "q",
                    "message": message,
                    "language": "english",
                    "flash": 0,
                    "numbers": phone,
                }
            )
            data = response.json()
            if data.get("return"):
                logger.info(f"SMS sent to {phone}")
                return True
            else:
                logger.error(f"SMS failed: {data}")
                return False
    except Exception as e:
        logger.error(f"SMS error: {e}")
        return False
        