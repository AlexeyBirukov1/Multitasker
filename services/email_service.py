import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailService:
    def __init__(self, smtp_server: str, smtp_port: int, smtp_user: str, smtp_password: str, from_email: str):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
        self.from_email = from_email

    def send_email(self, to_email: str, subject: str, body: str):
        msg = MIMEMultipart()
        msg['From'] = self.from_email
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        try:

            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.from_email, to_email, msg.as_string())
            return True
        except Exception as e:
            print(f"Ошибка при отправке письма: {e}")
            return False

    def send_password_reset(self, to_email: str, user, token):
        return self.send_email(to_email,
                        subject="Сброс пароля",
        body = (
            f"Здравствуйте, {user.name}!\n\n"
            f"Вы запросили сброс пароля. Используйте токен: {token}\n\n"
            f"Если вы не запрашивали сброс, проигнорируйте это письмо.\n"
            f"С уважением,\nMultitasker_TUSUR"
        )
        )

email_service = EmailService(
    smtp_server="smtp.yandex.com",
    smtp_port=465,
    smtp_user="darkmage6677@yandex.com",
    smtp_password="ysquzfkbqfsrexit",
    from_email="darkmage6677@yandex.com"
)