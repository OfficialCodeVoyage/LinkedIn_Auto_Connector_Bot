from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Replace with your LinkedIn credentials
LINKEDIN_USERNAME = 'your_username'
LINKEDIN_PASSWORD = 'your_password'

# Replace with your search link
SEARCH_LINK = 'your_search_link'

# Connection message
CONNECTION_MESSAGE = "Hi, I'd like to connect with you on LinkedIn!"


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


def send_connection_request(driver, button, message):
    try:
        ActionChains(driver).move_to_element(button).click(button).perform()
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                (By.XPATH, "//button[contains(@class, 'artdeco-button--secondary') and text()='Add a note']"))
        )
        add_note_button = driver.find_element(By.XPATH,
                                              "//button[contains(@class, 'artdeco-button--secondary') and text()='Add a note']")
        add_note_button.click()

        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "custom-message")))
        note_field = driver.find_element(By.ID, "custom-message")
        note_field.send_keys(message)

        send_button = driver.find_element(By.XPATH,
                                          "//button[contains(@class, 'artdeco-button--primary') and text()='Send']")
        send_button.click()
        logging.info("Connection request sent.")
    except Exception as e:
        logging.error(f"Error sending connection request: {e}")


def send_connection_requests(driver, search_link, max_requests, message):
    driver.get(search_link)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(
        (By.XPATH, "//button[contains(@class, 'artdeco-button--2') and text()='Connect']")))

    requests_sent = 0
    while requests_sent < max_requests:
        connect_buttons = driver.find_elements(By.XPATH,
                                               "//button[contains(@class, 'artdeco-button--2') and text()='Connect']")

        if not connect_buttons:
            logging.info("No more connect buttons found.")
            break

        for button in connect_buttons:
            if requests_sent >= max_requests:
                break
            send_connection_request(driver, button, message)
            requests_sent += 1

        # Scroll down to load more results
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                (By.XPATH, "//button[contains(@class, 'artdeco-button--2') and text()='Connect']"))
        )


if __name__ == "__main__":
    # Setup the webdriver (Replace the path with the path to your webdriver)
    driver = webdriver.Chrome(executable_path='/path/to/chromedriver')

    try:
        login_to_linkedin(driver, LINKEDIN_USERNAME, LINKEDIN_PASSWORD)
        send_connection_requests(driver, SEARCH_LINK, 50, CONNECTION_MESSAGE)
    finally:
        driver.quit()
