"""
Main application file for the Email Viewer with Spam Blocking.
This file ties together all the components and provides the main GUI application.
"""

import tkinter as tk
from tkinter import messagebox
from typing import List, Dict, Optional
import re

# Import our custom modules
from config import config
from spam_blocker import SpamBlocker
from email_service import EmailService
from email_utils import EmailFormatter, EmailValidator
from gui_frames import StartupFrame, EmailListFrame, EmailContentFrame, SpamSettingsFrame


class EmailApp(tk.Tk):
    """Main email application class."""
    
    def __init__(self):
        super().__init__()
        self.title("Email Viewer with Spam Blocking")
        self.geometry(f"{config.window_width}x{config.window_height}")
        
        # Initialize services
        self.email_service = EmailService(config.imap_server)
        self.spam_blocker = SpamBlocker(config.blocked_emails_file)
        
        # Data storage
        self.email_data: List[Dict] = []
        
        # Configure grid weights
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Initialize GUI frames
        self._init_frames()
        
        # Start with startup frame
        self.show_frame("startup")
        
        # Establish email connection
        self._connect_to_email()
        
        # Handle app closing
        self.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _init_frames(self):
        """Initialize all GUI frames."""
        # Define callbacks for each frame
        startup_callbacks = {
            "fetch_emails": self._fetch_and_show_emails,
            "show_spam_settings": lambda: self.show_frame("spam"),
            "close_app": self._on_close
        }
        
        list_callbacks = {
            "email_selected": self._display_email_content,
            "block_sender": self._block_sender,
            "back_to_startup": lambda: self.show_frame("startup")
        }
        
        content_callbacks = {
            "back_to_list": lambda: self.show_frame("list")
        }
        
        spam_callbacks = {
            "add_blocked_email": self._add_blocked_email,
            "unblock_email": self._unblock_email,
            "back_to_startup": lambda: self.show_frame("startup")
        }
        
        # Create frame instances
        self.frames = {
            "startup": StartupFrame(self, startup_callbacks),
            "list": EmailListFrame(self, list_callbacks),
            "content": EmailContentFrame(self, content_callbacks),
            "spam": SpamSettingsFrame(self, spam_callbacks)
        }
        
        # Grid all frames in the same location
        for frame_name, frame_obj in self.frames.items():
            frame_obj.frame.grid(row=0, column=0, sticky="nsew")
    
    def show_frame(self, frame_name: str):
        """Show the specified frame."""
        if frame_name in self.frames:
            self.frames[frame_name].frame.tkraise()
            
            # Refresh spam settings when showing spam frame
            if frame_name == "spam":
                self.frames["spam"].refresh_blocked_list(
                    self.spam_blocker.get_blocked_emails()
                )
    
    def _connect_to_email(self):
        """Establish email connection and update UI."""
        success = self.email_service.connect(config.email, config.password)
        self.frames["startup"].update_connection_status(success)
        
        if not success:
            messagebox.showerror(
                "Connection Error", 
                "Failed to connect to the email server. Please check your credentials."
            )
    
    def _fetch_and_show_emails(self):
        """Fetch emails and display them in the list frame."""
        if not self.email_service.is_connected():
            messagebox.showerror("Error", "Email connection is not established.")
            return
        
        try:
            # Fetch emails using the email service
            self.email_data = self.email_service.fetch_recent_emails(self.spam_blocker)
            
            # Populate the email list frame
            self.frames["list"].populate_email_list(self.email_data)
            
            # Show the list frame
            self.show_frame("list")
            
            if not self.email_data:
                messagebox.showinfo("No Emails", "No recent emails found.")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch emails: {e}")
    
    def _display_email_content(self, event):
        """Display the selected email content."""
        selected_idx = self.frames["list"].get_selected_email_index()
        if selected_idx is not None and selected_idx < len(self.email_data):
            email_data = self.email_data[selected_idx]
            self.frames["content"].display_email(email_data)
            self.show_frame("content")
    
    def _block_sender(self):
        """Block the sender of the selected email."""
        selected_idx = self.frames["list"].get_selected_email_index()
        if selected_idx is None or selected_idx >= len(self.email_data):
            return
        
        email_info = self.email_data[selected_idx]
        sender = email_info["from"]
        
        # Extract clean email address
        email_address = EmailValidator.extract_email_from_string(sender)
        
        if not EmailValidator.is_valid_email(email_address):
            messagebox.showerror("Error", "Invalid email address format.")
            return
        
        # Confirm blocking
        result = messagebox.askyesno(
            "Block Sender", 
            f"Block emails from {email_address}?"
        )
        
        if result:
            self.spam_blocker.add_blocked_email(email_address)
            messagebox.showinfo("Success", f"Blocked {email_address}")
            # Refresh email list to hide blocked emails
            self._fetch_and_show_emails()
    
    def _add_blocked_email(self, email_address: str) -> bool:
        """Add an email address to the blocked list."""
        if not EmailValidator.is_valid_email(email_address):
            messagebox.showerror("Error", "Please enter a valid email address.")
            return False
        
        self.spam_blocker.add_blocked_email(email_address)
        self.frames["spam"].refresh_blocked_list(
            self.spam_blocker.get_blocked_emails()
        )
        messagebox.showinfo("Success", f"Blocked {email_address}")
        return True
    
    def _unblock_email(self, email_address: str):
        """Remove an email address from the blocked list."""
        result = messagebox.askyesno(
            "Unblock Email", 
            f"Unblock {email_address}?"
        )
        
        if result:
            if self.spam_blocker.remove_blocked_email(email_address):
                self.frames["spam"].refresh_blocked_list(
                    self.spam_blocker.get_blocked_emails()
                )
                messagebox.showinfo("Success", f"Unblocked {email_address}")
            else:
                messagebox.showerror("Error", "Email address not found in blocked list.")
    
    def _on_close(self):
        """Handle application closing."""
        self.email_service.disconnect()
        self.destroy()


def main():
    """Main function to run the application."""
    try:
        # Validate configuration
        if not config.email or not config.password:
            print("Error: EMAIL and PASSWORD must be set in .env file")
            return
        
        # Create and run the application
        app = EmailApp()
        app.mainloop()
        
    except Exception as e:
        print(f"Error starting application: {e}")
        messagebox.showerror("Startup Error", f"Failed to start application: {e}")


if __name__ == "__main__":
    main()