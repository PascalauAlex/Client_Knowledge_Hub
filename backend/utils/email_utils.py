from email.message import EmailMessage
import aiosmtplib
from fastapi.templating import Jinja2Templates
from config import settings

templates = Jinja2Templates(directory="templates")


async def send_email(to: str,
                     subject: str,
                     plain_text: str,
                     html_content: str | None) -> None:
    message = EmailMessage()
    message['From'] = settings.mail_from
    message['to'] = to
    message['Subject'] = subject

    message.set_content(plain_text)

    if html_content:
        message.add_alternative(html_content, subtype="html")
    await aiosmtplib.send(
        message,
        hostname=settings.mail_host,
        port=settings.mail_port,
        username=settings.mail_username,
        password=settings.mail_password,
        start_tls=settings.mail_tls
    )


async def send_password_reset_email(to_email: str, username: str, token: str) -> None:
    reset_url = f"{settings.frontend_url}/reset-password?token={token}"

    plain_text = f"""Hi {username},
    You requested to reset your password. Click on the following link, to set a new password:\n
    {reset_url}"""
    template = templates.env.get_template("reset_password_tempalte.html")
    html_content =template.render(reset_url=reset_url, username=username)


    await send_email(to=to_email, plain_text=plain_text,subject="Reset token",html_content=html_content)
