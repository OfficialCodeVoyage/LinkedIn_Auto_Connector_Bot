"""
Comprehensive configuration management system for LinkedIn Auto Connector Bot.

This module provides type-safe configuration management with support for
multiple configuration sources (.env, YAML, JSON) and validation.
"""

import os
import json
import yaml
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List, Union
from dataclasses import dataclass, field, asdict
from dotenv import load_dotenv
from enum import Enum

# Configure logging
logger = logging.getLogger(__name__)


class BrowserType(Enum):
    """Supported browser types."""
    CHROME = "chrome"
    FIREFOX = "firefox"
    EDGE = "edge"
    SAFARI = "safari"


class LogLevel(Enum):
    """Logging levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class BrowserConfig:
    """Browser configuration settings."""
    browser_type: BrowserType = BrowserType.CHROME
    headless: bool = False
    window_size: tuple = (1920, 1080)
    user_agent: Optional[str] = None
    disable_images: bool = False
    disable_javascript: bool = False
    proxy: Optional[str] = None
    download_dir: Optional[Path] = None
    profile_path: Optional[Path] = None
    extensions: List[str] = field(default_factory=list)
    arguments: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Validate and set default browser arguments."""
        default_args = [
            '--no-sandbox',
            '--disable-dev-shm-usage',
            '--disable-blink-features=AutomationControlled',
            '--disable-notifications',
            '--disable-popup-blocking',
        ]

        # Merge default arguments with user-provided ones
        self.arguments = list(set(default_args + self.arguments))

        if self.window_size:
            self.arguments.append(f'--window-size={self.window_size[0]},{self.window_size[1]}')


@dataclass
class RateLimitConfig:
    """Rate limiting configuration."""
    daily_connection_limit: int = 100
    weekly_connection_limit: int = 500
    daily_message_limit: int = 50
    daily_profile_view_limit: int = 250

    # Time delays (in seconds)
    min_delay_between_actions: float = 2.0
    max_delay_between_actions: float = 7.0
    min_delay_between_connections: float = 10.0
    max_delay_between_connections: float = 30.0

    # Cooldown periods (in seconds)
    rate_limit_cooldown: int = 3600  # 1 hour
    daily_reset_hour: int = 0  # Reset at midnight

    def validate(self) -> bool:
        """Validate rate limit configuration."""
        validations = [
            self.daily_connection_limit > 0,
            self.weekly_connection_limit > 0,
            self.daily_message_limit > 0,
            self.daily_profile_view_limit > 0,
            self.min_delay_between_actions >= 0,
            self.max_delay_between_actions > self.min_delay_between_actions,
            self.min_delay_between_connections >= 0,
            self.max_delay_between_connections > self.min_delay_between_connections,
            0 <= self.daily_reset_hour <= 23
        ]

        if not all(validations):
            raise ValueError("Invalid rate limit configuration")

        return True


@dataclass
class SecurityConfig:
    """Security configuration settings."""
    encrypt_credentials: bool = True
    encrypt_sessions: bool = True
    use_keyring: bool = True
    session_timeout: int = 86400  # 24 hours in seconds
    max_login_attempts: int = 3
    require_strong_password: bool = True
    min_password_length: int = 12
    clear_sessions_on_exit: bool = False
    rotate_user_agents: bool = True
    use_proxy_rotation: bool = False
    proxy_list: List[str] = field(default_factory=list)


@dataclass
class LoggingConfig:
    """Logging configuration settings."""
    level: LogLevel = LogLevel.INFO
    file_path: Path = Path("logs/linkedin_bot.log")
    max_file_size: int = 10485760  # 10MB
    backup_count: int = 5
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    console_output: bool = True
    log_api_calls: bool = True
    log_browser_console: bool = False


@dataclass
class DataConfig:
    """Data storage configuration."""
    data_dir: Path = Path("data")
    database_path: Path = Path("data/linkedin_bot.db")
    export_format: str = "csv"  # csv, json, excel
    backup_enabled: bool = True
    backup_interval: int = 86400  # 24 hours
    max_backups: int = 7
    compress_backups: bool = True


@dataclass
class LinkedInConfig:
    """LinkedIn-specific configuration."""
    base_url: str = "https://www.linkedin.com"
    login_url: str = "https://www.linkedin.com/login"
    feed_url: str = "https://www.linkedin.com/feed"
    mynetwork_url: str = "https://www.linkedin.com/mynetwork"
    search_url: str = "https://www.linkedin.com/search/results/people"

    # Connection settings
    auto_accept_connections: bool = False
    send_personalized_messages: bool = True
    message_template_path: Optional[Path] = None
    skip_premium_accounts: bool = False
    target_keywords: List[str] = field(default_factory=list)
    exclude_keywords: List[str] = field(default_factory=list)

    # Search filters
    location_filter: Optional[str] = None
    industry_filter: Optional[str] = None
    company_filter: Optional[str] = None
    school_filter: Optional[str] = None

    # Limits
    max_message_length: int = 300
    max_connection_note_length: int = 300


@dataclass
class Settings:
    """Main settings configuration class."""
    browser: BrowserConfig = field(default_factory=BrowserConfig)
    rate_limit: RateLimitConfig = field(default_factory=RateLimitConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    data: DataConfig = field(default_factory=DataConfig)
    linkedin: LinkedInConfig = field(default_factory=LinkedInConfig)

    # General settings
    debug_mode: bool = False
    dry_run: bool = False
    auto_restart_on_error: bool = True
    max_retries: int = 3
    retry_delay: int = 60

    @classmethod
    def load_from_env(cls, env_path: Optional[Path] = None) -> 'Settings':
        """
        Load settings from environment variables.

        Args:
            env_path: Path to .env file

        Returns:
            Settings instance
        """
        if env_path:
            load_dotenv(env_path)
        else:
            load_dotenv()

        settings = cls()

        # Browser settings
        if browser_type := os.getenv('BROWSER_TYPE'):
            settings.browser.browser_type = BrowserType(browser_type.lower())
        settings.browser.headless = os.getenv('HEADLESS', 'false').lower() == 'true'

        # Rate limit settings
        if daily_limit := os.getenv('DAILY_CONNECTION_LIMIT'):
            settings.rate_limit.daily_connection_limit = int(daily_limit)
        if weekly_limit := os.getenv('WEEKLY_CONNECTION_LIMIT'):
            settings.rate_limit.weekly_connection_limit = int(weekly_limit)

        # Security settings
        settings.security.encrypt_credentials = os.getenv('ENCRYPT_CREDENTIALS', 'true').lower() == 'true'
        settings.security.use_keyring = os.getenv('USE_KEYRING', 'true').lower() == 'true'

        # Logging settings
        if log_level := os.getenv('LOG_LEVEL'):
            settings.logging.level = LogLevel(log_level.upper())

        # LinkedIn settings
        if keywords := os.getenv('TARGET_KEYWORDS'):
            settings.linkedin.target_keywords = [k.strip() for k in keywords.split(',')]

        # General settings
        settings.debug_mode = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
        settings.dry_run = os.getenv('DRY_RUN', 'false').lower() == 'true'

        return settings

    @classmethod
    def load_from_yaml(cls, yaml_path: Path) -> 'Settings':
        """
        Load settings from YAML file.

        Args:
            yaml_path: Path to YAML configuration file

        Returns:
            Settings instance
        """
        with open(yaml_path, 'r') as f:
            config_dict = yaml.safe_load(f)

        return cls._from_dict(config_dict)

    @classmethod
    def load_from_json(cls, json_path: Path) -> 'Settings':
        """
        Load settings from JSON file.

        Args:
            json_path: Path to JSON configuration file

        Returns:
            Settings instance
        """
        with open(json_path, 'r') as f:
            config_dict = json.load(f)

        return cls._from_dict(config_dict)

    @classmethod
    def _from_dict(cls, config_dict: Dict[str, Any]) -> 'Settings':
        """
        Create Settings instance from dictionary.

        Args:
            config_dict: Configuration dictionary

        Returns:
            Settings instance
        """
        settings = cls()

        # Browser configuration
        if browser_config := config_dict.get('browser'):
            if browser_type := browser_config.get('browser_type'):
                settings.browser.browser_type = BrowserType(browser_type)
            settings.browser.headless = browser_config.get('headless', False)
            if window_size := browser_config.get('window_size'):
                settings.browser.window_size = tuple(window_size)
            settings.browser.user_agent = browser_config.get('user_agent')
            settings.browser.proxy = browser_config.get('proxy')

        # Rate limit configuration
        if rate_config := config_dict.get('rate_limit'):
            for key, value in rate_config.items():
                if hasattr(settings.rate_limit, key):
                    setattr(settings.rate_limit, key, value)

        # Security configuration
        if security_config := config_dict.get('security'):
            for key, value in security_config.items():
                if hasattr(settings.security, key):
                    setattr(settings.security, key, value)

        # Logging configuration
        if logging_config := config_dict.get('logging'):
            if log_level := logging_config.get('level'):
                settings.logging.level = LogLevel(log_level.upper())
            if file_path := logging_config.get('file_path'):
                settings.logging.file_path = Path(file_path)

        # Data configuration
        if data_config := config_dict.get('data'):
            if data_dir := data_config.get('data_dir'):
                settings.data.data_dir = Path(data_dir)
            if db_path := data_config.get('database_path'):
                settings.data.database_path = Path(db_path)

        # LinkedIn configuration
        if linkedin_config := config_dict.get('linkedin'):
            for key, value in linkedin_config.items():
                if hasattr(settings.linkedin, key):
                    setattr(settings.linkedin, key, value)

        # General settings
        settings.debug_mode = config_dict.get('debug_mode', False)
        settings.dry_run = config_dict.get('dry_run', False)
        settings.auto_restart_on_error = config_dict.get('auto_restart_on_error', True)
        settings.max_retries = config_dict.get('max_retries', 3)

        return settings

    def validate(self) -> bool:
        """
        Validate all configuration settings.

        Returns:
            True if all settings are valid

        Raises:
            ValueError: If any setting is invalid
        """
        try:
            # Validate rate limits
            self.rate_limit.validate()

            # Validate file paths
            if not self.logging.file_path.parent.exists():
                self.logging.file_path.parent.mkdir(parents=True, exist_ok=True)

            if not self.data.data_dir.exists():
                self.data.data_dir.mkdir(parents=True, exist_ok=True)

            # Validate security settings
            if self.security.min_password_length < 8:
                raise ValueError("Minimum password length must be at least 8")

            # Validate LinkedIn settings
            if self.linkedin.max_message_length <= 0:
                raise ValueError("Maximum message length must be positive")

            logger.info("Configuration validation successful")
            return True

        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            raise

    def save_to_json(self, json_path: Path) -> None:
        """
        Save current settings to JSON file.

        Args:
            json_path: Path to save JSON configuration
        """
        config_dict = self.to_dict()
        with open(json_path, 'w') as f:
            json.dump(config_dict, f, indent=2, default=str)

        logger.info(f"Settings saved to {json_path}")

    def save_to_yaml(self, yaml_path: Path) -> None:
        """
        Save current settings to YAML file.

        Args:
            yaml_path: Path to save YAML configuration
        """
        config_dict = self.to_dict()
        with open(yaml_path, 'w') as f:
            yaml.dump(config_dict, f, default_flow_style=False)

        logger.info(f"Settings saved to {yaml_path}")

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert settings to dictionary.

        Returns:
            Dictionary representation of settings
        """
        return {
            'browser': {
                'browser_type': self.browser.browser_type.value,
                'headless': self.browser.headless,
                'window_size': list(self.browser.window_size),
                'user_agent': self.browser.user_agent,
                'proxy': self.browser.proxy,
                'disable_images': self.browser.disable_images,
                'disable_javascript': self.browser.disable_javascript,
            },
            'rate_limit': asdict(self.rate_limit),
            'security': asdict(self.security),
            'logging': {
                'level': self.logging.level.value,
                'file_path': str(self.logging.file_path),
                'max_file_size': self.logging.max_file_size,
                'backup_count': self.logging.backup_count,
                'format': self.logging.format,
                'console_output': self.logging.console_output,
            },
            'data': {
                'data_dir': str(self.data.data_dir),
                'database_path': str(self.data.database_path),
                'export_format': self.data.export_format,
                'backup_enabled': self.data.backup_enabled,
                'backup_interval': self.data.backup_interval,
            },
            'linkedin': asdict(self.linkedin),
            'debug_mode': self.debug_mode,
            'dry_run': self.dry_run,
            'auto_restart_on_error': self.auto_restart_on_error,
            'max_retries': self.max_retries,
            'retry_delay': self.retry_delay,
        }


# Singleton instance
_settings: Optional[Settings] = None


def get_settings(reload: bool = False) -> Settings:
    """
    Get global settings instance.

    Args:
        reload: Force reload of settings

    Returns:
        Settings instance
    """
    global _settings

    if _settings is None or reload:
        # Try to load from different sources in order of preference
        config_paths = [
            Path('.env'),
            Path('config.yaml'),
            Path('config.json'),
        ]

        for config_path in config_paths:
            if config_path.exists():
                if config_path.suffix == '.env':
                    _settings = Settings.load_from_env(config_path)
                elif config_path.suffix == '.yaml':
                    _settings = Settings.load_from_yaml(config_path)
                elif config_path.suffix == '.json':
                    _settings = Settings.load_from_json(config_path)
                break
        else:
            # No configuration file found, use defaults
            _settings = Settings()

        # Validate settings
        _settings.validate()

    return _settings