"""
Test email configuration and demonstrate the issue
"""
import os
import sys
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

from django.conf import settings
from django.core.mail import send_mail
from apps.depts.services.actions.email_action_service import EmailActionService

def test_email_configuration():
    """Test current email configuration"""
    
    print("📧 Testing Email Configuration...")
    print("=" * 50)
    
    # Check current email settings
    print(f"Email Backend: {settings.EMAIL_BACKEND}")
    print(f"Email Host: {settings.EMAIL_HOST}")
    print(f"Email Port: {settings.EMAIL_PORT}")
    print(f"Email Use TLS: {settings.EMAIL_USE_TLS}")
    print(f"Default From Email: {settings.DEFAULT_FROM_EMAIL}")
    print(f"Email Host User: {settings.EMAIL_HOST_USER}")
    print(f"Email Host Password: {'*' * len(settings.EMAIL_HOST_PASSWORD) if settings.EMAIL_HOST_PASSWORD else 'Not set'}")
    
    print("\n" + "=" * 50)
    
    # Test email service
    test_result = EmailActionService.test_email_config()
    print("Email Service Test Result:")
    print(test_result)
    
    print("\n" + "=" * 50)
    
    # Try to send a test email
    try:
        print("Attempting to send test email...")
        result = send_mail(
            subject='Test Email from Emergency System',
            message='This is a test email to check if emails are working.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['test@example.com'],
            fail_silently=False
        )
        print(f"Send mail result: {result}")
        print("✅ Email sent successfully!")
        
    except Exception as e:
        print(f"❌ Email sending failed: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🔍 DIAGNOSIS:")
    
    if settings.EMAIL_BACKEND == 'django.core.mail.backends.console.EmailBackend':
        print("❌ PROBLEM FOUND: Using console backend!")
        print("   Emails are being printed to console instead of being sent.")
        print("   This happens when EMAIL_HOST_USER and EMAIL_HOST_PASSWORD are not configured.")
        print("\n💡 SOLUTION:")
        print("   1. Create a .env file with email credentials:")
        print("      EMAIL_HOST_USER=your-email@example.com")
        print("      EMAIL_HOST_PASSWORD=your-app-password")
        print("      DEFAULT_FROM_EMAIL=Emergency System <your-email@example.com>")
        print("   2. Or configure SMTP settings in Django settings")
        print("   3. For Gmail, use App Passwords instead of your regular password")
    else:
        print("✅ Email backend is configured for actual sending")
        print("   Check your SMTP credentials if emails still don't arrive")

if __name__ == "__main__":
    test_email_configuration()
