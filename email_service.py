import imaplib
import email
from email.header import decode_header
from email.message import Message
import datetime
from typing import List, Dict, Optional
from spam_blocker import SpamBlocker


class EmailService:
    """Service class for handling email operations."""
    
    def __init__(self, imap_server: str):
        self.imap_server = imap_server
        self.mail_connection: Optional[imaplib.IMAP4_SSL] = None
    
    def connect(self, email_address: str, password: str) -> bool:
        """Establish IMAP connection."""
        try:
            self.mail_connection = imaplib.IMAP4_SSL(self.imap_server)
            self.mail_connection.login(email_address, password)
            return True
        except Exception as e:
            print(f"Failed to connect to email server: {e}")
            self.mail_connection = None
            return False
    
    def disconnect(self) -> None:
        """Close IMAP connection."""
        if self.mail_connection:
            try:
                self.mail_connection.logout()
            except:
                pass
            self.mail_connection = None
    
    def is_connected(self) -> bool:
        """Check if connection is active."""
        return self.mail_connection is not None
    
    def fetch_recent_emails(self, spam_blocker: SpamBlocker, days: int = 1) -> List[Dict]:
        """Fetch emails from the last specified number of days."""
        try:
            if not self.mail_connection:
                raise Exception("No active email connection.")

            self.mail_connection.select("inbox")

            # Calculate the date for filtering emails
            date_threshold = (datetime.datetime.now() - datetime.timedelta(days=days)).strftime("%d-%b-%Y")

            # Search for emails since the calculated date
            result, data = self.mail_connection.search(None, f'SINCE {date_threshold}')
            if result != "OK":
                raise Exception("Failed to search inbox.")

            mail_ids = data[0].split()
            emails = []

            for mail_id in reversed(mail_ids):  # Most recent first
                email_data = self._fetch_single_email(mail_id)
                if email_data and not spam_blocker.is_blocked(email_data["from"]):
                    emails.append(email_data)

            return emails

        except Exception as e:
            print(f"Error fetching emails: {e}")
            return []
    
    def _fetch_single_email(self, mail_id: bytes) -> Optional[Dict]:
        """Fetch and parse a single email."""
        try:
            res, msg_data = self.mail_connection.fetch(mail_id, "(RFC822)")
            if res != "OK":
                return None

            msg = email.message_from_bytes(msg_data[0][1])

            # Decode subject
            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding if encoding else "utf-8")

            from_ = msg.get("From")
            date_ = msg.get("Date")

            # Extract email body
            body = self._extract_email_body(msg)

            return {
                "subject": subject,
                "from": from_,
                "date": date_,
                "body": body
            }

        except Exception as e:
            print(f"Error processing email {mail_id}: {e}")
            return None
    
    def _extract_email_body(self, msg: Message) -> str:
        """Extract text body from email message."""
        body = ""
        try:
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))

                    if content_type == "text/plain" and "attachment" not in content_disposition:
                        payload = part.get_payload(decode=True)
                        if payload:
                            body = payload.decode("utf-8", errors="ignore")
                        break
            else:
                payload = msg.get_payload(decode=True)
                if payload:
                    body = payload.decode("utf-8", errors="ignore")
        except Exception as e:
            print(f"Error extracting email body: {e}")
            body = "Error reading email content"
        
        return body