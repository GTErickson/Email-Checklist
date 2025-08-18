"""
Claude API service for generating checklist items from email content.
"""

import requests
import json
from typing import Optional, Dict, List
from config import config


class ClaudeService:
    """Service for interacting with the Claude API."""
    
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or config.claude_api_key
        self.model = model or config.claude_model
        self.base_url = "https://api.anthropic.com/v1/messages"
        
        if not self.api_key:
            raise ValueError("Claude API key is required. Set CLAUDE_API_KEY in your .env file.")
    
    def _make_request(self, messages: List[Dict], max_tokens: int = 1000) -> Optional[str]:
        """Make a request to the Claude API."""
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }
        
        payload = {
            "model": self.model,
            "max_tokens": max_tokens,
            "messages": messages
        }
        
        try:
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            return result.get("content", [{}])[0].get("text", "")
            
        except requests.exceptions.RequestException as e:
            print(f"Error making Claude API request: {e}")
            return None
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            print(f"Error parsing Claude API response: {e}")
            return None
    
    def generate_checklist_item(self, email_subject: str, email_body: str, email_sender: str = "") -> Optional[str]:
        """Generate a checklist item based on email content."""
        
        # Create a focused prompt for checklist generation
        prompt = f"""Based on the following email, generate a single, actionable checklist item. The item should be:
- Concise (under 80 characters)
- Action-oriented (start with a verb)
- Specific to the email content
- Something that can be completed/checked off

Email Subject: {email_subject}
From: {email_sender}

Email Content:
{email_body[:2000]}  # Limit content to avoid token limits

Please respond with ONLY the checklist item text, no additional explanation or formatting."""

        messages = [
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        response = self._make_request(messages, max_tokens=150)
        if response:
            # Clean up the response - remove any extra whitespace or formatting
            cleaned_response = response.strip().strip('"').strip("'")
            # Ensure it's not too long for a checklist item
            if len(cleaned_response) > 100:
                cleaned_response = cleaned_response[:97] + "..."
            return cleaned_response
        
        return None
    
    def generate_multiple_checklist_items(self, email_subject: str, email_body: str, email_sender: str = "", count: int = 3) -> List[str]:
        """Generate multiple checklist items based on email content."""
        
        prompt = f"""Based on the following email, generate {count} actionable checklist items. Each item should be:
- Concise (under 80 characters each)
- Action-oriented (start with a verb)
- Specific to the email content
- Something that can be completed/checked off

Email Subject: {email_subject}
From: {email_sender}

Email Content:
{email_body[:2000]}

Please respond with only the checklist items, one per line, no numbers or bullets, no additional explanation."""

        messages = [
            {
                "role": "user", 
                "content": prompt
            }
        ]
        
        response = self._make_request(messages, max_tokens=300)
        if response:
            # Split response into individual items and clean them up
            items = []
            for line in response.strip().split('\n'):
                cleaned_line = line.strip().strip('"').strip("'").strip('-').strip('*').strip()
                if cleaned_line and len(cleaned_line) > 5:  # Ignore very short lines
                    if len(cleaned_line) > 100:
                        cleaned_line = cleaned_line[:97] + "..."
                    items.append(cleaned_line)
            
            return items[:count]  # Return only the requested number of items
        
        return []
    
    def summarize_email(self, email_subject: str, email_body: str, email_sender: str = "") -> Optional[str]:
        """Generate a brief summary of the email."""
        
        prompt = f"""Provide a brief 1-2 sentence summary of this email's main point or request:

Email Subject: {email_subject}
From: {email_sender}

Email Content:
{email_body[:2000]}

Summary:"""

        messages = [
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        response = self._make_request(messages, max_tokens=200)
        if response:
            return response.strip()
        
        return None
    
    def is_available(self) -> bool:
        """Check if the Claude API is available and configured."""
        return bool(self.api_key)


# Global instance for easy access
claude_service = ClaudeService() if config.claude_api_key else None