import os
from dotenv import load_dotenv

class Config:
    """Configuration class for email application settings."""
    
    def __init__(self):
        load_dotenv()
        
    @property
    def email(self):
        return os.getenv("EMAIL")
    
    @property
    def password(self):
        return os.getenv("PASSWORD")
    
    @property
    def imap_server(self):
        return os.getenv("IMAP_SERVER", "imap.mail.yahoo.com")
    
    @property
    def blocked_emails_file(self):
        return os.getenv("BLOCKED_EMAILS_FILE", "blocked_emails.json")
    
    @property
    def window_width(self):
        return int(os.getenv("WINDOW_WIDTH", "700"))
    
    @property
    def window_height(self):
        return int(os.getenv("WINDOW_HEIGHT", "600"))

# Global config instance
config = Config()