import imaplib
import email
import re
from email.header import decode_header
from constant import FROM_EMAIL, FROM_SUBJECT


class ConfirmationCodeExtractor:
    """
    A class that extracts confirmation codes from emails using IMAP.

    Attributes:
    - imap_server (str): The IMAP server address.
    - imap_email (str): The email address to log in with.
    - imap_password (str): The password for the email account.

    Methods:
    - __init__(self, imap_server: str, imap_email: str, imap_password: str):
        Initializes an instance of the ConfirmationCodeExtractor class.
    - get_confirmation_code(self) -> str:
        Retrieves the confirmation code from the latest email.
    - _decode_bytes(self, value: bytes) -> str:
        Decode the value if it's in bytes format.

    """

    def __init__(self, imap_server: str, imap_email: str, imap_password: str):
        """
        Initialize an instance of the ConfirmationCodeExtractor class.

        Args:
        - imap_server (str): The IMAP server address.
        - imap_email (str): The email address to log in with.
        - imap_password (str): The password for the email account.

        Returns:
        - None
        """
        self.imap_server = imap_server
        self.imap_email = imap_email
        self.imap_password = imap_password

    def get_confirmation_code(self) -> str:
        """
        Retrieve the confirmation code from the latest email.

        Returns:
        - confirmation_code (str): The extracted confirmation code.
        """
        confirmation_code = None
        with imaplib.IMAP4_SSL(self.imap_server) as imap:
            imap.login(self.imap_email, self.imap_password)
            imap.select("INBOX")
            _, messages = imap.search(None, "UNSEEN")

            for email_id in messages[0].split():
                _, msg = imap.fetch(email_id, "(RFC822)")
                email_message = email.message_from_bytes(msg[0][1])
                subject_header, from_header = (
                    decode_header(email_message["Subject"])[0][0],
                    decode_header(email_message["From"])[0][0],
                )

                subject = self._decode_bytes(subject_header)
                email_from = self._decode_bytes(from_header)

                if FROM_EMAIL in email_from and FROM_SUBJECT in subject:
                    for part in email_message.walk():
                        if part.get_content_type() == "text/plain":
                            payload = part.get_payload(decode=True)
                            match = re.search(r"\b\d{4}\b", payload.decode())
                            if match:
                                return match.group(0)

        return confirmation_code

    @staticmethod
    def _decode_bytes(value: bytes) -> str:
        """
        Decode the value if it's in bytes format.

        Args:
        - value (bytes): The value to decode.

        Returns:
        - Decoded value (str).
        """
        return value.decode() if isinstance(value, bytes) else value
