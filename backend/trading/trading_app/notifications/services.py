

from typing import Dict, List, Optional
import logging
from datetime import datetime
import firebase_admin
from firebase_admin import messaging
from django.conf import settings
from django.core.mail import send_mail
from telegram import Bot
import aiohttp
import asyncio
from dataclasses import dataclass


@dataclass
class NotificationPreference:
    email: bool = True
    push: bool = True
    telegram: bool = False
    slack: bool = False
    notification_types: List[str] = None
    quiet_hours: Dict[str, str] = None


class NotificationService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.firebase_app = firebase_admin.initialize_app()
        self.telegram_bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)

    async def send_notification(self,
                                user_id: int,
                                notification_type: str,
                                content: Dict,
                                priority: str = 'normal') -> bool:
        """Envoie une notification via tous les canaux configurés"""
        try:
            # Récupération des préférences utilisateur
            preferences = await self.get_user_preferences(user_id)

            if not self._should_send_notification(
                    preferences,
                    notification_type,
                    priority
            ):
                return False

            # Envoi asynchrone sur tous les canaux activés
            tasks = []

            if preferences.email:
                tasks.append(self._send_email_notification(
                    user_id,
                    content
                ))

            if preferences.push:
                tasks.append(self._send_push_notification(
                    user_id,
                    content
                ))

            if preferences.telegram:
                tasks.append(self._send_telegram_notification(
                    user_id,
                    content
                ))

            if preferences.slack:
                tasks.append(self._send_slack_notification(
                    user_id,
                    content
                ))

            # Exécution asynchrone de toutes les notifications
            await asyncio.gather(*tasks)

            # Journalisation de la notification
            await self._log_notification(
                user_id,
                notification_type,
                content,
                priority
            )

            return True

        except Exception as e:
            self.logger.error(
                f"Erreur lors de l'envoi de la notification: {str(e)}"
            )
            return False

    async def _send_push_notification(self,
                                      user_id: int,
                                      content: Dict) -> None:
        """Envoie une notification push via Firebase"""
        try:
            # Récupération du token Firebase de l'utilisateur
            token = await self.get_user_firebase_token(user_id)

            if not token:
                return

            message = messaging.Message(
                notification=messaging.Notification(
                    title=content['title'],
                    body=content['message']
                ),
                data=content.get('data', {}),
                token=token,
                android=messaging.AndroidConfig(
                    priority='high' if content.get('urgent') else 'normal'
                ),
                apns=messaging.APNSConfig(
                    payload=messaging.APNSPayload(
                        aps=messaging.Aps(
                            sound='default',
                            badge=1
                        )
                    )
                )
            )

            response = messaging.send(message)
            self.logger.info(f"Notification push envoyée: {response}")

        except Exception as e:
            self.logger.error(f"Erreur lors de l'envoi push: {str(e)}")
            raise

    async def _send_telegram_notification(self,
                                          user_id: int,
                                          content: Dict) -> None:
        """Envoie une notification via Telegram"""
        try:
            chat_id = await self.get_user_telegram_chat_id(user_id)

            if not chat_id:
                return

            message = f"*{content['title']}*\n\n{content['message']}"

            if 'data' in content:
                message += f"\n\nDétails:\n```\n{content['data']}\n```"

            await self.telegram_bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode='Markdown'
            )

        except Exception as e:
            self.logger.error(f"Erreur lors de l'envoi Telegram: {str(e)}")
            raise

    async def _send_slack_notification(self,
                                       user_id: int,
                                       content: Dict) -> None:
        """Envoie une notification via Slack"""
        try:
            webhook_url = await self.get_user_slack_webhook(user_id)

            if not webhook_url:
                return

            async with aiohttp.ClientSession() as session:
                payload = {
                    "text": content['message'],
                    "attachments": [{
                        "title": content['title'],
                        "color": "#36a64f" if content.get('success') else "#ff0000",
                        "fields": [
                            {
                                "title": k,
                                "value": str(v),
                                "short": True
                            }
                            for k, v in content.get('data', {}).items()
                        ]
                    }]
                }

                async with session.post(webhook_url, json=payload) as response:
                    if response.status != 200:
                        raise Exception(f"Erreur Slack: {await response.text()}")

        except Exception as e:
            self.logger.error(f"Erreur lors de l'envoi Slack: {str(e)}")
            raise