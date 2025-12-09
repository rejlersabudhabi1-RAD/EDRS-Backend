#!/usr/bin/env python3
"""
Railway Environment Variables Generator
Generates secure keys and provides Railway setup instructions
"""

import secrets
import string
import os
from datetime import datetime

def generate_django_secret_key():
    """Generate Django SECRET_KEY"""
    chars = string.ascii_letters + string.digits + '!@#$%^&*(-_=+)'
    return ''.join(secrets.choice(chars) for _ in range(50))

def generate_jwt_secret():
    """Generate JWT secret key"""
    chars = string.ascii_letters + string.digits + '-_'
    return ''.join(secrets.choice(chars) for _ in range(64))

def main():
    print("🚀 Railway Environment Variables Generator")
    print("=" * 55)
    print()
    
    # Generate secure keys
    django_secret = generate_django_secret_key()
    jwt_secret = generate_jwt_secret()
    
    print("🔑 SECURE KEYS GENERATED:")
    print("-" * 30)
    print(f"SECRET_KEY={django_secret}")
    print(f"JWT_SECRET_KEY={jwt_secret}")
    print()
    
    print("📋 COPY THESE TO RAILWAY DASHBOARD:")
    print("=" * 40)
    print()
    
    # Required variables
    required_vars = {
        "SECRET_KEY": django_secret,
        "DEBUG": "False",
        "DJANGO_SETTINGS_MODULE": "rejlers_api.settings", 
        "ALLOWED_HOSTS": "your-railway-domain.up.railway.app,edrs.rejlers.ae",
        "FRONTEND_URL": "https://edrs-frontend-rejlers.vercel.app",
        "CORS_ALLOWED_ORIGINS": "https://edrs-frontend-rejlers.vercel.app,https://edrs.rejlers.ae",
        "JWT_SECRET_KEY": jwt_secret,
        "ACCESS_TOKEN_LIFETIME_MINUTES": "60",
        "REFRESH_TOKEN_LIFETIME_DAYS": "7",
    }
    
    print("🔧 REQUIRED VARIABLES (Set these first):")
    print("-" * 45)
    for key, value in required_vars.items():
        print(f"{key}={value}")
    
    print()
    print("📧 EMAIL VARIABLES (Recommended):")
    print("-" * 35)
    email_vars = {
        "EMAIL_BACKEND": "django.core.mail.backends.smtp.EmailBackend",
        "EMAIL_HOST": "smtp.gmail.com",
        "EMAIL_PORT": "587", 
        "EMAIL_USE_TLS": "True",
        "EMAIL_HOST_USER": "rejlersabudhabi1@gmail.com",
        "EMAIL_HOST_PASSWORD": "your-gmail-app-password",
        "DEFAULT_FROM_EMAIL": "noreply@rejlers.ae"
    }
    
    for key, value in email_vars.items():
        print(f"{key}={value}")
    
    print()
    print("🤖 AI SERVICES (Optional):")
    print("-" * 25)
    ai_vars = {
        "OPENAI_API_KEY": "sk-your-openai-api-key-here",
        "OPENAI_MODEL": "gpt-4o-mini",
        "OPENAI_MAX_TOKENS": "4000",
        "OPENAI_TEMPERATURE": "0.3"
    }
    
    for key, value in ai_vars.items():
        print(f"{key}={value}")
    
    print()
    print("🔒 SECURITY VARIABLES (Production):")
    print("-" * 35)
    security_vars = {
        "SECURE_SSL_REDIRECT": "True",
        "SECURE_PROXY_SSL_HEADER": "HTTP_X_FORWARDED_PROTO,https",
        "SESSION_COOKIE_SECURE": "True",
        "CSRF_COOKIE_SECURE": "True",
        "LOG_LEVEL": "INFO"
    }
    
    for key, value in security_vars.items():
        print(f"{key}={value}")
    
    print()
    print("📝 RAILWAY SETUP STEPS:")
    print("=" * 25)
    print("1. Go to: https://railway.app/dashboard")
    print("2. Select your EDRS project")
    print("3. Click on your backend service")
    print("4. Go to 'Variables' tab")
    print("5. Click 'New Variable' for each variable above")
    print("6. Copy/paste Name and Value exactly")
    print("7. Click 'Deploy' after adding all variables")
    print()
    
    print("⚠️  IMPORTANT REMINDERS:")
    print("-" * 20)
    print("• Change 'your-railway-domain.up.railway.app' to your actual Railway URL")
    print("• Update 'your-gmail-app-password' with real Gmail app password")
    print("• Add your OpenAI API key if using AI features")
    print("• DATABASE_URL is automatically provided by Railway PostgreSQL")
    print("• Never share or commit these secret keys!")
    print()
    
    print("✅ Your database is already migrated and ready!")
    print("🚀 Deploy and test your API endpoints!")
    
    # Save to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"railway_env_vars_{timestamp}.txt"
    
    with open(filename, 'w') as f:
        f.write("# Railway Environment Variables\n")
        f.write(f"# Generated: {datetime.now()}\n\n")
        
        f.write("# REQUIRED VARIABLES\n")
        for key, value in required_vars.items():
            f.write(f"{key}={value}\n")
        
        f.write("\n# EMAIL VARIABLES\n")
        for key, value in email_vars.items():
            f.write(f"{key}={value}\n")
            
        f.write("\n# AI SERVICES (OPTIONAL)\n")
        for key, value in ai_vars.items():
            f.write(f"{key}={value}\n")
            
        f.write("\n# SECURITY VARIABLES\n")
        for key, value in security_vars.items():
            f.write(f"{key}={value}\n")
    
    print(f"💾 Variables saved to: {filename}")

if __name__ == "__main__":
    main()