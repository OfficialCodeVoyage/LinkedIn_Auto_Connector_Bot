"""
Connection request handling module for LinkedIn Auto Connector Bot.

This module manages sending connection requests, handling personalized messages,
and tracking connection status.
"""

import time
import logging
import random
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementClickInterceptedException,
    StaleElementReferenceException
)

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Manages LinkedIn connection requests and follow actions.

    Features:
    - Send personalized connection requests
    - Follow profiles
    - Handle connection limits
    - Track connection history
    - Error recovery and retry logic
    """

    def __init__(self, driver, rate_limiter=None, config=None):
        """
        Initialize the ConnectionManager.

        Args:
            driver: Selenium WebDriver instance
            rate_limiter: Optional RateLimiter instance
            config: Optional configuration object
        """
        self.driver = driver
        self.rate_limiter = rate_limiter
        self.config = config
        self.wait = WebDriverWait(driver, 10)
        self.connections_sent = 0
        self.connections_failed = 0
        self.profiles_followed = 0

    def send_connection_request(
        self,
        profile_url: Optional[str] = None,
        message: Optional[str] = None,
        retry_count: int = 3
    ) -> Dict[str, Any]:
        """
        Send a connection request to a profile.

        Args:
            profile_url: Optional profile URL to connect with
            message: Optional personalized message
            retry_count: Number of retry attempts

        Returns:
            Dictionary with status and details of the connection attempt
        """
        result = {
            'success': False,
            'profile_url': profile_url,
            'timestamp': datetime.now().isoformat(),
            'message': '',
            'error': None
        }

        try:
            # Check rate limits
            if self.rate_limiter and not self.rate_limiter.can_send_request():
                logger.warning("Rate limit reached, cannot send more requests")
                result['error'] = "Rate limit reached"
                result['message'] = "Daily or weekly connection limit reached"
                return result

            # Navigate to profile if URL provided
            if profile_url:
                logger.info(f"Navigating to profile: {profile_url}")
                self.driver.get(profile_url)
                self._human_delay(3, 5)

            # Find and click Connect button
            connect_button = self._find_connect_button()
            if not connect_button:
                logger.warning("Connect button not found")
                result['error'] = "Connect button not found"
                result['message'] = "Could not find Connect button on profile"
                return result

            # Check if already pending or connected
            button_text = connect_button.text.lower()
            if 'pending' in button_text:
                logger.info("Connection request already pending")
                result['message'] = "Connection request already pending"
                return result
            elif 'message' in button_text:
                logger.info("Already connected with this profile")
                result['message'] = "Already connected"
                return result

            # Click Connect button with retry logic
            for attempt in range(retry_count):
                try:
                    self._scroll_to_element(connect_button)
                    self._human_delay(0.5, 1)
                    connect_button.click()
                    logger.info("Clicked Connect button")
                    break
                except ElementClickInterceptedException:
                    if attempt < retry_count - 1:
                        logger.warning(f"Click intercepted, retry {attempt + 1}/{retry_count}")
                        self._human_delay(2, 3)
                        # Try to close any popups
                        self._close_popups()
                    else:
                        raise

            self._human_delay(2, 3)

            # Check if "How do you know" modal appears
            if self._handle_how_you_know_modal():
                self._human_delay(1, 2)

            # Add personalized note if message provided
            if message:
                if self._add_personalized_note(message):
                    logger.info("Added personalized note")
                    result['message'] = "Sent with personalized note"
                else:
                    logger.warning("Could not add personalized note")
                    result['message'] = "Sent without note"
            else:
                # Send without note
                if self._send_without_note():
                    result['message'] = "Sent without note"
                else:
                    result['error'] = "Failed to send connection"
                    return result

            # Track the connection
            self.connections_sent += 1
            if self.rate_limiter:
                profile_name = self._get_profile_name()
                self.rate_limiter.log_request(
                    profile_url or self.driver.current_url,
                    'sent',
                    profile_name
                )

            result['success'] = True
            logger.info(f"Successfully sent connection request #{self.connections_sent}")

            return result

        except Exception as e:
            logger.error(f"Error sending connection request: {str(e)}")
            result['error'] = str(e)
            result['message'] = "Failed to send connection request"
            self.connections_failed += 1
            return result

    def follow_profile(self, profile_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Follow a LinkedIn profile.

        Args:
            profile_url: Optional profile URL to follow

        Returns:
            Dictionary with status and details of the follow attempt
        """
        result = {
            'success': False,
            'profile_url': profile_url,
            'timestamp': datetime.now().isoformat(),
            'message': '',
            'error': None
        }

        try:
            # Navigate to profile if URL provided
            if profile_url:
                logger.info(f"Navigating to profile: {profile_url}")
                self.driver.get(profile_url)
                self._human_delay(3, 5)

            # Find Follow button
            follow_button = self._find_follow_button()
            if not follow_button:
                logger.warning("Follow button not found")
                result['error'] = "Follow button not found"
                result['message'] = "Could not find Follow button on profile"
                return result

            # Check if already following
            button_text = follow_button.text.lower()
            if 'following' in button_text:
                logger.info("Already following this profile")
                result['message'] = "Already following"
                return result

            # Click Follow button
            self._scroll_to_element(follow_button)
            self._human_delay(0.5, 1)
            follow_button.click()

            self.profiles_followed += 1
            result['success'] = True
            result['message'] = "Successfully followed profile"
            logger.info(f"Successfully followed profile #{self.profiles_followed}")

            return result

        except Exception as e:
            logger.error(f"Error following profile: {str(e)}")
            result['error'] = str(e)
            result['message'] = "Failed to follow profile"
            return result

    def process_search_results(
        self,
        message_template: str,
        max_connections: int = 20,
        follow_profiles: bool = True
    ) -> Dict[str, Any]:
        """
        Process LinkedIn search results and send connection requests.

        Args:
            message_template: Template for connection messages
            max_connections: Maximum number of connections to send
            follow_profiles: Whether to also follow profiles

        Returns:
            Summary of processing results
        """
        results = {
            'connections_sent': 0,
            'connections_failed': 0,
            'profiles_followed': 0,
            'total_processed': 0,
            'start_time': datetime.now(),
            'profiles': []
        }

        try:
            page_num = 1
            while results['connections_sent'] < max_connections:
                logger.info(f"Processing page {page_num}")

                # Get all profile cards on current page
                profile_cards = self._get_profile_cards()
                if not profile_cards:
                    logger.warning("No profile cards found on page")
                    if not self._go_to_next_page():
                        break
                    page_num += 1
                    continue

                # Process each profile
                for card in profile_cards:
                    if results['connections_sent'] >= max_connections:
                        break

                    profile_info = self._extract_profile_info(card)
                    if not profile_info:
                        continue

                    results['total_processed'] += 1

                    # Check if should connect
                    if self._should_connect(profile_info):
                        # Personalize message
                        personalized_message = self._personalize_message(
                            message_template,
                            profile_info
                        )

                        # Send connection request
                        connect_result = self._send_connection_from_card(
                            card,
                            personalized_message
                        )

                        if connect_result['success']:
                            results['connections_sent'] += 1
                            profile_info['connection_status'] = 'sent'
                        else:
                            results['connections_failed'] += 1
                            profile_info['connection_status'] = 'failed'

                        results['profiles'].append(profile_info)

                    # Follow profile if enabled
                    if follow_profiles:
                        if self._follow_from_card(card):
                            results['profiles_followed'] += 1

                    # Add delay between profiles
                    self._human_delay(3, 7)

                # Go to next page
                if not self._go_to_next_page():
                    logger.info("No more pages to process")
                    break

                page_num += 1
                self._human_delay(5, 10)

            results['end_time'] = datetime.now()
            results['duration'] = (results['end_time'] - results['start_time']).total_seconds()

            logger.info(f"Processing complete: {results['connections_sent']} connections sent")
            return results

        except Exception as e:
            logger.error(f"Error processing search results: {str(e)}")
            results['error'] = str(e)
            return results

    def _find_connect_button(self):
        """Find Connect button on profile page."""
        selectors = [
            "//button[contains(@aria-label, 'Connect')]",
            "//button[contains(text(), 'Connect')]",
            "//button[contains(@class, 'artdeco-button--primary') and contains(., 'Connect')]",
            "//div[contains(@class, 'pvs-profile-actions')]//button[contains(., 'Connect')]"
        ]

        for selector in selectors:
            try:
                buttons = self.driver.find_elements(By.XPATH, selector)
                for button in buttons:
                    if button.is_displayed() and button.is_enabled():
                        text = button.text.lower()
                        if 'connect' in text and 'pending' not in text:
                            return button
            except:
                continue

        return None

    def _find_follow_button(self):
        """Find Follow button on profile page."""
        selectors = [
            "//button[contains(@aria-label, 'Follow')]",
            "//button[contains(text(), 'Follow')]",
            "//button[contains(@class, 'follow')]"
        ]

        for selector in selectors:
            try:
                buttons = self.driver.find_elements(By.XPATH, selector)
                for button in buttons:
                    if button.is_displayed() and button.is_enabled():
                        text = button.text.lower()
                        if 'follow' in text and 'following' not in text:
                            return button
            except:
                continue

        return None

    def _handle_how_you_know_modal(self) -> bool:
        """Handle 'How do you know' modal if it appears."""
        try:
            # Check for modal
            modal = self.driver.find_element(
                By.XPATH,
                "//div[@role='dialog']//h2[contains(text(), 'How do you know')]"
            )

            if modal:
                logger.info("'How do you know' modal detected")

                # Select an option (e.g., "Other")
                other_option = self.driver.find_element(
                    By.XPATH,
                    "//button[contains(@aria-label, 'Other')]"
                )
                if other_option:
                    other_option.click()
                    self._human_delay(1, 2)

                    # Click Connect
                    connect_btn = self.driver.find_element(
                        By.XPATH,
                        "//div[@role='dialog']//button[contains(@aria-label, 'Connect')]"
                    )
                    if connect_btn:
                        connect_btn.click()
                        return True

        except NoSuchElementException:
            pass

        return False

    def _add_personalized_note(self, message: str) -> bool:
        """Add personalized note to connection request."""
        try:
            # Click "Add a note" button
            add_note_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(@aria-label, 'Add a note')]")
                )
            )
            add_note_button.click()
            self._human_delay(1, 2)

            # Find message textarea
            message_box = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//textarea[@name='message']")
                )
            )

            # Type message with human-like speed
            self._human_type(message_box, message)
            self._human_delay(1, 2)

            # Send the request
            send_button = self.driver.find_element(
                By.XPATH,
                "//button[contains(@aria-label, 'Send') or contains(text(), 'Send')]"
            )
            send_button.click()

            return True

        except Exception as e:
            logger.error(f"Error adding personalized note: {str(e)}")
            return False

    def _send_without_note(self) -> bool:
        """Send connection request without note."""
        try:
            # Look for Send or Connect button in modal
            send_button = self.driver.find_element(
                By.XPATH,
                "//div[@role='dialog']//button[contains(@aria-label, 'Send') or contains(text(), 'Send')]"
            )
            if send_button:
                send_button.click()
                return True

            # Sometimes it's just a Connect button
            connect_button = self.driver.find_element(
                By.XPATH,
                "//div[@role='dialog']//button[contains(text(), 'Connect')]"
            )
            if connect_button:
                connect_button.click()
                return True

        except NoSuchElementException:
            pass

        return False

    def _get_profile_cards(self) -> List:
        """Get all profile cards on search results page."""
        try:
            # Wait for results to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//ul[contains(@class, 'reusable-search__entity-result-list')]")
                )
            )

            # Find all profile cards
            cards = self.driver.find_elements(
                By.XPATH,
                "//li[contains(@class, 'reusable-search__result-container')]"
            )

            return cards

        except Exception as e:
            logger.error(f"Error getting profile cards: {str(e)}")
            return []

    def _extract_profile_info(self, card) -> Optional[Dict]:
        """Extract profile information from a search result card."""
        try:
            info = {}

            # Get name
            name_element = card.find_element(
                By.XPATH,
                ".//span[contains(@class, 'entity-result__title-text')]//span[@aria-hidden='true']"
            )
            info['name'] = name_element.text if name_element else 'Unknown'

            # Get title/headline
            title_element = card.find_element(
                By.XPATH,
                ".//div[contains(@class, 'entity-result__primary-subtitle')]"
            )
            info['title'] = title_element.text if title_element else ''

            # Get location
            location_element = card.find_element(
                By.XPATH,
                ".//div[contains(@class, 'entity-result__secondary-subtitle')]"
            )
            info['location'] = location_element.text if location_element else ''

            # Get profile URL
            link_element = card.find_element(
                By.XPATH,
                ".//a[contains(@class, 'app-aware-link')]"
            )
            info['profile_url'] = link_element.get_attribute('href') if link_element else ''

            return info

        except Exception as e:
            logger.error(f"Error extracting profile info: {str(e)}")
            return None

    def _should_connect(self, profile_info: Dict) -> bool:
        """Determine if should connect with profile."""
        # Add your filtering logic here
        # For example, check keywords in title, location, etc.
        return True

    def _personalize_message(self, template: str, profile_info: Dict) -> str:
        """Personalize connection message based on profile info."""
        message = template

        # Replace placeholders
        replacements = {
            '{name}': profile_info.get('name', '').split()[0] if profile_info.get('name') else 'there',
            '{title}': profile_info.get('title', 'your role'),
            '{location}': profile_info.get('location', 'your location'),
            '{company}': profile_info.get('company', 'your company')
        }

        for placeholder, value in replacements.items():
            message = message.replace(placeholder, value)

        # Ensure message is within LinkedIn's limit (300 characters)
        if len(message) > 300:
            message = message[:297] + "..."

        return message

    def _send_connection_from_card(self, card, message: str) -> Dict:
        """Send connection request from search result card."""
        try:
            # Find Connect button in card
            connect_button = card.find_element(
                By.XPATH,
                ".//button[contains(text(), 'Connect')]"
            )

            if not connect_button:
                return {'success': False, 'error': 'No connect button in card'}

            # Check if already pending
            if 'pending' in connect_button.text.lower():
                return {'success': False, 'message': 'Already pending'}

            connect_button.click()
            self._human_delay(2, 3)

            # Handle modal and add message
            if self._handle_how_you_know_modal():
                self._human_delay(1, 2)

            if message and self._add_personalized_note(message):
                return {'success': True, 'message': 'Sent with note'}
            elif self._send_without_note():
                return {'success': True, 'message': 'Sent without note'}
            else:
                return {'success': False, 'error': 'Failed to send'}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _follow_from_card(self, card) -> bool:
        """Follow profile from search result card."""
        try:
            follow_button = card.find_element(
                By.XPATH,
                ".//button[contains(text(), 'Follow')]"
            )

            if follow_button and 'following' not in follow_button.text.lower():
                follow_button.click()
                return True

        except:
            pass

        return False

    def _go_to_next_page(self) -> bool:
        """Navigate to next page of search results."""
        try:
            # Scroll to bottom first
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            self._human_delay(2, 3)

            # Find Next button
            next_button = self.driver.find_element(
                By.XPATH,
                "//button[@aria-label='Next']"
            )

            if next_button and next_button.is_enabled():
                next_button.click()
                self._human_delay(3, 5)
                return True

        except NoSuchElementException:
            logger.info("No next page button found")

        return False

    def _get_profile_name(self) -> str:
        """Get name from current profile page."""
        try:
            name_element = self.driver.find_element(
                By.XPATH,
                "//h1[contains(@class, 'text-heading-xlarge')]"
            )
            return name_element.text if name_element else 'Unknown'
        except:
            return 'Unknown'

    def _close_popups(self):
        """Close any popup modals."""
        try:
            # Close messaging popup
            close_buttons = self.driver.find_elements(
                By.XPATH,
                "//button[@aria-label='Dismiss' or @aria-label='Close']"
            )
            for button in close_buttons:
                if button.is_displayed():
                    button.click()
                    self._human_delay(0.5, 1)
        except:
            pass

    def _scroll_to_element(self, element):
        """Scroll element into view."""
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)

    def _human_type(self, element, text: str):
        """Type text with human-like speed."""
        element.clear()
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))

    def _human_delay(self, min_seconds: float, max_seconds: float):
        """Add human-like random delay."""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)

    def get_statistics(self) -> Dict:
        """Get connection statistics."""
        return {
            'connections_sent': self.connections_sent,
            'connections_failed': self.connections_failed,
            'profiles_followed': self.profiles_followed,
            'success_rate': (
                (self.connections_sent / (self.connections_sent + self.connections_failed) * 100)
                if (self.connections_sent + self.connections_failed) > 0 else 0
            )
        }


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
    # connector = ConnectionManager(driver)
    # result = connector.send_connection_request(message="Hi, let's connect!")