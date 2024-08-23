"""
This script is a LinkedIn bot that automatically sends connection requests with a custom note to profiles on LinkedIn.
It uses the Selenium WebDriver to navigate LinkedIn and interact with the UI elements.
Do 100 requests per week!!!!!
If not, LinkedIn will block your account.
Add my LinkedIn also - https://www.linkedin.com/in/mrbondarenko/
Replace your search link with keywords you need!
Go to LinkedIn main page, press on the search bar, put the keywords you need(Tech Recruter or Cloud Engineer for example),
press enter, select people only! copy the link and paste it in the SEARCH_LINK variable.
 Have fun!
"""

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException, MoveTargetOutOfBoundsException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
import logging
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Replace with your LinkedIn credentials
LINKEDIN_USERNAME = '#' # your email
LINKEDIN_PASSWORD = '#' # your password

SEARCH_LINK = ("https://www.linkedin.com/search/results/people/?geoUrn=%5B%22103644278%22%5D&keywords=technical%20software%20recruiter&origin=FACETED_SEARCH&page=26&sid=h)4")
# Base connection message template
BASE_CONNECTION_MESSAGE = """Hi there,

I hope this message finds you well. I'm exploring new opportunities in tech and would love to connect. I have a strong background in Azure Cloud and Software Development, with a focus on Cloud Engineering and AI/ML.

Looking forward to connecting!

Best regards,
Pavlo Bondarenko
"""

MAX_CONNECT_REQUESTS = 20  # Limit for connection requests

def login_to_linkedin(driver, username, password):
    try:
        driver.get("https://www.linkedin.com/login")
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "username")))

        # Enter username
        username_field = driver.find_element(By.ID, "username")
        username_field.send_keys(username)

        # Enter password
        password_field = driver.find_element(By.ID, "password")
        password_field.send_keys(password)
        password_field.send_keys(Keys.RETURN)
        time.sleep(5)  # Wait for the page to load or enter captcha
        WebDriverWait(driver, 20).until(EC.url_contains("/feed"))
        logging.info("Successfully logged into LinkedIn.")
        time.sleep(5)  # Wait for the feed to load
    except Exception as e:
        logging.error(f"Error during LinkedIn login: {e}")

def go_to_next_page(driver):
    try:
        time.sleep(5)  # Wait for the page to load
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")  # Scroll down
        next_page_button = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//button[@aria-label='Next']"))
        )
        next_page_button.click()
        logging.info("Navigated to the next page")
        time.sleep(5)  # Wait for the new page to load
    except NoSuchElementException as e:
        logging.error(f"Element not found: {e}")
        return False
    except Exception as e:
        logging.error(f"Error navigating to the next page: {e}")
        return False
    return True

def scrool_down(driver):
    try:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")  # Scroll down
        time.sleep(5)  # Wait for the page to load
    except Exception as e:
        logging.error(f"Error during scrolling down: {e}")

def handle_connect_button(driver, button):
    try:
        button.click()
        time.sleep(2)  # Wait for the connect modal to appear

        # Click "Add a note"
        add_note_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//button[@aria-label='Add a note']"))
        )
        add_note_button.click()
        time.sleep(2)

        # Paste the custom message
        message_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//textarea[@name='message']"))
        )
        message_box.send_keys(BASE_CONNECTION_MESSAGE)
        time.sleep(2)

        # Click "Send"
        send_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//span[contains(@class, 'artdeco-button__text') and text()='Send']"))
        )
        send_button.click()
        logging.info("Sent connection request with a custom note.")
        time.sleep(2)
    except Exception as e:
        logging.error(f"Error handling 'Connect' button: {e}")

def handle_follow_button(button):
    try:
        button.click()
        logging.info("Followed the user.")
        time.sleep(1)
    except Exception as e:
        logging.error(f"Error handling 'Follow' button: {e}")

def process_buttons(driver):
    try:
        # Navigate to the search page
        driver.get(SEARCH_LINK)
        scrool_down(driver)
        time.sleep(5)

        connect_requests_sent = 0

        working = True


        while working:
            # Find all buttons on the page
            buttons = driver.find_elements(By.TAG_NAME, "button")

            # Count "Connect" and "Follow" buttons
            connect_buttons_count = sum(1 for button in buttons if button.text.strip().lower() == "connect")
            follow_buttons_count = sum(1 for button in buttons if button.text.strip().lower() == "follow")
            logging.info(f"Total 'Connect' buttons on the page: {connect_buttons_count}")
            logging.info(f"Total 'Follow' buttons on the page: {follow_buttons_count}")

            # Process each "Connect" and "Follow" button
            for button in buttons:
                button_text = button.text.strip().lower()
                if button_text == "connect" and connect_requests_sent < MAX_CONNECT_REQUESTS:
                    handle_connect_button(driver, button)
                    connect_requests_sent += 1
                    if connect_requests_sent >= MAX_CONNECT_REQUESTS:
                        logging.info(
                            f"Reached the limit of {MAX_CONNECT_REQUESTS} connection requests. Stopping connection requests.")
                        working = False
                        break
                    time.sleep(5)
                elif button_text == "follow":
                    handle_follow_button(button)
                    time.sleep(5)

            # Attempt to navigate to the next page
            if not go_to_next_page(driver):
                logging.info("No more pages to process. Exiting.")
                break

            # Scroll down to load all elements on the new page
            scrool_down(driver)
            time.sleep(5)

    except Exception as e:
        logging.error(f"Error while processing buttons: {e}")

if __name__ == "__main__":
    options = Options()
    options.binary_location = 'C:/Program Files/Mozilla Firefox/firefox.exe' ## path to your firefox browser(must install firefox browser)

    # Set up the webdriver (Replace the path with the path to your webdriver) // mine is geckodriver32.exe already installed in the directory
    # go to https://github.com/mozilla/geckodriver/releases to download latest version of geckodriver
    service = Service('geckodriver32.exe')
    driver = webdriver.Firefox(service=service, options=options)

    try:
        login_to_linkedin(driver, LINKEDIN_USERNAME, LINKEDIN_PASSWORD)
        process_buttons(driver)
    finally:
        driver.quit()
