from app.core.config import settings
from loguru import logger
import httpx
import re


async def send_sms(phone: str, message: str) -> bool:
    try:
        # OTP extract karo
        otp_match = re.search(r'\d{6}', message)
        otp = otp_match.group() if otp_match else "000000"

        full_message = f"TanzeelKart OTP: {otp}. Valid 10 min. -QalbConverfy"

        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://www.fast2sms.com/dev/bulkV2",
                headers={
                    "authorization": settings.SMS_API_KEY,
                },
                params={
                    "route": "q",
                    "message": full_message,
                    "language": "english",
                    "flash": 0,
                    "numbers": phone,
                },
                timeout=10.0
            )
            data = response.json()
            logger.info(f"Fast2SMS response: {data}")

            if data.get("return") == True:
                logger.info(f"✅ SMS sent to {phone}")
                return True
            else:
                logger.error(f"❌ SMS failed: {data}")
                return False

    except Exception as e:
        logger.error(f"SMS error: {e}")
        return False
