#!/usr/bin/env python3
"""Setup script to create .env file with Deriv API token"""

import os

def setup_env_file():
    """Create or update .env file with Deriv API token"""
    print("🔧 Deriv API Token Setup")
    print("=" * 30)

    # Check if .env file exists
    env_file = ".env"

    # Get existing content if file exists
    existing_content = ""
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            existing_content = f.read()
        print("📄 Found existing .env file")

    # Get API token from user
    print("\n🔑 Please enter your Deriv API token:")
    print("   Get it from: https://app.deriv.com/account/api-token")
    print("   Make sure it has 'payments', 'trading_information', and 'read' scopes")
    print()

    api_token = input("Enter your API token: ").strip()

    if not api_token:
        print("❌ No token provided. Exiting.")
        return False

    if api_token == "your_deriv_api_token_here":
        print("⚠️  Please use your real API token, not the placeholder!")
        return False

    # Create new .env content
    new_content = f"""# Deriv API Configuration
# Get your API token from: https://app.deriv.com/account/api-token
DERIV_API_TOKEN={api_token}

# Optional: Set to 'demo' for demo trading, 'real' for real money trading
# ACCOUNT_TYPE=demo
"""

    # Write to .env file
    with open(env_file, 'w') as f:
        f.write(new_content)

    print("✅ .env file updated successfully!")
    print(f"📄 File location: {os.path.abspath(env_file)}")
    print("🔐 Your API token has been saved securely")

    # Test the token format
    if len(api_token) < 20:
        print("⚠️  Warning: API token seems too short. Please verify it's correct.")

    return True

def main():
    """Main setup function"""
    print("🚀 Setting up Deriv Trading Bot Environment")
    print("=" * 45)

    success = setup_env_file()

    if success:
        print("\n🎉 Setup completed successfully!")
        print("💡 Next steps:")
        print("   1. Test your connection: python test_deriv_connection.py")
        print("   2. Start backend: ./start_backend.sh")
        print("   3. Start frontend: cd frontend && npm start")
        print("\n✅ Your bot will now trade with real money using your API token!")
    else:
        print("\n❌ Setup failed. Please try again with a valid API token.")

if __name__ == "__main__":
    main()
