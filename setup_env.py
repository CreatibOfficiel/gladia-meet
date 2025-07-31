#!/usr/bin/env python3
"""
Setup script for Google Meet Bot environment configuration
"""

import os
import shutil
import sys

def create_env_file():
    """Create .env file from env.example if it doesn't exist"""
    if os.path.exists(".env"):
        print("✅ .env file already exists")
        return True
    
    if not os.path.exists("env.example"):
        print("❌ env.example file not found")
        return False
    
    print("📝 Creating .env file from env.example...")
    try:
        shutil.copy("env.example", ".env")
        print("✅ .env file created successfully")
        print("\n⚠️  IMPORTANT: Please edit .env file with your actual values:")
        print("   nano .env")
        print("   or")
        print("   code .env")
        return True
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False

def validate_env_file():
    """Validate that .env file has required values"""
    if not os.path.exists(".env"):
        print("❌ .env file not found")
        return False
    
    required_vars = [
        "GMEET_LINK",
        "GMAIL_USER_EMAIL", 
        "GMAIL_USER_PASSWORD",
        "GLADIA_API_KEY"
    ]
    
    missing_vars = []
    
    with open(".env", "r") as f:
        content = f.read()
        lines = content.split("\n")
        
        for var in required_vars:
            found = False
            for line in lines:
                if line.strip().startswith(f"{var}=") and not line.strip().startswith("#"):
                    value = line.split("=", 1)[1].strip()
                    if value and value != "your-email@gmail.com" and value != "your-password-or-app-password" and value != "your-gladia-api-key" and value != "https://meet.google.com/your-meet-id":
                        found = True
                        break
            if not found:
                missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing or invalid values in .env file:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease edit .env file with your actual values")
        return False
    
    print("✅ .env file is properly configured")
    return True

def show_env_status():
    """Show current environment configuration status"""
    print("🔍 Environment Configuration Status")
    print("=" * 40)
    
    if os.path.exists(".env"):
        print("✅ .env file exists")
        if validate_env_file():
            print("✅ .env file is properly configured")
        else:
            print("❌ .env file needs configuration")
    else:
        print("❌ .env file not found")
        if os.path.exists("env.example"):
            print("✅ env.example file found")
            print("   Run: python setup_env.py --create")
        else:
            print("❌ env.example file not found")

def main():
    """Main function"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "--create":
            if create_env_file():
                print("\n🎉 Setup completed!")
                print("Next steps:")
                print("1. Edit .env file with your values")
                print("2. Start the API: docker-compose up -d gmeet-api")
                print("3. Test the API: python test_api.py")
            else:
                sys.exit(1)
        elif sys.argv[1] == "--validate":
            if validate_env_file():
                print("🎉 Environment is ready!")
            else:
                sys.exit(1)
        elif sys.argv[1] == "--status":
            show_env_status()
        else:
            print("Usage:")
            print("  python setup_env.py --create    # Create .env file")
            print("  python setup_env.py --validate  # Validate .env file")
            print("  python setup_env.py --status    # Show status")
    else:
        show_env_status()
        print("\nUsage:")
        print("  python setup_env.py --create    # Create .env file")
        print("  python setup_env.py --validate  # Validate .env file")
        print("  python setup_env.py --status    # Show status")

if __name__ == "__main__":
    main() 