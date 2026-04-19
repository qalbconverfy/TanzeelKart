from app.core.config import settings
from loguru import logger
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


async def send_email(
    to: str,
    subject: str,
    body: str,
    html: bool = False,
) -> bool:
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = settings.EMAIL_FROM
        msg["To"] = to

        part = MIMEText(
            body,
            "html" if html else "plain"
        )
        msg.attach(part)

        with smtplib.SMTP(
            settings.SMTP_HOST,
            settings.SMTP_PORT
        ) as server:
            server.starttls()
            server.login(
                settings.SMTP_USER,
                settings.SMTP_PASSWORD,
            )
            server.sendmail(
                settings.EMAIL_FROM,
                to,
                msg.as_string(),
            )

        logger.info(f"✅ Email sent: {to}")
        return True

    except Exception as e:
        logger.error(f"❌ Email error: {e}")
        return False


async def send_otp_email(
    to: str,
    otp: str,
    name: str = "",
) -> bool:
    subject = "TanzeelKart — Your OTP"
    body = f"""
    <h2>TanzeelKart OTP</h2>
    <p>Hello {name or 'User'},</p>
    <p>Your OTP is: <strong style="font-size:24px">{otp}</strong></p>
    <p>Valid for 10 minutes. Do not share.</p>
    <br>
    <p>— TanzeelKart by QalbConverfy</p>
    """
    return await send_email(to, subject, body, html=True)
