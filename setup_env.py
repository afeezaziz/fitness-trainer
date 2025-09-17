#!/usr/bin/env python3
"""
Script to help set up the .env file with proper secret key generation
"""
import secrets
import os

def generate_secret_key():
    """Generate a secure secret key for Flask"""
    return secrets.token_hex(32)

def create_env_file():
    """Create a .env file with placeholder values"""

    secret_key = generate_secret_key()

    env_content = f"""# Google OAuth Configuration
# Get these from Google Cloud Console: https://console.cloud.google.com/
GOOGLE_CLIENT_ID=your-google-client-id-here
GOOGLE_CLIENT_SECRET=your-google-client-secret-here

# Flask Configuration
SECRET_KEY={secret_key}
FLASK_ENV=development

# Application Configuration
# Add any additional environment variables here
"""

    with open('.env', 'w') as f:
        f.write(env_content)

    print("✅ Created .env file with secure secret key")
    print(f"🔑 Generated SECRET_KEY: {secret_key}")
    print("\n📋 Next steps:")
    print("1. Follow the setup guide in GOOGLE_OAUTH_SETUP.md")
    print("2. Replace the placeholder values in .env with your Google OAuth credentials")
    print("3. Run the app with: uv run python run.py")

if __name__ == "__main__":
    if os.path.exists('.env'):
        print("⚠️  .env file already exists. Overwrite? (y/N)")
        response = input().lower()
        if response != 'y':
            print("Setup cancelled.")
            exit()

    create_env_file()