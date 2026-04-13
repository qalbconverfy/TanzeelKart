from app.core.config import settings
from loguru import logger
import httpx
import re


async def send_sms(phone: str, message: str) -> bool:
    try:
        phone = str(phone).strip().replace(
            " ", ""
        ).replace("+91", "")

        otp_match = re.search(r'\d{6}', message)
        otp = otp_match.group() if otp_match else "000000"

        sms_message = (
            f"Your TanzeelKart OTP is {otp}. "
            f"Valid for 10 minutes. "
            f"Do not share. -QalbConverfy"
        )

        logger.info(f"📱 Sending to: {phone}")
        logger.info(f"🔑 API Key: {settings.SMS_API_KEY[:10]}...")

        async with httpx.AsyncClient() as client:
    response = await client.post(
        "https://www.fast2sms.com/dev/bulkV2",
        headers={
            "authorization": settings.SMS_API_KEY,
            "Cache-Control": "no-cache",
        },
        json={
            "route": "q",
            "message": sms_message,
            "language": "english",
            "flash": "0",
            "numbers": phone,
        },
        timeout=15.0
    )

            data = response.json()
            logger.info(f"Fast2SMS: {data}")

            if data.get("return") == True:
                logger.info(f"✅ Sent: {phone}")
                return True
            else:
                logger.error(f"❌ Failed: {data}")
                return False

    except Exception as e:
        logger.error(f"💥 Error: {e}")
        return False
