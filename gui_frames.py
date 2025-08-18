import tkinter as tk
from tkinter import messagebox, simpledialog
from typing import Callable, List, Dict, Optional
from email_utils import EmailFormatter


class StartupFrame:
    """Startup frame for the email application."""
    
    def __init__(self, parent: tk.Widget, callbacks: Dict[str, Callable]):
        self.frame = tk.Frame(parent)
        self.callbacks = callbacks
        self.connection_status = None
        self._create_widgets()
    
    def _create_widgets(self):
        # Configure grid
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_rowconfigure(5, weight=1)

        # Title
        tk.Label(
            self.frame,
            text="Welcome to Email Viewer",
            font=("Arial", 16)
        ).grid(row=1, column=0, pady=10)

        # Connection status
        self.connection_status = tk.Label(
            self.frame,
            text="Connecting...",
            font=("Arial", 12),
            fg="blue"
        )
        self.connection_status.grid(row=2, column=0, pady=10)

        # Buttons
        button_frame = tk.Frame(self.frame)
        button_frame.grid(row=3, column=0, pady=10)

        tk.Button(
            button_frame,
            text="Fetch Emails",
            font=("Arial", 14),
            command=self.callbacks.get("fetch_emails")
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            button_frame,
            text="Spam Settings",
            font=("Arial", 14),
            command=self.callbacks.get("show_spam_settings")
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            button_frame,
            text="Close",
            font=("Arial", 14),
            command=self.callbacks.get("close_app")
        ).pack(side=tk.LEFT, padx=5)
    
    def update_connection_status(self, connected: bool):
        """Update connection status display."""
        if connected:
            self.connection_status.config(text="Connected to Email Server", fg="green")
        else:
            self.connection_status.config(text="Failed to Connect to Email Server", fg="red")


class EmailListFrame:
    """Frame for displaying email list and checklist."""
    
    def __init__(self, parent: tk.Widget, callbacks: Dict[str, Callable]):
        self.frame = tk.Frame(parent)
        self.callbacks = callbacks
        self.email_listbox: Optional[tk.Listbox] = None
        self.checklist_listbox: Optional[tk.Listbox] = None
        self.email_context_menu: Optional[tk.Menu] = None
        self.checklist_context_menu: Optional[tk.Menu] = None
        self._create_widgets()
    
    def _create_widgets(self):
        main_frame = tk.Frame(self.frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Email list section
        self._create_email_list(main_frame)
        
        # Checklist section
        self._create_checklist(main_frame)

        # Back button
        tk.Button(
            self.frame,
            text="Back to Startup",
            command=self.callbacks.get("back_to_startup")
        ).pack(pady=10)
    
    def _create_email_list(self, parent):
        email_frame = tk.Frame(parent)
        email_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        tk.Label(email_frame, text="Email List", font=("Arial", 16)).pack(pady=5)
        
        self.email_listbox = tk.Listbox(email_frame, activestyle="none")
        self.email_listbox.pack(fill=tk.BOTH, expand=True)
        self.email_listbox.bind("<Motion>", self._highlight_email)
        self.email_listbox.bind("<<ListboxSelect>>", self._on_email_select)
        self.email_listbox.bind("<Button-3>", self._show_email_context_menu)

        # Email context menu
        self.email_context_menu = tk.Menu(self.email_listbox, tearoff=0)
        self.email_context_menu.add_command(label="Block Sender", command=self._block_sender)
    
    def _create_checklist(self, parent):
        checklist_frame = tk.Frame(parent)
        checklist_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

        # Header with add button
        header_frame = tk.Frame(checklist_frame)
        header_frame.pack(fill=tk.X, pady=5)

        tk.Label(header_frame, text="Checklist", font=("Arial", 16)).pack(side=tk.LEFT, padx=5)
        tk.Button(
            header_frame,
            text="+",
            font=("Arial", 10),
            command=self._add_checklist_item
        ).pack(side=tk.RIGHT, padx=5)

        # Checklist
        self.checklist_listbox = tk.Listbox(checklist_frame, activestyle="none")
        self.checklist_listbox.pack(fill=tk.BOTH, expand=True)
        self.checklist_listbox.bind("<Double-1>", self._toggle_checklist_item)
        self.checklist_listbox.bind("<Button-3>", self._show_checklist_context_menu)

        # Checklist context menu
        self.checklist_context_menu = tk.Menu(self.checklist_listbox, tearoff=0)
        self.checklist_context_menu.add_command(label="Delete Item", command=self._delete_checklist_item)
    
    def _highlight_email(self, event):
        """Highlight email under cursor."""
        widget = event.widget
        widget.select_clear(0, tk.END)
        widget.select_set(widget.nearest(event.y))
    
    def _on_email_select(self, event):
        """Handle email selection."""
        if self.callbacks.get("email_selected"):
            self.callbacks["email_selected"](event)
    
    def _show_email_context_menu(self, event):
        """Show email context menu."""
        try:
            self.email_listbox.select_clear(0, tk.END)
            self.email_listbox.select_set(self.email_listbox.nearest(event.y))
            self.email_context_menu.post(event.x_root, event.y_root)
        finally:
            self.email_context_menu.grab_release()
    
    def _block_sender(self):
        """Handle block sender action."""
        if self.callbacks.get("block_sender"):
            self.callbacks["block_sender"]()
    
    def _add_checklist_item(self):
        """Add item to checklist."""
        new_item = simpledialog.askstring("Add Item", "Enter a new checklist item:")
        if new_item:
            self.checklist_listbox.insert(tk.END, new_item)
    
    def _toggle_checklist_item(self, event):
        """Toggle checklist item."""
        selected_idx = self.checklist_listbox.curselection()
        if not selected_idx:
            return
        
        current_text = self.checklist_listbox.get(selected_idx)
        if current_text.startswith("✔ "):
            updated_text = current_text[2:]
        else:
            updated_text = f"✔ {current_text}"
        
        self.checklist_listbox.delete(selected_idx)
        self.checklist_listbox.insert(selected_idx, updated_text)
    
    def _show_checklist_context_menu(self, event):
        """Show checklist context menu."""
        try:
            self.checklist_listbox.select_clear(0, tk.END)
            self.checklist_listbox.select_set(self.checklist_listbox.nearest(event.y))
            self.checklist_context_menu.post(event.x_root, event.y_root)
        finally:
            self.checklist_context_menu.grab_release()
    
    def _delete_checklist_item(self):
        """Delete checklist item."""
        selected_idx = self.checklist_listbox.curselection()
        if selected_idx:
            self.checklist_listbox.delete(selected_idx)
    
    def populate_email_list(self, emails: List[Dict]):
        """Populate email listbox with email data."""
        self.email_listbox.delete(0, tk.END)
        for email_data in emails:
            formatted_item = EmailFormatter.format_email_list_item(email_data)
            self.email_listbox.insert(tk.END, formatted_item)
    
    def get_selected_email_index(self) -> Optional[int]:
        """Get index of selected email."""
        selected = self.email_listbox.curselection()
        return selected[0] if selected else None


class EmailContentFrame:
    """Frame for displaying email content."""
    
    def __init__(self, parent: tk.Widget, callbacks: Dict[str, Callable]):
        self.frame = tk.Frame(parent)
        self.callbacks = callbacks
        self.content_text: Optional[tk.Text] = None
        self.current_email_data: Optional[Dict] = None
        self._create_widgets()
    
    def _create_widgets(self):
        self.content_text = tk.Text(self.frame, wrap="word", width=80, height=25)
        self.content_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Button frame for multiple buttons
        button_frame = tk.Frame(self.frame)
        button_frame.pack(pady=10)

        # Back button
        tk.Button(
            button_frame,
            text="Back to Email List",
            command=self.callbacks.get("back_to_list")
        ).pack(side=tk.LEFT, padx=5)

        # Generate checklist item button
        tk.Button(
            button_frame,
            text="Generate Checklist Item",
            command=self._generate_checklist_item,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold")
        ).pack(side=tk.LEFT, padx=5)
    
    def _generate_checklist_item(self):
        """Generate a checklist item from the current email."""
        if self.callbacks.get("generate_checklist_item") and self.current_email_data:
            self.callbacks["generate_checklist_item"](self.current_email_data)
    
    def display_email(self, email_data: Dict):
        """Display email content."""
        self.current_email_data = email_data
        self.content_text.delete(1.0, tk.END)
        content = EmailFormatter.format_email_content(email_data)
        self.content_text.insert(tk.END, content)


class SpamSettingsFrame:
    """Frame for spam blocking settings."""
    
    def __init__(self, parent: tk.Widget, callbacks: Dict[str, Callable]):
        self.frame = tk.Frame(parent)
        self.callbacks = callbacks
        self.block_email_entry: Optional[tk.Entry] = None
        self.blocked_listbox: Optional[tk.Listbox] = None
        self.blocked_context_menu: Optional[tk.Menu] = None
        self._create_widgets()
    
    def _create_widgets(self):
        # Title
        tk.Label(self.frame, text="Spam Blocking Settings", font=("Arial", 16)).pack(pady=10)

        # Add blocked email section
        add_frame = tk.Frame(self.frame)
        add_frame.pack(pady=10)

        tk.Label(add_frame, text="Block Email Address:", font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
        self.block_email_entry = tk.Entry(add_frame, width=30)
        self.block_email_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(add_frame, text="Add", command=self._add_blocked_email).pack(side=tk.LEFT, padx=5)

        # Blocked emails list
        tk.Label(self.frame, text="Blocked Email Addresses:", font=("Arial", 12)).pack(pady=(20, 5))
        
        list_frame = tk.Frame(self.frame)
        list_frame.pack(pady=5, padx=20, fill=tk.BOTH, expand=True)

        self.blocked_listbox = tk.Listbox(list_frame, height=15)
        self.blocked_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.blocked_listbox.bind("<Button-3>", self._show_blocked_context_menu)

        # Scrollbar
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.blocked_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.blocked_listbox.yview)

        # Context menu
        self.blocked_context_menu = tk.Menu(self.blocked_listbox, tearoff=0)
        self.blocked_context_menu.add_command(label="Unblock", command=self._unblock_email)

        # Back button
        tk.Button(
            self.frame,
            text="Back to Startup",
            command=self.callbacks.get("back_to_startup")
        ).pack(pady=10)
    
    def _add_blocked_email(self):
        """Add blocked email."""
        email_address = self.block_email_entry.get().strip()
        if email_address and self.callbacks.get("add_blocked_email"):
            if self.callbacks["add_blocked_email"](email_address):
                self.block_email_entry.delete(0, tk.END)
    
    def _show_blocked_context_menu(self, event):
        """Show blocked email context menu."""
        try:
            self.blocked_listbox.select_clear(0, tk.END)
            self.blocked_listbox.select_set(self.blocked_listbox.nearest(event.y))
            self.blocked_context_menu.post(event.x_root, event.y_root)
        finally:
            self.blocked_context_menu.grab_release()
    
    def _unblock_email(self):
        """Unblock selected email."""
        selected_idx = self.blocked_listbox.curselection()
        if selected_idx and self.callbacks.get("unblock_email"):
            email_address = self.blocked_listbox.get(selected_idx)
            self.callbacks["unblock_email"](email_address)
    
    def refresh_blocked_list(self, blocked_emails: List[str]):
        """Refresh the blocked emails list."""
        self.blocked_listbox.delete(0, tk.END)
        for email_address in blocked_emails:
            self.blocked_listbox.insert(tk.END, email_address)