"""
FILE: src/email/templates.py
HTML email templates
"""
from datetime import datetime
from src.email.config import email_settings


def get_welcome_email_template(
    firstname: str,
    lastname: str,
    username: str,
    temp_password: str,
    lga_name: str = "your assigned LGA"
) -> tuple[str, str]:
    """
    Welcome email template for new officer registration
    
    Returns:
        (subject, html_body)
    """
    subject = "Welcome to Oyo State Agricultural Data Management System"
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Welcome to Oyo Agro System</title>
    </head>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background-color: #2e7d32; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0;">
            <h1 style="margin: 0;">Welcome to Oyo Agro System</h1>
        </div>
        
        <div style="background-color: #f9f9f9; padding: 30px; border-radius: 0 0 5px 5px;">
            <h2 style="color: #2e7d32;">Account Created Successfully!</h2>
            
            <p>Dear <strong>{firstname} {lastname}</strong>,</p>
            
            <p>Your account has been successfully created in the Oyo State Agricultural Data Management System. You have been assigned to <strong>{lga_name}</strong>.</p>
            
            <div style="background-color: white; padding: 20px; border-left: 4px solid #2e7d32; margin: 20px 0;">
                <h3 style="margin-top: 0; color: #2e7d32;">Your Login Credentials:</h3>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 8px 0;"><strong>Username:</strong></td>
                        <td style="padding: 8px 0; font-family: monospace; background-color: #f5f5f5; padding: 4px 8px;">{username}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0;"><strong>Temporary Password:</strong></td>
                        <td style="padding: 8px 0; font-family: monospace; background-color: #f5f5f5; padding: 4px 8px;">{temp_password}</td>
                    </tr>
                </table>
            </div>
            
            <div style="margin: 30px 0; text-align: center;">
                <a href="{email_settings.LOGIN_URL}" 
                   style="background-color: #2e7d32; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                    Login to Your Account
                </a>
            </div>
            
            <div style="background-color: #fff3cd; border: 1px solid #ffc107; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <p style="margin: 0; color: #856404;">
                    <strong>⚠️ Important Security Steps:</strong>
                </p>
                <ol style="margin: 10px 0 0 0; padding-left: 20px; color: #856404;">
                    <li>Log in using the credentials above</li>
                    <li>Change your password immediately after first login</li>
                    <li>Keep your login credentials secure and do not share them</li>
                </ol>
            </div>
            <!-- 
            <h3 style="color: #2e7d32;">What's Next?</h3>
            <ul style="color: #666;">
                <li>Access the dashboard to view system overview</li>
                <li>Register farmers in your assigned LGA</li>
                <li>Record farm and agricultural data</li>
                <li>Generate reports on agricultural activities</li>
            </ul>
            -->
            <p>If you have any questions or need assistance, please contact your system administrator.</p>
            
            <p style="margin-top: 30px;">Best regards,<br>
            <strong>Oyo State Ministry of Agriculture and Rural Development</strong></p>
        </div>
        
        <div style="text-align: center; margin-top: 20px; color: #666; font-size: 12px;">
            <p>This is an automated message. Please do not reply to this email.</p>
            <p>&copy; {datetime.now().year} Oyo State Agricultural Data Management System. All rights reserved.</p>
        </div>
    </body>
    </html>
    """
    
    return (subject, html)


def get_password_reset_email_template(
    firstname: str,
    username: str,
    reset_token: str,
    expires_hours: int = 24
) -> tuple[str, str]:
    """
    Password reset email template
    
    Returns:
        (subject, html_body)
    """
    subject = "Password Reset Request - Oyo Agro System"
    reset_url = f"{email_settings.PASSWORD_RESET_URL}?token={reset_token}"
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Password Reset Request</title>
    </head>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background-color: #d32f2f; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0;">
            <h1 style="margin: 0;">Password Reset Request</h1>
        </div>
        
        <div style="background-color: #f9f9f9; padding: 30px; border-radius: 0 0 5px 5px;">
            <h2 style="color: #d32f2f;">Reset Your Password</h2>
            
            <p>Dear <strong>{firstname}</strong>,</p>
            
            <p>We received a request to reset the password for your account (<strong>{username}</strong>) in the Oyo Agro System.</p>
            
            <p>If you made this request, click the button below to reset your password:</p>
            
            <div style="margin: 30px 0; text-align: center;">
                <a href="{reset_url}" 
                   style="background-color: #d32f2f; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                    Reset Password
                </a>
            </div>
            
            <div style="background-color: white; padding: 15px; border: 1px solid #ddd; border-radius: 5px; margin: 20px 0;">
                <p style="margin: 0; font-size: 14px; color: #666;">
                    Or copy and paste this link into your browser:
                </p>
                <p style="word-break: break-all; color: #2e7d32; margin: 10px 0; font-size: 13px;">
                    {reset_url}
                </p>
            </div>
            
            <div style="background-color: #ffebee; border-left: 4px solid #d32f2f; padding: 15px; margin: 20px 0;">
                <p style="margin: 0; color: #c62828;">
                    <strong>⏰ Important:</strong> This password reset link will expire in {expires_hours} hours.
                </p>
            </div>
            
            <div style="background-color: #fff3cd; border: 1px solid #ffc107; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <p style="margin: 0; color: #856404;">
                    <strong>⚠️ Security Alert:</strong> If you did not request a password reset, please ignore this email and ensure your account is secure. Your password will not be changed.
                </p>
            </div>
            
            <h3 style="color: #2e7d32;">Password Requirements:</h3>
            <ul style="color: #666;">
                <li>At least 8 characters long</li>
                <li>Include uppercase and lowercase letters</li>
                <li>Include at least one number</li>
                <li>Use a unique password not used elsewhere</li>
            </ul>
            
            <p>If you need additional assistance, please contact your system administrator.</p>
            
            <p style="margin-top: 30px;">Best regards,<br>
            <strong>Oyo State Ministry of Agriculture and Rural Development</strong></p>
        </div>
        
        <div style="text-align: center; margin-top: 20px; color: #666; font-size: 12px;">
            <p>This is an automated message. Please do not reply to this email.</p>
            <p>&copy; {datetime.now().year} Oyo State Agricultural Data Management System. All rights reserved.</p>
        </div>
    </body>
    </html>
    """
    
    return (subject, html)


def get_password_changed_email_template(
    firstname: str,
    username: str,
    changed_at: datetime
) -> tuple[str, str]:
    """
    Password changed confirmation email template
    
    Returns:
        (subject, html_body)
    """
    subject = "Password Changed Successfully - Oyo Agro System"
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Password Changed Successfully</title>
    </head>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background-color: #2e7d32; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0;">
            <h1 style="margin: 0;">Password Changed Successfully</h1>
        </div>
        
        <div style="background-color: #f9f9f9; padding: 30px; border-radius: 0 0 5px 5px;">
            <h2 style="color: #2e7d32;">Your Password Has Been Updated</h2>
            
            <p>Dear <strong>{firstname}</strong>,</p>
            
            <p>This is to confirm that your password for account <strong>{username}</strong> was successfully changed.</p>
            
            <div style="background-color: #e8f5e9; border-left: 4px solid #2e7d32; padding: 15px; margin: 20px 0;">
                <p style="margin: 0;">
                    ✓ Your password was changed on: <strong>{changed_at.strftime("%B %d, %Y at %I:%M %p")}</strong>
                </p>
            </div>
            
            <div style="background-color: #fff3cd; border: 1px solid #ffc107; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <p style="margin: 0; color: #856404;">
                    <strong>⚠️ Security Alert:</strong> If you did not make this change, please contact your system administrator immediately as your account may be compromised.
                </p>
            </div>
            
            <p>You can now log in to the system using your new password.</p>
            
            <div style="margin: 30px 0; text-align: center;">
                <a href="{email_settings.LOGIN_URL}" 
                   style="background-color: #2e7d32; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                    Login to Your Account
                </a>
            </div>
            
            <p style="margin-top: 30px;">Best regards,<br>
            <strong>Oyo State Ministry of Agriculture and Rural Development</strong></p>
        </div>
        
        <div style="text-align: center; margin-top: 20px; color: #666; font-size: 12px;">
            <p>This is an automated message. Please do not reply to this email.</p>
            <p>&copy; {datetime.now().year} Oyo State Agricultural Data Management System. All rights reserved.</p>
        </div>
    </body>
    </html>
    """
    
    return (subject, html)


def get_account_locked_email_template(
    firstname: str,
    username: str,
    locked_at: datetime,
    reason: str
) -> tuple[str, str]:
    """
    Account locked notification email template
    
    Returns:
        (subject, html_body)
    """
    subject = "Account Locked - Oyo Agro System"
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Account Locked</title>
    </head>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background-color: #d32f2f; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0;">
            <h1 style="margin: 0;">⚠️ Account Locked</h1>
        </div>
        
        <div style="background-color: #f9f9f9; padding: 30px; border-radius: 0 0 5px 5px;">
            <h2 style="color: #d32f2f;">Your Account Has Been Locked</h2>
            
            <p>Dear <strong>{firstname}</strong>,</p>
            
            <p>Your account (<strong>{username}</strong>) has been temporarily locked for security reasons.</p>
            
            <div style="background-color: #ffebee; border-left: 4px solid #d32f2f; padding: 15px; margin: 20px 0;">
                <p style="margin: 0; color: #c62828;">
                    <strong>Reason:</strong> {reason}
                </p>
                <p style="margin: 10px 0 0 0; color: #c62828;">
                    <strong>Locked at:</strong> {locked_at.strftime("%B %d, %Y at %I:%M %p")}
                </p>
            </div>
            
            <p>This is a security measure to protect your account from unauthorized access.</p>
            
            <h3 style="color: #2e7d32;">What to do next:</h3>
            <ol style="color: #666;">
                <li>Contact your system administrator to unlock your account</li>
                <li>Once unlocked, you may need to reset your password</li>
                <li>Ensure you're using the correct login credentials</li>
            </ol>
            
            <div style="background-color: #fff3cd; border: 1px solid #ffc107; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <p style="margin: 0; color: #856404;">
                    <strong>💡 Tip:</strong> Make sure Caps Lock is off and you're typing your password correctly. If you've forgotten your password, you can request a password reset after your account is unlocked.
                </p>
            </div>
            
            <p>If you believe this is an error or need immediate assistance, please contact your system administrator.</p>
            
            <p style="margin-top: 30px;">Best regards,<br>
            <strong>Oyo State Ministry of Agriculture and Rural Development</strong></p>
        </div>
        
        <div style="text-align: center; margin-top: 20px; color: #666; font-size: 12px;">
            <p>This is an automated message. Please do not reply to this email.</p>
            <p>&copy; {datetime.now().year} Oyo State Agricultural Data Management System. All rights reserved.</p>
        </div>
    </body>
    </html>
    """
    
    return (subject, html)