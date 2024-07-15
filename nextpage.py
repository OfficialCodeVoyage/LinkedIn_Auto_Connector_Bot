from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
import logging
import time

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Replace with your LinkedIn credentials
LINKEDIN_USERNAME = '#@#.com'
LINKEDIN_PASSWORD = '#'

# Replace with your search link
SEARCH_LINK = 'https://www.linkedin.com/search/results/people/?keywords=tech%20recruiter&origin=CLUSTER_EXPANSION&searchId=3226caea-b928-4aec-9985-46e505d5f6b7&sid=iRG'

def login_to_linkedin(driver, username, password):
    try:
        driver.get("https://www.linkedin.com/login")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username")))

        # Enter username
        username_field = driver.find_element(By.ID, "username")
        username_field.send_keys(username)

        # Enter password
        password_field = driver.find_element(By.ID, "password")
        password_field.send_keys(password)
        password_field.send_keys(Keys.RETURN)

        WebDriverWait(driver, 10).until(EC.url_contains("/feed"))
        logging.info("Successfully logged into LinkedIn.")
    except Exception as e:
        logging.error(f"Error during LinkedIn login: {e}")

def go_to_next_page(driver):
    try:
        next_page_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//button[contains(@aria-label, 'Next')]"))
        )
        next_page_button.click()
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//li[contains(@class, 'artdeco-pagination__indicator--number') and contains(@class, 'active')]"))
        )
        logging.info("Navigated to the next page")
    except Exception as e:
        logging.error(f"Error navigating to the next page: {e}")

if __name__ == "__main__":
    # Setup the Firefox options
    options = Options()
    options.binary_location = 'C:/Program Files/Mozilla Firefox/firefox.exe'  # Update with your actual Firefox binary path

    # Setup the webdriver (Replace the path with the path to your webdriver)
    service = Service('geckodriver.exe')  # Update with your actual path
    driver = webdriver.Firefox(service=service, options=options)

    try:
        login_to_linkedin(driver, LINKEDIN_USERNAME, LINKEDIN_PASSWORD)
        driver.get(SEARCH_LINK)

        for _ in range(5):  # Navigate through 5 pages as a test
            time.sleep(10)  # Wait for 10 seconds
            go_to_next_page(driver)
    finally:
        driver.quit()
