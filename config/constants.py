"""
LinkedIn-specific constants and selectors for the Auto Connector Bot.

This module contains all LinkedIn URLs, CSS selectors, XPath expressions,
rate limits, and other constants used throughout the application.
"""

from enum import Enum
from typing import Dict, List


class LinkedInURLs:
    """LinkedIn URL endpoints."""

    # Base URLs
    BASE_URL = "https://www.linkedin.com"
    MOBILE_URL = "https://www.linkedin.com/m"

    # Authentication
    LOGIN_URL = f"{BASE_URL}/login"
    LOGOUT_URL = f"{BASE_URL}/m/logout"
    CHECKPOINT_URL = f"{BASE_URL}/checkpoint"
    TWO_FACTOR_URL = f"{BASE_URL}/checkpoint/challenge"

    # Main pages
    FEED_URL = f"{BASE_URL}/feed"
    PROFILE_URL = f"{BASE_URL}/in"
    MY_NETWORK_URL = f"{BASE_URL}/mynetwork"
    MESSAGING_URL = f"{BASE_URL}/messaging"
    NOTIFICATIONS_URL = f"{BASE_URL}/notifications"
    JOBS_URL = f"{BASE_URL}/jobs"

    # Search
    SEARCH_PEOPLE_URL = f"{BASE_URL}/search/results/people"
    SEARCH_COMPANIES_URL = f"{BASE_URL}/search/results/companies"
    SEARCH_JOBS_URL = f"{BASE_URL}/search/results/jobs"
    SEARCH_GROUPS_URL = f"{BASE_URL}/search/results/groups"

    # Network
    INVITATIONS_URL = f"{BASE_URL}/mynetwork/invitation-manager"
    CONNECTIONS_URL = f"{BASE_URL}/mynetwork/invite-connect/connections"
    SENT_INVITATIONS_URL = f"{BASE_URL}/mynetwork/invitation-manager/sent"

    # Settings
    SETTINGS_URL = f"{BASE_URL}/settings"
    PRIVACY_SETTINGS_URL = f"{BASE_URL}/settings/privacy"


class Selectors:
    """CSS selectors for LinkedIn elements."""

    # Login page
    LOGIN_EMAIL = "input#username"
    LOGIN_PASSWORD = "input#password"
    LOGIN_SUBMIT = "button[type='submit']"
    LOGIN_ERROR = "div[role='alert']"
    REMEMBER_ME = "input#rememberMeOptIn"

    # Two-factor authentication
    TWO_FACTOR_CODE = "input#input__phone_verification_pin"
    TWO_FACTOR_SUBMIT = "button#two-step-submit-button"

    # Navigation
    NAV_HOME = "a[href='/feed/']"
    NAV_NETWORK = "a[href='/mynetwork/']"
    NAV_JOBS = "a[href='/jobs/']"
    NAV_MESSAGING = "a[href='/messaging/']"
    NAV_NOTIFICATIONS = "a[href='/notifications/']"
    NAV_PROFILE = "div.global-nav__me"

    # Profile page
    PROFILE_NAME = "h1.text-heading-xlarge"
    PROFILE_HEADLINE = "div.text-body-medium"
    PROFILE_LOCATION = "span.text-body-small"
    PROFILE_CONNECTIONS = "span.t-bold"
    PROFILE_ABOUT = "div.pv-about__summary-text"

    # Connection buttons
    CONNECT_BUTTON = "button[aria-label*='Connect']"
    CONNECT_BUTTON_SECONDARY = "button.pvs-profile-actions__action"
    MESSAGE_BUTTON = "button[aria-label*='Message']"
    FOLLOW_BUTTON = "button[aria-label*='Follow']"
    MORE_BUTTON = "button[aria-label='More actions']"

    # Connection modal
    ADD_NOTE_BUTTON = "button[aria-label='Add a note']"
    NOTE_TEXTAREA = "textarea#custom-message"
    SEND_INVITE_BUTTON = "button[aria-label='Send invitation']"
    SEND_WITHOUT_NOTE = "button[aria-label='Send without a note']"

    # Search page
    SEARCH_INPUT = "input.search-global-typeahead__input"
    SEARCH_RESULT_ITEM = "li.reusable-search__result-container"
    SEARCH_RESULT_NAME = "span.entity-result__title-text"
    SEARCH_RESULT_HEADLINE = "div.entity-result__primary-subtitle"
    SEARCH_RESULT_LOCATION = "div.entity-result__secondary-subtitle"
    SEARCH_PAGINATION = "div.artdeco-pagination"
    SEARCH_NEXT_BUTTON = "button[aria-label='Next']"

    # Search filters
    FILTER_CONNECTIONS = "button[aria-label*='Connections']"
    FILTER_LOCATION = "button[aria-label*='Locations']"
    FILTER_COMPANY = "button[aria-label*='Current company']"
    FILTER_INDUSTRY = "button[aria-label*='Industries']"
    FILTER_SCHOOL = "button[aria-label*='Schools']"

    # My Network page
    NETWORK_INVITATION = "div.invitation-card"
    ACCEPT_BUTTON = "button[aria-label*='Accept']"
    IGNORE_BUTTON = "button[aria-label*='Ignore']"
    INVITATION_MESSAGE = "div.invitation-card__message"
    PEOPLE_YOU_MAY_KNOW = "section.mn-pymk-list"

    # Messaging
    MESSAGE_THREAD = "div.msg-conversation-listitem"
    MESSAGE_INPUT = "div.msg-form__contenteditable"
    MESSAGE_SEND_BUTTON = "button.msg-form__send-button"
    NEW_MESSAGE_BUTTON = "button[aria-label='Compose a new message']"
    MESSAGE_RECIPIENT = "input.msg-connections-typeahead__input"

    # Feed
    POST_CONTAINER = "div.feed-shared-update-v2"
    LIKE_BUTTON = "button[aria-label*='Like']"
    COMMENT_BUTTON = "button[aria-label*='Comment']"
    SHARE_BUTTON = "button[aria-label*='Share']"
    POST_AUTHOR = "span.feed-shared-actor__name"

    # Common elements
    MODAL_CLOSE = "button[aria-label='Dismiss']"
    LOADING_SPINNER = "div.artdeco-spinner"
    ERROR_MESSAGE = "div.artdeco-inline-feedback--error"
    SUCCESS_MESSAGE = "div.artdeco-inline-feedback--success"


class XPaths:
    """XPath expressions for complex element selection."""

    # Profile elements
    PROFILE_EXPERIENCE = "//section[contains(@class, 'experience')]//ul/li"
    PROFILE_EDUCATION = "//section[contains(@class, 'education')]//ul/li"
    PROFILE_SKILLS = "//section[contains(@class, 'skills')]//span[contains(@class, 'skill-name')]"

    # Connection elements
    CONNECT_BUTTON_TEXT = "//button[contains(text(), 'Connect')]"
    PENDING_BUTTON = "//button[contains(text(), 'Pending')]"
    MESSAGE_BUTTON_TEXT = "//button[contains(text(), 'Message')]"

    # Search results
    SEARCH_RESULT_CONTAINER = "//div[@class='search-results-container']//ul/li"
    RESULT_CONNECT_BUTTON = ".//button[contains(@aria-label, 'Connect')]"
    RESULT_NAME_LINK = ".//a[contains(@class, 'app-aware-link')]//span[@dir='ltr']"

    # Network page
    INVITATION_CARDS = "//div[contains(@class, 'invitation-card__container')]"
    PYMK_CARDS = "//div[contains(@class, 'discover-entity-type-card')]"

    # Pagination
    PAGINATION_NEXT = "//button[@aria-label='Next' and not(@disabled)]"
    PAGINATION_PREVIOUS = "//button[@aria-label='Previous' and not(@disabled)]"
    PAGE_NUMBERS = "//button[@type='button' and contains(@aria-label, 'Page')]"


class RateLimits:
    """LinkedIn rate limits and safety thresholds."""

    # Daily limits
    DAILY_CONNECTION_LIMIT = 100
    DAILY_MESSAGE_LIMIT = 50
    DAILY_PROFILE_VIEW_LIMIT = 250
    DAILY_SEARCH_LIMIT = 300
    DAILY_FOLLOW_LIMIT = 100
    DAILY_UNFOLLOW_LIMIT = 100

    # Weekly limits
    WEEKLY_CONNECTION_LIMIT = 500
    WEEKLY_MESSAGE_LIMIT = 300
    WEEKLY_PROFILE_VIEW_LIMIT = 1500

    # Hourly limits
    HOURLY_CONNECTION_LIMIT = 20
    HOURLY_MESSAGE_LIMIT = 15
    HOURLY_SEARCH_LIMIT = 50

    # Time delays (in seconds)
    MIN_DELAY_BETWEEN_ACTIONS = 2.0
    MAX_DELAY_BETWEEN_ACTIONS = 7.0
    MIN_DELAY_BETWEEN_CONNECTIONS = 10.0
    MAX_DELAY_BETWEEN_CONNECTIONS = 30.0
    MIN_DELAY_BETWEEN_MESSAGES = 15.0
    MAX_DELAY_BETWEEN_MESSAGES = 45.0
    MIN_PAGE_LOAD_DELAY = 3.0
    MAX_PAGE_LOAD_DELAY = 10.0

    # Typing delays (in seconds)
    MIN_TYPING_DELAY = 0.1
    MAX_TYPING_DELAY = 0.3

    # Session limits
    MAX_ACTIONS_PER_SESSION = 150
    MAX_SESSION_DURATION = 7200  # 2 hours
    MIN_BREAK_DURATION = 1800  # 30 minutes
    MAX_BREAK_DURATION = 7200  # 2 hours


class MessageLimits:
    """LinkedIn message and text limits."""

    MAX_CONNECTION_MESSAGE_LENGTH = 300
    MAX_INMAIL_LENGTH = 1900
    MAX_MESSAGE_LENGTH = 8000
    MAX_PROFILE_HEADLINE_LENGTH = 220
    MAX_PROFILE_SUMMARY_LENGTH = 2600
    MAX_POST_LENGTH = 3000
    MAX_COMMENT_LENGTH = 1250
    MAX_COMPANY_NAME_LENGTH = 100
    MAX_JOB_TITLE_LENGTH = 100


class BrowserConfig:
    """Browser configuration constants."""

    # Chrome options
    CHROME_OPTIONS = [
        '--no-sandbox',
        '--disable-dev-shm-usage',
        '--disable-blink-features=AutomationControlled',
        '--disable-notifications',
        '--disable-popup-blocking',
        '--disable-extensions',
        '--disable-gpu',
        '--disable-images',
        '--disable-javascript',
        '--disable-web-security',
        '--disable-features=VizDisplayCompositor',
        '--start-maximized'
    ]

    # Firefox options
    FIREFOX_OPTIONS = [
        '-headless',
        '-safe-mode',
        '-private'
    ]

    # User agents
    USER_AGENTS = [
        # Chrome on Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",

        # Chrome on macOS
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",

        # Firefox on Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:119.0) Gecko/20100101 Firefox/119.0",

        # Firefox on macOS
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15) Gecko/20100101 Firefox/120.0",

        # Edge on Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",

        # Safari on macOS
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15"
    ]

    # Viewport sizes
    VIEWPORT_SIZES = [
        (1920, 1080),  # Full HD
        (1366, 768),   # Most common
        (1440, 900),   # Common Mac
        (1536, 864),   # Common laptop
        (1680, 1050),  # Common desktop
        (1280, 720),   # HD
    ]


class HTTPHeaders:
    """HTTP headers for requests."""

    DEFAULT_HEADERS = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0'
    }

    AJAX_HEADERS = {
        'Accept': 'application/vnd.linkedin.normalized+json+2.1',
        'x-restli-protocol-version': '2.0.0',
        'x-li-lang': 'en_US',
        'x-li-track': '{"clientVersion":"1.13.0","mpVersion":"1.13.0","osName":"web","timezoneOffset":-5}'
    }


class ConnectionStatus(Enum):
    """Connection request status types."""
    PENDING = "pending"
    ACCEPTED = "accepted"
    IGNORED = "ignored"
    WITHDRAWN = "withdrawn"
    SENT = "sent"


class ProfileFields:
    """LinkedIn profile field names."""

    BASIC_FIELDS = [
        'firstName', 'lastName', 'headline', 'location',
        'industry', 'summary', 'publicProfileUrl'
    ]

    EXPERIENCE_FIELDS = [
        'title', 'companyName', 'location', 'startDate',
        'endDate', 'description', 'current'
    ]

    EDUCATION_FIELDS = [
        'schoolName', 'degree', 'fieldOfStudy',
        'startDate', 'endDate', 'grade'
    ]

    SKILL_FIELDS = ['name', 'endorsementCount']


class ErrorMessages:
    """Common LinkedIn error messages."""

    RATE_LIMIT_ERROR = "You've reached the weekly invitation limit"
    NETWORK_ERROR = "Network request failed"
    AUTH_ERROR = "Authentication required"
    PROFILE_NOT_FOUND = "Profile not found"
    INVALID_SESSION = "Your session has expired"
    BLOCKED_ACTION = "This action is temporarily blocked"
    PREMIUM_REQUIRED = "This feature requires LinkedIn Premium"


class Timeouts:
    """Timeout values in seconds."""

    PAGE_LOAD = 30
    ELEMENT_WAIT = 10
    AJAX_WAIT = 15
    NETWORK_WAIT = 30
    LOGIN_WAIT = 20
    SEARCH_WAIT = 15
    ACTION_WAIT = 5
    IMPLICIT_WAIT = 3


class CookieNames:
    """LinkedIn cookie names."""

    SESSION_COOKIES = [
        'li_at',  # Main session cookie
        'JSESSIONID',
        'liap',
        'li_gc',
        'bcookie',
        'bscookie',
        'lissc',
        'lidc'
    ]

    TRACKING_COOKIES = [
        'UserMatchHistory',
        'AnalyticsSyncHistory',
        'lms_ads',
        'lms_analytics'
    ]


class APIEndpoints:
    """LinkedIn API endpoints (unofficial)."""

    VOYAGER_API = "https://www.linkedin.com/voyager/api"

    # Profile endpoints
    PROFILE_VIEW = f"{VOYAGER_API}/identity/profiles/{{profile_id}}/profileView"
    PROFILE_CONTACT_INFO = f"{VOYAGER_API}/identity/profiles/{{profile_id}}/profileContactInfo"

    # Connection endpoints
    SEND_INVITATION = f"{VOYAGER_API}/growth/normInvitations"
    WITHDRAW_INVITATION = f"{VOYAGER_API}/growth/normInvitations/{{invitation_id}}"

    # Search endpoints
    PEOPLE_SEARCH = f"{VOYAGER_API}/search/blended"
    TYPEAHEAD_SEARCH = f"{VOYAGER_API}/typeahead/hitsV2"

    # Messaging endpoints
    SEND_MESSAGE = f"{VOYAGER_API}/messaging/conversations"
    GET_CONVERSATIONS = f"{VOYAGER_API}/messaging/conversations"


# Regex patterns
class Patterns:
    """Regular expression patterns."""

    LINKEDIN_URL = r'https?://(?:www\.)?linkedin\.com/.*'
    PROFILE_URL = r'https?://(?:www\.)?linkedin\.com/in/([^/]+)/?'
    COMPANY_URL = r'https?://(?:www\.)?linkedin\.com/company/([^/]+)/?'
    URN_ID = r'urn:li:fs_miniProfile:(.+)'
    EMAIL = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    PHONE = r'^\+?[1-9]\d{1,14}$'