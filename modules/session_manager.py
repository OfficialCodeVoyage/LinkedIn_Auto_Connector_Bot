"""
Session management module for LinkedIn Auto Connector Bot.

This module handles browser session persistence, including saving and loading
cookies, managing session timeouts, and ensuring secure session storage.
"""

import os
import json
import pickle
import logging
from pathlib import Path
from typing import Dict, Optional, Any, List
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
import base64

logger = logging.getLogger(__name__)


class SessionManager:
    """
    Manages browser sessions for LinkedIn automation.

    Features:
    - Save and restore browser cookies
    - Session encryption for security
    - Automatic session expiration
    - Multi-user session support
    """

    def __init__(self, session_dir: str = "sessions", encryption_key: Optional[str] = None):
        """
        Initialize the SessionManager.

        Args:
            session_dir: Directory to store session files
            encryption_key: Optional encryption key for session data
        """
        self.session_dir = Path(session_dir)
        self.session_dir.mkdir(exist_ok=True)

        # Initialize encryption
        if encryption_key:
            self.cipher = Fernet(encryption_key.encode())
        else:
            # Generate a new key if not provided
            key = Fernet.generate_key()
            self.cipher = Fernet(key)
            self._save_encryption_key(key)

        logger.info(f"SessionManager initialized with session directory: {self.session_dir}")

    def _save_encryption_key(self, key: bytes) -> None:
        """
        Save encryption key securely.

        Args:
            key: Encryption key to save
        """
        key_file = self.session_dir / ".session_key"
        with open(key_file, 'wb') as f:
            f.write(key)
        # Set restrictive permissions (Unix/Linux/Mac)
        os.chmod(key_file, 0o600)

    def _load_encryption_key(self) -> Optional[bytes]:
        """
        Load encryption key from file.

        Returns:
            Encryption key if found, None otherwise
        """
        key_file = self.session_dir / ".session_key"
        if key_file.exists():
            with open(key_file, 'rb') as f:
                return f.read()
        return None

    def save_session(self, driver, username: str, additional_data: Optional[Dict] = None) -> bool:
        """
        Save browser session including cookies and metadata.

        Args:
            driver: Selenium WebDriver instance
            username: LinkedIn username for session identification
            additional_data: Optional additional data to store with session

        Returns:
            True if session saved successfully, False otherwise
        """
        try:
            # Get cookies from browser
            cookies = driver.get_cookies()

            # Get browser metadata
            user_agent = driver.execute_script("return navigator.userAgent")
            window_size = driver.get_window_size()

            # Prepare session data
            session_data = {
                'cookies': cookies,
                'timestamp': datetime.now().isoformat(),
                'user_agent': user_agent,
                'window_size': window_size,
                'username': username,
                'url': driver.current_url,
                'additional_data': additional_data or {}
            }

            # Serialize session data
            session_json = json.dumps(session_data)

            # Encrypt session data
            encrypted_data = self.cipher.encrypt(session_json.encode())

            # Save to file
            session_file = self.session_dir / f"{username}_session.enc"
            with open(session_file, 'wb') as f:
                f.write(encrypted_data)

            # Set restrictive permissions
            os.chmod(session_file, 0o600)

            logger.info(f"Session saved successfully for user: {username}")
            return True

        except Exception as e:
            logger.error(f"Error saving session: {str(e)}")
            return False

    def load_session(self, driver, username: str, max_age_hours: int = 24) -> bool:
        """
        Load saved session into browser.

        Args:
            driver: Selenium WebDriver instance
            username: LinkedIn username to load session for
            max_age_hours: Maximum age of session in hours

        Returns:
            True if session loaded successfully, False otherwise
        """
        try:
            session_file = self.session_dir / f"{username}_session.enc"

            if not session_file.exists():
                logger.info(f"No saved session found for user: {username}")
                return False

            # Read encrypted session data
            with open(session_file, 'rb') as f:
                encrypted_data = f.read()

            # Decrypt session data
            decrypted_data = self.cipher.decrypt(encrypted_data)
            session_data = json.loads(decrypted_data.decode())

            # Check session age
            timestamp = datetime.fromisoformat(session_data['timestamp'])
            if datetime.now() - timestamp > timedelta(hours=max_age_hours):
                logger.info(f"Session expired for user: {username}")
                self.delete_session(username)
                return False

            # Navigate to LinkedIn first
            driver.get("https://www.linkedin.com")

            # Clear existing cookies
            driver.delete_all_cookies()

            # Add saved cookies
            for cookie in session_data['cookies']:
                # LinkedIn requires specific cookie handling
                if 'expiry' in cookie:
                    # Convert expiry to int if it's float
                    cookie['expiry'] = int(cookie['expiry'])

                try:
                    driver.add_cookie(cookie)
                except Exception as e:
                    logger.warning(f"Could not add cookie {cookie.get('name', 'unknown')}: {e}")

            # Refresh page to apply cookies
            driver.refresh()

            # Verify session is valid by checking if we're logged in
            import time
            time.sleep(3)  # Wait for page to load

            if self._verify_logged_in(driver):
                logger.info(f"Session loaded successfully for user: {username}")
                return True
            else:
                logger.warning(f"Session loaded but user not logged in: {username}")
                return False

        except Exception as e:
            logger.error(f"Error loading session: {str(e)}")
            return False

    def _verify_logged_in(self, driver) -> bool:
        """
        Verify if the user is logged into LinkedIn.

        Args:
            driver: Selenium WebDriver instance

        Returns:
            True if logged in, False otherwise
        """
        try:
            # Check for common LinkedIn logged-in elements
            logged_in_indicators = [
                "nav-item__profile-member-photo",  # Profile photo in nav
                "global-nav__me",  # Me dropdown
                "feed-shared-update-v2",  # Feed items
                "global-nav__primary-link--active"  # Active nav links
            ]

            for indicator in logged_in_indicators:
                try:
                    driver.find_element("class name", indicator)
                    return True
                except:
                    continue

            # Check if we're on the login page (not logged in)
            if "linkedin.com/login" in driver.current_url:
                return False

            # Check for feed URL (logged in)
            if "linkedin.com/feed" in driver.current_url:
                return True

            return False

        except Exception as e:
            logger.error(f"Error verifying login status: {e}")
            return False

    def delete_session(self, username: str) -> bool:
        """
        Delete a saved session.

        Args:
            username: Username whose session to delete

        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            session_file = self.session_dir / f"{username}_session.enc"
            if session_file.exists():
                session_file.unlink()
                logger.info(f"Session deleted for user: {username}")
                return True
            else:
                logger.info(f"No session found to delete for user: {username}")
                return False
        except Exception as e:
            logger.error(f"Error deleting session: {str(e)}")
            return False

    def list_sessions(self) -> List[Dict[str, Any]]:
        """
        List all saved sessions with metadata.

        Returns:
            List of session information dictionaries
        """
        sessions = []

        for session_file in self.session_dir.glob("*_session.enc"):
            try:
                # Extract username from filename
                username = session_file.stem.replace("_session", "")

                # Read and decrypt session data
                with open(session_file, 'rb') as f:
                    encrypted_data = f.read()

                decrypted_data = self.cipher.decrypt(encrypted_data)
                session_data = json.loads(decrypted_data.decode())

                # Calculate age
                timestamp = datetime.fromisoformat(session_data['timestamp'])
                age_hours = (datetime.now() - timestamp).total_seconds() / 3600

                sessions.append({
                    'username': username,
                    'timestamp': session_data['timestamp'],
                    'age_hours': round(age_hours, 2),
                    'url': session_data.get('url', 'unknown'),
                    'file_size': session_file.stat().st_size
                })

            except Exception as e:
                logger.error(f"Error reading session file {session_file}: {e}")
                continue

        return sessions

    def clean_expired_sessions(self, max_age_hours: int = 48) -> int:
        """
        Clean up expired session files.

        Args:
            max_age_hours: Maximum age of sessions to keep

        Returns:
            Number of sessions cleaned
        """
        cleaned_count = 0

        for session_file in self.session_dir.glob("*_session.enc"):
            try:
                with open(session_file, 'rb') as f:
                    encrypted_data = f.read()

                decrypted_data = self.cipher.decrypt(encrypted_data)
                session_data = json.loads(decrypted_data.decode())

                timestamp = datetime.fromisoformat(session_data['timestamp'])
                if datetime.now() - timestamp > timedelta(hours=max_age_hours):
                    session_file.unlink()
                    cleaned_count += 1
                    logger.info(f"Cleaned expired session: {session_file.name}")

            except Exception as e:
                logger.error(f"Error processing session file {session_file}: {e}")
                # Delete corrupted session files
                try:
                    session_file.unlink()
                    cleaned_count += 1
                    logger.info(f"Deleted corrupted session: {session_file.name}")
                except:
                    pass

        logger.info(f"Cleaned {cleaned_count} expired/corrupted sessions")
        return cleaned_count

    def export_session(self, username: str, export_path: str) -> bool:
        """
        Export a session for backup or transfer.

        Args:
            username: Username whose session to export
            export_path: Path to export session to

        Returns:
            True if exported successfully, False otherwise
        """
        try:
            session_file = self.session_dir / f"{username}_session.enc"
            if not session_file.exists():
                logger.error(f"No session found for user: {username}")
                return False

            # Copy encrypted session file
            import shutil
            shutil.copy2(session_file, export_path)

            logger.info(f"Session exported for user: {username} to {export_path}")
            return True

        except Exception as e:
            logger.error(f"Error exporting session: {str(e)}")
            return False

    def import_session(self, import_path: str, username: str) -> bool:
        """
        Import a session from backup.

        Args:
            import_path: Path to import session from
            username: Username to import session for

        Returns:
            True if imported successfully, False otherwise
        """
        try:
            if not Path(import_path).exists():
                logger.error(f"Import file not found: {import_path}")
                return False

            # Copy to session directory
            import shutil
            destination = self.session_dir / f"{username}_session.enc"
            shutil.copy2(import_path, destination)

            # Set restrictive permissions
            os.chmod(destination, 0o600)

            logger.info(f"Session imported for user: {username}")
            return True

        except Exception as e:
            logger.error(f"Error importing session: {str(e)}")
            return False


# Example usage and testing
if __name__ == "__main__":
    # Configure logging for testing
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Initialize session manager
    session_mgr = SessionManager()

    # List existing sessions
    sessions = session_mgr.list_sessions()
    print(f"Found {len(sessions)} saved sessions:")
    for session in sessions:
        print(f"  - {session['username']}: {session['age_hours']:.1f} hours old")

    # Clean expired sessions
    cleaned = session_mgr.clean_expired_sessions(max_age_hours=48)
    print(f"Cleaned {cleaned} expired sessions")