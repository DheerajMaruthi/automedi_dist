"""
Password Protection Module for AutoMediClaim
Simple password prompt to unlock the application.
"""
import os
import sys
import hashlib
from pathlib import Path


# Password hash (bcrypt recommended for production, using simple hash for now)
# To generate: python3 -c "import hashlib; print(hashlib.sha256(b'YourPassword123').hexdigest())"
DEFAULT_PASSWORD_HASH = hashlib.sha256(b"AutoMediClaim@2024").hexdigest()

# Get password from environment variable (for automation/CI/CD)
ENV_PASSWORD = os.environ.get("AUTOMEDICLAIM_PASSWORD")


def hash_password(password):
    """Hash password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(entered_password, stored_hash=DEFAULT_PASSWORD_HASH):
    """Verify entered password against stored hash."""
    return hash_password(entered_password) == stored_hash


def prompt_for_password(max_attempts=3):
    """
    Prompt user for password with limited attempts.
    
    Args:
        max_attempts: Maximum number of password attempts allowed
        
    Returns:
        True if correct password entered, False if max attempts exceeded
        
    Raises:
        RuntimeError: If password verification fails after max attempts
    """
    # Check if password provided via environment variable (for automation)
    if ENV_PASSWORD:
        if verify_password(ENV_PASSWORD):
            print("[✓] Password verified via environment variable")
            return True
        else:
            raise RuntimeError(
                "❌ BLOCKED: Incorrect password in AUTOMEDICLAIM_PASSWORD environment variable"
            )
    
    # Interactive password prompt
    print("\n" + "="*60)
    print("🔐 AutoMediClaim - Password Required")
    print("="*60)
    
    for attempt in range(1, max_attempts + 1):
        try:
            # Python 3 - use getpass for hidden password input
            import getpass
            password = getpass.getpass(
                f"Enter password (Attempt {attempt}/{max_attempts}): "
            )
        except (ImportError, Exception):
            # Fallback for non-interactive environments
            password = input(f"Enter password (Attempt {attempt}/{max_attempts}): ")
        
        if verify_password(password):
            print("[✓] Password verified successfully. Starting application...\n")
            return True
        else:
            remaining = max_attempts - attempt
            if remaining > 0:
                print(f"❌ Incorrect password. {remaining} attempt(s) remaining.\n")
            else:
                print("❌ Maximum password attempts exceeded.\n")
    
    # All attempts failed
    raise RuntimeError(
        "❌ APPLICATION BLOCKED - AUTHENTICATION FAILED\n"
        f"Too many incorrect password attempts ({max_attempts}).\n"
        "Please contact your administrator."
    )


def protect_application(max_attempts=3, skip_if_env_var=False):
    """
    Main function to protect application startup.
    
    Args:
        max_attempts: Maximum password attempts
        skip_if_env_var: If True, skip prompt when AUTOMEDICLAIM_PASSWORD is set
    """
    # Skip protection if explicitly disabled (development only)
    if os.environ.get("SKIP_PASSWORD_CHECK", "False").lower() == "true":
        print("[⚠] Password protection disabled (development mode)")
        return True
    
    try:
        prompt_for_password(max_attempts=max_attempts)
        return True
    except RuntimeError as e:
        # Authentication failed - block execution
        print(f"\n{str(e)}\n")
        sys.exit(1)


if __name__ == "__main__":
    # Test password protection
    protect_application()
    print("✓ Password verification succeeded!")
