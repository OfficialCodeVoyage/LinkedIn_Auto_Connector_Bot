# LinkedIn Auto Connector Bot - Setup & Usage Instructions

## 📋 Table of Contents
1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Running the Bot](#running-the-bot)
5. [Command Line Interface](#command-line-interface)
6. [Troubleshooting](#troubleshooting)
7. [Safety Guidelines](#safety-guidelines)

## 🔧 Prerequisites

### System Requirements
- **Operating System:** Windows 10/11, macOS 10.14+, or Linux (Ubuntu 20.04+)
- **Python:** Version 3.8 or higher
- **RAM:** Minimum 4GB (8GB recommended)
- **Internet:** Stable connection required

### Browser Requirements
Choose one of the following:

#### Option 1: Chrome
- Google Chrome (latest version)
- ChromeDriver matching your Chrome version
- Download from: https://chromedriver.chromium.org/

#### Option 2: Firefox
- Mozilla Firefox (latest version)
- GeckoDriver matching your Firefox version
- Download from: https://github.com/mozilla/geckodriver/releases

## 📦 Installation

### Step 1: Clone or Download the Repository
```bash
# Clone from GitHub (if available)
git clone https://github.com/yourusername/LinkedIn_Auto_Connector_Bot.git
cd LinkedIn_Auto_Connector_Bot

# Or extract from ZIP file
unzip LinkedIn_Auto_Connector_Bot.zip
cd LinkedIn_Auto_Connector_Bot
```

### Step 2: Create Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
# Install required packages
pip install -r requirements.txt

# For full features (including rich CLI):
pip install -r requirements.txt --upgrade
```

### Step 4: Install WebDriver

#### For Chrome:
```bash
# macOS (using Homebrew)
brew install chromedriver

# Windows (using Chocolatey)
choco install chromedriver

# Linux
sudo apt-get install chromium-chromedriver

# Or download manually and add to PATH
```

#### For Firefox:
```bash
# macOS (using Homebrew)
brew install geckodriver

# Windows (using Chocolatey)
choco install geckodriver

# Linux
sudo apt-get install firefox-geckodriver

# Or download manually and add to PATH
```

## ⚙️ Configuration

### Step 1: Set Up Environment Variables
```bash
# Copy the environment template
cp .env.example .env

# Edit .env file with your favorite editor
nano .env  # or vim, code, notepad++, etc.
```

Edit the `.env` file with your LinkedIn credentials:
```env
# Required Settings
LINKEDIN_USERNAME=your_email@example.com
LINKEDIN_PASSWORD=your_password

# Optional: Customize limits (recommended to start small)
MAX_DAILY_REQUESTS=10
MAX_WEEKLY_REQUESTS=50
MAX_CONNECT_REQUESTS_PER_SESSION=5

# Browser Settings
HEADLESS_MODE=false  # Set to true to run without browser window
USE_CHROME=true      # Set to false to use Firefox
```

### Step 2: Configure Search Parameters (Optional)
Edit `config.yaml` to customize bot behavior:
```yaml
# Edit config.yaml
nano config.yaml
```

Key settings to modify:
- `limits:` Connection limits per day/week
- `messages: templates:` Your connection message templates
- `search: keywords:` Keywords for searching profiles
- `anti_detection:` Security features (keep enabled)

### Step 3: Set Up Your LinkedIn Search

1. **Login to LinkedIn** in your regular browser
2. **Perform a search** for the profiles you want to connect with:
   - Use the search bar at the top
   - Enter keywords like "technical recruiter" or "software engineer"
   - Click "People" filter
   - Apply any additional filters (location, industry, etc.)
3. **Copy the URL** from your browser's address bar
4. **Save this URL** - you'll need it when running the bot

Example search URL:
```
https://www.linkedin.com/search/results/people/?keywords=technical%20recruiter&location=United%20States
```

## 🚀 Running the Bot

### Method 1: Using the CLI (Recommended)

#### Basic Run Command
```bash
# Interactive mode (will prompt for credentials)
python cli.py run

# With parameters
python cli.py run --username your_email@example.com --limit 10

# With search URL
python cli.py run -u your_email@example.com -s "YOUR_LINKEDIN_SEARCH_URL" -l 10

# In headless mode (no browser window)
python cli.py run --username your_email@example.com --headless --limit 5
```

#### Check Statistics
```bash
# View your connection statistics
python cli.py stats

# View today's statistics only
python cli.py stats --today

# Export stats as JSON
python cli.py stats --format json > stats.json
```

#### Manage Sessions
```bash
# List saved sessions
python cli.py sessions

# Clean old sessions
python cli.py clean --max-age 48
```

#### Test Setup
```bash
# Test browser setup
python cli.py test --check-browser

# Test authentication
python cli.py test --check-auth

# Check rate limits
python cli.py test --check-rate-limits
```

### Method 2: Direct Python Execution

```bash
# Basic execution
python main.py

# With command-line arguments
python main.py --username your_email@example.com \
               --search-url "YOUR_SEARCH_URL" \
               --limit 10 \
               --headless
```

### Method 3: Using Python Script

Create a file `run_bot.py`:
```python
from main import LinkedInBot

# Create bot instance
bot = LinkedInBot(headless=False)

# Login
success = bot.login("your_email@example.com", "your_password")
if not success:
    print("Login failed!")
    exit(1)

# Set search URL
bot.set_search_url("YOUR_LINKEDIN_SEARCH_URL")

# Run bot
results = bot.run(max_connections=10, follow_profiles=True)

# Print results
print(f"Sent {results['connections_sent']} connections")
print(f"Failed {results['connections_failed']} connections")

# Cleanup
bot.cleanup()
```

Run it:
```bash
python run_bot.py
```

## 💻 Command Line Interface

### Available Commands

```bash
# Main command
python cli.py [OPTIONS] COMMAND [ARGS]

# Commands:
run       # Run the bot to send connections
stats     # Display statistics
sessions  # Manage saved sessions
clean     # Clean old data
config    # View/edit configuration
test      # Test bot components

# Global options:
--debug   # Enable debug logging
--config  # Path to custom config file
```

### Command Examples

#### Run with Custom Message
```bash
python cli.py run --message "Hi {name}, I'd love to connect and expand my network. Best regards!"
```

#### Run with Keywords Instead of URL
```bash
python cli.py run --keywords "software engineer python" --limit 15
```

#### View Configuration
```bash
# List all configuration
python cli.py config --list

# Get specific value
python cli.py config --key daily_limit

# Set configuration value
python cli.py config --key daily_limit --set 20
```

## 🔍 Monitoring & Logs

### Log Files Location
```
logs/
├── LinkedInBot.log         # Main log file
├── LinkedInBot_errors.log  # Error logs only
└── LinkedInBot_daily.log   # Daily rotating log
```

### View Logs in Real-Time
```bash
# Watch main log
tail -f logs/LinkedInBot.log

# Watch errors only
tail -f logs/LinkedInBot_errors.log

# Search logs
grep "ERROR" logs/LinkedInBot.log
grep "connection sent" logs/LinkedInBot.log
```

### Check Bot Status
```bash
# View current statistics
python cli.py stats

# Check if within limits
python cli.py test --check-rate-limits
```

## ❗ Troubleshooting

### Common Issues and Solutions

#### 1. Browser Driver Not Found
**Error:** `WebDriver not found` or `chromedriver not in PATH`

**Solution:**
```bash
# Check if driver is installed
which chromedriver  # or geckodriver

# If not found, download and add to PATH
# Or specify path in .env:
GECKODRIVER_PATH=/path/to/geckodriver
```

#### 2. Login Fails
**Error:** `Failed to login to LinkedIn`

**Solutions:**
- Check credentials in `.env` file
- Try logging in manually first to check for:
  - CAPTCHA requirements
  - Security verification
  - Account restrictions
- Use `--no-headless` to see what's happening

#### 3. Rate Limit Reached
**Error:** `Rate limit reached`

**Solutions:**
```bash
# Check current limits
python cli.py stats

# Wait until tomorrow or next week
# Or adjust limits in config.yaml (not recommended)
```

#### 4. Connection Button Not Found
**Error:** `Connect button not found`

**Solutions:**
- LinkedIn may have changed their UI
- Try updating the search URL
- Check if you're already connected
- Profile might be premium-only

#### 5. Session Issues
**Error:** `Session expired` or `Session corrupted`

**Solutions:**
```bash
# Clean old sessions
python cli.py clean --execute

# Delete specific session
rm sessions/your_email_session.enc

# Disable sessions temporarily
# In .env: SESSION_ENABLED=false
```

### Debug Mode
For detailed debugging:
```bash
# Run with debug logging
python cli.py --debug run --limit 1

# Check debug log
tail -n 100 logs/LinkedInBot.log
```

## 🛡️ Safety Guidelines

### ⚠️ IMPORTANT: LinkedIn Terms of Service
- **This bot violates LinkedIn's Terms of Service**
- **Your account may be restricted or banned**
- **Use at your own risk**

### 📊 Recommended Limits
- **Daily:** Maximum 10-15 connections
- **Weekly:** Maximum 50-80 connections
- **Per Session:** Maximum 5-10 connections
- **Time Between Actions:** 3-8 seconds

### 🔒 Best Practices

1. **Start Small**
   - Begin with 5 connections per day
   - Gradually increase if no issues

2. **Use Random Delays**
   - Keep `anti_detection` enabled in config
   - Don't disable human behavior simulation

3. **Vary Your Activity**
   - Don't run at the same time every day
   - Mix automated and manual activity
   - Take breaks (don't use every day)

4. **Monitor Your Account**
   - Check for warning messages from LinkedIn
   - Stop immediately if you receive warnings
   - Watch for "unusual activity" notifications

5. **Use Personalized Messages**
   - Customize message templates
   - Make them relevant to the recipient
   - Avoid generic spam-like messages

6. **Session Management**
   - Don't login too frequently
   - Use saved sessions when possible
   - Clean old sessions regularly

### 🚨 Warning Signs to Stop
- LinkedIn asks for phone verification frequently
- You receive "unusual activity" warnings
- Connection requests start failing consistently
- Your account gets temporarily restricted
- Search results become limited

## 📊 Performance Tips

1. **Run During Business Hours**
   - More natural activity pattern
   - Better response rates

2. **Target Relevant Profiles**
   - Use specific search keywords
   - Filter by location and industry
   - Quality over quantity

3. **Optimize Message Templates**
   - Keep under 300 characters
   - Personalize with {name} and {title}
   - A/B test different messages

4. **System Resources**
   - Close unnecessary programs
   - Use headless mode for better performance
   - Ensure stable internet connection

## 🆘 Getting Help

### Check Documentation
- `README.md` - Project overview
- `CLAUDE.md` - Technical documentation
- `config.yaml` - Configuration options

### View Help
```bash
# General help
python cli.py --help

# Command-specific help
python cli.py run --help
python cli.py stats --help
```

### Report Issues
- Check logs first: `logs/LinkedInBot_errors.log`
- Include error messages and stack traces
- Specify your environment (OS, Python version, browser)

## 🔄 Updating the Bot

```bash
# Pull latest changes (if using git)
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Check for configuration changes
diff .env.example .env
diff config.yaml.example config.yaml
```

---

## 📝 Quick Start Checklist

- [ ] Python 3.8+ installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] WebDriver installed (ChromeDriver or GeckoDriver)
- [ ] `.env` file created with LinkedIn credentials
- [ ] LinkedIn search URL obtained
- [ ] Test run with small limit (5 connections)
- [ ] Logs checked for errors
- [ ] Statistics reviewed

---

**Remember:** Use responsibly and within LinkedIn's acceptable use limits to avoid account restrictions!