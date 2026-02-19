# Live Email Testing Guide

## 🎯 Overview

This guide shows you how to run live email tests that actually send emails via Resend to verify everything works correctly.

---

## 📋 Prerequisites

### 1. Resend Account Setup
```bash
# Already done if you followed setup guide:
1. Sign up at https://resend.com
2. Get API key from dashboard
3. Have API key ready
```

### 2. Environment Configuration

**Update your `.env` file:**
```bash
# Email Configuration
RESEND_API_KEY=re_your_actual_api_key_here
SEND_EMAILS=True
MAIL_FROM=onboarding@resend.dev
MAIL_FROM_NAME=Oyo Agro System

# Test Configuration (optional)
TEST_EMAIL_RECIPIENT=your-email@example.com
```

### 3. Install Dependencies
```bash
pip install pytest pytest-asyncio resend
```

---

## 🚀 Running Live Email Tests

### **Method 1: Run All Live Tests**
```bash
pytest tests/test_email_live.py -v -m live
```

**What happens:**
- Prompts for test email address (if not in .env)
- Sends all 4 email types to your inbox
- Shows Resend email IDs
- Validates all responses

**Expected Output:**
```
tests/test_email_live.py::TestLiveEmailService::test_send_welcome_email_live 
📧 Sending test email to: your-email@example.com
📤 Sending welcome email to your-email@example.com...
✅ Welcome email sent successfully!
   Resend ID: re_abc123...
   Message: Welcome email sent to your-email@example.com
📬 Check your inbox: your-email@example.com
PASSED

tests/test_email_live.py::TestLiveEmailService::test_send_password_reset_email_live 
📤 Sending password reset email to your-email@example.com...
✅ Password reset email sent successfully!
   Resend ID: re_def456...
PASSED

[... continues for all 4 email types ...]

========== 4 passed in 5.2s ==========
```

### **Method 2: Run Individual Email Test**
```bash
# Test welcome email only
pytest tests/test_email_live.py::TestLiveEmailService::test_send_welcome_email_live -v -s

# Test password reset only
pytest tests/test_email_live.py::TestLiveEmailService::test_send_password_reset_email_live -v -s

# Test all in sequence
pytest tests/test_email_live.py::TestLiveEmailService::test_all_email_types_sequence_live -v -s
```

### **Method 3: Run Without Email Prompt**

Set test email in `.env`:
```bash
echo "TEST_EMAIL_RECIPIENT=your-email@example.com" >> .env
```

Then run:
```bash
pytest tests/test_email_live.py -v -m live
```

### **Method 4: Run Validation Tests Only (No Emails Sent)**
```bash
pytest tests/test_email_live.py -v -m "email and not live"
```

**These tests:**
- ✅ Validate schemas
- ✅ Test email format validation
- ❌ Don't send actual emails

---

## 📧 Test Email Types

### **1. Welcome Email**
**Sent when:** New user registration

**Contains:**
- ✅ Username
- ✅ Temporary password
- ✅ Login link
- ✅ LGA assignment
- ✅ Security instructions

**Subject:** "Welcome to Oyo Agro System - Your Account Details"

### **2. Password Reset Email**
**Sent when:** User requests password reset

**Contains:**
- ✅ Reset link with token
- ✅ Expiration time (24 hours)
- ✅ Security warnings
- ✅ Password requirements

**Subject:** "Password Reset Request - Oyo Agro System"

### **3. Password Changed Email**
**Sent when:** Password successfully changed

**Contains:**
- ✅ Change confirmation
- ✅ Timestamp
- ✅ Security alert
- ✅ Login link

**Subject:** "Password Changed Successfully - Oyo Agro System"

### **4. Account Locked Email**
**Sent when:** Account locked (failed attempts or admin action)

**Contains:**
- ✅ Lock reason
- ✅ Lock timestamp
- ✅ Unlock instructions
- ✅ Security tips

**Subject:** "Account Locked - Security Alert"

---

## ✅ Verification Checklist

After running tests, verify:

### **In Your Inbox:**
- [ ] Received 4 emails (if ran all tests)
- [ ] All emails arrived within 1-2 minutes
- [ ] Subject lines are correct
- [ ] Sender is "Oyo Agro System <onboarding@resend.dev>"
- [ ] All links work
- [ ] HTML formatting looks good
- [ ] Mobile responsive

### **In Terminal:**
- [ ] All tests passed (green checkmarks)
- [ ] Resend IDs displayed (format: `re_xxxxx`)
- [ ] No error messages
- [ ] Success messages shown

### **In Resend Dashboard:**
- [ ] Go to https://resend.com/emails
- [ ] See 4 sent emails
- [ ] All show "Delivered" status
- [ ] Click on each to see details
- [ ] No bounces or errors

---

## 🔍 Test Details

### **Test Structure**

```python
# Each test:
1. Creates email data
2. Calls EmailService method
3. Asserts success = True
4. Asserts email_id is not None
5. Asserts no errors
6. Prints confirmation
```

### **Test Coverage**

```
✅ Individual Tests (4):
   - test_send_welcome_email_live
   - test_send_password_reset_email_live
   - test_send_password_changed_email_live
   - test_send_account_locked_email_live

✅ Sequence Test (1):
   - test_all_email_types_sequence_live
   (Sends all 4 in one test)

✅ Validation Tests (3):
   - Schema validation
   - Email format validation
   - All data models
```

---

## 🐛 Troubleshooting

### **Issue 1: "Resend API key not configured"**

**Error:**
```
SKIPPED [1] Resend API key not configured
```

**Solution:**
```bash
# Check .env file
cat .env | grep RESEND_API_KEY

# Should show:
RESEND_API_KEY=re_your_key_here

# If empty, add your key:
echo "RESEND_API_KEY=re_your_actual_key" >> .env
```

### **Issue 2: "Email sending is disabled"**

**Error:**
```
SKIPPED [1] Email sending is disabled
```

**Solution:**
```bash
# Check .env file
cat .env | grep SEND_EMAILS

# Should show:
SEND_EMAILS=True

# If False, change it:
# Edit .env and set SEND_EMAILS=True
```

### **Issue 3: No test email address**

**Error:**
```
SKIPPED [1] No valid test email address provided
```

**Solution:**
```bash
# Option 1: Set in .env
echo "TEST_EMAIL_RECIPIENT=your-email@example.com" >> .env

# Option 2: Enter when prompted
pytest tests/test_email_live.py -v -m live
# (Enter email when asked)
```

### **Issue 4: Tests pass but no email received**

**Checklist:**
1. ✅ Check spam folder
2. ✅ Verify email address is correct
3. ✅ Check Resend dashboard (https://resend.com/emails)
4. ✅ Look for "Delivered" status
5. ✅ Check for bounce messages
6. ✅ Try different email address

### **Issue 5: "Daily sending limit exceeded"**

**Error:**
```
Failed to send email: Daily sending limit exceeded
```

**Cause:** Using `onboarding@resend.dev` (limited to 100/day)

**Solution:**
1. **Wait 24 hours**, OR
2. **Verify your own domain** in Resend
3. Update `MAIL_FROM` in .env to use your domain

### **Issue 6: ImportError or ModuleNotFoundError**

**Error:**
```
ImportError: cannot import name 'EmailService'
```

**Solution:**
```bash
# Ensure you're in the project root
cd /path/to/oyoagro-api

# Install dependencies
pip install -r requirements.txt

# Run tests again
pytest tests/test_email_live.py -v -m live
```

---

## 📊 Example Test Run

### **Complete Output:**
```bash
$ pytest tests/test_email_live.py -v -m live

============================================================
test session starts
============================================================
platform darwin -- Python 3.11.0
plugins: asyncio-0.21.0

tests/test_email_live.py::TestLiveEmailService::test_send_welcome_email_live 
📧 Sending test email to: john.doe@example.com
📤 Sending welcome email to john.doe@example.com...
✅ Welcome email sent successfully!
   Resend ID: re_abc123def456
   Message: Welcome email sent to john.doe@example.com
📬 Check your inbox: john.doe@example.com
PASSED                                                  [25%]

tests/test_email_live.py::TestLiveEmailService::test_send_password_reset_email_live 
📧 Sending test email to: john.doe@example.com
📤 Sending password reset email to john.doe@example.com...
✅ Password reset email sent successfully!
   Resend ID: re_ghi789jkl012
   Reset Token: live_test_token_123abc456def
📬 Check your inbox: john.doe@example.com
PASSED                                                  [50%]

tests/test_email_live.py::TestLiveEmailService::test_send_password_changed_email_live 
📧 Sending test email to: john.doe@example.com
📤 Sending password changed email to john.doe@example.com...
✅ Password changed email sent successfully!
   Resend ID: re_mno345pqr678
📬 Check your inbox: john.doe@example.com
PASSED                                                  [75%]

tests/test_email_live.py::TestLiveEmailService::test_send_account_locked_email_live 
📧 Sending test email to: john.doe@example.com
📤 Sending account locked email to john.doe@example.com...
✅ Account locked email sent successfully!
   Resend ID: re_stu901vwx234
📬 Check your inbox: john.doe@example.com
PASSED                                                 [100%]

============================================================
4 passed in 3.45s
============================================================
```

---

## 🎯 Quick Start

**1-Minute Setup:**
```bash
# 1. Set API key and enable sending
cat >> .env << EOF
RESEND_API_KEY=re_your_key_here
SEND_EMAILS=True
TEST_EMAIL_RECIPIENT=your-email@example.com
EOF

# 2. Run live tests
pytest tests/test_email_live.py -v -m live

# 3. Check your inbox!
```

---

## 📝 Test Commands Reference

```bash
# Run ALL live tests
pytest tests/test_email_live.py -v -m live

# Run validation tests only (no emails sent)
pytest tests/test_email_live.py -v -m "email and not live"

# Run specific test
pytest tests/test_email_live.py::TestLiveEmailService::test_send_welcome_email_live -v -s

# Run with verbose output
pytest tests/test_email_live.py -v -s -m live

# Run and show print statements
pytest tests/test_email_live.py -v -s -m live

# Run with coverage
pytest tests/test_email_live.py --cov=src.email -m live

# Run and stop on first failure
pytest tests/test_email_live.py -v -x -m live
```

---

## ✅ Success Criteria

Tests are successful when:

1. ✅ All tests show `PASSED` status
2. ✅ Each test displays a Resend ID
3. ✅ No error messages in terminal
4. ✅ All 4 emails received in inbox
5. ✅ Emails look professional and correct
6. ✅ All links work
7. ✅ Resend dashboard shows "Delivered"

---

## 🎉 After Testing

Once tests pass:

1. ✅ **Emails work!** - Your Resend integration is complete
2. ✅ **Production ready** - Deploy to Render with confidence
3. ✅ **Monitor usage** - Check Resend dashboard for stats
4. ✅ **Set up domain** - (Optional) Add custom domain for better deliverability

---

## 📞 Support

**If issues persist:**
1. Check Resend dashboard for delivery status
2. Review Resend logs for error details
3. Verify API key is correct
4. Test with different email address
5. Check Resend status page: https://status.resend.com

---

**Happy Testing! 📧**