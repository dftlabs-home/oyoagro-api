"""
FILE: src/email/service.py
Email service for sending transactional emails
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
import logging

from src.email.config import email_settings
from src.email.schemas import (
    WelcomeEmailData,
    PasswordResetEmailData,
    PasswordChangedEmailData,
    AccountLockedEmailData,
    EmailResponse
)
from src.email.templates import (
    get_welcome_email_template,
    get_password_reset_email_template,
    get_password_changed_email_template,
    get_account_locked_email_template
)

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending transactional emails"""
    
    @staticmethod
    def _send_email(
        to_email: str,
        subject: str,
        html_body: str,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None
    ) -> EmailResponse:
        """
        Send an email using SMTP
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_body: HTML email body
            cc: CC recipients (optional)
            bcc: BCC recipients (optional)
            
        Returns:
            EmailResponse with success/failure status
        """
        # Check if email sending is enabled
        if not email_settings.SEND_EMAILS:
            logger.info(f"Email sending disabled. Would send to: {to_email}")
            logger.info(f"Subject: {subject}")
            return EmailResponse(
                success=True,
                message="Email sending is disabled (dev mode)",
                email_sent_to=to_email
            )
        
        # Validate SMTP configuration
        if not email_settings.MAIL_USERNAME or not email_settings.MAIL_PASSWORD:
            logger.error("Email credentials not configured")
            return EmailResponse(
                success=False,
                message="Email service not configured",
                error="Missing SMTP credentials"
            )
        
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{email_settings.MAIL_FROM_NAME} <{email_settings.MAIL_FROM}>"
            message["To"] = to_email
            
            if cc:
                message["Cc"] = ", ".join(cc)
            if bcc:
                message["Bcc"] = ", ".join(bcc)
            
            # Attach HTML body
            html_part = MIMEText(html_body, "html")
            message.attach(html_part)
            
            # Connect to SMTP server
            if email_settings.MAIL_SSL_TLS:
                # Use SSL/TLS
                server = smtplib.SMTP_SSL(
                    email_settings.MAIL_SERVER,
                    email_settings.MAIL_PORT
                )
            else:
                # Use STARTTLS
                server = smtplib.SMTP(
                    email_settings.MAIL_SERVER,
                    email_settings.MAIL_PORT
                )
                if email_settings.MAIL_STARTTLS:
                    server.starttls()
            
            # Login
            if email_settings.USE_CREDENTIALS:
                server.login(
                    email_settings.MAIL_USERNAME,
                    email_settings.MAIL_PASSWORD
                )
            
            # Send email
            recipients = [to_email]
            if cc:
                recipients.extend(cc)
            if bcc:
                recipients.extend(bcc)
            
            server.sendmail(
                email_settings.MAIL_FROM,
                recipients,
                message.as_string()
            )
            
            # Close connection
            server.quit()
            
            logger.info(f"Email sent successfully to: {to_email}")
            return EmailResponse(
                success=True,
                message="Email sent successfully",
                email_sent_to=to_email
            )
            
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP authentication failed: {str(e)}")
            return EmailResponse(
                success=False,
                message="Email authentication failed",
                error=str(e)
            )
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error: {str(e)}")
            return EmailResponse(
                success=False,
                message="Failed to send email",
                error=str(e)
            )
        except Exception as e:
            logger.error(f"Unexpected error sending email: {str(e)}")
            return EmailResponse(
                success=False,
                message="An error occurred while sending email",
                error=str(e)
            )
    
    @staticmethod
    async def send_welcome_email(data: WelcomeEmailData) -> EmailResponse:
        """
        Send welcome email to new officer
        
        Args:
            data: WelcomeEmailData with user credentials
            
        Returns:
            EmailResponse
        """
        logger.info(f"Sending welcome email to: {data.email}")
        
        subject, html_body = get_welcome_email_template(
            firstname=data.firstname,
            lastname=data.lastname,
            username=data.username,
            temp_password=data.temp_password,
            lga_name=data.lga_name or "your assigned LGA"
        )
        
        return EmailService._send_email(
            to_email=data.email,
            subject=subject,
            html_body=html_body
        )
    
    @staticmethod
    async def send_password_reset_email(data: PasswordResetEmailData) -> EmailResponse:
        """
        Send password reset email
        
        Args:
            data: PasswordResetEmailData with reset token
            
        Returns:
            EmailResponse
        """
        logger.info(f"Sending password reset email to: {data.email}")
        
        # Calculate hours until expiration
        from datetime import datetime
        hours_until_expiration = int(
            (data.expires_at - datetime.utcnow()).total_seconds() / 3600
        )
        
        subject, html_body = get_password_reset_email_template(
            firstname=data.firstname,
            username=data.username,
            reset_token=data.reset_token,
            expires_hours=max(1, hours_until_expiration)  # At least 1 hour
        )
        
        return EmailService._send_email(
            to_email=data.email,
            subject=subject,
            html_body=html_body
        )
    
    @staticmethod
    async def send_password_changed_email(data: PasswordChangedEmailData) -> EmailResponse:
        """
        Send password changed confirmation email
        
        Args:
            data: PasswordChangedEmailData
            
        Returns:
            EmailResponse
        """
        logger.info(f"Sending password changed email to: {data.email}")
        
        subject, html_body = get_password_changed_email_template(
            firstname=data.firstname,
            username=data.username,
            changed_at=data.changed_at
        )
        
        return EmailService._send_email(
            to_email=data.email,
            subject=subject,
            html_body=html_body
        )
    
    @staticmethod
    async def send_account_locked_email(data: AccountLockedEmailData) -> EmailResponse:
        """
        Send account locked notification email
        
        Args:
            data: AccountLockedEmailData
            
        Returns:
            EmailResponse
        """
        logger.info(f"Sending account locked email to: {data.email}")
        
        subject, html_body = get_account_locked_email_template(
            firstname=data.firstname,
            username=data.username,
            locked_at=data.locked_at,
            reason=data.reason
        )
        
        return EmailService._send_email(
            to_email=data.email,
            subject=subject,
            html_body=html_body
        )