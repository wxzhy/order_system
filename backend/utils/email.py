from email.message import EmailMessage
import smtplib

from ..config import get_config

# 从配置文件读取SMTP配置
config = get_config()
smtp_config = config["smtp"]

SMTP_HOST = smtp_config["host"]
SMTP_PORT = smtp_config["port"]
SMTP_USER = smtp_config["user"]
SMTP_PASSWORD = smtp_config["password"]
SMTP_FROM = smtp_config["from"]
SMTP_USE_TLS = smtp_config["use_tls"]


def send_email(subject: str, body: str, to_email: str) -> None:
    if not all([SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SMTP_FROM]):
        raise RuntimeError("SMTP 服务尚未正确配置")

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = SMTP_FROM
    message["To"] = to_email
    message.set_content(body)

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as server:
            if SMTP_USE_TLS:
                server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(message)
    except Exception as exc:  # pragma: no cover - 网络相关异常无法稳定复现
        raise RuntimeError(f"邮件发送失败: {exc}") from exc
