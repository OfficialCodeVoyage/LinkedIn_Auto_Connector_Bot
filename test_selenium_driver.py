import os
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options

def check_geckodriver_executable(geckodriver_path):
    if not os.path.isfile(geckodriver_path):
        raise FileNotFoundError(f"Geckodriver not found at {geckodriver_path}. Please ensure the path is correct.")

def setup_firefox_driver(geckodriver_path):
    check_geckodriver_executable(geckodriver_path)
    service = Service(executable_path=geckodriver_path)
    options = Options()
    # Add any necessary options here
    # options.headless = True  # Uncomment if you want to run in headless mode
    return webdriver.Firefox(service=service, options=options)

def main():
    geckodriver_path = "geckodriver32.exe"
    try:
        driver = setup_firefox_driver(geckodriver_path)
        driver.get("https://www.linkedin.com")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if 'driver' in locals():
            driver.quit()

if __name__ == "__main__":
    main()
