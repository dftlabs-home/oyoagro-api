"""
FILE: tests/test_email_live.py
Live email service tests - Actually sends emails via Resend
"""
import pytest
import os
from datetime import datetime, timedelta
from src.email.service import EmailService
from src.email.config import email_settings
from src.email.schemas import (
    WelcomeEmailData,
    PasswordResetEmailData,
    PasswordChangedEmailData,
    AccountLockedEmailData,
    EmailResponse
)


# ============================================================================
# TEST CONFIGURATION
# ============================================================================

def get_test_recipient():
    """Get test recipient email from environment or prompt"""
    test_email = os.getenv("TEST_EMAIL_RECIPIENT")
    if not test_email:
        print("\n" + "="*70)
        print("📧 LIVE EMAIL TEST CONFIGURATION")
        print("="*70)
        print("\nThese tests will send REAL emails via Resend.")
        print("Please provide a test email address to receive the emails.")
        print("\nTip: Set TEST_EMAIL_RECIPIENT in .env to skip this prompt")
        print("="*70)
        test_email = input("\nEnter your test email address: ").strip()
    
    if not test_email or '@' not in test_email:
        pytest.skip("No valid test email address provided")
    
    return test_email


def check_resend_configured():
    """Check if Resend is properly configured"""
    if not email_settings.RESEND_API_KEY or email_settings.RESEND_API_KEY == "":
        pytest.skip(
            "Resend API key not configured. "
            "Set RESEND_API_KEY in .env to run live email tests."
        )
    
    if not email_settings.SEND_EMAILS:
        pytest.skip(
            "Email sending is disabled. "
            "Set SEND_EMAILS=True in .env to run live email tests."
        )


# ============================================================================
# LIVE EMAIL TESTS
# ============================================================================

@pytest.mark.email
@pytest.mark.live
@pytest.mark.asyncio
class TestLiveEmailService:
    """Live email service tests - sends actual emails"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test"""
        check_resend_configured()
        self.test_email = get_test_recipient()
        print(f"\n📧 Sending test email to: {self.test_email}")
    
    async def test_send_welcome_email_live(self):
        """Test sending actual welcome email via Resend"""
        data = WelcomeEmailData(
            email=self.test_email,
            firstname="Test",
            lastname="User",
            username="testuser",
            temp_password="TempPass123",
            lga_name="Ibadan North"
        )
        
        print(f"📤 Sending welcome email to {self.test_email}...")
        result = await EmailService.send_welcome_email(data)
        
        # Assertions
        assert result.success is True, f"Email failed: {result.error}"
        assert result.email_id is not None, "No email ID returned from Resend"
        assert result.error is None
        assert "sent" in result.message.lower()
        
        print(f"✅ Welcome email sent successfully!")
        print(f"   Resend ID: {result.email_id}")
        print(f"   Message: {result.message}")
        print(f"\n📬 Check your inbox: {self.test_email}")
    
    async def test_send_password_reset_email_live(self):
        """Test sending actual password reset email via Resend"""
        data = PasswordResetEmailData(
            email=self.test_email,
            username="testuser",
            firstname="Test",
            reset_token="live_test_token_123abc456def",
            expires_at=datetime.utcnow() + timedelta(hours=24)
        )
        
        print(f"📤 Sending password reset email to {self.test_email}...")
        result = await EmailService.send_password_reset_email(data)
        
        # Assertions
        assert result.success is True, f"Email failed: {result.error}"
        assert result.email_id is not None
        assert result.error is None
        
        print(f"✅ Password reset email sent successfully!")
        print(f"   Resend ID: {result.email_id}")
        print(f"   Reset Token: {data.reset_token}")
        print(f"\n📬 Check your inbox: {self.test_email}")
    
    async def test_send_password_changed_email_live(self):
        """Test sending actual password changed email via Resend"""
        data = PasswordChangedEmailData(
            email=self.test_email,
            username="testuser",
            firstname="Test",
            changed_at=datetime.utcnow()
        )
        
        print(f"📤 Sending password changed email to {self.test_email}...")
        result = await EmailService.send_password_changed_email(data)
        
        # Assertions
        assert result.success is True, f"Email failed: {result.error}"
        assert result.email_id is not None
        assert result.error is None
        
        print(f"✅ Password changed email sent successfully!")
        print(f"   Resend ID: {result.email_id}")
        print(f"\n📬 Check your inbox: {self.test_email}")
    
    async def test_send_account_locked_email_live(self):
        """Test sending actual account locked email via Resend"""
        data = AccountLockedEmailData(
            email=self.test_email,
            username="testuser",
            firstname="Test",
            locked_at=datetime.utcnow(),
            reason="Live test - Multiple failed login attempts"
        )
        
        print(f"📤 Sending account locked email to {self.test_email}...")
        result = await EmailService.send_account_locked_email(data)
        
        # Assertions
        assert result.success is True, f"Email failed: {result.error}"
        assert result.email_id is not None
        assert result.error is None
        
        print(f"✅ Account locked email sent successfully!")
        print(f"   Resend ID: {result.email_id}")
        print(f"\n📬 Check your inbox: {self.test_email}")
    
    async def test_all_email_types_sequence_live(self):
        """Test sending all email types in sequence"""
        print(f"\n📧 Sending all 4 email types to {self.test_email}...")
        print("="*70)
        
        results = []
        
        # 1. Welcome email
        print("\n1️⃣  Sending Welcome Email...")
        welcome_result = await EmailService.send_welcome_email(
            WelcomeEmailData(
                email=self.test_email,
                firstname="Test",
                lastname="User",
                username="testuser",
                temp_password="Pass123",
                lga_name="Test LGA"
            )
        )
        assert welcome_result.success is True
        results.append(("Welcome", welcome_result))
        print(f"   ✅ Sent - ID: {welcome_result.email_id}")
        
        # 2. Password reset email
        print("\n2️⃣  Sending Password Reset Email...")
        reset_result = await EmailService.send_password_reset_email(
            PasswordResetEmailData(
                email=self.test_email,
                username="testuser",
                firstname="Test",
                reset_token="sequence_test_token",
                expires_at=datetime.utcnow() + timedelta(hours=24)
            )
        )
        assert reset_result.success is True
        results.append(("Password Reset", reset_result))
        print(f"   ✅ Sent - ID: {reset_result.email_id}")
        
        # 3. Password changed email
        print("\n3️⃣  Sending Password Changed Email...")
        changed_result = await EmailService.send_password_changed_email(
            PasswordChangedEmailData(
                email=self.test_email,
                username="testuser",
                firstname="Test",
                changed_at=datetime.utcnow()
            )
        )
        assert changed_result.success is True
        results.append(("Password Changed", changed_result))
        print(f"   ✅ Sent - ID: {changed_result.email_id}")
        
        # 4. Account locked email
        print("\n4️⃣  Sending Account Locked Email...")
        locked_result = await EmailService.send_account_locked_email(
            AccountLockedEmailData(
                email=self.test_email,
                username="testuser",
                firstname="Test",
                locked_at=datetime.utcnow(),
                reason="Sequence test"
            )
        )
        assert locked_result.success is True
        results.append(("Account Locked", locked_result))
        print(f"   ✅ Sent - ID: {locked_result.email_id}")
        
        # Summary
        print("\n" + "="*70)
        print("📊 EMAIL SENDING SUMMARY")
        print("="*70)
        for email_type, result in results:
            print(f"✅ {email_type:20} - ID: {result.email_id}")
        
        print(f"\n📬 Check your inbox: {self.test_email}")
        print("📧 You should have received 4 test emails")
        print("="*70)


# ============================================================================
# EMAIL VALIDATION TESTS (Still using mocks - no actual sending)
# ============================================================================

@pytest.mark.email
@pytest.mark.asyncio
class TestEmailValidation:
    """Test email validation without sending actual emails"""
    
    async def test_email_response_schema_validation(self):
        """Test EmailResponse schema"""
        response = EmailResponse(
            success=True,
            message="Test message",
            email_id="re_abc123",
            error=None
        )
        
        assert response.success is True
        assert response.email_id == "re_abc123"
    
    async def test_invalid_email_format(self):
        """Test that invalid email format is caught"""
        with pytest.raises(Exception):
            WelcomeEmailData(
                email="not-an-email",
                firstname="Test",
                lastname="User",
                username="test",
                temp_password="pass"
            )
    
    async def test_all_email_schemas_validate(self):
        """Test all email data schemas"""
        # Welcome
        welcome = WelcomeEmailData(
            email="test@example.com",
            firstname="Test",
            lastname="User",
            username="test",
            temp_password="pass"
        )
        assert welcome.email == "test@example.com"
        
        # Password reset
        reset = PasswordResetEmailData(
            email="test@example.com",
            username="test",
            firstname="Test",
            reset_token="token",
            expires_at=datetime.utcnow()
        )
        assert reset.reset_token == "token"
        
        # Password changed
        changed = PasswordChangedEmailData(
            email="test@example.com",
            username="test",
            firstname="Test",
            changed_at=datetime.utcnow()
        )
        assert changed.username == "test"
        
        # Account locked
        locked = AccountLockedEmailData(
            email="test@example.com",
            username="test",
            firstname="Test",
            locked_at=datetime.utcnow()
        )
        assert locked.reason == "Multiple failed login attempts"


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🧪 LIVE EMAIL TESTS")
    print("="*70)
    print("\nThese tests will send REAL emails via Resend!")
    print("\nPrerequisites:")
    print("1. RESEND_API_KEY must be set in .env")
    print("2. SEND_EMAILS=True must be set in .env")
    print("3. Valid test email address required")
    print("\nTests marked with '@pytest.mark.live' will send actual emails.")
    print("="*70)
    
    # Run only validation tests by default
    pytest.main([__file__, "-v", "-m", "email and not live"])
    
    print("\n" + "="*70)
    print("To run LIVE email sending tests, use:")
    print("pytest tests/test_email_live.py -v -m live")
    print("="*70)