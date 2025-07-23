import email.utils
import datetime
import re
from typing import Dict


class EmailFormatter:
    """Utility class for formatting email data for display."""
    
    @staticmethod
    def format_sender_name(from_address: str) -> str:
        """Extract and format sender name from email address."""
        if not from_address:
            return "Unknown Sender"
        
        name_match = re.match(r"([^<]+)", from_address)
        if name_match:
            return name_match.group(1).strip()
        return from_address
    
    @staticmethod
    def format_subject(subject: str, max_chars: int = 50) -> str:
        """Truncate subject line if too long."""
        if not subject:
            return "No Subject"
        
        if len(subject) > max_chars:
            return subject[:max_chars - 3] + "..."
        return subject
    
    @staticmethod
    def format_date(date_string: str) -> str:
        """Format email date for display."""
        try:
            email_date = email.utils.parsedate_to_datetime(date_string)
            now = datetime.datetime.now()
            
            # Show time if today, otherwise show date
            if email_date.date() == now.date():
                return email_date.strftime("%I:%M %p").lstrip("0")
            else:
                return email_date.strftime("%b %d")
        except:
            return "Unknown Date"
    
    @staticmethod
    def format_email_list_item(email_data: Dict) -> str:
        """Format email data for listbox display."""
        name = EmailFormatter.format_sender_name(email_data["from"])
        subject = EmailFormatter.format_subject(email_data["subject"])
        date_str = EmailFormatter.format_date(email_data["date"])
        
        return f"{name} - {subject} - {date_str}\n\n"
    
    @staticmethod
    def format_email_content(email_data: Dict) -> str:
        """Format email data for content display."""
        separator = "-" * 80
        return (
            f"Subject: {email_data['subject']}\n"
            f"From: {email_data['from']}\n"
            f"Date: {email_data['date']}\n"
            f"{separator}\n\n"
            f"{email_data['body']}\n\n"
            f"{separator}"
        )


class EmailValidator:
    """Utility class for email validation."""
    
    @staticmethod
    def is_valid_email(email_address: str) -> bool:
        """Basic email validation."""
        if not email_address:
            return False
        
        # Simple regex for email validation
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email_address.strip()) is not None
    
    @staticmethod
    def extract_email_from_string(email_string: str) -> str:
        """Extract email address from various formats."""
        if not email_string:
            return ""
        
        # Extract from "Name <email@domain.com>" format
        email_match = re.search(r'<([^>]+)>', email_string)
        if email_match:
            return email_match.group(1).strip()
        
        # Return original if already in plain format
        return email_string.strip()