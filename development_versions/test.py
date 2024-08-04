from selenium.webdriver import ActionChains
from selenium.webdriver.support.wait import WebDriverWait

import unittest
from unittest.mock import patch, MagicMock
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium import webdriver
from linked_with_selenium import login_to_linkedin, extract_recruiter_name, send_connection_request, go_to_next_page, \
    send_connection_requests, BASE_CONNECTION_MESSAGE


class TestLinkedInBot(unittest.TestCase):
    @patch('linked_with_selenium.webdriver.Firefox')
    def setUp(self, MockWebDriver):
        options = Options()
        service = Service('geckodriver.exe')
        self.driver = MockWebDriver(service=service, options=options)

    def test_login_to_linkedin_success(self):
        with patch.object(self.driver, 'get'), \
                patch.object(WebDriverWait, 'until'), \
                patch.object(self.driver, 'find_element', return_value=MagicMock()) as mock_find_element:
            username_field = MagicMock()
            password_field = MagicMock()
            mock_find_element.side_effect = [username_field, password_field]

            login_to_linkedin(self.driver, 'username', 'password')

            self.driver.get.assert_called_with("https://www.linkedin.com/login")
            username_field.send_keys.assert_any_call('username')
            password_field.send_keys.assert_any_call('password')
            password_field.send_keys.assert_any_call(Keys.RETURN)

    def test_extract_recruiter_name_success(self):
        button = MagicMock()
        parent_div = MagicMock()
        name_element = MagicMock()
        button.find_element.return_value = parent_div
        parent_div.find_element.return_value = name_element
        name_element.text = "John Doe"

        name = extract_recruiter_name(button)

        self.assertEqual(name, "John Doe")
        button.find_element.assert_called_with(By.XPATH, "./ancestor::div[contains(@class, 'entity-result__item')]")
        parent_div.find_element.assert_called_with(By.XPATH,
                                                   ".//span[contains(@class, 'entity-result__title-text')]/a/span[1]")

    def test_send_connection_request_success(self):
        button = MagicMock()
        button.find_element.side_effect = [MagicMock(), MagicMock()]
        recruiter_name = "John Doe"
        base_message = BASE_CONNECTION_MESSAGE.format(name=recruiter_name)

        with patch('linked_with_selenium.extract_recruiter_name', return_value=recruiter_name), \
                patch.object(ActionChains, 'move_to_element', return_value=MagicMock()), \
                patch.object(WebDriverWait, 'until'):
            send_connection_request(self.driver, button, BASE_CONNECTION_MESSAGE)

            ActionChains(self.driver).move_to_element(button).click(button).perform.assert_called()
            button.find_element.assert_any_call(By.XPATH,
                                                "//span[contains(@class, 'artdeco-button__text') and text()='Add a note']")
            button.find_element.assert_any_call(By.ID, "custom-message")
            button.find_element.assert_any_call(By.XPATH,
                                                "//span[contains(@class, 'artdeco-button__text') and text()='Send']")

    def test_go_to_next_page_success(self):
        next_page_button = MagicMock()

        with patch.object(WebDriverWait, 'until', return_value=next_page_button):
            result = go_to_next_page(self.driver)

            next_page_button.click.assert_called_once()
            self.assertTrue(result)

    def test_send_connection_requests_success(self):
        search_link = 'https://www.linkedin.com/search/results/people/?keywords=tech%20recruiter'
        max_requests = 2

        with patch.object(self.driver, 'get'), \
                patch.object(WebDriverWait, 'until'), \
                patch.object(self.driver, 'find_elements', return_value=[MagicMock(), MagicMock()]), \
                patch('linked_with_selenium.send_connection_request'):
            send_connection_requests(self.driver, search_link, max_requests, BASE_CONNECTION_MESSAGE)

            self.assertEqual(send_connection_request.call_count, max_requests)
            self.driver.get.assert_called_with(search_link)


if __name__ == "__main__":
    unittest.main()
