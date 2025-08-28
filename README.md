# Email Viewer with Spam Blocking

A Python desktop application for viewing emails with built-in spam blocking functionality and a checklist feature. The application is designed with a modular architecture to support future API integrations.

## Features

- **Email Viewing**: Connect to IMAP servers and view recent emails
- **Spam Blocking**: Block unwanted senders and manage blocked email lists
- **AI-Powered Checklist Generation**: Generate actionable checklist items from email content using Claude AI
- **Checklist**: Built-in task management with checkable items
- **Modular Design**: Clean separation of concerns for easy maintenance

## Project Structure

```
email-app/
├── main.py                 # Main application entry point
├── config.py              # Configuration management
├── spam_blocker.py        # Spam blocking logic
├── email_service.py       # Email fetching service
├── email_utils.py         # Email utility functions
├── gui_frames.py          # GUI frame components
├── claude_service.py      # Claude AI integration for checklist generation
├── api_integration.py     # Future API integration framework
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (create this)
└── README.md             # This file
```

## Installation

1. **Clone or download the project files**

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Create a `.env` file** in the project root with your email credentials:
   ```
   EMAIL=your_email@example.com
   PASSWORD=your_app_password
   CLAUDE_API_KEY=your_claude_api_key
   IMAP_SERVER=imap.mail.yahoo.com
   WINDOW_WIDTH=700
   WINDOW_HEIGHT=600
   BLOCKED_EMAILS_FILE=blocked_emails.json
   ```

## Configuration

### Email Setup

For **Yahoo Mail**:

- Use your Yahoo email address
- Generate an app password (not your regular password)
- IMAP server: `imap.mail.yahoo.com`

For **Gmail**:

- Enable 2-factor authentication
- Generate an app password
- IMAP server: `imap.gmail.com`

For **Outlook**:

- IMAP server: `outlook.office365.com`

### Environment Variables

| Variable              | Description                         | Default               |
| --------------------- | ----------------------------------- | --------------------- |
| `EMAIL`               | Your email address                  | Required              |
| `PASSWORD`            | Your app password                   | Required              |
| `CLAUDE_API_KEY`      | Your Claude API key for AI features | Optional              |
| `IMAP_SERVER`         | IMAP server address                 | `imap.mail.yahoo.com` |
| `WINDOW_WIDTH`        | Application window width            | `700`                 |
| `WINDOW_HEIGHT`       | Application window height           | `600`                 |
| `BLOCKED_EMAILS_FILE` | Blocked emails storage file         | `blocked_emails.json` |

## Usage

1. **Run the application**:

   ```bash
   python main.py
   ```

2. **Main Features**:c

   - **Fetch Emails**: Retrieves emails from the last 24 hours
   - **Block Senders**: Right-click on emails to block senders
   - **Spam Settings**: Manage blocked email addresses
   - **AI Checklist Generation**: Click "Generate Checklist Item" when viewing an email to create actionable tasks
   - **Checklist Management**: Add, toggle, and delete checklist items

3. **Navigation**:
   - Use the buttons to navigate between different screens
   - Right-click for context menus with additional options
   - Double-click checklist items to toggle completion

## Module Documentation

### Core Modules

- **`main.py`**: Application entry point and main GUI controller
- **`config.py`**: Centralized configuration management using environment variables
- **`spam_blocker.py`**: Handles blocking/unblocking email addresses with persistent storage
- **`email_service.py`**: IMAP email fetching and connection management
- **`email_utils.py`**: Utility functions for email formatting and validation

### Additional Features

- Email composition and sending
- Attachment handling
- Email search and filtering
- Multiple account support
- Email templates
- Scheduling and reminders

### Code Structure

The application follows these principles:

- **Separation of Concerns**: Each module has a specific responsibility
- **Dependency Injection**: Callbacks and services are passed between components
- **Configuration Management**: All settings centralized in `config.py`
- **Error Handling**: Comprehensive exception handling throughout
- **Type Hints**: Full type annotation for better code msaintainability

## Future Features

1. **New GUI Components**: Add frames to `gui_frames.py`
2. **Email Processing**: Extend `email_service.py` or `email_utils.py`
3. **Configuration**: Add new settings to `config.py`

## Troubleshooting

### Common Issues

1. **Connection Failed**: Check email credentials and IMAP settings
2. **No Emails Found**: Verify IMAP is enabled for your email provider
3. **Authentication Error**: Ensure you're using an app password, not your regular password
4. **GUI Issues**: Check that tkinter is properly installed with your Python distribution

### Support

For issues or questions:

1. Check your `.env` file configuration
2. Verify your email provider's IMAP settings
3. Ensure all dependencies are installed correctly
4. Check the console output for detailed error messages

## License

This project is open source and available under the MIT License.
