"""
FILE: tests/test_email.py
Comprehensive email service and integration tests
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from datetime import datetime, timedelta

from src.email.service import EmailService
from src.email.schemas import (
    WelcomeEmailData,
    PasswordResetEmailData,
    PasswordChangedEmailData,
    AccountLockedEmailData,
    EmailResponse
)
from src.email.config import email_settings
from src.shared.models import Useraccount, PasswordResetToken


# ============================================================================
# EMAIL SERVICE UNIT TESTS
# ============================================================================

@pytest.mark.email
class TestEmailService:
    """Test email service functionality"""
    
    @pytest.mark.asyncio
    async def test_welcome_email_disabled(self):
        """Test welcome email when sending is disabled"""
        email_settings.SEND_EMAILS = False
        
        data = WelcomeEmailData(
            email="test@example.com",
            firstname="John",
            lastname="Doe",
            username="john.doe",
            temp_password="TempPass123",
            lga_name="Ibadan North"
        )
        
        response = await EmailService.send_welcome_email(data)
        
        assert response.success is True
        assert "disabled" in response.message.lower()
        assert response.email_sent_to == "test@example.com"
    
    @pytest.mark.asyncio
    async def test_password_reset_email_disabled(self):
        """Test password reset email when sending is disabled"""
        email_settings.SEND_EMAILS = False
        
        data = PasswordResetEmailData(
            email="test@example.com",
            username="john.doe",
            firstname="John",
            reset_token="abc123",
            expires_at=datetime.utcnow() + timedelta(hours=24)
        )
        
        response = await EmailService.send_password_reset_email(data)
        
        assert response.success is True
        assert response.email_sent_to == "test@example.com"
    
    @pytest.mark.asyncio
    async def test_password_changed_email_disabled(self):
        """Test password changed email when sending is disabled"""
        email_settings.SEND_EMAILS = False
        
        data = PasswordChangedEmailData(
            email="test@example.com",
            username="john.doe",
            firstname="John",
            changed_at=datetime.utcnow()
        )
        
        response = await EmailService.send_password_changed_email(data)
        
        assert response.success is True
    
    @pytest.mark.asyncio
    async def test_account_locked_email_disabled(self):
        """Test account locked email when sending is disabled"""
        email_settings.SEND_EMAILS = False
        
        data = AccountLockedEmailData(
            email="test@example.com",
            username="john.doe",
            firstname="John",
            locked_at=datetime.utcnow(),
            reason="Multiple failed login attempts"
        )
        
        response = await EmailService.send_account_locked_email(data)
        
        assert response.success is True
    
    @pytest.mark.asyncio
    async def test_email_without_credentials(self):
        """Test email sending fails gracefully without credentials"""
        # Backup settings
        original_send = email_settings.SEND_EMAILS
        original_user = email_settings.MAIL_USERNAME
        original_pass = email_settings.MAIL_PASSWORD
        
        # Set up test
        email_settings.SEND_EMAILS = True
        email_settings.MAIL_USERNAME = ""
        email_settings.MAIL_PASSWORD = ""
        
        data = WelcomeEmailData(
            email="test@example.com",
            firstname="John",
            lastname="Doe",
            username="john.doe",
            temp_password="TempPass123"
        )
        
        response = await EmailService.send_welcome_email(data)
        
        # Restore settings
        email_settings.SEND_EMAILS = original_send
        email_settings.MAIL_USERNAME = original_user
        email_settings.MAIL_PASSWORD = original_pass
        
        assert response.success is False
        assert "not configured" in response.message.lower()


# ============================================================================
# EMAIL INTEGRATION TESTS (AUTH ENDPOINTS)
# ============================================================================

@pytest.mark.email
@pytest.mark.integration
class TestEmailIntegrationAuth:
    """Test email integration with auth endpoints"""
    
    @pytest.mark.asyncio
    async def test_register_sends_welcome_email(
        self, client: TestClient, admin_headers: dict, test_lga, test_region, monkeypatch
    ):
        """Test user registration sends welcome email"""
        # Mock email service
        mock_send = AsyncMock(return_value=EmailResponse(
            success=True,
            message="Email sent",
            email_sent_to="newofficer@oyoagro.gov.ng"
        ))
        
        monkeypatch.setattr(
            "src.email.service.EmailService.send_welcome_email",
            mock_send
        )
        
        # Register user
        response = client.post(
            "/api/v1/auth/register",
            headers=admin_headers,
            json={
                "firstname": "New",
                "lastname": "Officer",
                "emailAddress": "newofficer@oyoagro.gov.ng",
                "phonenumber": "08099999999",
                "lgaid": test_lga.lgaid,
                "regionid": test_region.regionid,
                "streetaddress": "123 Street",
                "town": "Ibadan",
                "postalcode": "200001"
            }
        )
        
        assert response.status_code == 200
        
        # Verify email was sent
        mock_send.assert_called_once()
        call_args = mock_send.call_args[0][0]
        assert call_args.email == "newofficer@oyoagro.gov.ng"
        assert call_args.firstname == "New"
        assert call_args.lastname == "Officer"
        assert hasattr(call_args, 'temp_password')
    
    @pytest.mark.asyncio
    async def test_forgot_password_sends_email(
        self, client: TestClient, test_user: dict, session: Session, monkeypatch
    ):
        """Test forgot password sends reset email"""
        # Mock email service
        mock_send = AsyncMock(return_value=EmailResponse(
            success=True,
            message="Email sent",
            email_sent_to=test_user["user"].email
        ))
        
        monkeypatch.setattr(
            "src.email.service.EmailService.send_password_reset_email",
            mock_send
        )
        
        # Request password reset
        response = client.post(
            "/api/v1/auth/forgot-password",
            json={"email": test_user["user"].email}
        )
        
        assert response.status_code == 200
        
        # Verify email was sent
        mock_send.assert_called_once()
        call_args = mock_send.call_args[0][0]
        assert call_args.email == test_user["user"].email
        assert call_args.username == test_user["user"].username
        assert hasattr(call_args, 'reset_token')
    
    @pytest.mark.asyncio
    async def test_reset_password_sends_confirmation(
        self, client: TestClient, test_user: dict, session: Session, monkeypatch
    ):
        """Test password reset sends confirmation email"""
        from src.core.security import generate_reset_token
        
        # Create reset token
        reset_token = generate_reset_token()
        expires_at = datetime.utcnow() + timedelta(hours=24)
        
        token_record = PasswordResetToken(
            userid=test_user["user"].userid,
            token=reset_token,
            expiresat=expires_at,
            isused=False,
            createdat=datetime.utcnow()
        )
        session.add(token_record)
        session.commit()
        
        # Mock email service
        mock_send = AsyncMock(return_value=EmailResponse(
            success=True,
            message="Email sent"
        ))
        
        monkeypatch.setattr(
            "src.email.service.EmailService.send_password_changed_email",
            mock_send
        )
        
        # Reset password
        response = client.post(
            "/api/v1/auth/reset-password",
            json={
                "token": reset_token,
                "newPassword": "NewPassword123",
                "confirmPassword": "NewPassword123"
            }
        )
        
        assert response.status_code == 200
        
        # Verify confirmation email was sent
        mock_send.assert_called_once()
        call_args = mock_send.call_args[0][0]
        assert call_args.email == test_user["user"].email
        assert isinstance(call_args.changed_at, datetime)
    
    @pytest.mark.asyncio
    async def test_change_password_sends_confirmation(
        self, client: TestClient, test_user: dict, session: Session, monkeypatch
    ):
        """Test manual password change sends confirmation email"""
        # Login first
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "username": test_user["user"].username,
                "password": test_user["password"]
            }
        )
        token = login_response.json()["data"]["token"]
        
        # Mock email service
        mock_send = AsyncMock(return_value=EmailResponse(
            success=True,
            message="Email sent"
        ))
        
        monkeypatch.setattr(
            "src.email.service.EmailService.send_password_changed_email",
            mock_send
        )
        
        # Change password - send as JSON body
        response = client.post(
            "/api/v1/auth/change-password",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "currentPassword": test_user["password"],
                "newPassword": "NewPassword456"
            }
        )
        
        assert response.status_code == 200
        
        # Verify confirmation email was sent
        mock_send.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_account_lock_sends_notification(
        self, client: TestClient, test_user: dict, session: Session, monkeypatch
    ):
        """Test account lock sends notification email"""
        # Mock email service
        mock_send = AsyncMock(return_value=EmailResponse(
            success=True,
            message="Email sent"
        ))
        
        monkeypatch.setattr(
            "src.email.service.EmailService.send_account_locked_email",
            mock_send
        )
        
        # Make 5 failed login attempts to lock account
        for _ in range(5):
            client.post(
                "/api/v1/auth/login",
                json={
                    "username": test_user["user"].username,
                    "password": "WrongPassword"
                }
            )
        
        # Verify lock email was sent
        mock_send.assert_called_once()
        call_args = mock_send.call_args[0][0]
        assert call_args.email == test_user["user"].email
        assert call_args.reason == "Multiple failed login attempts"
    
    @pytest.mark.asyncio
    async def test_admin_lock_sends_notification(
        self, client: TestClient, admin_headers: dict, test_user: dict, monkeypatch
    ):
        """Test admin account lock sends notification email"""
        # Mock email service
        mock_send = AsyncMock(return_value=EmailResponse(
            success=True,
            message="Email sent"
        ))
        
        monkeypatch.setattr(
            "src.email.service.EmailService.send_account_locked_email",
            mock_send
        )
        
        # Admin locks account
        response = client.post(
            f"/api/v1/auth/lock-account/{test_user['user'].userid}",
            headers=admin_headers
        )
        
        assert response.status_code == 200
        
        # Verify lock email was sent
        mock_send.assert_called_once()
        call_args = mock_send.call_args[0][0]
        assert call_args.reason == "Account locked by administrator"


# ============================================================================
# EMAIL TEMPLATE TESTS
# ============================================================================

@pytest.mark.email
class TestEmailTemplates:
    """Test email template generation"""
    
    def test_welcome_email_template(self):
        """Test welcome email template generation"""
        from src.email.templates import get_welcome_email_template
        
        subject, html = get_welcome_email_template(
            firstname="John",
            lastname="Doe",
            username="john.doe",
            temp_password="TempPass123",
            lga_name="Ibadan North"
        )
        
        assert "Welcome" in subject
        assert "john.doe" in html
        assert "TempPass123" in html
        assert "Ibadan North" in html
        assert "<!DOCTYPE html>" in html
    
    def test_password_reset_template(self):
        """Test password reset email template"""
        from src.email.templates import get_password_reset_email_template
        
        subject, html = get_password_reset_email_template(
            firstname="John",
            username="john.doe",
            reset_token="abc123token",
            expires_hours=24
        )
        
        assert "Password Reset" in subject
        assert "john.doe" in html
        assert "abc123token" in html
        assert "24" in html
        assert "<!DOCTYPE html>" in html
    
    def test_password_changed_template(self):
        """Test password changed email template"""
        from src.email.templates import get_password_changed_email_template
        
        changed_at = datetime.utcnow()
        subject, html = get_password_changed_email_template(
            firstname="John",
            username="john.doe",
            changed_at=changed_at
        )
        
        assert "Password Changed" in subject
        assert "john.doe" in html
        assert "<!DOCTYPE html>" in html
    
    def test_account_locked_template(self):
        """Test account locked email template"""
        from src.email.templates import get_account_locked_email_template
        
        locked_at = datetime.utcnow()
        subject, html = get_account_locked_email_template(
            firstname="John",
            username="john.doe",
            locked_at=locked_at,
            reason="Multiple failed login attempts"
        )
        
        assert "Account Locked" in subject or "Locked" in subject
        assert "john.doe" in html
        assert "Multiple failed login attempts" in html
        assert "<!DOCTYPE html>" in html


# ============================================================================
# EMAIL ERROR HANDLING TESTS
# ============================================================================

@pytest.mark.email
class TestEmailErrorHandling:
    """Test email error handling"""
    
    @pytest.mark.asyncio
    async def test_email_failure_does_not_prevent_registration(
        self, client: TestClient, admin_headers: dict, test_lga, test_region, monkeypatch
    ):
        """Test registration succeeds even if email fails"""
        # Mock email service to fail
        mock_send = AsyncMock(return_value=EmailResponse(
            success=False,
            message="SMTP error",
            error="Connection refused"
        ))
        
        monkeypatch.setattr(
            "src.email.service.EmailService.send_welcome_email",
            mock_send
        )
        
        # Register user
        response = client.post(
            "/api/v1/auth/register",
            headers=admin_headers,
            json={
                "firstname": "Test",
                "lastname": "User",
                "emailAddress": "test@example.com",
                "phonenumber": "08099999998",
                "lgaid": test_lga.lgaid,
                "regionid": test_region.regionid,
                "streetaddress": "123 Street",
                "town": "Ibadan",
                "postalcode": "200001"
            }
        )
        
        # Registration should succeed despite email failure
        assert response.status_code == 200
        assert response.json()["success"] is True
    
    @pytest.mark.asyncio
    async def test_email_failure_does_not_prevent_password_reset(
        self, client: TestClient, test_user: dict, monkeypatch
    ):
        """Test password reset succeeds even if email fails"""
        # Mock email service to fail
        mock_send = AsyncMock(return_value=EmailResponse(
            success=False,
            message="SMTP error",
            error="Connection refused"
        ))
        
        monkeypatch.setattr(
            "src.email.service.EmailService.send_password_reset_email",
            mock_send
        )
        
        # Request password reset
        response = client.post(
            "/api/v1/auth/forgot-password",
            json={"email": test_user["user"].email}
        )
        
        # Should still return success
        assert response.status_code == 200
        assert response.json()["success"] is True


# ============================================================================
# EMAIL DATA VALIDATION TESTS
# ============================================================================

@pytest.mark.email
class TestEmailDataValidation:
    """Test email data schema validation"""
    
    def test_welcome_email_data_validation(self):
        """Test WelcomeEmailData validation"""
        # Valid data
        data = WelcomeEmailData(
            email="test@example.com",
            firstname="John",
            lastname="Doe",
            username="john.doe",
            temp_password="Pass123"
        )
        assert data.email == "test@example.com"
        
        # Invalid email
        with pytest.raises(Exception):
            WelcomeEmailData(
                email="invalid-email",
                firstname="John",
                lastname="Doe",
                username="john.doe",
                temp_password="Pass123"
            )
    
    def test_password_reset_email_data_validation(self):
        """Test PasswordResetEmailData validation"""
        # Valid data
        data = PasswordResetEmailData(
            email="test@example.com",
            username="john.doe",
            firstname="John",
            reset_token="abc123",
            expires_at=datetime.utcnow() + timedelta(hours=24)
        )
        assert data.email == "test@example.com"
        
        # Invalid email
        with pytest.raises(Exception):
            PasswordResetEmailData(
                email="invalid-email",
                username="john.doe",
                firstname="John",
                reset_token="abc123",
                expires_at=datetime.utcnow()
            )


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])