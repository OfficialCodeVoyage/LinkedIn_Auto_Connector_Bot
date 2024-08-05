<div style="text-align: center;">
    <a href="https://www.youtube.com/channel/UCk2O3jSU3_B2MMGr8wLcAdw" target="_blank" title="CodeVoyage YouTube Channel">
        <img src="banner.jpg" alt="Alt text">
    </a>
</div>

# 🤖 LinkedIn Auto Connector Bot

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## 🌟 Overview

The LinkedIn Auto Connector Bot is a powerful tool designed to automate connection requests on LinkedIn. This bot helps users expand their professional network by sending connection requests to a targeted audience based on specified search criteria. It can be customized to send personalized connection messages.

:star::star::star::star::star: ---> Star the Repo!



### ⚠️ Important Notes

This script is a LinkedIn bot that automatically sends connection requests with a custom note to profiles on LinkedIn. It uses the Selenium WebDriver to navigate LinkedIn and interact with the UI elements.

# 🚨🚨🚨 Please use it on your own risk! This is against LinkedIn policy. You may get banned if they catch you! 🚨🚨🚨

## 🚨🚨🚨 **Do not exceed 80 requests per week!**  🚨🚨🚨

### LinkedIn may block your account if you exceed this limit.

P.S. For LinkedIn team - ooops, sorry! I was boring! 

### 🚀 Quick Start Guide

1. **💼 Add My LinkedIn:**  
   You can connect with me on LinkedIn: [My LinkedIn Profile](https://www.linkedin.com/in/mrbondarenko/)

2. **🔍 Set Up Your Search Link:**  
   To set up your search link, follow these steps:
   - Go to [LinkedIn's main page](https://www.linkedin.com/).
   - In the search bar at the top, type in the keywords relevant to the people you want to connect with (e.g., "Tech Recruiter", "Cloud Engineer").
   - Press Enter to see the search results.
   - On the search results page, click on the "People" filter to narrow the results to LinkedIn profiles only.
   - Copy the URL from your browser's address bar. This URL is your `SEARCH_LINK`.
   - Open the bot script and find the `SEARCH_LINK` variable. Replace the existing link with the one you copied from LinkedIn.

3. **🎉 Have Fun!**  
   Start the bot and watch as it expands your network with targeted connection requests.

## 🔧 Features

- **🤖 Automated Connection Requests:** Send connection requests to targeted LinkedIn users.
- **✉️ Personalized Messages:** Customize the connection request message for a more personalized outreach.
- **🔎 Search Criteria:** Target connections based on industry, location, job title, and more.
- **📊 Logging:** Keep track of connection requests and responses for analysis and optimization.

## 🛠 Installation

### 📋 Prerequisites

- [Python 3.8+](https://www.python.org/downloads/)
- [🌐 Mozilla Firefox](https://www.mozilla.org/en-US/firefox/new/) browser
- [🦊 Geckodriver download page](https://github.com/mozilla/geckodriver/releases) (Ensure that the Geckodriver version matches your installed version of Firefox)

### 📂 Clone the Repository

```bash
git clone https://github.com/OfficialCodeVoyage/LinkedIn_Auto_Connector_Bot.git
cd LinkedIn_Auto_Connector_Bot
```

### 📦 Install Dependencies
```bash
pip install -r requirements.txt
```

## 🛠️ Configuration

1. 🔐 Set up LinkedIn credentials:
   Change the ```LINKEDIN_USERNAME``` and ```LINKEDIN_PASSWORD``` in the ```Linkedin_auto_connector_bot.py```.

2. 🔍 Customize Your Search Link:
   Follow the instructions provided in the Quick Start Guide to generate your LinkedIn search link. Replace the SEARCH_LINK variable in the 
   ```Linkedin_auto_connector_bot.py``` with your copied search link.

3. 📝 Configure Message Template:
   Adjust the for ```BASE_CONNECTION_MESSAGE ``` your needs in the ```Linkedin_auto_connector_bot.py```.

   
## 🚀 Usage
### 🏃 Running the Bot

```bash
python linkedin_bot.py
```
The bot will log into your LinkedIn account and begin sending connection requests based on the search criteria provided in your SEARCH_LINK.

### 📜 Logging
Logs of sent connection requests and responses are saved in the logs directory. You can review these logs to analyze the performance of your outreach strategy.

### 🤝 Contributing

Contributions are welcome! Please follow these steps to contribute:

🍴 Fork the repository.

🌿 Create a new branch (git checkout -b feature-branch).

💻 Make your changes.

📝 Commit your changes (git commit -am 'Add new feature').

🚀 Push to the branch (git push origin feature-branch).

📬 Open a pull request.


### 📄 License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

### ⚠️ Disclaimer
This bot is intended for educational and research purposes only. The use of automated bots on LinkedIn may violate LinkedIn's terms of service. Use at your own risk.

### 🛠️ Support
For any questions or issues, please feel free to reach out via GitHub Issues or Discussions.

### 🙌 Acknowledgements
🤖 Selenium for web automation

🐍 Python for providing the programming language

🌍 The LinkedIn community for providing a platform to connect professionals worldwide


Made with ❤️ by [Pavlo Bondarenko](https://www.linkedin.com/in/mrbondarenko/)
