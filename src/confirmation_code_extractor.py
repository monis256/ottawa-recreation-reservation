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
    """

    def __init__(self, imap_server: str, imap_email: str, imap_password: str):
        """
        Initializes an instance of the ConfirmationCodeExtractor class.

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
        Retrieves the confirmation code from the latest email.

        Returns:
        - confirmation_code (str): The extracted confirmation code.
        """
        confirmation_code = None
        with imaplib.IMAP4_SSL(self.imap_server) as imap:
            imap.login(self.imap_email, self.imap_password)
            imap.select("INBOX")
            _, messages = imap.search(None, "UNSEEN")
            email_ids = messages[0].split()

            for email_id in email_ids:
                _, msg = imap.fetch(email_id, "(RFC822)")
                for response in msg:
                    if isinstance(response, tuple):
                        msg = email.message_from_bytes(response[1])
                        subject, encoding = decode_header(msg["Subject"])[0]
                        if isinstance(subject, bytes):
                            subject = subject.decode(encoding)
                        email_from, encoding = \
                            decode_header(msg.get("From"))[0]
                        if isinstance(email_from, bytes):
                            email_from = email_from.decode(encoding)
                        if FROM_EMAIL in email_from and \
                           FROM_SUBJECT in subject:
                            if msg.is_multipart():
                                for part in msg.walk():
                                    content_type = part.get_content_type()
                                    if content_type == "text/plain":
                                        body = part.get_payload(decode=True)\
                                            .decode()
                                        pattern = r"\b\d{4}\b"
                                        match = re.search(pattern, body)
                                        if match:
                                            confirmation_code = match.group(0)
                                            break
                            else:
                                body = msg.get_payload(decode=True).decode()
                                pattern = r"\b\d{4}\b"
                                match = re.search(pattern, body)
                                if match:
                                    confirmation_code = match.group(0)
                                    break

        return confirmation_code
