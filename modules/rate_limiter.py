"""
SQLite-based rate limiting system for LinkedIn Auto Connector Bot.

This module tracks and enforces rate limits to prevent account restrictions
and maintains connection history for reporting and analytics.
"""

import sqlite3
import logging
import time
from datetime import datetime, timedelta, date
from pathlib import Path
from typing import Optional, Dict, List, Tuple, Any
from dataclasses import dataclass, asdict
from contextlib import contextmanager
from enum import Enum
import json

# Configure logging
logger = logging.getLogger(__name__)


class ActionType(Enum):
    """Types of LinkedIn actions that are rate-limited."""
    CONNECTION_REQUEST = "connection_request"
    MESSAGE = "message"
    PROFILE_VIEW = "profile_view"
    SEARCH = "search"
    FOLLOW = "follow"
    UNFOLLOW = "unfollow"
    POST_LIKE = "post_like"
    POST_COMMENT = "post_comment"
    INVITATION_ACCEPT = "invitation_accept"
    INVITATION_WITHDRAW = "invitation_withdraw"


@dataclass
class ActionRecord:
    """Record of a LinkedIn action."""
    id: Optional[int] = None
    action_type: str = ""
    profile_url: Optional[str] = None
    profile_name: Optional[str] = None
    timestamp: float = 0.0
    success: bool = True
    error_message: Optional[str] = None
    metadata: Optional[str] = None  # JSON string for additional data


@dataclass
class RateLimitStatus:
    """Current rate limit status."""
    action_type: ActionType
    daily_used: int
    daily_limit: int
    weekly_used: int
    weekly_limit: int
    hourly_used: int
    hourly_limit: int
    can_proceed: bool
    reset_in_seconds: int
    message: str


class RateLimiter:
    """SQLite-based rate limiting system."""

    def __init__(self, database_path: Optional[Path] = None,
                 daily_limits: Optional[Dict[ActionType, int]] = None,
                 weekly_limits: Optional[Dict[ActionType, int]] = None,
                 hourly_limits: Optional[Dict[ActionType, int]] = None):
        """
        Initialize rate limiter.

        Args:
            database_path: Path to SQLite database
            daily_limits: Daily limits per action type
            weekly_limits: Weekly limits per action type
            hourly_limits: Hourly limits per action type
        """
        self.database_path = database_path or Path("data/rate_limits.db")
        self.database_path.parent.mkdir(parents=True, exist_ok=True)

        # Default limits (conservative for safety)
        self.daily_limits = daily_limits or {
            ActionType.CONNECTION_REQUEST: 80,
            ActionType.MESSAGE: 40,
            ActionType.PROFILE_VIEW: 200,
            ActionType.SEARCH: 250,
            ActionType.FOLLOW: 80,
            ActionType.UNFOLLOW: 80,
            ActionType.POST_LIKE: 100,
            ActionType.POST_COMMENT: 50,
            ActionType.INVITATION_ACCEPT: 50,
            ActionType.INVITATION_WITHDRAW: 20
        }

        self.weekly_limits = weekly_limits or {
            ActionType.CONNECTION_REQUEST: 400,
            ActionType.MESSAGE: 250,
            ActionType.PROFILE_VIEW: 1200,
            ActionType.SEARCH: 1500,
            ActionType.FOLLOW: 400,
            ActionType.UNFOLLOW: 400,
        }

        self.hourly_limits = hourly_limits or {
            ActionType.CONNECTION_REQUEST: 15,
            ActionType.MESSAGE: 10,
            ActionType.PROFILE_VIEW: 40,
            ActionType.SEARCH: 40,
            ActionType.FOLLOW: 15,
            ActionType.UNFOLLOW: 15,
        }

        self._initialize_database()

    @contextmanager
    def _get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(str(self.database_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _initialize_database(self):
        """Create database tables if they don't exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Actions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS actions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    action_type TEXT NOT NULL,
                    profile_url TEXT,
                    profile_name TEXT,
                    timestamp REAL NOT NULL,
                    success BOOLEAN DEFAULT 1,
                    error_message TEXT,
                    metadata TEXT,
                    date TEXT NOT NULL,
                    hour INTEGER NOT NULL,
                    week INTEGER NOT NULL,
                    INDEX idx_action_type (action_type),
                    INDEX idx_timestamp (timestamp),
                    INDEX idx_date (date),
                    INDEX idx_week (week)
                )
            ''')

            # Daily statistics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS daily_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    action_type TEXT NOT NULL,
                    count INTEGER DEFAULT 0,
                    successful INTEGER DEFAULT 0,
                    failed INTEGER DEFAULT 0,
                    UNIQUE(date, action_type)
                )
            ''')

            # Blocks table (for tracking when limits are hit)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS blocks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    action_type TEXT NOT NULL,
                    blocked_at REAL NOT NULL,
                    unblock_at REAL NOT NULL,
                    reason TEXT
                )
            ''')

            # Settings table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at REAL NOT NULL
                )
            ''')

            conn.commit()
            logger.info("Rate limiter database initialized")

    def record_action(self, action_type: ActionType,
                      profile_url: Optional[str] = None,
                      profile_name: Optional[str] = None,
                      success: bool = True,
                      error_message: Optional[str] = None,
                      metadata: Optional[Dict] = None) -> bool:
        """
        Record an action and check if it's within rate limits.

        Args:
            action_type: Type of action performed
            profile_url: LinkedIn profile URL
            profile_name: Name of the profile
            success: Whether the action was successful
            error_message: Error message if failed
            metadata: Additional metadata

        Returns:
            True if action was recorded successfully
        """
        try:
            timestamp = time.time()
            current_date = date.today().isoformat()
            current_hour = datetime.now().hour
            current_week = datetime.now().isocalendar()[1]

            with self._get_connection() as conn:
                cursor = conn.cursor()

                # Insert action record
                cursor.execute('''
                    INSERT INTO actions
                    (action_type, profile_url, profile_name, timestamp,
                     success, error_message, metadata, date, hour, week)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    action_type.value,
                    profile_url,
                    profile_name,
                    timestamp,
                    success,
                    error_message,
                    json.dumps(metadata) if metadata else None,
                    current_date,
                    current_hour,
                    current_week
                ))

                # Update daily statistics
                cursor.execute('''
                    INSERT OR REPLACE INTO daily_stats
                    (date, action_type, count, successful, failed)
                    VALUES (
                        ?, ?,
                        COALESCE((SELECT count + 1 FROM daily_stats
                                 WHERE date = ? AND action_type = ?), 1),
                        COALESCE((SELECT successful + ? FROM daily_stats
                                 WHERE date = ? AND action_type = ?), ?),
                        COALESCE((SELECT failed + ? FROM daily_stats
                                 WHERE date = ? AND action_type = ?), ?)
                    )
                ''', (
                    current_date, action_type.value,
                    current_date, action_type.value,
                    1 if success else 0, current_date, action_type.value, 1 if success else 0,
                    0 if success else 1, current_date, action_type.value, 0 if success else 1
                ))

                conn.commit()

                logger.debug(f"Recorded {action_type.value} action for {profile_name or 'unknown'}")
                return True

        except Exception as e:
            logger.error(f"Failed to record action: {e}")
            return False

    def check_limits(self, action_type: ActionType) -> RateLimitStatus:
        """
        Check if an action is within rate limits.

        Args:
            action_type: Type of action to check

        Returns:
            RateLimitStatus with current limits and availability
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Get current counts
            now = time.time()
            hour_ago = now - 3600
            day_ago = now - 86400
            week_ago = now - 604800

            # Hourly count
            cursor.execute('''
                SELECT COUNT(*) FROM actions
                WHERE action_type = ? AND timestamp > ?
            ''', (action_type.value, hour_ago))
            hourly_count = cursor.fetchone()[0]

            # Daily count
            cursor.execute('''
                SELECT COUNT(*) FROM actions
                WHERE action_type = ? AND timestamp > ?
            ''', (action_type.value, day_ago))
            daily_count = cursor.fetchone()[0]

            # Weekly count
            cursor.execute('''
                SELECT COUNT(*) FROM actions
                WHERE action_type = ? AND timestamp > ?
            ''', (action_type.value, week_ago))
            weekly_count = cursor.fetchone()[0]

            # Check if currently blocked
            cursor.execute('''
                SELECT unblock_at FROM blocks
                WHERE action_type = ? AND unblock_at > ?
                ORDER BY unblock_at DESC LIMIT 1
            ''', (action_type.value, now))
            block_result = cursor.fetchone()

            if block_result:
                unblock_at = block_result[0]
                reset_in = int(unblock_at - now)
                return RateLimitStatus(
                    action_type=action_type,
                    daily_used=daily_count,
                    daily_limit=self.daily_limits.get(action_type, 100),
                    weekly_used=weekly_count,
                    weekly_limit=self.weekly_limits.get(action_type, 500),
                    hourly_used=hourly_count,
                    hourly_limit=self.hourly_limits.get(action_type, 20),
                    can_proceed=False,
                    reset_in_seconds=reset_in,
                    message=f"Action blocked for {reset_in} seconds"
                )

            # Check limits
            hourly_limit = self.hourly_limits.get(action_type, float('inf'))
            daily_limit = self.daily_limits.get(action_type, float('inf'))
            weekly_limit = self.weekly_limits.get(action_type, float('inf'))

            can_proceed = (
                hourly_count < hourly_limit and
                daily_count < daily_limit and
                weekly_count < weekly_limit
            )

            # Calculate reset time
            if not can_proceed:
                if hourly_count >= hourly_limit:
                    reset_in = 3600 - int(now - hour_ago)
                    message = f"Hourly limit reached ({hourly_count}/{hourly_limit})"
                elif daily_count >= daily_limit:
                    reset_in = 86400 - int(now - day_ago)
                    message = f"Daily limit reached ({daily_count}/{daily_limit})"
                else:
                    reset_in = 604800 - int(now - week_ago)
                    message = f"Weekly limit reached ({weekly_count}/{weekly_limit})"

                # Create a block record
                self._create_block(action_type, now + reset_in, message)
            else:
                reset_in = 0
                message = "Within limits"

            return RateLimitStatus(
                action_type=action_type,
                daily_used=daily_count,
                daily_limit=daily_limit,
                weekly_used=weekly_count,
                weekly_limit=weekly_limit,
                hourly_used=hourly_count,
                hourly_limit=hourly_limit,
                can_proceed=can_proceed,
                reset_in_seconds=reset_in,
                message=message
            )

    def _create_block(self, action_type: ActionType, unblock_at: float, reason: str):
        """Create a block record when rate limit is hit."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO blocks (action_type, blocked_at, unblock_at, reason)
                VALUES (?, ?, ?, ?)
            ''', (action_type.value, time.time(), unblock_at, reason))
            conn.commit()

    def wait_if_needed(self, action_type: ActionType) -> bool:
        """
        Check limits and wait if necessary.

        Args:
            action_type: Type of action to perform

        Returns:
            True if action can proceed, False if limit exceeded
        """
        status = self.check_limits(action_type)

        if not status.can_proceed:
            logger.warning(f"Rate limit hit for {action_type.value}: {status.message}")

            if status.reset_in_seconds < 3600:  # Wait if less than 1 hour
                logger.info(f"Waiting {status.reset_in_seconds} seconds...")
                time.sleep(status.reset_in_seconds)
                return True
            else:
                logger.error(f"Rate limit exceeded. Reset in {status.reset_in_seconds/3600:.1f} hours")
                return False

        return True

    def get_statistics(self, days: int = 7) -> Dict[str, Any]:
        """
        Get usage statistics.

        Args:
            days: Number of days to include

        Returns:
            Dictionary with statistics
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cutoff = time.time() - (days * 86400)

            stats = {
                'period_days': days,
                'by_action_type': {},
                'daily_breakdown': {},
                'success_rate': {},
                'recent_blocks': []
            }

            # Get counts by action type
            cursor.execute('''
                SELECT action_type,
                       COUNT(*) as total,
                       SUM(success) as successful,
                       COUNT(*) - SUM(success) as failed
                FROM actions
                WHERE timestamp > ?
                GROUP BY action_type
            ''', (cutoff,))

            for row in cursor.fetchall():
                action = row['action_type']
                total = row['total']
                successful = row['successful'] or 0
                failed = row['failed'] or 0

                stats['by_action_type'][action] = {
                    'total': total,
                    'successful': successful,
                    'failed': failed
                }

                if total > 0:
                    stats['success_rate'][action] = round(successful / total * 100, 2)

            # Get daily breakdown
            cursor.execute('''
                SELECT date, action_type, count
                FROM daily_stats
                WHERE date >= date('now', '-{} days')
                ORDER BY date DESC, action_type
            '''.format(days))

            for row in cursor.fetchall():
                date_str = row['date']
                if date_str not in stats['daily_breakdown']:
                    stats['daily_breakdown'][date_str] = {}
                stats['daily_breakdown'][date_str][row['action_type']] = row['count']

            # Get recent blocks
            cursor.execute('''
                SELECT action_type, blocked_at, unblock_at, reason
                FROM blocks
                WHERE blocked_at > ?
                ORDER BY blocked_at DESC
                LIMIT 10
            ''', (cutoff,))

            for row in cursor.fetchall():
                stats['recent_blocks'].append({
                    'action': row['action_type'],
                    'blocked_at': datetime.fromtimestamp(row['blocked_at']).isoformat(),
                    'unblock_at': datetime.fromtimestamp(row['unblock_at']).isoformat(),
                    'reason': row['reason']
                })

            return stats

    def get_connection_history(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get connection request history.

        Args:
            days: Number of days to include

        Returns:
            List of connection records
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cutoff = time.time() - (days * 86400)

            cursor.execute('''
                SELECT profile_url, profile_name, timestamp, success, error_message
                FROM actions
                WHERE action_type = ? AND timestamp > ?
                ORDER BY timestamp DESC
            ''', (ActionType.CONNECTION_REQUEST.value, cutoff))

            history = []
            for row in cursor.fetchall():
                history.append({
                    'profile_url': row['profile_url'],
                    'profile_name': row['profile_name'],
                    'timestamp': datetime.fromtimestamp(row['timestamp']).isoformat(),
                    'success': bool(row['success']),
                    'error_message': row['error_message']
                })

            return history

    def reset_limits(self, action_type: Optional[ActionType] = None):
        """
        Manually reset rate limits (for testing/recovery).

        Args:
            action_type: Specific action type to reset, or None for all
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            if action_type:
                cursor.execute('''
                    DELETE FROM blocks WHERE action_type = ?
                ''', (action_type.value,))
                logger.info(f"Reset limits for {action_type.value}")
            else:
                cursor.execute('DELETE FROM blocks')
                logger.info("Reset all rate limits")

            conn.commit()

    def export_data(self, export_path: Path, format: str = 'csv'):
        """
        Export action history to file.

        Args:
            export_path: Path to export file
            format: Export format ('csv' or 'json')
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute('''
                SELECT * FROM actions
                ORDER BY timestamp DESC
            ''')

            rows = cursor.fetchall()

            if format == 'csv':
                import csv
                with open(export_path, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([desc[0] for desc in cursor.description])
                    for row in rows:
                        writer.writerow(row)
            elif format == 'json':
                data = []
                for row in rows:
                    data.append(dict(zip([desc[0] for desc in cursor.description], row)))
                with open(export_path, 'w') as f:
                    json.dump(data, f, indent=2)

            logger.info(f"Exported {len(rows)} records to {export_path}")

    def cleanup_old_records(self, days_to_keep: int = 90):
        """
        Remove old records to keep database size manageable.

        Args:
            days_to_keep: Number of days of history to keep
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cutoff = time.time() - (days_to_keep * 86400)

            cursor.execute('DELETE FROM actions WHERE timestamp < ?', (cutoff,))
            deleted_actions = cursor.rowcount

            cursor.execute('DELETE FROM blocks WHERE unblock_at < ?', (cutoff,))
            deleted_blocks = cursor.rowcount

            # Clean up old daily stats
            cutoff_date = (date.today() - timedelta(days=days_to_keep)).isoformat()
            cursor.execute('DELETE FROM daily_stats WHERE date < ?', (cutoff_date,))
            deleted_stats = cursor.rowcount

            conn.commit()

            logger.info(f"Cleaned up: {deleted_actions} actions, "
                       f"{deleted_blocks} blocks, {deleted_stats} daily stats")

    def get_current_usage(self) -> Dict[ActionType, Dict[str, int]]:
        """
        Get current usage for all action types.

        Returns:
            Dictionary mapping action types to their current usage
        """
        usage = {}

        for action_type in ActionType:
            status = self.check_limits(action_type)
            usage[action_type] = {
                'hourly': status.hourly_used,
                'daily': status.daily_used,
                'weekly': status.weekly_used,
                'can_proceed': status.can_proceed
            }

        return usage

    def update_limits(self, daily: Optional[Dict[ActionType, int]] = None,
                     weekly: Optional[Dict[ActionType, int]] = None,
                     hourly: Optional[Dict[ActionType, int]] = None):
        """
        Update rate limits.

        Args:
            daily: New daily limits
            weekly: New weekly limits
            hourly: New hourly limits
        """
        if daily:
            self.daily_limits.update(daily)
        if weekly:
            self.weekly_limits.update(weekly)
        if hourly:
            self.hourly_limits.update(hourly)

        # Store in database for persistence
        with self._get_connection() as conn:
            cursor = conn.cursor()

            settings = {
                'daily_limits': json.dumps({k.value: v for k, v in self.daily_limits.items()}),
                'weekly_limits': json.dumps({k.value: v for k, v in self.weekly_limits.items()}),
                'hourly_limits': json.dumps({k.value: v for k, v in self.hourly_limits.items()})
            }

            for key, value in settings.items():
                cursor.execute('''
                    INSERT OR REPLACE INTO settings (key, value, updated_at)
                    VALUES (?, ?, ?)
                ''', (key, value, time.time()))

            conn.commit()

        logger.info("Rate limits updated")