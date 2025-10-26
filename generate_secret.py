#!/usr/bin/env python3
"""
Generate a secure secret key for UptimeRobot authentication
"""
import secrets

def generate_secret_key():
    """Generate a secure random secret key"""
    secret = secrets.token_urlsafe(32)
    return secret

def main():
    print("🔐 UptimeRobot Secret Key Generator")
    print("=" * 40)
    
    secret = generate_secret_key()
    
    print(f"Your secure secret key: {secret}")
    print()
    print("📋 Usage:")
    print("1. Copy this key to your .env file:")
    print(f"   UPTIMEROBOT_SECRET={secret}")
    print()
    print("2. Use this URL in UptimeRobot:")
    print(f"   https://your-app-domain.com/cron/{secret}")
    print()
    print("3. Status check URL:")
    print(f"   https://your-app-domain.com/cron-status/{secret}")
    print()
    print("⚠️  Keep this secret key safe and don't share it publicly!")

if __name__ == '__main__':
    main()
