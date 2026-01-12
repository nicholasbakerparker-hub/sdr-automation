"""
Test Setup Script
Run this to make sure everything is configured correctly
"""

import os
import sys
from dotenv import load_dotenv


def test_python_version():
    """Check if Python version is adequate"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Good!")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor} - Need Python 3.8+")
        return False


def test_packages():
    """Check if required packages are installed"""
    required = [
        'anthropic',
        'dotenv',
        'requests',
        'simple_salesforce',
        'dateutil',
        'pytz'
    ]
    
    missing = []
    
    for package in required:
        try:
            if package == 'dotenv':
                __import__('dotenv')
            elif package == 'dateutil':
                __import__('dateutil')
            else:
                __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - Not installed")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print("Run: pip install -r requirements.txt")
        return False
    else:
        print("\n✅ All packages installed!")
        return True


def test_env_file():
    """Check if .env file exists and has required keys"""
    
    if not os.path.exists('.env'):
        print("❌ .env file not found")
        print("💡 Copy .env.example to .env and fill in your details")
        return False
    
    print("✅ .env file found")
    
    # Load environment variables
    load_dotenv()
    
    # Check for required keys
    required_keys = [
        'ANTHROPIC_API_KEY',
        'OUTREACH_API_KEY',
        'SALESFORCE_USERNAME',
        'SALESFORCE_PASSWORD',
        'SALESFORCE_SECURITY_TOKEN',
        'ORUM_API_KEY',
        'YOUR_NAME',
        'YOUR_EMAIL',
        'YOUR_CALENDAR_LINK'
    ]
    
    missing = []
    
    print("\nChecking configuration:")
    for key in required_keys:
        value = os.getenv(key)
        if value and value != f'your-{key.lower().replace("_", "-")}-here':
            print(f"  ✅ {key}")
        else:
            print(f"  ❌ {key} - Not configured")
            missing.append(key)
    
    if missing:
        print(f"\n⚠️  Missing configuration: {', '.join(missing)}")
        print("💡 Edit your .env file and fill in these values")
        return False
    else:
        print("\n✅ All configuration values set!")
        return True


def test_api_connections():
    """Test if we can connect to APIs"""
    
    load_dotenv()
    
    print("\nTesting API connections:")
    
    # Test Anthropic
    try:
        from anthropic import Anthropic
        client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        # Try a simple call
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=50,
            messages=[{"role": "user", "content": "Say 'Connection successful'"}]
        )
        print("✅ Anthropic (Claude) API")
    except Exception as e:
        print(f"❌ Anthropic API: {str(e)[:50]}")
    
    # Test Salesforce
    try:
        from simple_salesforce import Salesforce
        sf = Salesforce(
            username=os.getenv('SALESFORCE_USERNAME'),
            password=os.getenv('SALESFORCE_PASSWORD'),
            security_token=os.getenv('SALESFORCE_SECURITY_TOKEN')
        )
        print("✅ Salesforce API")
    except Exception as e:
        print(f"❌ Salesforce API: {str(e)[:50]}")
    
    # Test Outreach (basic)
    try:
        import requests
        headers = {'Authorization': f'Bearer {os.getenv("OUTREACH_API_KEY")}'}
        # Don't make actual request in test, just check if key exists
        if os.getenv('OUTREACH_API_KEY'):
            print("✅ Outreach API key configured")
        else:
            print("❌ Outreach API key not set")
    except Exception as e:
        print(f"❌ Outreach: {str(e)[:50]}")
    
    # Test Orum (basic)
    if os.getenv('ORUM_API_KEY'):
        print("✅ Orum API key configured")
    else:
        print("❌ Orum API key not set")


def main():
    """Run all tests"""
    
    print("=" * 60)
    print("SDR AUTOMATION - SETUP TEST")
    print("=" * 60)
    print()
    
    print("1️⃣  Testing Python version:")
    python_ok = test_python_version()
    print()
    
    print("2️⃣  Testing required packages:")
    packages_ok = test_packages()
    print()
    
    print("3️⃣  Testing configuration:")
    config_ok = test_env_file()
    print()
    
    print("4️⃣  Testing API connections:")
    test_api_connections()
    print()
    
    print("=" * 60)
    
    if python_ok and packages_ok and config_ok:
        print("✅ ALL TESTS PASSED - READY TO GO!")
        print()
        print("Next steps:")
        print("  • Run a manual test: python main.py --manual test_call.txt")
        print("  • Run automatic mode: python main.py --auto")
    else:
        print("⚠️  SOME TESTS FAILED - FIX ISSUES ABOVE")
        print()
        print("Common fixes:")
        print("  • Install packages: pip install -r requirements.txt")
        print("  • Copy .env.example to .env and fill it in")
        print("  • Check your API keys are correct")
    
    print("=" * 60)


if __name__ == "__main__":
    main()
