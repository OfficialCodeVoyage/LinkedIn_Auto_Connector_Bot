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
LINKEDIN_USERNAME = '#'
LINKEDIN_PASSWORD = '#'

SEARCH_LINK = "https://www.linkedin.com/search/results/people/?geoUrn=%5B%22103644278%22%5D&keywords=tech%20recruiter&origin=FACETED_SEARCH&sid=8VI"
# Base connection message template
BASE_CONNECTION_MESSAGE = """Hi there,

I hope this message finds you well. I'm exploring new opportunities in tech and would love to connect. I have a strong background in Azure Cloud and Software Development, with a focus on Cloud Engineering and AI/ML.

Looking forward to connecting!

Best regards,
Pavlo Bondarenko
"""

XPATH_CONNECT_BUTTON = [
    "/html/body/div[5]/div[3]/div[2]/div/div[1]/main/div/div/div[2]/div/ul/li[1]/div/div/div/div[3]/div/button/span",
    "/html/body/div[5]/div[3]/div[2]/div/div[1]/main/div/div/div[2]/div/ul/li[2]/div/div/div/div[3]/div/button/span",
    "/html/body/div[5]/div[3]/div[2]/div/div[1]/main/div/div/div[2]/div/ul/li[3]/div/div/div/div[3]/div/button/span",
    "/html/body/div[5]/div[3]/div[2]/div/div[1]/main/div/div/div[2]/div/ul/li[4]/div/div/div/div[3]/div/button/span",
    "/html/body/div[5]/div[3]/div[2]/div/div[1]/main/div/div/div[2]/div/ul/li[5]/div/div/div/div[3]/div/button/span",
    "/html/body/div[5]/div[3]/div[2]/div/div[1]/main/div/div/div[2]/div/ul/li[6]/div/div/div/div[3]/div/button/span",
    "/html/body/div[5]/div[3]/div[2]/div/div[1]/main/div/div/div[2]/div/ul/li[7]/div/div/div/div[3]/div/button/span",
    "/html/body/div[5]/div[3]/div[2]/div/div[1]/main/div/div/div[2]/div/ul/li[8]/div/div/div/div[3]/div/button/span",
    "/html/body/div[5]/div[3]/div[2]/div/div[1]/main/div/div/div[2]/div/ul/li[9]/div/div/div/div[3]/div/button/span",
    "/html/body/div[5]/div[3]/div[2]/div/div[1]/main/div/div/div[2]/div/ul/li[10]/div/div/div/div[3]/div/button/span"
]


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


def check_and_click_buttons(driver):
    for xpath in XPATH_CONNECT_BUTTON:
        try:
            button = driver.find_element(By.XPATH, xpath)
            if button.text.lower() in ["connect", "follow", "message"]:
                button.click()
                time.sleep(2)  # Wait for action to complete
                logging.info(f"Clicked {button.text} button.")
            else:
                logging.info(f"No action needed for button with text: {button.text}")
        except NoSuchElementException:
            logging.info(f"No button found for xpath: {xpath}")


def scroll_and_check_buttons(driver):
    scroll_pause_time = 2
    while True:
        # Get the current height
        last_height = driver.execute_script("return document.body.scrollHeight")

        check_and_click_buttons(driver)

        # Scroll down by 100 pixels
        driver.execute_script("window.scrollBy(0, 100);")
        time.sleep(scroll_pause_time)

        # Get the new height and compare with the last height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break  # End of page reached


def go_to_next_page(driver):
    try:
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


if __name__ == "__main__":
    options = Options()
    options.binary_location = 'C:/Program Files/Mozilla Firefox/firefox.exe'
    options.add_argument("--start-fullscreen")

    # Setup the webdriver (Replace the path with the path to your webdriver)
    service = Service('geckodriver32.exe')  # Update with your actual path
    driver = webdriver.Firefox(service=service, options=options)

    try:
        login_to_linkedin(driver, LINKEDIN_USERNAME, LINKEDIN_PASSWORD)
        driver.get(SEARCH_LINK)
        time.sleep(5)  # Wait for the search page to load

        while True:
            scroll_and_check_buttons(driver)
            if not go_to_next_page(driver):
                break  # No more pages left
    finally:
        driver.quit()
