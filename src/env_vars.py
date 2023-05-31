import os
import sys
import logging
from typing import Dict, Tuple
from dotenv import load_dotenv


class EnvVars:
    """
    A class that represents a set of required environment variables.

    Attributes:
    - phone_number (str): The phone number.
    - imap_email (str): The email address to get confirmation to.
    - imap_password (str): The email password.
    - imap_server (str): The email IMAP server.
    - name (str): Your name for reservation.
    - telegram_bot_token (str): The Telegram bot token used to authenticate requests.
    - telegram_chat_id (str): The chat ID of the configured Telegram chat.

    Methods:
    - check_env_vars(required_vars: Tuple[str, ...]) -> Dict[str, str]:
        Checks whether the required environment variables are set.
    - __init__(self, env_vars: Dict[str, str]):
        Initializes an instance of the EnvVars class with environment variables.
    """
    REQUIRED_VARS = (
        'PHONE_NUMBER',
        'IMAP_EMAIL',
        'IMAP_PASSWORD',
        'IMAP_SERVER',
        'NAME',
        'TELEGRAM_BOT_TOKEN',
        'TELEGRAM_CHAT_ID'
    )

    def __init__(self, env_vars: Dict[str, str]):
        """
        Initializes an instance of the EnvVars class with environment variables.

        Args:
        - env_vars (Dict[str, str]): A dictionary containing environment variable names and values.

        Returns:
        - None
        """
        self.phone_number = env_vars['PHONE_NUMBER']
        self.imap_email = env_vars['IMAP_EMAIL']
        self.imap_password = env_vars['IMAP_PASSWORD']
        self.imap_server = env_vars['IMAP_SERVER']
        self.name = env_vars['NAME']
        self.telegram_bot_token = env_vars['TELEGRAM_BOT_TOKEN']
        self.telegram_chat_id = env_vars['TELEGRAM_CHAT_ID']

    @staticmethod
    def check_env_vars(required_vars: Tuple[str, ...]) -> Dict[str, str]:
        """
        Checks whether the required environment variables are set.

        Args:
        - required_vars (Tuple[str, ...]): A tuple of environment variable names that are required.

        Returns:
        - env_vars (Dict[str, str]): A dictionary containing environment variable names and values.
        """
        load_dotenv()
        logging.basicConfig(level=logging.INFO)
        env_vars = {var: os.environ.get(var) for var in required_vars}

        if all(env_vars.values()):
            logging.info('✅ All required environment variables are set...')
            return env_vars

        missing_vars = [var for var in required_vars if not env_vars[var]]
        for var in missing_vars:
            logging.error('❌ Environment variable %s not set', var)
        sys.exit(1)
