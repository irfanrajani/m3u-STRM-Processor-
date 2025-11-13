"""Notification manager - send notifications via multiple channels."""
import logging
import asyncio
from enum import Enum
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
import httpx

logger = logging.getLogger(__name__)


class NotificationLevel(str, Enum):
    """Notification severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class NotificationChannel(str, Enum):
    """Supported notification channels."""
    TELEGRAM = "telegram"
    PUSHOVER = "pushover"
    WEBHOOK = "webhook"
    EMAIL = "email"


@dataclass
class NotificationConfig:
    """Configuration for a notification channel."""
    channel: NotificationChannel
    enabled: bool
    config: Dict[str, Any]
    min_level: NotificationLevel = NotificationLevel.INFO


class TelegramNotifier:
    """Send notifications via Telegram."""

    def __init__(self, bot_token: str, chat_id: str):
        """
        Initialize Telegram notifier.

        Args:
            bot_token: Telegram bot API token
            chat_id: Telegram chat ID to send messages to
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"

    async def send(self, title: str, message: str, level: NotificationLevel) -> bool:
        """Send notification via Telegram."""
        try:
            # Format message with emoji based on level
            emoji = {
                NotificationLevel.INFO: "ℹ️",
                NotificationLevel.WARNING: "⚠️",
                NotificationLevel.ERROR: "❌",
                NotificationLevel.CRITICAL: "🔥"
            }.get(level, "📢")

            text = f"{emoji} *{title}*\n\n{message}"

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/sendMessage",
                    json={
                        "chat_id": self.chat_id,
                        "text": text,
                        "parse_mode": "Markdown"
                    },
                    timeout=10
                )

                if response.status_code == 200:
                    logger.info(f"Telegram notification sent successfully")
                    return True
                else:
                    logger.error(f"Telegram API error: {response.status_code} - {response.text}")
                    return False

        except Exception as e:
            logger.error(f"Failed to send Telegram notification: {str(e)}")
            return False


class PushoverNotifier:
    """Send notifications via Pushover."""

    def __init__(self, user_key: str, api_token: str):
        """
        Initialize Pushover notifier.

        Args:
            user_key: Pushover user key
            api_token: Pushover API token
        """
        self.user_key = user_key
        self.api_token = api_token
        self.api_url = "https://api.pushover.net/1/messages.json"

    async def send(self, title: str, message: str, level: NotificationLevel) -> bool:
        """Send notification via Pushover."""
        try:
            # Map notification level to Pushover priority
            priority = {
                NotificationLevel.INFO: 0,
                NotificationLevel.WARNING: 0,
                NotificationLevel.ERROR: 1,
                NotificationLevel.CRITICAL: 2
            }.get(level, 0)

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.api_url,
                    data={
                        "token": self.api_token,
                        "user": self.user_key,
                        "title": title,
                        "message": message,
                        "priority": priority
                    },
                    timeout=10
                )

                if response.status_code == 200:
                    logger.info(f"Pushover notification sent successfully")
                    return True
                else:
                    logger.error(f"Pushover API error: {response.status_code} - {response.text}")
                    return False

        except Exception as e:
            logger.error(f"Failed to send Pushover notification: {str(e)}")
            return False


class WebhookNotifier:
    """Send notifications via generic webhook."""

    def __init__(self, webhook_url: str, headers: Optional[Dict[str, str]] = None):
        """
        Initialize webhook notifier.

        Args:
            webhook_url: Webhook URL to POST notifications to
            headers: Optional HTTP headers
        """
        self.webhook_url = webhook_url
        self.headers = headers or {"Content-Type": "application/json"}

    async def send(self, title: str, message: str, level: NotificationLevel) -> bool:
        """Send notification via webhook."""
        try:
            payload = {
                "title": title,
                "message": message,
                "level": level.value,
                "timestamp": asyncio.get_event_loop().time()
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.webhook_url,
                    json=payload,
                    headers=self.headers,
                    timeout=10
                )

                if response.status_code in [200, 201, 202]:
                    logger.info(f"Webhook notification sent successfully")
                    return True
                else:
                    logger.error(f"Webhook error: {response.status_code} - {response.text}")
                    return False

        except Exception as e:
            logger.error(f"Failed to send webhook notification: {str(e)}")
            return False


class NotificationManager:
    """Manages all notification channels and routing."""

    def __init__(self):
        """Initialize notification manager."""
        self.notifiers: Dict[NotificationChannel, Any] = {}
        self.configs: Dict[NotificationChannel, NotificationConfig] = {}

    def configure_telegram(self, bot_token: str, chat_id: str,
                          enabled: bool = True,
                          min_level: NotificationLevel = NotificationLevel.INFO):
        """Configure Telegram notifications."""
        config = NotificationConfig(
            channel=NotificationChannel.TELEGRAM,
            enabled=enabled,
            config={"bot_token": bot_token, "chat_id": chat_id},
            min_level=min_level
        )
        self.configs[NotificationChannel.TELEGRAM] = config
        if enabled:
            self.notifiers[NotificationChannel.TELEGRAM] = TelegramNotifier(bot_token, chat_id)
        logger.info(f"Telegram notifications configured (enabled: {enabled})")

    def configure_pushover(self, user_key: str, api_token: str,
                          enabled: bool = True,
                          min_level: NotificationLevel = NotificationLevel.INFO):
        """Configure Pushover notifications."""
        config = NotificationConfig(
            channel=NotificationChannel.PUSHOVER,
            enabled=enabled,
            config={"user_key": user_key, "api_token": api_token},
            min_level=min_level
        )
        self.configs[NotificationChannel.PUSHOVER] = config
        if enabled:
            self.notifiers[NotificationChannel.PUSHOVER] = PushoverNotifier(user_key, api_token)
        logger.info(f"Pushover notifications configured (enabled: {enabled})")

    def configure_webhook(self, webhook_url: str, headers: Optional[Dict[str, str]] = None,
                         enabled: bool = True,
                         min_level: NotificationLevel = NotificationLevel.INFO):
        """Configure webhook notifications."""
        config = NotificationConfig(
            channel=NotificationChannel.WEBHOOK,
            enabled=enabled,
            config={"webhook_url": webhook_url, "headers": headers},
            min_level=min_level
        )
        self.configs[NotificationChannel.WEBHOOK] = config
        if enabled:
            self.notifiers[NotificationChannel.WEBHOOK] = WebhookNotifier(webhook_url, headers)
        logger.info(f"Webhook notifications configured (enabled: {enabled})")

    async def send(
        self,
        title: str,
        message: str,
        level: NotificationLevel = NotificationLevel.INFO,
        channels: Optional[List[NotificationChannel]] = None
    ) -> Dict[NotificationChannel, bool]:
        """
        Send notification through enabled channels.

        Args:
            title: Notification title
            message: Notification message
            level: Notification severity level
            channels: Specific channels to use (None = all enabled)

        Returns:
            Dictionary mapping channels to success status
        """
        results = {}

        # Determine which channels to use
        target_channels = channels if channels else list(self.notifiers.keys())

        # Send to each enabled channel
        tasks = []
        for channel in target_channels:
            config = self.configs.get(channel)
            notifier = self.notifiers.get(channel)

            # Skip if not configured or disabled
            if not config or not config.enabled or not notifier:
                continue

            # Check minimum level
            level_priorities = {
                NotificationLevel.INFO: 0,
                NotificationLevel.WARNING: 1,
                NotificationLevel.ERROR: 2,
                NotificationLevel.CRITICAL: 3
            }
            if level_priorities.get(level, 0) < level_priorities.get(config.min_level, 0):
                logger.debug(f"Skipping {channel} notification - level {level} below minimum {config.min_level}")
                continue

            # Send notification
            logger.info(f"Sending {level} notification via {channel}: {title}")
            tasks.append(self._send_to_channel(channel, notifier, title, message, level))

        # Wait for all notifications to complete
        if tasks:
            channel_results = await asyncio.gather(*tasks, return_exceptions=True)
            for (channel, _), result in zip([(c, n) for c, n in self.notifiers.items() if c in target_channels], channel_results):
                if isinstance(result, Exception):
                    logger.error(f"Notification to {channel} failed with exception: {str(result)}")
                    results[channel] = False
                else:
                    results[channel] = result

        return results

    async def _send_to_channel(self, channel: NotificationChannel, notifier: Any,
                              title: str, message: str, level: NotificationLevel) -> tuple:
        """Send to a specific channel and return (channel, success)."""
        try:
            success = await notifier.send(title, message, level)
            return (channel, success)
        except Exception as e:
            logger.error(f"Exception sending to {channel}: {str(e)}")
            return (channel, False)

    async def send_info(self, title: str, message: str):
        """Send INFO level notification."""
        return await self.send(title, message, NotificationLevel.INFO)

    async def send_warning(self, title: str, message: str):
        """Send WARNING level notification."""
        return await self.send(title, message, NotificationLevel.WARNING)

    async def send_error(self, title: str, message: str):
        """Send ERROR level notification."""
        return await self.send(title, message, NotificationLevel.ERROR)

    async def send_critical(self, title: str, message: str):
        """Send CRITICAL level notification."""
        return await self.send(title, message, NotificationLevel.CRITICAL)


# Global notification manager instance
notification_manager = NotificationManager()
