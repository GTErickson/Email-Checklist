import json
import os
import re
from typing import Set, List


class SpamBlocker:
    """Handles spam blocking functionality for email addresses."""
    
    def __init__(self, blocked_file: str = "blocked_emails.json"):
        self.blocked_file = blocked_file
        self.blocked_emails = self.load_blocked_emails()
    
    def load_blocked_emails(self) -> Set[str]:
        """Load blocked email addresses from file."""
        try:
            if os.path.exists(self.blocked_file):
                with open(self.blocked_file, 'r') as f:
                    return set(json.load(f))
            return set()
        except Exception as e:
            print(f"Error loading blocked emails: {e}")
            return set()
    
    def save_blocked_emails(self) -> None:
        """Save blocked email addresses to file."""
        try:
            with open(self.blocked_file, 'w') as f:
                json.dump(list(self.blocked_emails), f, indent=2)
        except Exception as e:
            print(f"Error saving blocked emails: {e}")
    
    def add_blocked_email(self, email_address: str) -> None:
        """Add an email address to the blocked list."""
        email_address = email_address.lower().strip()
        self.blocked_emails.add(email_address)
        self.save_blocked_emails()
    
    def remove_blocked_email(self, email_address: str) -> bool:
        """Remove an email address from the blocked list."""
        email_address = email_address.lower().strip()
        if email_address in self.blocked_emails:
            self.blocked_emails.remove(email_address)
            self.save_blocked_emails()
            return True
        return False
    
    def is_blocked(self, email_address: str) -> bool:
        """Check if an email address is blocked."""
        if not email_address:
            return False
        
        # Extract email address from "Name <email@domain.com>" format
        email_match = re.search(r'<([^>]+)>', email_address)
        if email_match:
            email_address = email_match.group(1)
        
        return email_address.lower().strip() in self.blocked_emails
    
    def get_blocked_emails(self) -> List[str]:
        """Get sorted list of blocked email addresses."""
        return sorted(list(self.blocked_emails))
    
    def extract_email_address(self, email_string: str) -> str:
        """Extract clean email address from various formats."""
        if not email_string:
            return ""
        
        # Extract email address from "Name <email@domain.com>" format
        email_match = re.search(r'<([^>]+)>', email_string)
        if email_match:
            return email_match.group(1).strip()
        
        # Return the original string if no angle brackets found
        return email_string.strip()