from selenium import webdriver
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
LINKEDIN_USERNAME = 'a@ya'
LINKEDIN_PASSWORD = '1'

# Replace with your search link
SEARCH_LINK = 'https://www.linkedin.com/search/results/people/?keywords=tech%20recruiter&origin=CLUSTER_EXPANSION&searchId=3226caea-b928-4aec-9985-46e505d5f6b7&sid=iRG'

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
    except Exception as e:
        logging.error(f"Error during LinkedIn login: {e}")

def extract_recruiter_name(button):
    try:
        parent_div = button.find_element(By.XPATH, "./ancestor::div[contains(@class, 'entity-result__item')]")
        name_element = parent_div.find_element(By.XPATH, ".//span[contains(@class, 'entity-result__title-text')]/a/span[1]")
        return name_element.text.strip()
    except Exception as e:
        logging.error(f"Error extracting recruiter name: {e}")
        return None

def send_connection_request(driver, button, base_message):
    recruiter_name = extract_recruiter_name(button)
    if recruiter_name:
        message = base_message.format(name=recruiter_name)
    else:
        message = base_message.format(name="there")

    try:
        ActionChains(driver).move_to_element(button).click(button).perform()
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//span[contains(@class, 'artdeco-button__text') and text()='Add a note']")
            )
        )
        add_note_button = driver.find_element(By.XPATH, "//span[contains(@class, 'artdeco-button__text') and text()='Add a note']")
        add_note_button.click()

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "custom-message")))
        note_field = driver.find_element(By.ID, "custom-message")
        note_field.send_keys(message)

        send_button = driver.find_element(By.XPATH, "//span[contains(@class, 'artdeco-button__text') and text()='Send']")
        send_button.click()
        logging.info(f"Connection request sent to {recruiter_name}.")

        time.sleep(10)  # Sleep for 10 seconds after sending each connection request
    except Exception as e:
        logging.error(f"Error sending connection request: {e}")

def go_to_next_page(driver):
    try:
        next_page_button = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//button[contains(@aria-label, 'Next')]"))
        )
        next_page_button.click()
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//li[contains(@class, 'artdeco-pagination__indicator--number') and contains(@class, 'active')]"))
        )
        logging.info("Navigated to the next page")
        time.sleep(5)  # Wait for the new page to load
    except Exception as e:
        logging.error(f"Error navigating to the next page: {e}")
        return False
    return True

def send_connection_requests(driver, search_link, max_requests, base_message):
    driver.get(search_link)
    requests_sent = 0

    while requests_sent < max_requests:
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//span[contains(@class, 'artdeco-button__text') and text()='Connect']"))
            )
        except Exception as e:
            logging.error(f"No Connect button found on this page: {e}")
            if not go_to_next_page(driver):
                break
            continue

        results = driver.find_elements(By.XPATH, "//div[contains(@class, 'entity-result__item')]")

        found_connect_buttons = False

        for result in results:
            if requests_sent >= max_requests:
                break
            try:
                # Check if the "Connect" button is present
                connect_button = result.find_element(By.XPATH, ".//span[contains(@class, 'artdeco-button__text') and text()='Connect']")
                found_connect_buttons = True
                send_connection_request(driver, connect_button, base_message)
                requests_sent += 1
            except Exception as e:
                # Skip if "Message" button is present
                logging.info(f"Skipping already connected or unavailable user: {e}")
                continue

        if not found_connect_buttons:
            logging.info("No Connect buttons found on this page.")
            if not go_to_next_page(driver):
                break

        # Scroll down to load more results
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

if __name__ == "__main__":
    # Setup the Firefox options
    options = Options()
    options.binary_location = 'C:/Program Files/Mozilla Firefox/firefox.exe'  # Update with your actual Firefox binary path

    # Setup the webdriver (Replace the path with the path to your webdriver)
    service = Service('geckodriver.exe')  # Update with your actual path
    driver = webdriver.Firefox(service=service, options=options)

    try:
        login_to_linkedin(driver, LINKEDIN_USERNAME, LINKEDIN_PASSWORD)
        send_connection_requests(driver, SEARCH_LINK, 50, BASE_CONNECTION_MESSAGE)
    finally:
        driver.quit()
