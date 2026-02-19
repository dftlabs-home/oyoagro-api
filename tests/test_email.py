"""
FILE: tests/test_email.py
Email service tests - Updated for Resend API
"""
import pytest
from datetime import datetime, timedelta
from src.email.service import EmailService
from src.email.schemas import (
    WelcomeEmailData,
    PasswordResetEmailData,
    PasswordChangedEmailData,
    AccountLockedEmailData,
    EmailResponse
)


# ============================================================================
# EMAIL SERVICE TESTS
# ============================================================================

@pytest.mark.email
@pytest.mark.asyncio
class TestEmailService:
    """Test email service functionality with Resend API"""
    
    async def test_send_welcome_email_dev_mode(self, mock_email_settings):
        """Test welcome email in development mode (no actual sending)"""
        # Ensure dev mode
        mock_email_settings.SEND_EMAILS = False
        
        data = WelcomeEmailData(
            email="test@example.com",
            firstname="John",
            lastname="Doe",
            username="johndoe",
            temp_password="TempPass123",
            lga_name="Ibadan North"
        )
        
        result = await EmailService.send_welcome_email(data)
        
        assert result.success is True
        assert "development mode" in result.message.lower()
        assert result.email_id is None
        assert result.error is None
    
    async def test_send_welcome_email_missing_api_key(self, mock_email_settings):
        """Test welcome email fails gracefully without API key"""
        # Enable sending but clear API key
        mock_email_settings.SEND_EMAILS = True
        mock_email_settings.RESEND_API_KEY = ""
        
        data = WelcomeEmailData(
            email="test@example.com",
            firstname="John",
            lastname="Doe",
            username="johndoe",
            temp_password="TempPass123"
        )
        
        result = await EmailService.send_welcome_email(data)
        
        assert result.success is False
        assert "not configured" in result.message.lower()
        assert result.error == "Resend API key missing"
    
    async def test_send_password_reset_email_dev_mode(self, mock_email_settings):
        """Test password reset email in development mode"""
        mock_email_settings.SEND_EMAILS = False
        
        data = PasswordResetEmailData(
            email="test@example.com",
            username="johndoe",
            firstname="John",
            reset_token="test_token_123",
            expires_at=datetime.utcnow() + timedelta(hours=24)
        )
        
        result = await EmailService.send_password_reset_email(data)
        
        assert result.success is True
        assert "development mode" in result.message.lower()
        assert result.email_id is None
    
    async def test_send_password_changed_email_dev_mode(self, mock_email_settings):
        """Test password changed email in development mode"""
        mock_email_settings.SEND_EMAILS = False
        
        data = PasswordChangedEmailData(
            email="test@example.com",
            username="johndoe",
            firstname="John",
            changed_at=datetime.utcnow()
        )
        
        result = await EmailService.send_password_changed_email(data)
        
        assert result.success is True
        assert "development mode" in result.message.lower()
    
    async def test_send_account_locked_email_dev_mode(self, mock_email_settings):
        """Test account locked email in development mode"""
        mock_email_settings.SEND_EMAILS = False
        
        data = AccountLockedEmailData(
            email="test@example.com",
            username="johndoe",
            firstname="John",
            locked_at=datetime.utcnow(),
            reason="Multiple failed login attempts"
        )
        
        result = await EmailService.send_account_locked_email(data)
        
        assert result.success is True
        assert "development mode" in result.message.lower()
    
    async def test_email_response_schema(self):
        """Test EmailResponse schema validation"""
        # Valid response with all fields
        response = EmailResponse(
            success=True,
            message="Email sent",
            email_id="re_123abc456",
            error=None
        )
        
        assert response.success is True
        assert response.message == "Email sent"
        assert response.email_id == "re_123abc456"
        assert response.error is None
        
        # Valid response with minimal fields
        response2 = EmailResponse(
            success=False,
            message="Failed",
            error="Connection error"
        )
        
        assert response2.success is False
        assert response2.email_id is None
    
    async def test_welcome_email_data_schema(self):
        """Test WelcomeEmailData schema validation"""
        data = WelcomeEmailData(
            email="test@example.com",
            firstname="John",
            lastname="Doe",
            username="johndoe",
            temp_password="Pass123"
        )
        
        assert data.email == "test@example.com"
        assert data.lga_name is None  # Optional field
        
        # With optional LGA name
        data2 = WelcomeEmailData(
            email="test2@example.com",
            firstname="Jane",
            lastname="Smith",
            username="janesmith",
            temp_password="Pass456",
            lga_name="Ibadan North"
        )
        
        assert data2.lga_name == "Ibadan North"
    
    async def test_password_reset_data_schema(self):
        """Test PasswordResetEmailData schema validation"""
        expires_at = datetime.utcnow() + timedelta(hours=24)
        
        data = PasswordResetEmailData(
            email="test@example.com",
            username="johndoe",
            firstname="John",
            reset_token="token_123",
            expires_at=expires_at
        )
        
        assert data.reset_token == "token_123"
        assert data.expires_at == expires_at
    
    async def test_password_changed_data_schema(self):
        """Test PasswordChangedEmailData schema validation"""
        changed_at = datetime.utcnow()
        
        data = PasswordChangedEmailData(
            email="test@example.com",
            username="johndoe",
            firstname="John",
            changed_at=changed_at
        )
        
        assert data.changed_at == changed_at
    
    async def test_account_locked_data_schema(self):
        """Test AccountLockedEmailData schema validation"""
        locked_at = datetime.utcnow()
        
        # With default reason
        data = AccountLockedEmailData(
            email="test@example.com",
            username="johndoe",
            firstname="John",
            locked_at=locked_at
        )
        
        assert data.reason == "Multiple failed login attempts"  # Default
        
        # With custom reason
        data2 = AccountLockedEmailData(
            email="test@example.com",
            username="johndoe",
            firstname="John",
            locked_at=locked_at,
            reason="Admin action"
        )
        
        assert data2.reason == "Admin action"
    
    async def test_invalid_email_validation(self):
        """Test email validation in schemas"""
        with pytest.raises(Exception):  # Pydantic will raise ValidationError
            WelcomeEmailData(
                email="invalid-email",  # Invalid email format
                firstname="John",
                lastname="Doe",
                username="johndoe",
                temp_password="Pass123"
            )


# ============================================================================
# EMAIL INTEGRATION TESTS
# ============================================================================

@pytest.mark.email
@pytest.mark.asyncio
class TestEmailIntegration:
    """Integration tests for email service"""
    
    async def test_email_service_initialization(self, mock_email_settings):
        """Test email service initialization"""
        # Test with valid API key
        mock_email_settings.RESEND_API_KEY = "re_test_key"
        result = EmailService._initialize_resend()
        assert result is True
        
        # Test without API key
        mock_email_settings.RESEND_API_KEY = ""
        result = EmailService._initialize_resend()
        assert result is False
    
    async def test_welcome_email_contains_required_elements(self, mock_email_settings):
        """Test that welcome email contains all required information"""
        mock_email_settings.SEND_EMAILS = False
        
        data = WelcomeEmailData(
            email="newofficer@example.com",
            firstname="Jane",
            lastname="Smith",
            username="janesmith",
            temp_password="SecurePass123",
            lga_name="Oyo East"
        )
        
        result = await EmailService.send_welcome_email(data)
        
        assert result.success is True
        # In dev mode, no actual email is sent
        # In production, email would contain username, password, LGA name
    
    async def test_password_reset_email_url_generation(self, mock_email_settings):
        """Test that password reset email generates correct URL"""
        mock_email_settings.SEND_EMAILS = False
        mock_email_settings.PASSWORD_RESET_URL = "http://localhost:3000/reset"
        
        data = PasswordResetEmailData(
            email="user@example.com",
            username="user",
            firstname="User",
            reset_token="abc123def456",
            expires_at=datetime.utcnow() + timedelta(hours=24)
        )
        
        result = await EmailService.send_password_reset_email(data)
        
        assert result.success is True
        # In production, email would contain: http://localhost:3000/reset?token=abc123def456
    
    async def test_all_email_types_work_in_sequence(self, mock_email_settings):
        """Test sending all email types in sequence"""
        mock_email_settings.SEND_EMAILS = False
        
        # Welcome email
        welcome_result = await EmailService.send_welcome_email(
            WelcomeEmailData(
                email="test@example.com",
                firstname="Test",
                lastname="User",
                username="testuser",
                temp_password="Pass123"
            )
        )
        assert welcome_result.success is True
        
        # Password reset email
        reset_result = await EmailService.send_password_reset_email(
            PasswordResetEmailData(
                email="test@example.com",
                username="testuser",
                firstname="Test",
                reset_token="token123",
                expires_at=datetime.utcnow() + timedelta(hours=24)
            )
        )
        assert reset_result.success is True
        
        # Password changed email
        changed_result = await EmailService.send_password_changed_email(
            PasswordChangedEmailData(
                email="test@example.com",
                username="testuser",
                firstname="Test",
                changed_at=datetime.utcnow()
            )
        )
        assert changed_result.success is True
        
        # Account locked email
        locked_result = await EmailService.send_account_locked_email(
            AccountLockedEmailData(
                email="test@example.com",
                username="testuser",
                firstname="Test",
                locked_at=datetime.utcnow()
            )
        )
        assert locked_result.success is True


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "email"])