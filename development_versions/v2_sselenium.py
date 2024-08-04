from selenium import webdriver
from selenium.common.exceptions import (NoSuchElementException, TimeoutException,
                                        MoveTargetOutOfBoundsException, ElementClickInterceptedException,
                                        ElementNotInteractableException, StaleElementReferenceException)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
import logging
import time
from typing import Optional

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Replace with your LinkedIn credentials
LINKEDIN_USERNAME = '#'
LINKEDIN_PASSWORD = '#'

# Replace with your search link
SEARCH_LINK = 'https://www.linkedin.com/search/results/people/?activelyHiringForJobTitles=%5B%22-100%22%5D&geoUrn=%5B%22103644278%22%5D&keywords=tech%20recruiter&origin=FACETED_SEARCH&searchId=3226caea-b928-4aec-9985-46e505d5f6b7&sid=3C5'

# Base connection message template
BASE_CONNECTION_MESSAGE = """Hi there,

I hope this message finds you well. I'm exploring new opportunities in tech and would love to connect. I have a strong background in Azure Cloud and Software Development, with a focus on Cloud Engineering and AI/ML.

Looking forward to connecting!

Best regards,
Pavlo Bondarenko
"""

def login_to_linkedin(driver: webdriver.Firefox, username: str, password: str) -> None:
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

        WebDriverWait(driver, 20).until(EC.url_contains("/feed"))
        logging.info("Successfully logged into LinkedIn.")
        time.sleep(5)  # Wait for the feed to load
    except Exception as e:
        logging.error(f"Error during LinkedIn login: {e}")

def process_buttons(driver: webdriver.Firefox, base_message: str, max_requests: int) -> None:
    requests_sent = 0
    buttons_processed = 0

    while buttons_processed < 10:
        try:
            buttons = driver.find_elements(By.XPATH, "//div[contains(@class, 'entity-result__actions')]/div/button")
            if not buttons:
                logging.info("No buttons found on this page.")
                break

            for button in buttons:
                if requests_sent >= max_requests:
                    break

                # Check the text content of the button
                try:
                    button_text = button.find_element(By.TAG_NAME, 'span').text.strip()
                except NoSuchElementException:
                    logging.info("No span element found in the button, skipping.")
                    continue

                logging.info(f"Button text: {button_text}")

                try:
                    driver.execute_script("arguments[0].scrollIntoView(true);", button)
                    time.sleep(1)  # Ensure the element is in view
                except MoveTargetOutOfBoundsException:
                    logging.info(f"Move target out of bounds for button with text: {button_text}")
                    continue

                if button_text.lower() == "connect":
                    if not retry_click(driver, button):
                        continue
                    try:
                        logging.info(f"Found Connect button with text: {button_text}")
                        send_connection_request(driver, button, base_message)
                        requests_sent += 1
                        print(requests_sent)
                        time.sleep(5)  # Sleep for 5 seconds after sending each connection request
                    except Exception as e:
                        logging.info(f"Skipping already connected or unavailable user: {e}")
                        continue
                elif button_text.lower() == "follow":
                    if not retry_click(driver, button):
                        continue
                    try:
                        logging.info(f"Found Follow button with text: {button_text}")
                        button.click()
                        logging.info(f"Followed user with text: {button_text}")
                        print(requests_sent)
                        time.sleep(5)  # Sleep for 5 seconds after following each user
                    except Exception as e:
                        logging.info(f"Error following user: {e}")
                        continue
                elif button_text.lower() == "message":
                    logging.info(f"Skipping user with Message button: {button_text}")
                    continue  # Skip users with the Message button

                buttons_processed += 1
                if buttons_processed >= 10:
                    break

        except TimeoutException:
            logging.error(f"Timeout while processing buttons.")
            break

        if not go_to_next_page(driver):
            break

def retry_click(driver: webdriver.Firefox, element: webdriver.remote.webelement.WebElement, retries: int = 3, delay: int = 2) -> bool:
    for attempt in range(retries):
        try:
            driver.execute_script("arguments[0].scrollIntoView(true);", element)
            time.sleep(1)  # Ensure the element is in view
            element.click()
            return True
        except ElementClickInterceptedException:
            backoff_time = delay * (2 ** attempt)  # Exponential backoff
            logging.warning(f"Attempt {attempt + 1}/{retries}: Element click intercepted, retrying in {backoff_time} seconds...")
            close_modal_if_present(driver)
            time.sleep(backoff_time)
        except ElementNotInteractableException:
            backoff_time = delay * (2 ** attempt)  # Exponential backoff
            logging.warning(f"Attempt {attempt + 1}/{retries}: Element not interactable, retrying in {backoff_time} seconds...")
            time.sleep(backoff_time)
        except StaleElementReferenceException:
            backoff_time = delay * (2 ** attempt)  # Exponential backoff
            logging.warning(f"Attempt {attempt + 1}/{retries}: Stale element reference, retrying in {backoff_time} seconds...")
            time.sleep(backoff_time)
    logging.error(f"Failed to click the element after {retries} attempts.")
    return False

def close_modal_if_present(driver: webdriver.Firefox) -> None:
    try:
        modal_close_buttons = driver.find_elements(By.XPATH, "//button[@aria-label='Dismiss'] | //button[@class='artdeco-modal__dismiss'] | //button[@class='artdeco-hoverable-content__close-btn']")
        for close_button in modal_close_buttons:
            if close_button.is_displayed():
                driver.execute_script("arguments[0].scrollIntoView(true);", close_button)
                time.sleep(1)
                close_button.click()
                logging.info("Closed a modal dialog.")
                time.sleep(2)
    except NoSuchElementException:
        logging.info("No modal dialog found to close.")
    except ElementNotInteractableException:
        logging.info("Modal dialog found but not interactable.")
    except Exception as e:
        logging.error(f"Error closing modal dialog: {e}")

def send_connection_requests(driver: webdriver.Firefox, search_link: str, max_requests: int, base_message: str) -> None:
    driver.get(search_link)

    while True:
        process_buttons(driver, base_message, max_requests)
        if not go_to_next_page(driver):
            break

def send_connection_request(driver: webdriver.Firefox, button: webdriver.remote.webelement.WebElement, base_message: str) -> None:
    try:
        button.click()
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//button[@aria-label='Add a note']")
            )
        )
        add_note_button = driver.find_element(By.XPATH, "//button[@aria-label='Add a note']")
        add_note_button.click()

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "custom-message")))
        note_field = driver.find_element(By.ID, "custom-message")
        note_field.send_keys(base_message)

        send_button = driver.find_element(By.XPATH, "//span[contains(@class, 'artdeco-button__text') and text()='Send']")
        send_button.click()
        logging.info(f"Connection request sent.")

        time.sleep(10)  # Sleep for 10 seconds after sending each connection request
    except NoSuchElementException as e:
        logging.error(f"Error sending connection request - No such element: {e}")
    except TimeoutException as e:
        logging.error(f"Error sending connection request - Timeout: {e}")
    except ElementClickInterceptedException as e:
        logging.error(f"Error sending connection request - Element click intercepted: {e}")
        close_modal_if_present(driver)
    except ElementNotInteractableException as e:
        logging.error(f"Error sending connection request - Element not interactable: {e}")
    except StaleElementReferenceException as e:
        logging.error(f"Error sending connection request - Stale element reference: {e}")
    except Exception as e:
        logging.error(f"Error sending connection request: {e}")

def go_to_next_page(driver: webdriver.Firefox) -> bool:
    try:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")   # Scroll down
        next_page_button = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//button[@aria-label='Next']"))
        )
        next_page_button.click()
        logging.info("Navigated to the next page")
        time.sleep(5)  # Wait for the new page to load
    except (NoSuchElementException, ElementClickInterceptedException) as e:
        logging.error(f"Element not found or not clickable: {e}")
        close_modal_if_present(driver)
        return False
    except Exception as e:
        logging.error(f"Error navigating to the next page: {e}")
        return False
    return True

if __name__ == "__main__":
    options = Options()
    options.binary_location = 'C:/Program Files/Mozilla Firefox/firefox.exe'

    # Setup the webdriver (Replace the path with the path to your webdriver)
    service = Service('geckodriver32.exe')  # Update with your actual path
    driver = webdriver.Firefox(service=service, options=options)

    try:
        login_to_linkedin(driver, LINKEDIN_USERNAME, LINKEDIN_PASSWORD)
        send_connection_requests(driver, SEARCH_LINK, 50, BASE_CONNECTION_MESSAGE)
    finally:
        driver.quit()
