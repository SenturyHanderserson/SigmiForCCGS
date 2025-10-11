import customtkinter as ctk
import webbrowser
from urllib.parse import quote
import time
import threading
from typing import List, Tuple

class BypassApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("Bypass Toolkit")
        self.geometry("950x650")
        self.resizable(True, True)
        self.configure(fg_color="black")
        
        # Remove default title bar
        self.overrideredirect(True)
        
        # Center window on screen
        self.center_window()
        
        # Set theme
        ctk.set_appearance_mode("dark")
        
        # Variables for dragging
        self.x = 0
        self.y = 0
        
        # Create loading screen first
        self.create_loading_screen()
        
        # Show loading animation
        self.animate_loading()
        
    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
    
    def create_loading_screen(self):
        # Loading screen frame
        self.loading_frame = ctk.CTkFrame(
            self,
            fg_color="#0f0f1a",
            corner_radius=0
        )
        self.loading_frame.place(relwidth=1, relheight=1)
        
        # Loading content
        loading_content = ctk.CTkFrame(
            self.loading_frame,
            fg_color="transparent"
        )
        loading_content.place(relx=0.5, rely=0.5, anchor="center")
        
        # Animated logo
        self.loading_logo = ctk.CTkLabel(
            loading_content,
            text="🚀",
            font=ctk.CTkFont(size=80, weight="bold"),
            text_color="#667eea"
        )
        self.loading_logo.pack(pady=20)
        
        # Loading text
        self.loading_text = ctk.CTkLabel(
            loading_content,
            text="Bypass Toolkit",
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color="white"
        )
        self.loading_text.pack(pady=10)
        
        # Loading bar
        self.loading_bar = ctk.CTkProgressBar(
            loading_content,
            width=300,
            height=4,
            progress_color="#667eea",
            fg_color="gray20"
        )
        self.loading_bar.pack(pady=20)
        self.loading_bar.set(0)
        
        # Loading subtitle
        self.loading_subtitle = ctk.CTkLabel(
            loading_content,
            text="Initializing secure bypass protocols...",
            font=ctk.CTkFont(size=14),
            text_color="gray70"
        )
        self.loading_subtitle.pack(pady=10)
    
    def animate_loading(self):
        def loading_animation():
            # Animate progress bar
            for i in range(101):
                self.loading_bar.set(i/100)
                time.sleep(0.02)
                if i == 30:
                    self.loading_subtitle.configure(text="Loading GUI components...")
                elif i == 60:
                    self.loading_subtitle.configure(text="Initializing bypass methods...")
                elif i == 80:
                    self.loading_subtitle.configure(text="Almost ready...")
            
            # Fade out loading screen
            time.sleep(0.5)
            self.loading_frame.place_forget()
            
            # Create main GUI
            self.create_main_gui()
            self.animate_main_gui()
        
        threading.Thread(target=loading_animation, daemon=True).start()
    
    def create_main_gui(self):
        # Main container with glass effect
        self.main_container = ctk.CTkFrame(
            self,
            fg_color="#0f0f1a",
            corner_radius=20,
            border_width=1,
            border_color="gray30"
        )
        self.main_container.place(relwidth=0.98, relheight=0.98, relx=0.01, rely=0.01)
        
        # Create custom title bar
        self.create_title_bar()
        
        # Create main content
        self.create_main_content()
    
    def create_title_bar(self):
        # Title bar frame
        title_bar = ctk.CTkFrame(
            self.main_container,
            fg_color="transparent",
            height=50,
            corner_radius=0
        )
        title_bar.pack(fill="x", padx=0, pady=0)
        title_bar.pack_propagate(False)
        
        # Bind dragging events
        title_bar.bind("<ButtonPress-1>", self.start_move)
        title_bar.bind("<ButtonRelease-1>", self.stop_move)
        title_bar.bind("<B1-Motion>", self.do_move)
        
        # Title
        title_label = ctk.CTkLabel(
            title_bar,
            text="🚀 Bypass Toolkit",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#667eea"
        )
        title_label.pack(side="left", padx=20, pady=15)
        title_label.bind("<ButtonPress-1>", self.start_move)
        title_label.bind("<B1-Motion>", self.do_move)
        
        # Window controls
        controls_frame = ctk.CTkFrame(
            title_bar,
            fg_color="transparent"
        )
        controls_frame.pack(side="right", padx=10, pady=10)
        
        # Minimize button
        minimize_btn = ctk.CTkButton(
            controls_frame,
            text="─",
            width=30,
            height=30,
            fg_color="gray20",
            hover_color="gray30",
            text_color="white",
            font=ctk.CTkFont(size=16, weight="bold"),
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
            fg_color="gray20",
            hover_color="#e74c3c",
            text_color="white",
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self.quit_app,
            corner_radius=8
        )
        close_btn.pack(side="left", padx=5)
    
    def create_main_content(self):
        # Main content frame
        content_frame = ctk.CTkFrame(
            self.main_container,
            fg_color="transparent"
        )
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create sidebar and main area
        self.create_sidebar(content_frame)
        self.create_main_area(content_frame)
    
    def create_sidebar(self, parent):
        # Sidebar frame
        sidebar = ctk.CTkFrame(
            parent,
            fg_color="#151522",
            width=250,
            corner_radius=15
        )
        sidebar.pack(side="left", fill="y", padx=(0, 20))
        sidebar.pack_propagate(False)
        
        # Navigation items
        nav_items = [
            ("🔓", "Bypasses", "bypasses"),
            ("🛠️", "Tools", "tools"), 
            ("⚙️", "Settings", "settings")
        ]
        
        for icon, text, section in nav_items:
            item = ctk.CTkButton(
                sidebar,
                text=f"   {icon}  {text}",
                font=ctk.CTkFont(size=14, weight="bold"),
                fg_color="transparent",
                hover_color="#1e1e2d",
                anchor="w",
                height=45,
                corner_radius=10
            )
            item.pack(fill="x", padx=15, pady=5)
        
        # Sub-items for bypasses
        sub_items = [
            ("🌐", "Linewize", "linewize"),
            ("🛡️", "Securly", "securly"),
            ("🔒", "GoGuardian", "goguardian")
        ]
        
        sub_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        sub_frame.pack(fill="x", padx=25, pady=10)
        
        for icon, text, subsection in sub_items:
            sub_item = ctk.CTkButton(
                sub_frame,
                text=f"   {icon}  {text}",
                font=ctk.CTkFont(size=12),
                fg_color="transparent",
                hover_color="#1a1a28",
                anchor="w",
                height=35,
                corner_radius=8
            )
            sub_item.pack(fill="x", pady=2)
    
    def create_main_area(self, parent):
        # Main content area
        main_area = ctk.CTkFrame(
            parent,
            fg_color="#151522",
            corner_radius=15
        )
        main_area.pack(side="left", fill="both", expand=True)
        
        # Content container
        content_container = ctk.CTkScrollableFrame(
            main_area,
            fg_color="transparent",
            corner_radius=0
        )
        content_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Section header
        header_frame = ctk.CTkFrame(content_container, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        
        title = ctk.CTkLabel(
            header_frame,
            text="Linewize Bypasses",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="white"
        )
        title.pack(side="left")
        
        badge = ctk.CTkLabel(
            header_frame,
            text="ACTIVE",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="white",
            fg_color="#667eea",
            corner_radius=10
        )
        badge.pack(side="left", padx=10, pady=5)
        
        # Method cards
        self.create_method_card(
            content_container,
            "Method 1: Google Translate Bypass",
            "WORKING",
            "#4CAF50",
            "Enter any blocked URL to bypass through Google Translate proxy:",
            "🚀 Bypass Now"
        )
        
        self.create_method_card(
            content_container,
            "Method 2: Advanced Proxy", 
            "BETA",
            "#FF9800",
            "Advanced proxy method with enhanced stealth features (coming soon):",
            "🔧 Coming Soon"
        )
    
    def create_method_card(self, parent, title, badge_text, badge_color, description, button_text):
        # Card frame
        card = ctk.CTkFrame(
            parent,
            fg_color="#1e1e2d",
            corner_radius=15,
            border_width=1,
            border_color="gray30"
        )
        card.pack(fill="x", pady=15)
        
        # Card content
        card_content = ctk.CTkFrame(card, fg_color="transparent")
        card_content.pack(fill="x", padx=25, pady=25)
        
        # Card header
        header = ctk.CTkFrame(card_content, fg_color="transparent")
        header.pack(fill="x", pady=(0, 15))
        
        title_label = ctk.CTkLabel(
            header,
            text=title,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="white"
        )
        title_label.pack(side="left")
        
        badge = ctk.CTkLabel(
            header,
            text=badge_text,
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="white",
            fg_color=badge_color,
            corner_radius=8
        )
        badge.pack(side="right")
        
        # Description
        desc_label = ctk.CTkLabel(
            card_content,
            text=description,
            font=ctk.CTkFont(size=14),
            text_color="gray80",
            wraplength=600
        )
        desc_label.pack(fill="x", pady=(0, 20))
        
        # Input area for first method
        if "Google Translate" in title:
            input_frame = ctk.CTkFrame(card_content, fg_color="transparent")
            input_frame.pack(fill="x", pady=(0, 20))
            
            self.url_entry = ctk.CTkEntry(
                input_frame,
                placeholder_text="https://example.com",
                height=45,
                font=ctk.CTkFont(size=14),
                fg_color="#252538",
                border_color="gray40",
                text_color="white"
            )
            self.url_entry.pack(fill="x", side="left", expand=True, padx=(0, 15))
            
            bypass_btn = ctk.CTkButton(
                input_frame,
                text=button_text,
                command=self.bypass_url,
                height=45,
                font=ctk.CTkFont(size=14, weight="bold"),
                fg_color=("#667eea", "#5a6fd8"),
                hover_color=("#5a6fd8", "#4a5fc8"),
                corner_radius=10
            )
            bypass_btn.pack(side="right")
            
            # Footer info
            footer = ctk.CTkLabel(
                card_content,
                text="✓ Encrypted connection • ✓ Fast • ✓ Reliable",
                font=ctk.CTkFont(size=12),
                text_color="gray60"
            )
            footer.pack(anchor="w")
        else:
            # Just button for second method
            placeholder_btn = ctk.CTkButton(
                card_content,
                text=button_text,
                height=45,
                font=ctk.CTkFont(size=14, weight="bold"),
                fg_color=("gray40", "gray50"),
                hover_color=("gray50", "gray60"),
                corner_radius=10,
                state="disabled"
            )
            placeholder_btn.pack(fill="x", pady=(0, 10))
            
            # Footer info
            footer = ctk.CTkLabel(
                card_content,
                text="⏳ Under development • Enhanced stealth",
                font=ctk.CTkFont(size=12),
                text_color="gray60"
            )
            footer.pack(anchor="w")
    
    def animate_main_gui(self):
        # Animate main container entrance
        self.main_container.configure(fg_color="#0a0a12")
        self.after(10, lambda: self.main_container.configure(fg_color="#0f0f1a"))
        self.after(20, lambda: self.main_container.configure(fg_color="#151522"))
        self.after(30, lambda: self.main_container.configure(fg_color="#1a1a2a"))
        self.after(40, lambda: self.main_container.configure(fg_color="#1e1e32"))
    
    def bypass_url(self):
        url = self.url_entry.get().strip()
        if not url:
            # Shake animation for empty input
            original_x = self.url_entry.winfo_x()
            for i in range(5):
                self.url_entry.place(x=original_x + 5 if i % 2 == 0 else original_x - 5)
                self.update()
                time.sleep(0.05)
            self.url_entry.place(x=original_x)
            return
        
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        bypass_url = f"https://translate.google.com/translate?sl=auto&tl=en&u={quote(url)}"
        webbrowser.open(bypass_url)
    
    # Window dragging functions
    def start_move(self, event):
        self.x = event.x
        self.y = event.y
    
    def stop_move(self, event):
        self.x = None
        self.y = None
    
    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry(f"+{x}+{y}")
    
    def minimize_window(self):
        self.overrideredirect(False)
        self.state('iconic')
        self.overrideredirect(True)
    
    def quit_app(self):
        # Fade out animation
        for i in range(10, -1, -1):
            self.attributes('-alpha', i/10)
            self.update()
            time.sleep(0.02)
        self.destroy()

if __name__ == "__main__":
    # Create and run app
    app = BypassApp()
    
    # Set window always on top initially for focus
    app.attributes('-alpha', 0.95)
    app.after(1000, lambda: app.attributes('-alpha', 1.0))
    
    app.mainloop()
