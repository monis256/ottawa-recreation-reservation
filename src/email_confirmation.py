import imaplib
import email
import re
from email.header import decode_header


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
        - confirmation_code (str): The extracted confirmation code, or None if not found.
        """

        imap = imaplib.IMAP4_SSL(self.imap_server)
        imap.login(self.imap_email, self.imap_password)

        FROM_EMAIL = "noreply@frontdesksuite.com"
        FROM_SUBJECT = "Verify your email"

        status, messages = imap.select("INBOX")
        emails_count = 1
        messages = int(messages[0])

        confirmation_code = None

        for i in range(messages, messages - emails_count, -1):
            res, msg = imap.fetch(str(i), "(RFC822)")
            for response in msg:
                if isinstance(response, tuple):
                    msg = email.message_from_bytes(response[1])
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding)
                    From, encoding = decode_header(msg.get("From"))[0]
                    if isinstance(From, bytes):
                        From = From.decode(encoding)
                    if FROM_EMAIL in From and FROM_SUBJECT in subject:
                        if msg.is_multipart():
                            for part in msg.walk():
                                try:
                                    body = part.get_payload(decode=True).decode()
                                except:
                                    pass
                        else:
                            body = msg.get_payload(decode=True).decode()
                        pattern = r"\b\d{4}\b"
                        confirmation_code = re.findall(pattern, body)[0]
        imap.close()
        imap.logout()

        return confirmation_code
