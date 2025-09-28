"""
Anti-detection utilities for LinkedIn Auto Connector Bot.

This module provides various techniques to avoid bot detection including
browser fingerprinting, human-like behavior simulation, and stealth measures.
"""

import random
import time
import logging
from typing import Dict, List, Optional, Tuple
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
import numpy as np

logger = logging.getLogger(__name__)


class StealthBrowser:
    """
    Creates and configures a stealth browser instance with anti-detection features.
    """

    def __init__(self, browser_type: str = "chrome", config: Optional[Dict] = None):
        """
        Initialize StealthBrowser.

        Args:
            browser_type: Type of browser ('chrome' or 'firefox')
            config: Optional configuration dictionary
        """
        self.browser_type = browser_type.lower()
        self.config = config or {}
        self.user_agents = self._load_user_agents()

    def _load_user_agents(self) -> List[str]:
        """Load list of realistic user agents."""
        return [
            # Chrome on Windows
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            # Chrome on Mac
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            # Firefox on Windows
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:119.0) Gecko/20100101 Firefox/119.0",
            # Firefox on Mac
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0",
            # Safari on Mac
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15"
        ]

    def create_driver(self, headless: bool = False) -> webdriver.Chrome:
        """
        Create a configured WebDriver with anti-detection features.

        Args:
            headless: Whether to run in headless mode

        Returns:
            Configured WebDriver instance
        """
        if self.browser_type == "chrome":
            return self._create_chrome_driver(headless)
        elif self.browser_type == "firefox":
            return self._create_firefox_driver(headless)
        else:
            raise ValueError(f"Unsupported browser type: {self.browser_type}")

    def _create_chrome_driver(self, headless: bool) -> webdriver.Chrome:
        """Create stealth Chrome driver."""
        options = ChromeOptions()

        # Randomize window size
        width = random.randint(1200, 1920)
        height = random.randint(800, 1080)
        options.add_argument(f'--window-size={width},{height}')

        # Anti-detection arguments
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        # Disable webdriver flag
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")

        # Random user agent
        user_agent = random.choice(self.user_agents)
        options.add_argument(f'user-agent={user_agent}')

        # Additional privacy settings
        prefs = {
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
            "profile.default_content_setting_values.notifications": 2,
            "profile.default_content_setting_values.geolocation": 2
        }
        options.add_experimental_option("prefs", prefs)

        if headless:
            options.add_argument('--headless=new')
            # Additional headless detection bypass
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-software-rasterizer')

        # Create driver
        driver = webdriver.Chrome(options=options)

        # Execute CDP commands to override navigator properties
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                // Override webdriver property
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });

                // Override plugins to look more realistic
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [
                        {
                            0: {type: "application/x-google-chrome-pdf", suffixes: "pdf", description: "Portable Document Format"},
                            description: "Portable Document Format",
                            filename: "internal-pdf-viewer",
                            length: 1,
                            name: "Chrome PDF Plugin"
                        }
                    ]
                });

                // Override permissions
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );

                // Override chrome runtime
                window.chrome = {
                    runtime: {},
                    loadTimes: function() {},
                    csi: function() {},
                    app: {}
                };

                // Override language and platform if needed
                Object.defineProperty(navigator, 'language', {
                    get: () => 'en-US'
                });
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en']
                });
            '''
        })

        logger.info(f"Created stealth Chrome driver with size {width}x{height}")
        return driver

    def _create_firefox_driver(self, headless: bool) -> webdriver.Firefox:
        """Create stealth Firefox driver."""
        options = FirefoxOptions()

        # Randomize window size
        width = random.randint(1200, 1920)
        height = random.randint(800, 1080)
        options.add_argument(f'--width={width}')
        options.add_argument(f'--height={height}')

        # Set user agent
        user_agent = random.choice(self.user_agents)
        options.set_preference("general.useragent.override", user_agent)

        # Disable telemetry and tracking
        options.set_preference("toolkit.telemetry.unified", False)
        options.set_preference("privacy.trackingprotection.enabled", True)

        # Disable WebDriver flags
        options.set_preference("dom.webdriver.enabled", False)
        options.set_preference('useAutomationExtension', False)

        if headless:
            options.add_argument('--headless')

        driver = webdriver.Firefox(options=options)

        # Execute script to override navigator properties
        driver.execute_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)

        logger.info(f"Created stealth Firefox driver with size {width}x{height}")
        return driver


class HumanBehaviorSimulator:
    """
    Simulates human-like behavior for browser interactions.
    """

    def __init__(self, driver):
        """
        Initialize HumanBehaviorSimulator.

        Args:
            driver: Selenium WebDriver instance
        """
        self.driver = driver
        self.actions = ActionChains(driver)

    def human_like_mouse_movement(self, element, duration: float = 1.0):
        """
        Move mouse to element with human-like curve.

        Args:
            element: Target WebElement
            duration: Duration of movement in seconds
        """
        try:
            # Get current mouse position (approximate)
            viewport_width = self.driver.execute_script("return window.innerWidth")
            viewport_height = self.driver.execute_script("return window.innerHeight")

            start_x = random.randint(100, viewport_width - 100)
            start_y = random.randint(100, viewport_height - 100)

            # Get element position
            location = element.location_once_scrolled_into_view
            size = element.size
            end_x = location['x'] + size['width'] // 2
            end_y = location['y'] + size['height'] // 2

            # Generate curved path
            points = self._generate_bezier_curve(start_x, start_y, end_x, end_y)

            # Move mouse along path
            action_chains = ActionChains(self.driver)
            for x, y in points:
                action_chains.move_by_offset(x - start_x, y - start_y)
                start_x, start_y = x, y

            action_chains.perform()
            time.sleep(random.uniform(0.1, 0.3))

        except Exception as e:
            logger.error(f"Error in mouse movement: {str(e)}")
            # Fallback to simple move
            ActionChains(self.driver).move_to_element(element).perform()

    def human_like_typing(self, element, text: str):
        """
        Type text with human-like speed and patterns.

        Args:
            element: Input element
            text: Text to type
        """
        element.click()
        element.clear()

        for i, char in enumerate(text):
            element.send_keys(char)

            # Variable typing speed
            base_delay = random.uniform(0.05, 0.15)

            # Occasionally longer pauses (thinking)
            if random.random() < 0.1:
                time.sleep(random.uniform(0.5, 1.5))
            # Faster for common words
            elif i > 0 and text[i-1] == ' ':
                time.sleep(base_delay * 0.5)
            else:
                time.sleep(base_delay)

            # Occasional typos and corrections
            if random.random() < 0.02 and i < len(text) - 1:
                wrong_char = random.choice('abcdefghijklmnopqrstuvwxyz')
                element.send_keys(wrong_char)
                time.sleep(0.3)
                element.send_keys('\ue003')  # Backspace

    def random_scrolling(self):
        """Perform random scrolling behavior."""
        # Decide scroll direction and amount
        scroll_amount = random.randint(100, 500)
        direction = random.choice([1, -1])

        # Smooth scrolling
        steps = random.randint(3, 7)
        for _ in range(steps):
            self.driver.execute_script(
                f"window.scrollBy(0, {(scroll_amount // steps) * direction})"
            )
            time.sleep(random.uniform(0.1, 0.3))

        # Random pause after scrolling
        time.sleep(random.uniform(1, 3))

    def random_mouse_movement(self):
        """Perform random mouse movements."""
        viewport_width = self.driver.execute_script("return window.innerWidth")
        viewport_height = self.driver.execute_script("return window.innerHeight")

        # Random movement pattern
        movements = random.randint(2, 5)
        action_chains = ActionChains(self.driver)

        for _ in range(movements):
            x = random.randint(-200, 200)
            y = random.randint(-200, 200)
            action_chains.move_by_offset(x, y)
            action_chains.pause(random.uniform(0.1, 0.5))

        action_chains.perform()

    def simulate_reading(self, duration: float = None):
        """
        Simulate reading behavior with scrolling and pauses.

        Args:
            duration: Reading duration in seconds (random if None)
        """
        if duration is None:
            duration = random.uniform(3, 10)

        start_time = time.time()

        while time.time() - start_time < duration:
            # Random scroll
            if random.random() < 0.3:
                self.random_scrolling()

            # Random mouse movement
            if random.random() < 0.2:
                self.random_mouse_movement()

            # Random pause
            time.sleep(random.uniform(0.5, 2))

    def _generate_bezier_curve(self, x1: float, y1: float, x2: float, y2: float, num_points: int = 20) -> List[Tuple[float, float]]:
        """
        Generate points along a Bezier curve for smooth movement.

        Args:
            x1, y1: Start coordinates
            x2, y2: End coordinates
            num_points: Number of points to generate

        Returns:
            List of (x, y) coordinates
        """
        # Generate control points for natural curve
        cx1 = x1 + random.uniform(-100, 100)
        cy1 = y1 + random.uniform(-100, 100)
        cx2 = x2 + random.uniform(-100, 100)
        cy2 = y2 + random.uniform(-100, 100)

        points = []
        for i in range(num_points + 1):
            t = i / num_points

            # Cubic Bezier curve formula
            x = (1-t)**3 * x1 + 3*(1-t)**2 * t * cx1 + 3*(1-t) * t**2 * cx2 + t**3 * x2
            y = (1-t)**3 * y1 + 3*(1-t)**2 * t * cy1 + 3*(1-t) * t**2 * cy2 + t**3 * y2

            points.append((x, y))

        return points


class ProxyManager:
    """
    Manages proxy rotation and configuration for browsers.
    """

    def __init__(self, proxy_list: Optional[List[str]] = None):
        """
        Initialize ProxyManager.

        Args:
            proxy_list: Optional list of proxy addresses
        """
        self.proxy_list = proxy_list or []
        self.current_proxy_index = 0

    def get_next_proxy(self) -> Optional[str]:
        """
        Get next proxy from the list.

        Returns:
            Proxy address or None if no proxies available
        """
        if not self.proxy_list:
            return None

        proxy = self.proxy_list[self.current_proxy_index]
        self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxy_list)

        logger.info(f"Using proxy: {proxy}")
        return proxy

    def configure_chrome_proxy(self, options: ChromeOptions, proxy: str):
        """
        Configure Chrome options with proxy.

        Args:
            options: Chrome options object
            proxy: Proxy address
        """
        if proxy:
            options.add_argument(f'--proxy-server={proxy}')
            logger.info(f"Configured Chrome with proxy: {proxy}")

    def configure_firefox_proxy(self, options: FirefoxOptions, proxy: str):
        """
        Configure Firefox options with proxy.

        Args:
            options: Firefox options object
            proxy: Proxy address (format: host:port)
        """
        if proxy and ':' in proxy:
            host, port = proxy.split(':')
            options.set_preference("network.proxy.type", 1)
            options.set_preference("network.proxy.http", host)
            options.set_preference("network.proxy.http_port", int(port))
            options.set_preference("network.proxy.ssl", host)
            options.set_preference("network.proxy.ssl_port", int(port))
            logger.info(f"Configured Firefox with proxy: {proxy}")

    def test_proxy(self, proxy: str) -> bool:
        """
        Test if proxy is working.

        Args:
            proxy: Proxy address to test

        Returns:
            True if proxy works, False otherwise
        """
        import requests

        try:
            response = requests.get(
                'http://httpbin.org/ip',
                proxies={'http': proxy, 'https': proxy},
                timeout=10
            )
            if response.status_code == 200:
                logger.info(f"Proxy {proxy} is working")
                return True
        except Exception as e:
            logger.error(f"Proxy {proxy} failed: {str(e)}")

        return False


class BehaviorRandomizer:
    """
    Randomizes various behavioral parameters to avoid patterns.
    """

    @staticmethod
    def get_random_delay(min_seconds: float = 1, max_seconds: float = 5) -> float:
        """Get randomized delay duration."""
        return random.uniform(min_seconds, max_seconds)

    @staticmethod
    def get_random_window_size() -> Tuple[int, int]:
        """Get randomized window dimensions."""
        widths = [1280, 1366, 1440, 1536, 1920]
        heights = [720, 768, 900, 1080]

        width = random.choice(widths)
        height = random.choice(heights)

        # Add small random variation
        width += random.randint(-50, 50)
        height += random.randint(-50, 50)

        return width, height

    @staticmethod
    def should_perform_action(probability: float = 0.5) -> bool:
        """Randomly decide whether to perform an action."""
        return random.random() < probability

    @staticmethod
    def get_random_timezone() -> str:
        """Get random timezone for browser."""
        timezones = [
            'America/New_York',
            'America/Chicago',
            'America/Denver',
            'America/Los_Angeles',
            'Europe/London',
            'Europe/Paris',
            'Europe/Berlin',
            'Asia/Tokyo',
            'Asia/Shanghai',
            'Australia/Sydney'
        ]
        return random.choice(timezones)

    @staticmethod
    def get_random_language() -> str:
        """Get random language setting."""
        languages = [
            'en-US',
            'en-GB',
            'en-CA',
            'en-AU',
            'es-ES',
            'fr-FR',
            'de-DE',
            'it-IT',
            'pt-BR',
            'ja-JP'
        ]
        return random.choice(languages)


# Example usage
if __name__ == "__main__":
    # Configure logging for testing
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Create stealth browser
    stealth = StealthBrowser(browser_type="chrome")

    # Example of behavior randomizer
    randomizer = BehaviorRandomizer()
    print(f"Random delay: {randomizer.get_random_delay()} seconds")
    print(f"Random window size: {randomizer.get_random_window_size()}")
    print(f"Should perform action: {randomizer.should_perform_action(0.7)}")