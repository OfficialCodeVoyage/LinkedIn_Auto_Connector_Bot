# test_linkedin_bot.py

import unittest
from unittest.mock import patch, MagicMock
from linkedln import create_personalized_message, connect_with_people


class TestLinkedinBot(unittest.TestCase):

    def test_create_personalized_message(self):
        message = create_personalized_message('John', 'Software Engineer', 'TechCorp')
        self.assertIn('Hi John', message)
        self.assertIn('Software Engineer', message)
        self.assertIn('TechCorp', message)

    @patch('linkedin_bot.api.search_people')
    @patch('linkedin_bot.api.get_profile')
    @patch('linkedin_bot.api.add_connection')
    def test_connect_with_people(self, mock_add_connection, mock_get_profile, mock_search_people):
        mock_search_people.return_value = [{'urn_id': '123', 'publicIdentifier': 'john-doe'}]
        mock_get_profile.return_value = {'urn_id': '123', 'publicIdentifier': 'john-doe', 'firstName': 'John',
                                         'lastName': 'Doe'}

        connect_with_people()

        mock_search_people.assert_called()
        mock_get_profile.assert_called_with('123')
        mock_add_connection.assert_called_with('john-doe', message=unittest.mock.ANY)


if __name__ == '__main__':
    unittest.main()
