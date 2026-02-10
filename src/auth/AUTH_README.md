# Authentication System Documentation

## Overview
The OyoAgro API authentication system provides secure user authentication, password management, and user registration capabilities. It maintains compatibility with the legacy C# .NET system while implementing modern security best practices.

## Table of Contents
1. [Architecture](#architecture)
2. [Endpoints](#endpoints)
3. [Security Features](#security-features)
4. [Database Schema](#database-schema)
5. [Implementation Details](#implementation-details)
6. [Testing](#testing)
7. [Migration from C#](#migration-from-c)

## Architecture

### Components
```
src/auth/
├── router.py          # API endpoints
src/core/
├── security.py        # Encryption & JWT utilities
├── config.py          # Configuration settings
src/shared/
├── models.py          # Database models
├── schemas.py         # Request/response schemas
```

### Flow Diagram
```
User Request → FastAPI Router → Security Layer → Database
                    ↓                  ↓
              Validation        Encryption/JWT
                    ↓                  ↓
              Response ← Session ← Query/Update
```

## Endpoints

### 1. Login
**POST** `/api/v1/auth/login`

Authenticates user and returns JWT token.

**Request:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response (Success):**
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "user": {
      "userid": 1,
      "username": "officer1",
      "email": "officer1@example.com",
      "firstname": "John",
      "lastname": "Doe",
      "roleid": 2
    }
  },
  "tag": 1
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid credentials
- `403 Forbidden`: Account locked or disabled

**Features:**
- Account locking after 5 failed attempts
- Failed attempt tracking
- Login count tracking
- Last login date tracking
- JWT token generation

### 2. Logout
**GET** `/api/v1/auth/logout`

Logs out user and invalidates JWT token.

**Headers:**
```
Authorization: Bearer {token}
```

**Response:**
```json
{
  "success": true,
  "message": "Logged out successfully",
  "tag": 1
}
```

### 3. Forgot Password
**POST** `/api/v1/auth/forgot-password`

Initiates password reset process.

**Request:**
```json
{
  "email": "user@example.com"
}
```

**Response:**
```json
{
  "success": true,
  "message": "If email exists, reset link has been sent",
  "tag": 1
}
```

**Note:** Always returns success (security best practice)

### 4. Reset Password
**POST** `/api/v1/auth/reset-password`

Resets user password using token.

**Request:**
```json
{
  "token": "reset_token_string",
  "newPassword": "NewSecure123",
  "confirmPassword": "NewSecure123"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Password reset successfully",
  "tag": 1
}
```

**Features:**
- Token validation (not expired, not used)
- Password confirmation matching
- Account unlocking
- Failed attempts reset

### 5. Validate Reset Token
**GET** `/api/v1/auth/validate-reset-token?token={token}`

Validates password reset token.

**Response:**
```json
{
  "success": true,
  "message": "Token is valid",
  "data": true,
  "tag": 1
}
```

### 6. Register User (Admin)
**POST** `/api/v1/auth/register`

Creates new extension officer account.

**Headers:**
```
Authorization: Bearer {admin_token}
```

**Request:**
```json
{
  "firstname": "John",
  "lastname": "Doe",
  "middlename": "Smith",
  "gender": "Male",
  "emailAddress": "john.doe@example.com",
  "phonenumber": "08012345678",
  "lgaid": 1,
  "regionid": 1,
  "streetaddress": "123 Main Street",
  "town": "Ibadan",
  "postalcode": "12345",
  "latitude": 7.3775,
  "longitude": 3.9470
}
```

**Response:**
```json
{
  "success": true,
  "message": "User registered successfully",
  "data": {
    "userid": 10,
    "username": "john.doe",
    "email": "john.doe@example.com",
    "temp_password": "12345" // Development only
  },
  "tag": 1
}
```

### 7. Get Officers List
**GET** `/api/v1/auth/officers`

Retrieves list of all registered officers.

**Headers:**
```
Authorization: Bearer {token}
```

**Response:**
```json
{
  "success": true,
  "message": "Officers retrieved successfully",
  "data": [
    {
      "userid": 1,
      "username": "officer1",
      "email": "officer1@example.com",
      "status": 1,
      "isactive": true,
      "firstname": "John",
      "lastname": "Doe",
      "phonenumber": "08012345678",
      "lgaid": 1,
      "logincount": 10,
      "lastlogindate": "2025-01-20"
    }
  ],
  "tag": 1,
  "total": 1
}
```

### 8. Get Officer Details
**GET** `/api/v1/auth/officers/{user_id}`

Retrieves detailed information about specific officer.

**Headers:**
```
Authorization: Bearer {token}
```

**Response:**
```json
{
  "success": true,
  "message": "Officer retrieved successfully",
  "data": {
    "userid": 1,
    "username": "officer1",
    "email": "officer1@example.com",
    "status": 1,
    "isactive": true,
    "firstname": "John",
    "lastname": "Doe",
    "middlename": "Smith",
    "gender": "Male",
    "phonenumber": "08012345678",
    "designation": "Extension Officer",
    "lgaid": 1,
    "regionid": 1,
    "streetaddress": "123 Main Street",
    "town": "Ibadan",
    "postalcode": "12345",
    "latitude": 7.3775,
    "longitude": 3.9470,
    "logincount": 10,
    "lastlogindate": "2025-01-20",
    "createdat": "2025-01-01T00:00:00"
  },
  "tag": 1
}
```

## Security Features

### 1. Password Encryption
**Legacy Compatibility Mode:**
- Uses simple XOR encryption with salt
- Maintains compatibility with C# .NET system
- Allows migration without password resets

```python
def simple_encrypt(plain_text: str, key: str) -> str:
    """XOR encryption matching C# implementation"""
    result = []
    for i, char in enumerate(plain_text):
        key_char = key[i % len(key)]
        encrypted_char = chr(ord(char) ^ ord(key_char))
        result.append(encrypted_char)
    encrypted = ''.join(result)
    return base64.b64encode(encrypted.encode()).decode()
```

### 2. JWT Tokens
**Configuration:**
```python
JWT_SECRET_KEY: str  # Secret key for signing
JWT_ALGORITHM: str = "HS256"  # HMAC SHA-256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days
JWT_ISSUER: str = "oyoagro-api"
JWT_AUDIENCE: str = "oyoagro-frontend"
```

**Token Payload:**
```json
{
  "UserId": 1,
  "UserName": "officer1",
  "UserStatus": 1,
  "Email": "officer1@example.com",
  "exp": 1234567890,
  "iss": "oyoagro-api",
  "aud": "oyoagro-frontend",
  "iat": 1234567890
}
```

### 3. Account Security
- **Failed Login Tracking**: Counts failed attempts
- **Account Locking**: Automatic after 5 failed attempts
- **Token Invalidation**: On logout and password reset
- **Password Reset Tokens**: Time-limited, single-use

### 4. Input Validation
All inputs validated using Pydantic schemas:
- Email format validation
- Password strength requirements (min 6 characters)
- Phone number format (11 digits)
- Required fields enforcement

## Database Schema

### useraccount Table
```sql
userid              INTEGER PRIMARY KEY
username            VARCHAR UNIQUE
email               VARCHAR UNIQUE
passwordhash        TEXT
salt                TEXT
status              INTEGER  -- 1=active, 0=inactive
isactive            BOOLEAN
islocked            BOOLEAN
apitoken            TEXT
logincount          INTEGER
lastlogindate       DATE
failedloginattempt  INTEGER
passwordresettoken  TEXT
passwordresettokenexpires TIMESTAMP
createdat           TIMESTAMP
updatedat           TIMESTAMP
lgaid               INTEGER FK
```

### userprofile Table
```sql
userprofileid   INTEGER PRIMARY KEY
userid          INTEGER FK -> useraccount
firstname       VARCHAR
middlename      VARCHAR
lastname        VARCHAR
gender          VARCHAR
email           VARCHAR
phonenumber     VARCHAR
designation     VARCHAR
roleid          INTEGER
lgaid           INTEGER
createdat       TIMESTAMP
updatedat       TIMESTAMP
```

### passwordresettokens Table
```sql
id          INTEGER PRIMARY KEY
userid      INTEGER FK -> useraccount
token       VARCHAR
expiresat   TIMESTAMP
isused      BOOLEAN
usedat      TIMESTAMP
ipaddress   VARCHAR
useragent   VARCHAR
createdat   TIMESTAMP
```

## Implementation Details

### Dependency Injection
```python
from fastapi import Depends
from sqlmodel import Session
from src.core.database import get_session

async def endpoint(session: Session = Depends(get_session)):
    # Session automatically managed
    pass
```

### Error Handling
```python
try:
    # Operation
    pass
except HTTPException:
    raise  # Re-raise HTTP exceptions
except Exception as e:
    logger.error(f"Error: {str(e)}")
    raise HTTPException(
        status_code=500,
        detail="Internal server error"
    )
```

### Logging
```python
import logging

logger = logging.getLogger(__name__)

logger.info("Successful login: username")
logger.warning("Login attempt for locked account")
logger.error("Login error: error_message")
```

## Testing

### Test Coverage
- ✅ 100% endpoint coverage
- ✅ All success scenarios
- ✅ All failure scenarios
- ✅ Edge cases
- ✅ Security validations

### Running Tests
```bash
# All auth tests
pytest tests/test_auth.py -v

# Specific test
pytest tests/test_auth.py::TestLogin::test_login_success

# With coverage
pytest tests/test_auth.py --cov=src.auth
```

### Test Fixtures
```python
@pytest.fixture
def test_user(session):
    """Create test user"""
    # ... setup
    return user

@pytest.fixture
def auth_token(client, test_user):
    """Get auth token"""
    # ... login and return token
    return token
```

## Migration from C#

### Password Compatibility
The system maintains 100% password compatibility with the C# system:

```python
# C# code (original)
private string Encrypt(string plainText, string key)
{
    StringBuilder result = new StringBuilder();
    for (int i = 0; i < plainText.Length; i++)
    {
        result.Append((char)(plainText[i] ^ key[i % key.Length]));
    }
    return Convert.ToBase64String(Encoding.UTF8.GetBytes(result.ToString()));
}

# Python equivalent
def simple_encrypt(plain_text: str, key: str) -> str:
    result = []
    for i, char in enumerate(plain_text):
        key_char = key[i % len(key)]
        encrypted_char = chr(ord(char) ^ ord(key_char))
        result.append(encrypted_char)
    encrypted = ''.join(result)
    return base64.b64encode(encrypted.encode()).decode()
```

### Database Migration
1. **No schema changes required** - Uses existing database
2. **Password migration** - Passwords work without reset
3. **Data migration** - All existing data accessible

### API Compatibility
Maintains C# response format:
```json
{
  "success": bool,
  "message": string,
  "Data": any,
  "tag": int
}
```

# Auth Router Email Integration - Complete ✅

## 📧 Email Integration Summary

Updated `src/auth/router.py` with complete email service integration for all authentication workflows.

---

## 🎯 Email Triggers (4 Scenarios)

### 1. **Welcome Email** (New Officer Registration)
**Trigger:** Admin creates new officer account via `/auth/register`

**When:**
- After successful user account creation
- After all database records created (user, profile, address, user-region)

**Contains:**
- Username
- Temporary password
- Login link
- Security instructions
- LGA assignment info

**Code Location:** Line ~285 in `register_user()`
```python
welcome_email_data = WelcomeEmailData(...)
await EmailService.send_welcome_email(welcome_email_data)
```

---

### 2. **Password Reset Email**
**Trigger:** User requests password reset via `/auth/forgot-password`

**When:**
- After reset token generated
- User exists and account is active

**Contains:**
- Reset link with token
- Token expiration time (24 hours)
- Security warnings
- Password requirements

**Code Location:** Line ~175 in `forgot_password()`
```python
reset_email_data = PasswordResetEmailData(...)
await EmailService.send_password_reset_email(reset_email_data)
```

---

### 3. **Password Changed Confirmation Email** (2 sources)

#### Source A: Password Reset Flow
**Trigger:** User completes password reset via `/auth/reset-password`

**When:**
- After password successfully updated via reset token
- Token validated and marked as used

**Code Location:** Line ~235 in `reset_password()`

#### Source B: Manual Password Change
**Trigger:** Logged-in user changes password via `/auth/change-password`

**When:**
- After password successfully changed
- Current password verified

**Code Location:** Line ~430 in `change_password()`

**Contains:**
- Confirmation of password change
- Timestamp of change
- Security alert
- Login link

---

### 4. **Account Locked Notification Email** (2 sources)

#### Source A: Failed Login Attempts
**Trigger:** Account locks after 5 failed login attempts via `/auth/login`

**When:**
- Login fails with 403 status
- "locked" keyword in error message
- Account was just locked by system

**Code Location:** Line ~65 in `login()` (exception handler)

#### Source B: Admin Action
**Trigger:** Admin manually locks account via `/auth/lock-account/{user_id}`

**When:**
- Admin explicitly locks a user account
- Account status updated to locked

**Code Location:** Line ~490 in `lock_account()`

**Contains:**
- Lock reason (failed attempts or admin action)
- Lock timestamp
- Unlock instructions
- Security tips

---

## 📊 Email Flow Diagram

```
┌─────────────────┐
│  Auth Router    │
│   Endpoints     │
└────────┬────────┘
         │
         ├─── /register ────────────────┐
         │                              ▼
         │                    ┌──────────────────┐
         │                    │  Welcome Email   │
         │                    └──────────────────┘
         │
         ├─── /forgot-password ─────────┐
         │                              ▼
         │                    ┌──────────────────┐
         │                    │ Reset Email      │
         │                    └──────────────────┘
         │
         ├─── /reset-password ──────────┐
         │                              ▼
         │                    ┌──────────────────┐
         │                    │ Changed Email    │
         │                    └──────────────────┘
         │
         ├─── /change-password ─────────┘
         │
         ├─── /login (on lock) ─────────┐
         │                              ▼
         ├─── /lock-account ────────────┤
         │                    ┌──────────────────┐
         └────────────────────│  Locked Email    │
                              └──────────────────┘
```

---

## 🔧 Key Changes Made

### 1. **Imports Added**
```python
from src.email.service import EmailService
from src.email.schemas import (
    WelcomeEmailData,
    PasswordResetEmailData,
    PasswordChangedEmailData,
    AccountLockedEmailData
)
```

### 2. **Login Endpoint Enhancement**
- Added try-catch block
- Detects account locking
- Sends lock notification email
- Preserves original error behavior

### 3. **Password Reset Flow**
- Fetches user info before reset
- Sends confirmation email after successful reset
- Logs email sending status

### 4. **User Registration**
- Sends welcome email with credentials
- Includes development mode flag
- Returns email send status in dev mode

### 5. **Password Change Endpoint**
- Sends confirmation email
- Gets user profile for firstname
- Comprehensive logging

### 6. **Admin Lock Account**
- Sends notification to locked user
- Includes lock reason
- Logs admin action

---

## ✅ Error Handling

All email operations include:
```python
email_response = await EmailService.send_email(...)

if not email_response.success:
    logger.error(f"Failed to send email: {email_response.error}")
else:
    logger.info(f"Email sent to: {email}")
```

**Non-blocking:** Email failures don't prevent authentication operations from completing.

---

## 🧪 Testing

### Development Mode
```env
SEND_EMAILS=False
```
- Emails logged but not sent
- Credentials shown in API response
- Useful for testing

### Production Mode
```env
SEND_EMAILS=True
MAIL_SERVER=smtp.gmail.com
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```
- Emails actually sent
- Credentials NOT in API response
- Real SMTP delivery

---

## 📝 Usage Examples

### 1. Register New Officer (sends welcome email)
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "firstname": "John",
    "lastname": "Doe",
    "emailAddress": "john.doe@oyoagro.gov.ng",
    "phonenumber": "08012345678",
    "lgaid": 1,
    "regionid": 1,
    "streetaddress": "123 Main St",
    "town": "Ibadan",
    "postalcode": "200001"
  }'
```

**Response (Development):**
```json
{
  "success": true,
  "message": "User registered successfully. Login credentials sent to email.",
  "data": {
    "userid": 5,
    "username": "john.doe",
    "email": "john.doe@oyoagro.gov.ng",
    "temp_password": "TempPass123",
    "email_sent": true
  }
}
```

### 2. Request Password Reset (sends reset email)
```bash
curl -X POST "http://localhost:8000/api/v1/auth/forgot-password" \
  -H "Content-Type: application/json" \
  -d '{"email": "john.doe@oyoagro.gov.ng"}'
```

**Email Received:**
- Subject: "Password Reset Request - Oyo Agro System"
- Contains reset link with token
- Expires in 24 hours

### 3. Change Password (sends confirmation email)
```bash
curl -X POST "http://localhost:8000/api/v1/auth/change-password" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "current_password": "OldPass123",
    "new_password": "NewPass456"
  }'
```

**Email Received:**
- Subject: "Password Changed Successfully - Oyo Agro System"
- Confirms password change
- Security alert if not user's action

---

## 🔍 Logging

All email operations logged:

```
INFO: Welcome email sent to: john.doe@oyoagro.gov.ng
INFO: Password reset email sent to: user@example.com
ERROR: Failed to send password changed email: SMTP auth failed
INFO: Account locked notification sent to: locked.user@example.com
```

---

## 🛡️ Security Features

1. **Non-blocking emails**
   - Auth operations complete even if email fails
   - Email failures logged but don't prevent login/registration

2. **Development vs Production**
   - Dev: Credentials in response for testing
   - Prod: Credentials only via email

3. **Email validation**
   - All email addresses validated by Pydantic
   - Type-safe email data models

4. **Error isolation**
   - Email errors don't crash endpoints
   - Comprehensive error logging

---

## 📋 Checklist

Installation:
- [ ] Copy `auth_router_final.py` to `src/auth/router.py`
- [ ] Ensure email module installed (`src/email/`)
- [ ] Configure email settings in `.env`
- [ ] Test email configuration

Testing:
- [ ] Test new user registration (welcome email)
- [ ] Test password reset flow (reset email)
- [ ] Test password change (confirmation email)
- [ ] Test account locking (lock notification)
- [ ] Verify emails arrive correctly

Production:
- [ ] Set `SEND_EMAILS=True`
- [ ] Configure production SMTP
- [ ] Test email delivery
- [ ] Monitor email logs

---

## 🎉 Summary

**Updated Endpoints:** 6
- `/auth/login` - Added lock notification
- `/auth/forgot-password` - Added reset email
- `/auth/reset-password` - Added confirmation email
- `/auth/register` - Added welcome email
- `/auth/change-password` - Added confirmation email
- `/auth/lock-account/{user_id}` - Added lock notification

**Email Scenarios:** 4
1. Welcome (new user)
2. Password reset
3. Password changed
4. Account locked



---


## Best Practices

### 1. Security
- ✅ Never log passwords or tokens
- ✅ Use HTTPS in production
- ✅ Rotate JWT secret regularly
- ✅ Implement rate limiting
- ✅ Sanitize all inputs

### 2. Error Messages
- ✅ Generic messages for auth failures
- ✅ Don't reveal if email exists
- ✅ Log detailed errors server-side
- ✅ Return user-friendly messages

### 3. Token Management
- ✅ Store tokens securely (httpOnly cookies)
- ✅ Implement token refresh
- ✅ Clear tokens on logout
- ✅ Validate token on each request

### 4. Database
- ✅ Use indexes on frequently queried fields
- ✅ Implement soft deletes
- ✅ Track audit trail
- ✅ Use transactions for multi-table operations

## Troubleshooting

### Common Issues

**1. Login fails with correct password**
- Check if account is locked (`islocked = true`)
- Check if account is active (`status = 1`)
- Verify salt matches in database

**2. Token invalid after logout**
- Expected behavior - token cleared on logout
- User must login again

**3. Password reset token expired**
- Tokens expire after 24 hours
- Request new reset token

**4. Can't create user - email exists**
- Each email must be unique
- Check for existing users with same email

## Future Enhancements

### Planned Features
- [ ] Email verification
- [ ] Two-factor authentication (2FA)
- [ ] OAuth2 integration
- [ ] Password strength meter
- [ ] Session management
- [ ] Password history
- [ ] Role-based access control (RBAC)
- [ ] API rate limiting

### Security Improvements
- [ ] Bcrypt for new passwords
- [ ] PBKDF2 key derivation
- [ ] Password complexity requirements
- [ ] Suspicious activity detection
- [ ] IP whitelist/blacklist

## Resources

- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [JWT.io](https://jwt.io/)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [Python-JOSE Documentation](https://python-jose.readthedocs.io/)

## Support

For questions or issues:
1. Check this documentation
2. Review test examples
3. Check application logs
4. Contact development team