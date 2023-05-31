import imaplib
import email
import re
from email.header import decode_header


def get_confirmation_code(imap_server, imap_email, imap_password):
    imap = imaplib.IMAP4_SSL(imap_server)
    imap.login(imap_email, imap_password)

    FROM_EMAIL = "noreply@frontdesksuite.com"
    FROM_SUBJECT = "Verify your email"

    status, messages = imap.select("INBOX")
    emails_count = 1
    messages = int(messages[0])

    for i in range(messages, messages-emails_count, -1):
        # fetch the email message by ID
        res, msg = imap.fetch(str(i), "(RFC822)")
        for response in msg:
            if isinstance(response, tuple):
                # parse a bytes email into a message object
                msg = email.message_from_bytes(response[1])
                # decode the email subject
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
                else:
                    confirmation_code = None
    imap.close()
    imap.logout()
    return confirmation_code
