from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
import logging
import time

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Replace with your LinkedIn credentials
LINKEDIN_USERNAME = '#'
LINKEDIN_PASSWORD = '#'

# Replace with your search link
SEARCH_LINK = 'https://www.linkedin.com/search/results/people/?activelyHiringForJobTitles=%5B%22-100%22%5D&geoUrn=%5B%22103644278%22%5D&keywords=tech%20recruiter&origin=FACETED_SEARCH&searchId=3226caea-b928-4aec-9985-46e505d5f6b7&sid=3C5'

# Base connection message template
BASE_CONNECTION_MESSAGE = """Hi {name},

I hope this message finds you well. I'm exploring new opportunities in tech and would love to connect. I have a strong background in Azure Cloud and Software Development, with a focus on Cloud Engineering and AI/ML.

Looking forward to connecting!

Best regards,
Pavlo Bondarenko
"""

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

        WebDriverWait(driver, 20).until(EC.url_contains("/feed"))
        logging.info("Successfully logged into LinkedIn.")
        time.sleep(5)  # Wait for the feed to load
    except Exception as e:
        logging.error(f"Error during LinkedIn login: {e}")

def extract_recruiter_name(result):
    try:
        name_element = result.find_element(By.XPATH, ".//span[contains(@class, 'entity-result__title-text')]//span[1]")
        full_name = name_element.text.strip()
        first_name = full_name.split()[0]
        return first_name
    except Exception as e:
        logging.error(f"Error extracting recruiter name: {e}")
        return None

def process_buttons(driver, base_message, max_requests):
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

                if button_text.lower() == "connect":
                    try:
                        logging.info(f"Found Connect button with text: {button_text}")
                        # Scroll to the "Connect" button
                        ActionChains(driver).move_to_element(button).perform()
                        result = button.find_element(By.XPATH, "../..")  # Assuming the result element is two levels up
                        send_connection_request(driver, result, button, base_message)
                        requests_sent += 1
                        time.sleep(5)  # Sleep for 5 seconds after sending each connection request
                    except Exception as e:
                        logging.info(f"Skipping already connected or unavailable user: {e}")
                        continue
                elif button_text.lower() == "follow":
                    try:
                        logging.info(f"Found Follow button with text: {button_text}")
                        # Scroll to the "Follow" button
                        ActionChains(driver).move_to_element(button).perform()
                        button.click()
                        logging.info(f"Followed user with text: {button_text}")
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

def send_connection_requests(driver, search_link, max_requests, base_message):
    driver.get(search_link)

    while True:
        process_buttons(driver, base_message, max_requests)
        if not go_to_next_page(driver):
            break

def send_connection_request(driver, result, button, base_message):
    recruiter_name = extract_recruiter_name(result)
    if recruiter_name:
        message = base_message.format(name=recruiter_name)
    else:
        message = base_message.format(name="there")

    try:
        ActionChains(driver).move_to_element(button).click(button).perform()
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//button[@aria-label='Add a note']")
            )
        )
        add_note_button = driver.find_element(By.XPATH, "//button[@aria-label='Add a note']")
        add_note_button.click()

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "custom-message")))
        note_field = driver.find_element(By.ID, "custom-message")
        note_field.send_keys(message)
        time.sleep(10)
        send_button = driver.find_element(By.XPATH, "//span[contains(@class, 'artdeco-button__text') and text()='Send']")
        send_button.click()
        logging.info(f"Connection request sent to {recruiter_name}.")

        time.sleep(10)  # Sleep for 10 seconds after sending each connection request
    except Exception as e:
        logging.error(f"Error sending connection request: {e}")

def go_to_next_page(driver):
    try:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")   # Scroll down
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
