import email.utils
import os
import imaplib
import email
from email.header import decode_header
import datetime
import re
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from dotenv import load_dotenv

# Load credentials from .env
load_dotenv()
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

# ----------- Email Fetching Logic ----------- 

# Global set to track fetched email IDs
fetched_email_ids = set()

def fetch_emails(mail_connection):
    try:
        if not mail_connection:
            raise Exception("No active email connection.")

        mail_connection.select("inbox")

        # Calculate the date 24 hours ago in the format '01-Jan-2025'
        date_24_hours_ago = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%d-%b-%Y")

        # Search for emails since the calculated date
        result, data = mail_connection.search(None, f'SINCE {date_24_hours_ago}')
        if result != "OK":
            raise Exception("Failed to search inbox.")

        mail_ids = data[0].split()
        emails = []

        for i in reversed(mail_ids):  # Iterate through the retrieved emails
            res, msg_data = mail_connection.fetch(i, "(RFC822)")
            if res != "OK":
                continue

            msg = email.message_from_bytes(msg_data[0][1])

            # Decode subject
            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding if encoding else "utf-8")

            from_ = msg.get("From")
            date_ = msg.get("Date")

            # Decode the full content
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))

                    if content_type == "text/plain" and "attachment" not in content_disposition:
                        body = part.get_payload(decode=True).decode("utf-8")
                        break
            else:
                body = msg.get_payload(decode=True).decode("utf-8")

            emails.append({"subject": subject, "from": from_, "date": date_, "body": body})

        return emails

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
        return []



# ----------- GUI Application ----------- 
class EmailApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Email Viewer")
        # Get screen width and height
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Set window size to screen size
        #self.geometry(f"{screen_width}x{screen_height}")
        self.geometry("700x600")

        # Initialize the IMAP connection
        self.mail_connection = None
        self.email_data = []

        # Create the three frames
        self.startup_frame = tk.Frame(self)
        self.list_frame = tk.Frame(self)
        self.content_frame = tk.Frame(self)

        for frame in (self.startup_frame, self.list_frame, self.content_frame):
            frame.grid(row=0, column=0, sticky="nsew")

        self.create_startup_frame()
        self.create_list_frame()
        self.create_content_frame()

        self.show_frame(self.startup_frame)

        # Establish connection after initializing the frames
        self.connect_to_email()

        # Handle app closing event
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def connect_to_email(self):
        """Establish a persistent IMAP connection."""
        global EMAIL, PASSWORD
        try:
            imap_server = "imap.mail.yahoo.com"
            self.mail_connection = imaplib.IMAP4_SSL(imap_server)
            self.mail_connection.login(EMAIL, PASSWORD)
            
            # Update status label to show connection success
            self.connection_status.config(text="Connected to Email Server", fg="green")
        except Exception as e:
            # Update status label to show connection failure
            self.connection_status.config(text="Failed to Connect to Email Server", fg="red")
            messagebox.showerror("Error", f"Failed to connect to the email server: {e}")
            self.mail_connection = None


    def on_close(self):
        """Close the IMAP connection and exit the app."""
        if self.mail_connection:
            self.mail_connection.logout()
        self.destroy()
        


    def show_frame(self, frame):
        """Switches between frames."""
        frame.tkraise()

    # ----------- Startup Frame ----------- 
    def create_startup_frame(self):
        # Configure columns and rows for centering
        self.startup_frame.grid_columnconfigure(0, weight=1)
        self.startup_frame.grid_rowconfigure(0, weight=1)  # Top spacer row
        self.startup_frame.grid_rowconfigure(4, weight=1)  # Bottom spacer row

        # Title label in row 1
        tk.Label(
            self.startup_frame,
            text="Welcome to Email Viewer",
            font=("Arial", 16)
        ).grid(row=1, column=0, pady=10, sticky="")

        # Connection status label in row 2
        self.connection_status = tk.Label(
            self.startup_frame,
            text="Connecting...",
            font=("Arial", 12),
            fg="blue"
        )
        self.connection_status.grid(row=2, column=0, pady=10, sticky="")

        # Frame for buttons in row 3
        button_frame = tk.Frame(self.startup_frame)
        button_frame.grid(row=3, column=0, pady=10, sticky="")

        # Fetch Emails button
        tk.Button(
            button_frame,
            text="Fetch Emails",
            font=("Arial", 14),
            command=self.fetch_and_show_emails
        ).pack(side=tk.LEFT, padx=5)

        # Close button
        tk.Button(
            button_frame,
            text="Close",
            font=("Arial", 14),
            command=self.on_close
        ).pack(side=tk.LEFT, padx=5)



    # ----------- List Frame ----------- 
    def create_list_frame(self):
        # Create a main frame to hold both the email list and the checklist
        main_frame = tk.Frame(self.list_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left: Email list box
        email_frame = tk.Frame(main_frame)
        email_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        tk.Label(email_frame, text="Email List", font=("Arial", 16)).pack(pady=5)
        self.email_listbox = tk.Listbox(email_frame, activestyle="none")
        self.email_listbox.pack(fill=tk.BOTH, expand=True)
        self.email_listbox.bind("<Motion>", self.highlight_item)
        self.email_listbox.bind("<<ListboxSelect>>", self.display_email_content)

        # Right: Checklist boxx
        checklist_frame = tk.Frame(main_frame)
        checklist_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

        # Header frame for the checklist label and add button
        header_frame = tk.Frame(checklist_frame)
        header_frame.pack(fill=tk.X, pady=5)

        tk.Label(header_frame, text="Checklist", font=("Arial", 16)).pack(side=tk.LEFT, padx=5)

        # Add item button (with "+" text)
        add_button = tk.Button(
            header_frame,
            text="+",
            font=("Arial", 10),
            command=self.add_checklist_item
        )
        add_button.pack(side=tk.RIGHT, padx=5)

        # Checklist listbox
        self.checklist_listbox = tk.Listbox(checklist_frame, activestyle="none")
        self.checklist_listbox.pack(fill=tk.BOTH, expand=True)
        self.checklist_listbox.bind("<Double-1>", self.toggle_checklist_item)  # Bind double-click
        self.checklist_listbox.bind("<Button-3>", self.show_context_menu)  # Bind right-click for deletion


        # Context menu for deletion
        self.context_menu = tk.Menu(self.checklist_listbox, tearoff=0)
        self.context_menu.add_command(label="Delete Item", command=self.delete_checklist_item)

        # Back button below the main frame
        tk.Button(
            self.list_frame,
            text="Back to Startup",
            command=lambda: self.show_frame(self.startup_frame)
        ).pack(pady=10)

    def add_checklist_item(self):
        """Prompt the user to add an item to the checklist."""
        new_item = simpledialog.askstring("Add Item", "Enter a new checklist item:")
        if new_item:  # Add the item if input is provided
            self.checklist_listbox.insert(tk.END, new_item)

    def toggle_checklist_item(self, event):
        """Toggle a checklist item between checked and unchecked states."""
        selected_idx = self.checklist_listbox.curselection()
        if not selected_idx:
            return
        current_text = self.checklist_listbox.get(selected_idx)
        if current_text.startswith("✔ "):  # If already checked, uncheck
            updated_text = current_text[2:]
        else:  # Otherwise, check the item
            updated_text = f"✔ {current_text}"
        self.checklist_listbox.delete(selected_idx)
        self.checklist_listbox.insert(selected_idx, updated_text)

    def show_context_menu(self, event):
        """Show context menu for deleting an item."""
        try:
            self.checklist_listbox.select_clear(0, tk.END)
            self.checklist_listbox.select_set(self.checklist_listbox.nearest(event.y))
            self.context_menu.post(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def delete_checklist_item(self):
        """Delete the selected checklist item."""
        selected_idx = self.checklist_listbox.curselection()
        if selected_idx:
            self.checklist_listbox.delete(selected_idx)

    def highlight_item(self, event):
        """Highlight the email item under the cursor."""
        widget = event.widget
        widget.select_clear(0, tk.END)
        widget.select_set(widget.nearest(event.y))

    def fetch_and_show_emails(self):
        """Fetch emails and populate the listbox."""
        if not self.mail_connection:
            messagebox.showerror("Error", "Email connection is not established.")
            return

        self.email_data = fetch_emails(self.mail_connection)  # Use persistent connection
        self.email_listbox.delete(0, tk.END)

        for email_info in self.email_data:

            name_match = re.match(r"([^<]+)", email_info["from"])
            name = name_match.group(1).strip() if name_match else email_info["from"]

            max_subject_chars = 50
            subject = email_info["subject"]
            if len(subject) > max_subject_chars:
                subject = subject[:max_subject_chars - 3] + "..."

            email_date = email.utils.parsedate_to_datetime(email_info["date"])
            now = datetime.datetime.now()
            if email_date.date() == now.date():
                date_str = email_date.strftime("%I:%M %p").lstrip("0")
            else:
                date_str = email_date.strftime("%b %d")

            self.email_listbox.insert(
                tk.END, f"{name} - {subject} - {date_str}\n\n"
            )

        self.show_frame(self.list_frame)


    # ----------- Content Frame ----------- 
    def create_content_frame(self):
        self.email_content_text = tk.Text(self.content_frame, wrap="word", width=80, height=25)
        self.email_content_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        tk.Button(
            self.content_frame,
            text="Back to Email List",
            command=lambda: self.show_frame(self.list_frame)
        ).pack(pady=10)

    def display_email_content(self, event):
        """Display the selected email content."""
        buffer = "--------------------------------------------------------------------------------"
        selected_idx = self.email_listbox.curselection()
        if not selected_idx:
            return

        email_info = self.email_data[selected_idx[0]]
        self.email_content_text.delete(1.0, tk.END)
        self.email_content_text.insert(
            tk.END, f"Subject: {email_info['subject']}\nFrom: {email_info['from']}\nDate: {email_info['date']}\n{buffer}\n\n{email_info['body']}\n\n{buffer}"
        )
        self.show_frame(self.content_frame)

# ----------- Run Application ----------- 
if __name__ == "__main__":
    app = EmailApp()
    app.mainloop()
