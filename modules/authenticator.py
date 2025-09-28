"""
Authentication module for LinkedIn Auto Connector Bot.

This module handles LinkedIn login, two-factor authentication,
CAPTCHA detection, and session management.
"""

import time
import logging
from typing import Optional, Tuple, Dict, Any
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import random

logger = logging.getLogger(__name__)


class LinkedInAuthenticator:
    """
    Handles LinkedIn authentication and login processes.

    Features:
    - Standard login with username/password
    - Session restoration from cookies
    - CAPTCHA detection and handling
    - Two-factor authentication support
    - Login verification
    """

    def __init__(self, driver, session_manager=None, config=None):
        """
        Initialize the LinkedInAuthenticator.

        Args:
            driver: Selenium WebDriver instance
            session_manager: Optional SessionManager for session persistence
            config: Optional configuration object
        """
        self.driver = driver
        self.session_manager = session_manager
        self.config = config
        self.wait = WebDriverWait(driver, 20)
        self.logged_in = False

    def login(self, username: str, password: str, use_session: bool = True) -> Tuple[bool, str]:
        """
        Login to LinkedIn with username and password.

        Args:
            username: LinkedIn username/email
            password: LinkedIn password
            use_session: Whether to try loading saved session first

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Try to use saved session if available
            if use_session and self.session_manager:
                logger.info(f"Attempting to load saved session for {username}")
                if self.session_manager.load_session(self.driver, username):
                    if self._verify_login():
                        self.logged_in = True
                        logger.info("Successfully logged in using saved session")
                        return True, "Logged in using saved session"
                    else:
                        logger.info("Saved session invalid, proceeding with regular login")

            # Navigate to login page
            logger.info("Navigating to LinkedIn login page")
            self.driver.get("https://www.linkedin.com/login")

            # Random delay to appear human
            self._human_delay(2, 4)

            # Check if already logged in
            if self._verify_login():
                self.logged_in = True
                logger.info("Already logged in")
                return True, "Already logged in"

            # Enter username
            logger.info("Entering username")
            username_field = self._wait_and_find_element(By.ID, "username")
            if not username_field:
                return False, "Could not find username field"

            self._human_type(username_field, username)
            self._human_delay(1, 2)

            # Enter password
            logger.info("Entering password")
            password_field = self._wait_and_find_element(By.ID, "password")
            if not password_field:
                return False, "Could not find password field"

            self._human_type(password_field, password)
            self._human_delay(1, 2)

            # Click login button
            logger.info("Clicking login button")
            login_button = self._wait_and_find_element(
                By.XPATH,
                "//button[@type='submit' and contains(@class, 'btn__primary')]"
            )
            if not login_button:
                return False, "Could not find login button"

            login_button.click()

            # Wait for login to complete
            self._human_delay(3, 5)

            # Check for CAPTCHA
            if self._detect_captcha():
                logger.warning("CAPTCHA detected, waiting for manual resolution")
                if not self._wait_for_captcha_resolution():
                    return False, "CAPTCHA not resolved within timeout"

            # Check for two-factor authentication
            if self._detect_two_factor():
                logger.info("Two-factor authentication detected")
                if not self._handle_two_factor():
                    return False, "Two-factor authentication failed"

            # Check for security checkpoint
            if self._detect_security_checkpoint():
                logger.warning("Security checkpoint detected")
                return False, "Security checkpoint detected - manual intervention required"

            # Verify successful login
            if self._verify_login():
                self.logged_in = True
                logger.info("Successfully logged in")

                # Save session for future use
                if self.session_manager:
                    logger.info("Saving session for future use")
                    self.session_manager.save_session(self.driver, username)

                return True, "Successfully logged in"
            else:
                # Check for error messages
                error_msg = self._get_error_message()
                if error_msg:
                    logger.error(f"Login failed with error: {error_msg}")
                    return False, f"Login failed: {error_msg}"
                else:
                    logger.error("Login failed for unknown reason")
                    return False, "Login failed - please check credentials"

        except Exception as e:
            logger.error(f"Exception during login: {str(e)}")
            return False, f"Login exception: {str(e)}"

    def logout(self) -> bool:
        """
        Logout from LinkedIn.

        Returns:
            True if logout successful, False otherwise
        """
        try:
            logger.info("Logging out from LinkedIn")

            # Navigate to feed first
            self.driver.get("https://www.linkedin.com/feed")
            self._human_delay(2, 3)

            # Click on Me dropdown
            me_button = self._wait_and_find_element(By.ID, "ember-global-nav-me-menu")
            if not me_button:
                me_button = self._wait_and_find_element(
                    By.XPATH,
                    "//button[contains(@class, 'global-nav__primary-link--me')]"
                )

            if me_button:
                me_button.click()
                self._human_delay(1, 2)

                # Click Sign Out
                sign_out = self._wait_and_find_element(
                    By.XPATH,
                    "//a[@href='/m/logout/' or contains(text(), 'Sign Out')]"
                )
                if sign_out:
                    sign_out.click()
                    self.logged_in = False
                    logger.info("Successfully logged out")
                    return True

            logger.error("Could not find logout option")
            return False

        except Exception as e:
            logger.error(f"Error during logout: {str(e)}")
            return False

    def _verify_login(self) -> bool:
        """
        Verify if currently logged into LinkedIn.

        Returns:
            True if logged in, False otherwise
        """
        try:
            # Quick check for login page URL
            current_url = self.driver.current_url
            if "linkedin.com/login" in current_url or "linkedin.com/checkpoint" in current_url:
                return False

            # Check for feed or home page
            if "linkedin.com/feed" in current_url or "linkedin.com/in/" in current_url:
                return True

            # Navigate to feed to verify
            self.driver.get("https://www.linkedin.com/feed")
            self._human_delay(2, 3)

            # Check URL again after navigation
            if "linkedin.com/feed" in self.driver.current_url:
                return True

            # Look for logged-in elements
            logged_in_indicators = [
                (By.ID, "global-nav"),
                (By.CLASS_NAME, "global-nav__me"),
                (By.CLASS_NAME, "feed-shared-update-v2"),
                (By.XPATH, "//div[@class='global-nav__content']")
            ]

            for by, value in logged_in_indicators:
                try:
                    self.driver.find_element(by, value)
                    return True
                except NoSuchElementException:
                    continue

            return False

        except Exception as e:
            logger.error(f"Error verifying login: {str(e)}")
            return False

    def _detect_captcha(self) -> bool:
        """
        Detect if CAPTCHA is present.

        Returns:
            True if CAPTCHA detected, False otherwise
        """
        try:
            captcha_indicators = [
                "//iframe[contains(@src, 'recaptcha')]",
                "//div[contains(@class, 'captcha')]",
                "//div[@id='captcha']",
                "//img[contains(@src, 'captcha')]"
            ]

            for xpath in captcha_indicators:
                try:
                    self.driver.find_element(By.XPATH, xpath)
                    logger.warning("CAPTCHA detected")
                    return True
                except NoSuchElementException:
                    continue

            return False

        except Exception as e:
            logger.error(f"Error detecting CAPTCHA: {str(e)}")
            return False

    def _wait_for_captcha_resolution(self, timeout: int = 120) -> bool:
        """
        Wait for user to manually resolve CAPTCHA.

        Args:
            timeout: Maximum time to wait in seconds

        Returns:
            True if CAPTCHA resolved, False if timeout
        """
        logger.info(f"Waiting up to {timeout} seconds for CAPTCHA resolution")
        start_time = time.time()

        while time.time() - start_time < timeout:
            if not self._detect_captcha():
                logger.info("CAPTCHA resolved")
                return True
            time.sleep(2)

        logger.error("CAPTCHA resolution timeout")
        return False

    def _detect_two_factor(self) -> bool:
        """
        Detect if two-factor authentication is required.

        Returns:
            True if 2FA detected, False otherwise
        """
        try:
            two_factor_indicators = [
                "//input[@name='pin' or @id='input__phone_verification_pin']",
                "//h1[contains(text(), 'verification')]",
                "//div[contains(text(), 'Enter the code')]"
            ]

            for xpath in two_factor_indicators:
                try:
                    self.driver.find_element(By.XPATH, xpath)
                    logger.info("Two-factor authentication detected")
                    return True
                except NoSuchElementException:
                    continue

            return False

        except Exception as e:
            logger.error(f"Error detecting 2FA: {str(e)}")
            return False

    def _handle_two_factor(self, timeout: int = 120) -> bool:
        """
        Handle two-factor authentication.

        Args:
            timeout: Maximum time to wait for 2FA completion

        Returns:
            True if 2FA completed, False otherwise
        """
        logger.info("Waiting for user to complete two-factor authentication")
        logger.info("Please enter the verification code manually")

        start_time = time.time()
        while time.time() - start_time < timeout:
            if not self._detect_two_factor():
                logger.info("Two-factor authentication completed")
                return True
            time.sleep(2)

        logger.error("Two-factor authentication timeout")
        return False

    def _detect_security_checkpoint(self) -> bool:
        """
        Detect if security checkpoint is present.

        Returns:
            True if checkpoint detected, False otherwise
        """
        try:
            if "linkedin.com/checkpoint" in self.driver.current_url:
                return True

            checkpoint_indicators = [
                "//h1[contains(text(), 'Security verification')]",
                "//div[contains(text(), 'unusual activity')]"
            ]

            for xpath in checkpoint_indicators:
                try:
                    self.driver.find_element(By.XPATH, xpath)
                    return True
                except NoSuchElementException:
                    continue

            return False

        except Exception as e:
            logger.error(f"Error detecting security checkpoint: {str(e)}")
            return False

    def _get_error_message(self) -> Optional[str]:
        """
        Get login error message if present.

        Returns:
            Error message text or None
        """
        try:
            error_selectors = [
                (By.ID, "error-for-password"),
                (By.ID, "error-for-username"),
                (By.CLASS_NAME, "form__label--error"),
                (By.XPATH, "//div[@role='alert']"),
                (By.XPATH, "//span[contains(@class, 'error')]")
            ]

            for by, value in error_selectors:
                try:
                    error_element = self.driver.find_element(by, value)
                    error_text = error_element.text.strip()
                    if error_text:
                        return error_text
                except NoSuchElementException:
                    continue

            return None

        except Exception as e:
            logger.error(f"Error getting error message: {str(e)}")
            return None

    def _wait_and_find_element(self, by: By, value: str, timeout: int = 10):
        """
        Wait for and find an element.

        Args:
            by: Selenium By locator type
            value: Locator value
            timeout: Maximum wait time

        Returns:
            WebElement if found, None otherwise
        """
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            logger.warning(f"Element not found: {by}={value}")
            return None

    def _human_type(self, element, text: str):
        """
        Type text with human-like speed and behavior.

        Args:
            element: Input element to type in
            text: Text to type
        """
        element.clear()
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))

    def _human_delay(self, min_seconds: float, max_seconds: float):
        """
        Add human-like random delay.

        Args:
            min_seconds: Minimum delay in seconds
            max_seconds: Maximum delay in seconds
        """
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)

    def is_logged_in(self) -> bool:
        """
        Check if currently logged in.

        Returns:
            True if logged in, False otherwise
        """
        return self.logged_in and self._verify_login()

    def require_login(self, username: str, password: str) -> bool:
        """
        Ensure user is logged in, login if necessary.

        Args:
            username: LinkedIn username
            password: LinkedIn password

        Returns:
            True if logged in (or successfully logged in), False otherwise
        """
        if self.is_logged_in():
            logger.info("Already logged in")
            return True

        success, message = self.login(username, password)
        if not success:
            logger.error(f"Failed to login: {message}")

        return success


# Example usage
if __name__ == "__main__":
    # Configure logging for testing
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Example usage would require a WebDriver instance
    # from selenium import webdriver
    # driver = webdriver.Chrome()
    # auth = LinkedInAuthenticator(driver)
    # success, message = auth.login("username", "password")
    # print(f"Login result: {success} - {message}")