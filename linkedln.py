import json
import logging
import os
import random
import time
from linkedin_api import Linkedin

# Load configuration
with open('config.json', 'r') as file:
    config = json.load(file)

# LinkedIn credentials
username = config['username']
password = config['password']

# Authenticate LinkedIn API
api = Linkedin(username, password)

# Set up logging
logging.basicConfig(filename='linkedin_bot.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Load sent connection requests from a file
sent_requests_file = 'sent_requests.json'
if os.path.exists(sent_requests_file):
    with open(sent_requests_file, 'r') as file:
        sent_requests = json.load(file)
else:
    sent_requests = []

# Save sent connection requests to a file
def save_sent_requests():
    with open(sent_requests_file, 'w') as file:
        json.dump(sent_requests, file)

# Function to create personalized connection messages
def create_personalized_message(first_name, job_title, company_name, industry):
    message_templates = config['message_templates']
    message = random.choice(message_templates)
    return message.format(first_name=first_name, job_title=job_title, company_name=company_name, industry=industry)

# Function to connect with people based on specific job titles, locations, and industries
def connect_with_people():
    job_titles = config['job_titles']
    locations = config['locations']
    industries = config['industries']

    for title in job_titles:
        for location in locations:
            for industry in industries:
                # Adjust the search criteria to match the LinkedIn API's expectations
                params = {
                    'keywords': title,
                    'regions': location,
                    'industries': industry,
                    'network_depth': 'S'
                }
                search_results = api.search(params)

                for person in search_results:
                    if person['urn_id'] in sent_requests:
                        logging.info(f'Skipping {person["publicIdentifier"]} - already sent request')
                        continue

                    profile = api.get_profile(person['urn_id'])
                    message = create_personalized_message(profile['firstName'], title,
                                                          profile.get('companyName', 'your company'), industry)

                    retry_count = 0
                    max_retries = config['retry_max_retries']
                    backoff = config['retry_backoff_initial']
                    success = False

                    while not success and retry_count < max_retries:
                        try:
                            api.add_connection(profile['publicIdentifier'], message=message)
                            logging.info(
                                f'Successfully connected with {profile["firstName"]} {profile["lastName"]} ({title}) in {location}, Industry: {industry}')
                            print(
                                f'Successfully connected with {profile["firstName"]} {profile["lastName"]} ({title}) in {location}, Industry: {industry}')
                            sent_requests.append(person['urn_id'])
                            save_sent_requests()
                            success = True
                            time.sleep(5)  # Delay between requests to handle rate limits
                        except Exception as e:
                            retry_count += 1
                            logging.error(
                                f'Error connecting with {profile["firstName"]} {profile["lastName"]} ({title}) in {location}, Industry: {industry}: {e}')
                            print(
                                f'Error connecting with {profile["firstName"]} {profile["lastName"]} ({title}) in {location}, Industry: {industry}: {e}')
                            if 'rate limit' in str(e).lower():
                                logging.warning('Rate limit encountered. Sleeping for 1 minute.')
                                time.sleep(60)  # Exponential backoff strategy
                            elif 'network error' in str(e).lower() or 'timeout' in str(e).lower():
                                logging.warning(f'Network error encountered. Retrying after {backoff} seconds.')
                                time.sleep(backoff)
                                backoff *= config['retry_backoff_factor']
                            else:
                                logging.error(f'Unexpected error: {e}')
                                break

# Run the bot continuously
while True:
    connect_with_people()
    time.sleep(config['connection_interval_seconds'])  # Wait for the configured interval before the next iteration
