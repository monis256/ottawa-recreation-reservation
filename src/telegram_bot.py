import logging
from typing import Union
import requests
from constant import TG_API_URL


class TelegramBot:
    """
    A class that interacts with the Telegram API to send messages and photos.

    Attributes:
    - telegram_bot_token (str): The Telegram bot token used to authenticate.
    - telegram_chat_id (int): The chat ID of the configured Telegram chat.
    - session (requests.Session): The requests session used to send requests.

    Methods:
    - send_message(text: str) -> Union[requests.Response, None]:
        Sends a text message to the configured Telegram chat.
    - send_photo(photo_file: file) -> Union[requests.Response, None]:
        Sends a photo file to the configured Telegram chat.
    """
    def __init__(self, env_var):
        """
        Initialize a TelegramBot object with the env vars and requests session.
        Args:
            env_var: Object with the environment variables.
        """
        self.telegram_bot_token: str = env_var.telegram_bot_token
        self.telegram_chat_id: int = env_var.telegram_chat_id
        self.session: requests.Session = requests.Session()
        self.session.headers.update({'User-Agent': 'My Telegram Bot'})

    def send_message(self, text: str) -> Union[requests.Response, None]:
        """
        Send a text message to the configured Telegram chat.

        Args:
            text (str): The text message to send.

        Returns:
            The response object from the Telegram API if successful.
        """
        url: str = f'{TG_API_URL}{self.telegram_bot_token}/sendMessage'
        payload: dict = {
            'chat_id': self.telegram_chat_id,
            'text': text
        }
        try:
            with self.session.post(url, json=payload) as response:
                response.raise_for_status()
                return response
        except requests.exceptions.RequestException as e:
            logging.error('❌ Error sending message: %s', e)
            return None

    def send_photo(self, photo_file):
        """
        Send a photo file to the configured Telegram chat.

        Args:
            photo_file (file): The file object of the photo to send.

        Returns:
            The response object from the Telegram API if successful.
        """
        url: str = f'{TG_API_URL}{self.telegram_bot_token}/sendPhoto'
        payload: dict = {
            'chat_id': self.telegram_chat_id
        }
        files = {'photo': photo_file}
        try:
            response: requests.Response = self.session.post(
                url,
                data=payload,
                files=files
            )
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            logging.error('❌ Error sending photo: %s', e)
            return None
