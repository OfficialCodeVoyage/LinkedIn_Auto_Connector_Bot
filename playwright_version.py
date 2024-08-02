import os
import time
from playwright.sync_api import sync_playwright


# Environment variables for security
LINKEDIN_EMAIL = "#@yahoo.com"
LINKEDIN_PASSWORD = "#"
TARGET_SEARCH_URL = 'https://www.linkedin.com/search/results/people/?activelyHiringForJobTitles=%5B%22-100%22%5D&geoUrn=%5B%22103644278%22%5D&keywords=tech%20recruiter&origin=FACETED_SEARCH&searchId=3226caea-b928-4aec-9985-46e505d5f6b7&sid=3C5'


def login_linkedin(page):
    page.goto("https://www.linkedin.com/login")
    page.fill("input#username", LINKEDIN_EMAIL)
    page.fill("input#password", LINKEDIN_PASSWORD)
    page.click("button[type='submit']")

    # Wait for a reliable element after login
    try:
        page.wait_for_selector("div.feed-identity-module", timeout=45000)
        print("Logged in successfully")
    except Exception as e:
        page.screenshot(path="login_error_screenshot.png")
        print(f"Login failed, screenshot saved as login_error_screenshot.png: {e}")


def process_profile(profile):
    # Check for Connect, Follow, or Message button using the span text
    if profile.query_selector("span.artdeco-button__text:has-text('Connect')"):
        connect_button = profile.query_selector("span.artdeco-button__text:has-text('Connect')")
        connect_button.click()
        page.wait_for_selector("button:has-text('Add a note')")
        page.click("button:has-text('Add a note')")
        page.fill("textarea[name='message']", "Hello, I'd like to connect with you on LinkedIn!")
        page.click("button:has-text('Send')")
        print("Connection request sent.")
    elif profile.query_selector("span.artdeco-button__text:has-text('Follow')"):
        follow_button = profile.query_selector("span.artdeco-button__text:has-text('Follow')")
        follow_button.click()
        print("Followed the user.")
    else:
        print("Skipped profile with Message button or no actionable button.")
    time.sleep(2)  # Pause to mimic human behavior


def process_search_results(page):
    # Use a more specific selector for the search results container
    container = page.query_selector("div.search-results-container")
    if container:
        profiles = container.query_selector_all("div.search-result__info")
        for profile in profiles:
            process_profile(profile, page)
    else:
        print("Search results container not found.")


def navigate_pagination(page):
    while True:
        process_search_results(page)
        next_button = page.query_selector("button:has-text('Next')")
        if next_button:
            next_button.click()
            # Use a more robust load state or custom wait condition
            try:
                page.wait_for_selector("div.search-result__info", timeout=45000)
            except Exception as e:
                print(f"Failed to load next page: {e}")
                break
            time.sleep(3)  # Allow some time for the next page to load
        else:
            break  # No more pages to process


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        login_linkedin(page)
        page.goto(TARGET_SEARCH_URL)
        try:
            page.wait_for_selector("div.search-result__info", timeout=45000)
        except Exception as e:
            page.screenshot(path="search_page_load_error.png")
            print(f"Search page load failed, screenshot saved as search_page_load_error.png: {e}")
            browser.close()
            return

        navigate_pagination(page)
        print("Processed all pages.")
        browser.close()


if __name__ == "__main__":
    main()