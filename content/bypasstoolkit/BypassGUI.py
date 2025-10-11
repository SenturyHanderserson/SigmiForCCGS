import customtkinter as ctk
import webbrowser
from urllib.parse import quote
import time

# Set appearance before creating the app
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class BypassApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Basic window configuration
        self.title("Bypass Toolkit")
        self.geometry("900x600")
        self.resizable(True, True)
        
        # Remove default title bar for custom one
        self.overrideredirect(True)
        
        # Make window always on top initially
        self.attributes('-topmost', True)
        
        # Center the window
        self.center_window()
        
        # Variables for window dragging
        self._drag_start_x = 0
        self._drag_start_y = 0
        
        # Create the GUI
        self.setup_gui()
        
        # Fade in animation
        self.fade_in()
        
    def center_window(self):
        """Center the window on screen"""
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = 900
        window_height = 600
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")

    def fade_in(self):
        """Fade in animation"""
        self.attributes('-alpha', 0.0)
        for i in range(1, 11):
            self.attributes('-alpha', i * 0.1)
            self.update()
            time.sleep(0.02)
        self.attributes('-topmost', False)  # Remove always on top after fade in

    def setup_gui(self):
        """Setup the main GUI components"""
        
        # Main container with glass effect
        self.main_frame = ctk.CTkFrame(
            self,
            fg_color="#1a1a2a",
            corner_radius=20,
            border_width=1,
            border_color="#333344"
        )
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create title bar
        self.create_title_bar()
        
        # Create main content
        self.create_content()

    def create_title_bar(self):
        """Create custom title bar"""
        title_bar = ctk.CTkFrame(
            self.main_frame,
            fg_color="#252538",
            height=50,
            corner_radius=12
        )
        title_bar.pack(fill="x", padx=15, pady=15)
        title_bar.pack_propagate(False)
        
        # Make title bar draggable
        title_bar.bind("<Button-1>", self.start_drag)
        title_bar.bind("<B1-Motion>", self.do_drag)
        
        # Title and icon
        title_container = ctk.CTkFrame(title_bar, fg_color="transparent")
        title_container.pack(side="left", padx=20, pady=10)
        
        # Icon
        icon_label = ctk.CTkLabel(
            title_container,
            text="🚀",
            font=("Arial", 20),
            text_color="#667eea"
        )
        icon_label.pack(side="left")
        icon_label.bind("<Button-1>", self.start_drag)
        icon_label.bind("<B1-Motion>", self.do_drag)
        
        # Title
        title_label = ctk.CTkLabel(
            title_container,
            text="Bypass Toolkit",
            font=("Arial", 16, "bold"),
            text_color="white"
        )
        title_label.pack(side="left", padx=10)
        title_label.bind("<Button-1>", self.start_drag)
        title_label.bind("<B1-Motion>", self.do_drag)
        
        # Window controls
        controls_frame = ctk.CTkFrame(title_bar, fg_color="transparent")
        controls_frame.pack(side="right", padx=15, pady=10)
        
        # Minimize button - FIXED: Use withdraw() instead of iconify() with overrideredirect
        minimize_btn = ctk.CTkButton(
            controls_frame,
            text="─",
            width=30,
            height=30,
            fg_color="#333344",
            hover_color="#444455",
            text_color="white",
            font=("Arial", 14, "bold"),
            command=self.minimize_window,
            corner_radius=8
        )
        minimize_btn.pack(side="left", padx=5)
        
        # Close button
        close_btn = ctk.CTkButton(
            controls_frame,
            text="×",
            width=30,
            height=30,
            fg_color="#333344",
            hover_color="#ff5555",
            text_color="white",
            font=("Arial", 14, "bold"),
            command=self.quit_app,
            corner_radius=8
        )
        close_btn.pack(side="left", padx=5)

    def create_content(self):
        """Create main content area"""
        content_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent"
        )
        content_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Create sidebar and main area
        self.create_sidebar(content_frame)
        self.create_main_area(content_frame)

    def create_sidebar(self, parent):
        """Create navigation sidebar"""
        sidebar = ctk.CTkFrame(
            parent,
            fg_color="#252538",
            width=200,
            corner_radius=12
        )
        sidebar.pack(side="left", fill="y", padx=(0, 15))
        sidebar.pack_propagate(False)
        
        # Navigation items
        nav_items = [
            ("🔓", "Bypasses"),
            ("🛠️", "Tools"), 
            ("⚙️", "Settings")
        ]
        
        for icon, text in nav_items:
            btn = ctk.CTkButton(
                sidebar,
                text=f"   {icon}  {text}",
                font=("Arial", 12),
                fg_color="transparent",
                hover_color="#333344",
                text_color="white",
                anchor="w",
                height=40,
                corner_radius=8
            )
            btn.pack(fill="x", padx=10, pady=5)

    def create_main_area(self, parent):
        """Create main content area"""
        main_area = ctk.CTkFrame(
            parent,
            fg_color="#252538",
            corner_radius=12
        )
        main_area.pack(side="left", fill="both", expand=True)
        
        # Scrollable content
        scroll_frame = ctk.CTkScrollableFrame(
            main_area,
            fg_color="transparent"
        )
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        header = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))
        
        title = ctk.CTkLabel(
            header,
            text="Linewize Bypasses",
            font=("Arial", 24, "bold"),
            text_color="white"
        )
        title.pack(side="left")
        
        status_badge = ctk.CTkLabel(
            header,
            text="ACTIVE",
            font=("Arial", 10, "bold"),
            text_color="white",
            fg_color="#667eea",
            corner_radius=8
        )
        status_badge.pack(side="left", padx=10, pady=5)
        
        # Method 1 Card
        self.create_method_card(
            scroll_frame,
            "Method 1: Google Translate Bypass",
            "WORKING",
            "#4CAF50",
            "Enter any blocked URL to bypass through Google Translate proxy:",
            True
        )
        
        # Method 2 Card
        self.create_method_card(
            scroll_frame,
            "Method 2: Advanced Proxy",
            "BETA", 
            "#FF9800",
            "Advanced proxy method with enhanced stealth features (coming soon):",
            False
        )

    def create_method_card(self, parent, title, status, status_color, description, has_input):
        """Create a method card"""
        card = ctk.CTkFrame(
            parent,
            fg_color="#2a2a3a",
            corner_radius=12,
            border_width=1,
            border_color="#333344"
        )
        card.pack(fill="x", pady=10)
        
        card_content = ctk.CTkFrame(card, fg_color="transparent")
        card_content.pack(fill="x", padx=20, pady=20)
        
        # Card header
        header = ctk.CTkFrame(card_content, fg_color="transparent")
        header.pack(fill="x", pady=(0, 10))
        
        title_label = ctk.CTkLabel(
            header,
            text=title,
            font=("Arial", 16, "bold"),
            text_color="white"
        )
        title_label.pack(side="left")
        
        status_badge = ctk.CTkLabel(
            header,
            text=status,
            font=("Arial", 9, "bold"),
            text_color="white",
            fg_color=status_color,
            corner_radius=6
        )
        status_badge.pack(side="right")
        
        # Description
        desc = ctk.CTkLabel(
            card_content,
            text=description,
            font=("Arial", 12),
            text_color="#cccccc",
            wraplength=600
        )
        desc.pack(fill="x", pady=(0, 15))
        
        if has_input:
            # Input area
            input_frame = ctk.CTkFrame(card_content, fg_color="transparent")
            input_frame.pack(fill="x", pady=(0, 10))
            
            # URL input
            self.url_entry = ctk.CTkEntry(
                input_frame,
                placeholder_text="https://example.com",
                height=40,
                font=("Arial", 12),
                fg_color="#1a1a2a",
                border_color="#444455",
                text_color="white",
                placeholder_text_color="#888888"
            )
            self.url_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
            
            # Bypass button
            bypass_btn = ctk.CTkButton(
                input_frame,
                text="🚀 Bypass Now",
                command=self.bypass_url,
                height=40,
                font=("Arial", 12, "bold"),
                fg_color="#667eea",
                hover_color="#5a6fd8",
                text_color="white",
                corner_radius=8
            )
            bypass_btn.pack(side="right")
            
            # Footer info
            footer = ctk.CTkLabel(
                card_content,
                text="✓ Encrypted connection • ✓ Fast • ✓ Reliable",
                font=("Arial", 10),
                text_color="#888888"
            )
            footer.pack(anchor="w")
        else:
            # Coming soon button
            soon_btn = ctk.CTkButton(
                card_content,
                text="🔧 Coming Soon",
                height=40,
                font=("Arial", 12, "bold"),
                fg_color="#555566",
                hover_color="#666677",
                text_color="white",
                corner_radius=8,
                state="disabled"
            )
            soon_btn.pack(fill="x", pady=(0, 10))
            
            # Footer info
            footer = ctk.CTkLabel(
                card_content,
                text="⏳ Under development • Enhanced stealth",
                font=("Arial", 10),
                text_color="#888888"
            )
            footer.pack(anchor="w")

    def bypass_url(self):
        """Handle URL bypass"""
        url = self.url_entry.get().strip()
        if not url:
            self.shake_input()
            return
        
        # Add https:// if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Create bypass URL
        bypass_url = f"https://translate.google.com/translate?sl=auto&tl=en&u={quote(url)}"
        
        # Open in browser
        webbrowser.open(bypass_url)

    def shake_input(self):
        """Shake animation for empty input"""
        # Simple visual feedback instead of complex animation
        original_bg = self.url_entry.cget("border_color")
        self.url_entry.configure(border_color="#ff5555")
        self.after(300, lambda: self.url_entry.configure(border_color=original_bg))

    def start_drag(self, event):
        """Start window dragging"""
        self._drag_start_x = event.x
        self._drag_start_y = event.y

    def do_drag(self, event):
        """Handle window dragging"""
        x = self.winfo_x() + (event.x - self._drag_start_x)
        y = self.winfo_y() + (event.y - self._drag_start_y)
        self.geometry(f"+{x}+{y}")

    def minimize_window(self):
        """Minimize window - FIXED VERSION"""
        # Simple hide/show instead of dealing with overrideredirect issues
        self.withdraw()  # Hide the window
        self.after(2000, self.restore_window)  # Restore after 2 seconds (for testing)

    def restore_window(self):
        """Restore window after minimize"""
        self.deiconify()  # Show the window
        self.lift()  # Bring to front
        self.attributes('-topmost', True)  # Make sure it's on top
        self.after(100, lambda: self.attributes('-topmost', False))  # Then disable

    def quit_app(self):
        """Quit application with fade out"""
        for i in range(10, -1, -1):
            self.attributes('-alpha', i * 0.1)
            self.update()
            time.sleep(0.02)
        self.destroy()

# Simple test to run the app
if __name__ == "__main__":
    try:
        print("Starting Bypass Toolkit...")
        app = BypassApp()
        app.mainloop()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to close...")
