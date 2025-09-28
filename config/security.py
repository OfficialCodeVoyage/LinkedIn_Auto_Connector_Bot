"""
Security module for LinkedIn Auto Connector Bot.

This module provides secure credential management with encryption,
keyring integration, and password validation.
"""

import os
import re
import base64
import hashlib
import secrets
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2

try:
    import keyring
    KEYRING_AVAILABLE = True
except ImportError:
    KEYRING_AVAILABLE = False
    logging.warning("Keyring not available. Credentials will be stored in encrypted files.")

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class PasswordPolicy:
    """Password policy configuration."""
    min_length: int = 12
    require_uppercase: bool = True
    require_lowercase: bool = True
    require_digits: bool = True
    require_special: bool = True
    special_characters: str = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    max_repeated_chars: int = 3
    prevent_common_passwords: bool = True


class PasswordValidator:
    """Validates passwords against security policies."""

    def __init__(self, policy: Optional[PasswordPolicy] = None):
        """
        Initialize password validator.

        Args:
            policy: Password policy to use (defaults to standard policy)
        """
        self.policy = policy or PasswordPolicy()
        self.common_passwords = self._load_common_passwords()

    def _load_common_passwords(self) -> set:
        """Load list of common passwords to check against."""
        # Common weak passwords (in production, load from a file)
        return {
            'password', 'password123', '123456', '123456789', 'qwerty',
            'abc123', '111111', '1234567', 'monkey', '1234567890',
            'password1', 'password123', 'linkedin', 'linkedin123'
        }

    def validate(self, password: str) -> Tuple[bool, str]:
        """
        Validate password against policy.

        Args:
            password: Password to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if len(password) < self.policy.min_length:
            return False, f"Password must be at least {self.policy.min_length} characters long"

        if self.policy.require_uppercase and not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"

        if self.policy.require_lowercase and not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"

        if self.policy.require_digits and not re.search(r'\d', password):
            return False, "Password must contain at least one digit"

        if self.policy.require_special:
            if not any(char in self.policy.special_characters for char in password):
                return False, "Password must contain at least one special character"

        # Check for repeated characters
        for i in range(len(password) - self.policy.max_repeated_chars):
            if password[i] == password[i+1] == password[i+2]:
                if self.policy.max_repeated_chars == 3 and i+3 < len(password) and password[i] == password[i+3]:
                    return False, f"Password cannot contain more than {self.policy.max_repeated_chars} repeated characters"

        # Check against common passwords
        if self.policy.prevent_common_passwords:
            if password.lower() in self.common_passwords:
                return False, "Password is too common. Please choose a more unique password"

        return True, "Password is valid"

    def calculate_strength(self, password: str) -> Dict[str, Any]:
        """
        Calculate password strength score.

        Args:
            password: Password to analyze

        Returns:
            Dictionary with strength metrics
        """
        score = 0
        feedback = []

        # Length score
        length = len(password)
        if length >= 20:
            score += 30
        elif length >= 16:
            score += 20
        elif length >= 12:
            score += 10
        else:
            feedback.append("Consider using a longer password")

        # Character diversity
        has_lower = bool(re.search(r'[a-z]', password))
        has_upper = bool(re.search(r'[A-Z]', password))
        has_digit = bool(re.search(r'\d', password))
        has_special = bool(re.search(r'[^a-zA-Z0-9]', password))

        diversity = sum([has_lower, has_upper, has_digit, has_special])
        score += diversity * 15

        if diversity < 4:
            feedback.append("Use a mix of uppercase, lowercase, numbers, and special characters")

        # Pattern detection
        if re.search(r'(.)\1{2,}', password):
            score -= 10
            feedback.append("Avoid repeated characters")

        if re.search(r'(012|123|234|345|456|567|678|789|890)', password):
            score -= 10
            feedback.append("Avoid sequential numbers")

        if re.search(r'(abc|bcd|cde|def|efg|fgh|ghi|hij)', password.lower()):
            score -= 10
            feedback.append("Avoid sequential letters")

        # Common patterns
        if password.lower() in self.common_passwords:
            score = min(score, 20)
            feedback.append("This password is too common")

        # Normalize score
        score = max(0, min(100, score))

        # Determine strength level
        if score >= 80:
            strength = "Very Strong"
        elif score >= 60:
            strength = "Strong"
        elif score >= 40:
            strength = "Moderate"
        elif score >= 20:
            strength = "Weak"
        else:
            strength = "Very Weak"

        return {
            'score': score,
            'strength': strength,
            'feedback': feedback,
            'length': length,
            'diversity': diversity
        }


class CredentialManager:
    """Manages secure storage and retrieval of credentials."""

    def __init__(self, app_name: str = "LinkedIn_Auto_Connector",
                 credentials_dir: Optional[Path] = None):
        """
        Initialize credential manager.

        Args:
            app_name: Application name for keyring storage
            credentials_dir: Directory for encrypted credential files
        """
        self.app_name = app_name
        self.credentials_dir = credentials_dir or Path.home() / '.linkedin_bot' / 'credentials'
        self.credentials_dir.mkdir(parents=True, exist_ok=True)

        self.key_file = self.credentials_dir / '.key'
        self.credentials_file = self.credentials_dir / 'credentials.enc'

        self.cipher = self._initialize_cipher()
        self.validator = PasswordValidator()

    def _initialize_cipher(self) -> Fernet:
        """
        Initialize encryption cipher.

        Returns:
            Fernet cipher instance
        """
        if self.key_file.exists():
            with open(self.key_file, 'rb') as f:
                key = f.read()
        else:
            key = self._generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(key)
            # Set restrictive permissions (Unix-like systems)
            os.chmod(self.key_file, 0o600)

        return Fernet(key)

    def _generate_key(self) -> bytes:
        """
        Generate encryption key using PBKDF2.

        Returns:
            Encryption key
        """
        # Generate salt
        salt = secrets.token_bytes(16)

        # Use machine-specific information for additional entropy
        machine_id = hashlib.sha256(
            f"{os.environ.get('USER', '')}{os.environ.get('COMPUTERNAME', '')}".encode()
        ).digest()

        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt + machine_id[:16],
            iterations=100000,
        )

        key = base64.urlsafe_b64encode(kdf.derive(secrets.token_bytes(32)))
        return key

    def store_credentials(self, username: str, password: str,
                          use_keyring: bool = True) -> bool:
        """
        Store credentials securely.

        Args:
            username: LinkedIn username/email
            password: LinkedIn password
            use_keyring: Whether to use system keyring

        Returns:
            True if successfully stored

        Raises:
            ValueError: If password doesn't meet security requirements
        """
        # Validate password
        is_valid, error_msg = self.validator.validate(password)
        if not is_valid:
            raise ValueError(f"Password validation failed: {error_msg}")

        try:
            if use_keyring and KEYRING_AVAILABLE:
                # Store in system keyring
                keyring.set_password(self.app_name, username, password)
                logger.info(f"Credentials stored in system keyring for user: {username}")
            else:
                # Store in encrypted file
                credentials = self._load_encrypted_credentials()
                credentials[username] = {
                    'password': password,
                    'timestamp': secrets.time_ns()
                }
                self._save_encrypted_credentials(credentials)
                logger.info(f"Credentials stored in encrypted file for user: {username}")

            return True

        except Exception as e:
            logger.error(f"Failed to store credentials: {e}")
            return False

    def retrieve_credentials(self, username: str,
                            use_keyring: bool = True) -> Optional[str]:
        """
        Retrieve stored credentials.

        Args:
            username: LinkedIn username/email
            use_keyring: Whether to use system keyring

        Returns:
            Password if found, None otherwise
        """
        try:
            if use_keyring and KEYRING_AVAILABLE:
                # Try system keyring first
                password = keyring.get_password(self.app_name, username)
                if password:
                    logger.debug(f"Credentials retrieved from keyring for user: {username}")
                    return password

            # Try encrypted file
            credentials = self._load_encrypted_credentials()
            if username in credentials:
                logger.debug(f"Credentials retrieved from encrypted file for user: {username}")
                return credentials[username]['password']

            logger.warning(f"No credentials found for user: {username}")
            return None

        except Exception as e:
            logger.error(f"Failed to retrieve credentials: {e}")
            return None

    def delete_credentials(self, username: str, use_keyring: bool = True) -> bool:
        """
        Delete stored credentials.

        Args:
            username: LinkedIn username/email
            use_keyring: Whether to use system keyring

        Returns:
            True if successfully deleted
        """
        try:
            deleted = False

            if use_keyring and KEYRING_AVAILABLE:
                try:
                    keyring.delete_password(self.app_name, username)
                    deleted = True
                    logger.info(f"Credentials deleted from keyring for user: {username}")
                except keyring.errors.PasswordDeleteError:
                    pass

            # Also try to delete from encrypted file
            credentials = self._load_encrypted_credentials()
            if username in credentials:
                del credentials[username]
                self._save_encrypted_credentials(credentials)
                deleted = True
                logger.info(f"Credentials deleted from encrypted file for user: {username}")

            return deleted

        except Exception as e:
            logger.error(f"Failed to delete credentials: {e}")
            return False

    def list_stored_accounts(self) -> list:
        """
        List all stored account usernames.

        Returns:
            List of usernames with stored credentials
        """
        accounts = set()

        # Get accounts from encrypted file
        credentials = self._load_encrypted_credentials()
        accounts.update(credentials.keys())

        # Get accounts from keyring if available
        if KEYRING_AVAILABLE:
            try:
                # This is platform-specific and may not work on all systems
                import keyring.backends
                backend = keyring.get_keyring()
                # Note: Getting all credentials from keyring is not standardized
                # This is a best-effort approach
                pass
            except Exception:
                pass

        return list(accounts)

    def _load_encrypted_credentials(self) -> dict:
        """
        Load credentials from encrypted file.

        Returns:
            Dictionary of credentials
        """
        if not self.credentials_file.exists():
            return {}

        try:
            with open(self.credentials_file, 'rb') as f:
                encrypted_data = f.read()

            decrypted_data = self.cipher.decrypt(encrypted_data)
            return json.loads(decrypted_data.decode())

        except Exception as e:
            logger.error(f"Failed to load encrypted credentials: {e}")
            return {}

    def _save_encrypted_credentials(self, credentials: dict) -> None:
        """
        Save credentials to encrypted file.

        Args:
            credentials: Dictionary of credentials to save
        """
        try:
            json_data = json.dumps(credentials).encode()
            encrypted_data = self.cipher.encrypt(json_data)

            with open(self.credentials_file, 'wb') as f:
                f.write(encrypted_data)

            # Set restrictive permissions (Unix-like systems)
            os.chmod(self.credentials_file, 0o600)

        except Exception as e:
            logger.error(f"Failed to save encrypted credentials: {e}")
            raise

    def validate_stored_password(self, username: str) -> Dict[str, Any]:
        """
        Validate strength of stored password.

        Args:
            username: LinkedIn username/email

        Returns:
            Password strength analysis
        """
        password = self.retrieve_credentials(username)
        if not password:
            return {'error': 'No credentials found for user'}

        return self.validator.calculate_strength(password)

    def update_password(self, username: str, old_password: str,
                       new_password: str) -> bool:
        """
        Update stored password after verification.

        Args:
            username: LinkedIn username/email
            old_password: Current password for verification
            new_password: New password to store

        Returns:
            True if successfully updated
        """
        stored_password = self.retrieve_credentials(username)

        if stored_password != old_password:
            logger.error("Old password verification failed")
            return False

        return self.store_credentials(username, new_password)

    def export_credentials(self, export_path: Path, password: str) -> bool:
        """
        Export credentials to encrypted backup file.

        Args:
            export_path: Path to export file
            password: Password to encrypt export

        Returns:
            True if successfully exported
        """
        try:
            # Generate export key from password
            salt = secrets.token_bytes(16)
            kdf = PBKDF2(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            cipher = Fernet(key)

            # Get all credentials
            credentials = self._load_encrypted_credentials()

            # Encrypt and save
            export_data = {
                'salt': base64.b64encode(salt).decode(),
                'data': base64.b64encode(
                    cipher.encrypt(json.dumps(credentials).encode())
                ).decode()
            }

            with open(export_path, 'w') as f:
                json.dump(export_data, f, indent=2)

            logger.info(f"Credentials exported to {export_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to export credentials: {e}")
            return False

    def import_credentials(self, import_path: Path, password: str) -> bool:
        """
        Import credentials from encrypted backup file.

        Args:
            import_path: Path to import file
            password: Password to decrypt import

        Returns:
            True if successfully imported
        """
        try:
            with open(import_path, 'r') as f:
                export_data = json.load(f)

            # Recreate key from password and salt
            salt = base64.b64decode(export_data['salt'])
            kdf = PBKDF2(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            cipher = Fernet(key)

            # Decrypt credentials
            encrypted_data = base64.b64decode(export_data['data'])
            decrypted_data = cipher.decrypt(encrypted_data)
            credentials = json.loads(decrypted_data.decode())

            # Merge with existing credentials
            existing = self._load_encrypted_credentials()
            existing.update(credentials)
            self._save_encrypted_credentials(existing)

            logger.info(f"Credentials imported from {import_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to import credentials: {e}")
            return False