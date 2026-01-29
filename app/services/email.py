import resend
from app.core.config import settings
from app.services.base import BaseService


class EmailService(BaseService):
    def __init__(self):
        self.api_key = settings.RESEND_API_KEY
        self.from_email = settings.RESEND_FROM_EMAIL
        self.from_name = settings.RESEND_FROM_NAME
        resend.api_key = settings.RESEND_API_KEY
        super().__init__()

    def send_email(self, to: str, subject: str, html: str):
        params: resend.Emails.SendParams = {
            "from": f"{self.from_name} <{self.from_email}>",
            "to": [to],
            "subject": subject,
            "html": html,
        }

        try:
            self.logger.info(f"Sending email to {to} with subject: {subject}")
            result = resend.Emails.send(params)
            self.logger.info(f"Email sent successfully: {result}")
            return result
        except Exception as e:
            self.logger.error(f"Failed to send email: {str(e)}")
            raise e

    def send_password_reset_email(self, to: str, token: str):
        reset_link = f"{settings.FRONTEND_URL}/reset-password?token={token}"
        subject = "Password Reset Request"
        html = f"""
        <h1>Reset Your Password</h1>
        <p>Click the link below to reset your password:</p>
        <a href="{reset_link}">{reset_link}</a>
        <p>This link expires in 15 minutes.</p>
        <p>If you didn't request this, please ignore this email.</p>
        """
        self.send_email(to, subject, html)

    def send_verification_email(self, to: str, token: str):
        verify_link = f"{settings.FRONTEND_URL}/verify-email?token={token}"
        subject = "Verify Your Email Address"
        html = f"""
        <h1>Verify Your Email</h1>
        <p>Click the link below to verify your email address:</p>
        <a href="{verify_link}">{verify_link}</a>
        <p>This link expires in 24 hours.</p>
        <p>If you didn't create an account, please ignore this email.</p>
        """
        self.send_email(to, subject, html)
