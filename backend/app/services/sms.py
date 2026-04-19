from app.core.config import settings
from loguru import logger
import httpx
import re


async def send_sms(
    phone: str,
    message: str,
) -> bool:
    try:
        phone = (
            str(phone)
            .strip()
            .replace(" ", "")
            .replace("+91", "")
        )

        otp_match = re.search(r"\d{6}", message)
        otp = otp_match.group() if otp_match else None

        logger.info(f"📱 SMS to: {phone}")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://www.fast2sms.com/dev/bulkV2",
                headers={
                    "authorization": settings.SMS_API_KEY,
                    "Cache-Control": "no-cache",
                },
                json={
                    "route": "q",
                    "message": message,
                    "language": "english",
                    "flash": "0",
                    "numbers": phone,
                },
                timeout=15.0,
            )
            data = response.json()
            logger.info(f"Fast2SMS: {data}")

            if data.get("return") is True:
                logger.info(f"✅ SMS sent: {phone}")
                return True

            logger.error(f"❌ SMS failed: {data}")
            return False

    except httpx.TimeoutException:
        logger.error(f"⏱️ SMS timeout: {phone}")
        return False
    except Exception as e:
        logger.error(f"💥 SMS error: {e}")
        return False
