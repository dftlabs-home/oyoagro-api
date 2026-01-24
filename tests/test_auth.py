"""
FILE: tests/test_auth.py
Comprehensive authentication tests
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from datetime import datetime, timedelta

from src.core.security import simple_encrypt, generate_salt, generate_reset_token
from src.shared.models import Useraccount, Userprofile, PasswordResetToken


# ============================================================================
# ADDITIONAL FIXTURES (specific to auth tests)
# ============================================================================

@pytest.fixture(name="test_user")
def test_user_fixture(session: Session):
    """Create test user with encrypted password"""
    salt = "12345"
    password = "TestPassword123"
    encrypted_password = simple_encrypt(password, salt)
    
    user = Useraccount(
        userid=1,
        username="testuser",
        email="test@example.com",
        passwordhash=encrypted_password,
        salt=salt,
        status=1,
        isactive=False,
        islocked=False,
        logincount=0,
        failedloginattempt=0,
        createdat=datetime.utcnow()
    )
    
    session.add(user)
    
    # Add profile
    profile = Userprofile(
        userprofileid=1,
        userid=1,
        firstname="Test",
        lastname="User",
        email="test@example.com",
        phonenumber="08012345678",
        createdat=datetime.utcnow()
    )
    
    session.add(profile)
    session.commit()
    session.refresh(user)
    
    return {"user": user, "password": password}


@pytest.fixture(name="locked_user")
def locked_user_fixture(session: Session):
    """Create locked user for testing"""
    salt = generate_salt()
    password = "LockedPassword123"
    encrypted_password = simple_encrypt(password, salt)
    
    user = Useraccount(
        userid=2,
        username="lockeduser",
        email="locked@example.com",
        passwordhash=encrypted_password,
        salt=salt,
        status=1,
        isactive=False,
        islocked=True,  # Locked
        logincount=0,
        failedloginattempt=5,
        createdat=datetime.utcnow()
    )
    
    session.add(user)
    session.commit()
    session.refresh(user)
    
    return {"user": user, "password": password}


@pytest.fixture(name="inactive_user")
def inactive_user_fixture(session: Session):
    """Create inactive user for testing"""
    salt = generate_salt()
    password = "InactivePassword123"
    encrypted_password = simple_encrypt(password, salt)
    
    user = Useraccount(
        userid=3,
        username="inactiveuser",
        email="inactive@example.com",
        passwordhash=encrypted_password,
        salt=salt,
        status=0,  # Inactive
        isactive=False,
        islocked=False,
        logincount=0,
        failedloginattempt=0,
        createdat=datetime.utcnow()
    )
    
    session.add(user)
    session.commit()
    session.refresh(user)
    
    return {"user": user, "password": password}


# ============================================================================
# LOGIN TESTS
# ============================================================================

@pytest.mark.auth
class TestLogin:
    """Test login endpoint"""
    
    def test_login_success(self, client: TestClient, test_user: dict):
        """Test successful login"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": "testuser",
                "password": test_user["password"]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["tag"] == 1
        assert "token" in data["data"]
        assert "user" in data["data"]
        assert data["data"]["user"]["username"] == "testuser"
    
    def test_login_invalid_username(self, client: TestClient):
        """Test login with invalid username"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": "nonexistent",
                "password": "AnyPassword123"
            }
        )
        
        assert response.status_code == 401
        assert "Invalid username or password" in response.json()["detail"]
    
    def test_login_invalid_password(self, client: TestClient, test_user: dict):
        """Test login with invalid password"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": "testuser",
                "password": "WrongPassword123"
            }
        )
        
        assert response.status_code == 401
        assert "Invalid username or password" in response.json()["detail"]
    
    def test_login_locked_account(self, client: TestClient, locked_user: dict):
        """Test login with locked account"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": "lockeduser",
                "password": locked_user["password"]
            }
        )
        
        assert response.status_code == 403
        assert "locked" in response.json()["detail"].lower()
    
    def test_login_inactive_account(self, client: TestClient, inactive_user: dict):
        """Test login with inactive account"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": "inactiveuser",
                "password": inactive_user["password"]
            }
        )
        
        assert response.status_code == 403
        assert "disabled" in response.json()["detail"].lower()
    
    def test_login_account_locks_after_failed_attempts(
        self, client: TestClient, test_user: dict, session: Session
    ):
        """Test account locks after 5 failed login attempts"""
        # Make 5 failed login attempts
        for _ in range(5):
            response = client.post(
                "/api/v1/auth/login",
                json={
                    "username": "testuser",
                    "password": "WrongPassword"
                }
            )
            assert response.status_code in [401, 403]
        
        # 6th attempt should return locked message
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": "testuser",
                "password": "WrongPassword"
            }
        )
        
        assert response.status_code == 403
        assert "locked" in response.json()["detail"].lower()
        
        # Verify user is locked in database
        user = session.get(Useraccount, test_user["user"].userid)
        assert user.islocked is True # type: ignore
    
    def test_login_resets_failed_attempts_on_success(
        self, client: TestClient, test_user: dict, session: Session
    ):
        """Test failed login attempts reset on successful login"""
        # Make 3 failed attempts
        for _ in range(3):
            client.post(
                "/api/v1/auth/login",
                json={
                    "username": "testuser",
                    "password": "WrongPassword"
                }
            )
        
        # Successful login
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": "testuser",
                "password": test_user["password"]
            }
        )
        
        assert response.status_code == 200
        
        # Verify failed attempts reset
        user = session.get(Useraccount, test_user["user"].userid)
        assert user.failedloginattempt == 0 # type: ignore
    
    def test_login_updates_login_count(
        self, client: TestClient, test_user: dict, session: Session
    ):
        """Test login count increases on successful login"""
        initial_count = test_user["user"].logincount or 0
        
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": "testuser",
                "password": test_user["password"]
            }
        )
        
        assert response.status_code == 200
        
        # Verify login count increased
        session.refresh(test_user["user"])
        assert test_user["user"].logincount == initial_count + 1


# ============================================================================
# LOGOUT TESTS
# ============================================================================

@pytest.mark.auth
class TestLogout:
    """Test logout endpoint"""
    
    def test_logout_success(self, client: TestClient, test_user: dict, session: Session):
        """Test successful logout"""
        # Login first
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "username": "testuser",
                "password": test_user["password"]
            }
        )
        token = login_response.json()["data"]["token"]
        
        # Logout
        response = client.get(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        # Verify token cleared in database
        session.refresh(test_user["user"])
        assert test_user["user"].apitoken is None
        assert test_user["user"].isactive is False
    
    def test_logout_no_token(self, client: TestClient):
        """Test logout without token"""
        response = client.get("/api/v1/auth/logout")
        
        assert response.status_code == 401
        assert "Not authenticated" in response.json()["detail"]
    
    def test_logout_invalid_token(self, client: TestClient):
        """Test logout with invalid token"""
        response = client.get(
            "/api/v1/auth/logout",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == 401


# ============================================================================
# PASSWORD RESET TESTS
# ============================================================================

@pytest.mark.auth
class TestPasswordReset:
    """Test password reset functionality"""
    
    def test_forgot_password_success(
        self, client: TestClient, test_user: dict, session: Session
    ):
        """Test forgot password creates reset token"""
        response = client.post(
            "/api/v1/auth/forgot-password",
            json={"email": "test@example.com"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        # Verify token created in database
        from sqlmodel import select
        statement = select(PasswordResetToken).where(
            PasswordResetToken.userid == test_user["user"].userid,
            PasswordResetToken.isused == False
        )
        token_record = session.exec(statement).first()
        
        assert token_record is not None
        assert token_record.expiresat > datetime.utcnow() # type: ignore
    
    def test_forgot_password_nonexistent_email(self, client: TestClient):
        """Test forgot password with non-existent email still returns success"""
        response = client.post(
            "/api/v1/auth/forgot-password",
            json={"email": "nonexistent@example.com"}
        )
        
        # Should still return success (security best practice)
        assert response.status_code == 200
        assert response.json()["success"] is True
    
    def test_reset_password_success(
        self, client: TestClient, test_user: dict, session: Session
    ):
        """Test successful password reset"""
        # Generate reset token
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
        
        # Reset password
        new_password = "NewPassword123"
        response = client.post(
            "/api/v1/auth/reset-password",
            json={
                "token": reset_token,
                "newPassword": new_password,
                "confirmPassword": new_password
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        # Verify can login with new password
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "username": "testuser",
                "password": new_password
            }
        )
        assert login_response.status_code == 200
    
    def test_reset_password_invalid_token(self, client: TestClient):
        """Test reset password with invalid token"""
        response = client.post(
            "/api/v1/auth/reset-password",
            json={
                "token": "invalid_token",
                "newPassword": "NewPassword123",
                "confirmPassword": "NewPassword123"
            }
        )
        
        assert response.status_code == 400
        assert "Invalid or expired token" in response.json()["detail"]
    
    def test_validate_reset_token_valid(
        self, client: TestClient, test_user: dict, session: Session
    ):
        """Test validate reset token with valid token"""
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
        
        # Validate token
        response = client.get(
            f"/api/v1/auth/validate-reset-token?token={reset_token}"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"] is True
    
    def test_validate_reset_token_invalid(self, client: TestClient):
        """Test validate reset token with invalid token"""
        response = client.get(
            "/api/v1/auth/validate-reset-token?token=invalid_token"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])