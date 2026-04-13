from app.core.config import settings
from loguru import logger
import httpx
import re


async def send_sms(phone: str, message: str) -> bool:
    """
    Fast2SMS se OTP SMS bhejta hai
    Route: q (Quick SMS)
    """
    try:
        # Phone number clean karo
        phone = str(phone).strip().replace(" ", "").replace("+91", "")

        # OTP extract karo message se
        otp_match = re.search(r'\d{6}', message)
        otp = otp_match.group() if otp_match else "000000"

        # SMS message
        sms_message = (
            f"Your TanzeelKart OTP is {otp}. "
            f"Valid for 10 minutes. "
            f"Do not share with anyone. "
            f"-QalbConverfy"
        )

        logger.info(f"📱 Sending OTP to: {phone}")

        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://www.fast2sms.com/dev/bulkV2",
                headers={
                    "authorization": settings.SMS_API_KEY,
                    "Cache-Control": "no-cache",
                },
                params={
                    "route": "q",
                    "message": sms_message,
                    "language": "english",
                    "flash": 0,
                    "numbers": phone,
                },
                timeout=15.0
            )

            data = response.json()
            logger.info(f"Fast2SMS Response: {data}")

            if data.get("return") == True:
                logger.info(f"✅ OTP SMS sent to {phone}")
                return True
            else:
                logger.error(
                    f"❌ SMS failed: "
                    f"code={data.get('status_code')} "
                    f"msg={data.get('message')}"
                )
                return False

    except httpx.TimeoutException:
        logger.error(f"⏱️ SMS timeout for {phone}")
        return False

    except httpx.ConnectError:
        logger.error(f"🔌 SMS connection error for {phone}")
        return False

    except Exception as e:
        logger.error(f"💥 SMS error: {e}")
        return False


async def send_custom_sms(
    phone: str,
    message: str
) -> bool:
    """
    Custom message SMS bhejta hai
    Notifications ke liye
    """
    try:
        phone = str(phone).strip().replace(
            " ", ""
        ).replace("+91", "")

        logger.info(f"📱 Sending SMS to: {phone}")

        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://www.fast2sms.com/dev/bulkV2",
                headers={
                    "authorization": settings.SMS_API_KEY,
                    "Cache-Control": "no-cache",
                },
                params={
                    "route": "q",
                    "message": message,
                    "language": "english",
                    "flash": 0,
                    "numbers": phone,
                },
                timeout=15.0
            )

            data = response.json()
            logger.info(f"Fast2SMS Response: {data}")

            if data.get("return") == True:
                logger.info(f"✅ SMS sent to {phone}")
                return True
            else:
                logger.error(f"❌ SMS failed: {data}")
                return False

    except Exception as e:
        logger.error(f"💥 SMS error: {e}")
        return False
