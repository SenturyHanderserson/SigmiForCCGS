import customtkinter as ctk
import webbrowser
from urllib.parse import quote
import time
import threading
import sys
import os

class BypassApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configure window for glass morphism effect
        self.title("Bypass Toolkit")
        self.geometry("950x650")
        self.resizable(True, True)
        
        # Set light theme for glass morphism
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Remove default title bar
        self.overrideredirect(True)
        
        # Center window on screen
        self.center_window()
        
        # Variables for dragging
        self.x = 0
        self.y = 0
        
        # Create loading screen first
        self.create_loading_screen()
        
        # Show loading animation
        self.animate_loading()
        
    def center_window(self):
        self.update_idletasks()
        width = 950
        height = 650
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
    
    def create_loading_screen(self):
        # Loading screen frame with glass effect
        self.loading_frame = ctk.CTkFrame(
            self,
            fg_color="white",
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
            text_color="#2d3748"
        )
        self.loading_text.pack(pady=10)
        
        # Loading bar
        self.loading_bar = ctk.CTkProgressBar(
            loading_content,
            width=300,
            height=4,
            progress_color="#667eea",
            fg_color="#e2e8f0"
        )
        self.loading_bar.pack(pady=20)
        self.loading_bar.set(0)
        
        # Loading subtitle
        self.loading_subtitle = ctk.CTkLabel(
            loading_content,
            text="Initializing secure bypass protocols...",
            font=ctk.CTkFont(size=14),
            text_color="#718096"
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
            fg_color="white",
            corner_radius=24,
            border_width=1,
            border_color="rgba(255, 255, 255, 0.2)"
        )
        self.main_container.place(relwidth=0.98, relheight=0.98, relx=0.01, rely=0.01)
        
        # Create custom title bar
        self.create_title_bar()
        
        # Create main content
        self.create_main_content()
    
    def create_title_bar(self):
        # Title bar frame with glass effect
        title_bar = ctk.CTkFrame(
            self.main_container,
            fg_color="rgba(255, 255, 255, 0.12)",
            height=60,
            corner_radius=0
        )
        title_bar.pack(fill="x", padx=0, pady=0)
        title_bar.pack_propagate(False)
        
        # Bind dragging events
        title_bar.bind("<ButtonPress-1>", self.start_move)
        title_bar.bind("<ButtonRelease-1>", self.stop_move)
        title_bar.bind("<B1-Motion>", self.do_move)
        
        # Title with gradient effect
        title_frame = ctk.CTkFrame(title_bar, fg_color="transparent")
        title_frame.pack(side="left", padx=30, pady=15)
        
        title_icon = ctk.CTkLabel(
            title_frame,
            text="🚀",
            font=ctk.CTkFont(size=24),
            text_color="#667eea"
        )
        title_icon.pack(side="left")
        
        title_label = ctk.CTkLabel(
            title_frame,
            text="Bypass Toolkit",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#2d3748"
        )
        title_label.pack(side="left", padx=(10, 0))
        title_label.bind("<ButtonPress-1>", self.start_move)
        title_label.bind("<B1-Motion>", self.do_move)
        
        # Window controls
        controls_frame = ctk.CTkFrame(title_bar, fg_color="transparent")
        controls_frame.pack(side="right", padx=20, pady=15)
        
        # Minimize button
        minimize_btn = ctk.CTkButton(
            controls_frame,
            text="−",
            width=32,
            height=32,
            fg_color="rgba(255, 255, 255, 0.15)",
            hover_color="rgba(255, 255, 255, 0.25)",
            text_color="#2d3748",
            font=ctk.CTkFont(size=18, weight="bold"),
            command=self.minimize_window,
            corner_radius=10
        )
        minimize_btn.pack(side="left", padx=5)
        
        # Close button
        close_btn = ctk.CTkButton(
            controls_frame,
            text="×",
            width=32,
            height=32,
            fg_color="rgba(255, 255, 255, 0.15)",
            hover_color="rgba(255, 75, 75, 0.4)",
            text_color="#2d3748",
            font=ctk.CTkFont(size=18, weight="bold"),
            command=self.quit_app,
            corner_radius=10
        )
        close_btn.pack(side="left", padx=5)
    
    def create_main_content(self):
        # Main content frame
        content_frame = ctk.CTkFrame(
            self.main_container,
            fg_color="transparent"
        )
        content_frame.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Create sidebar and main area
        self.create_sidebar(content_frame)
        self.create_main_area(content_frame)
    
    def create_sidebar(self, parent):
        # Sidebar frame with glass effect
        sidebar = ctk.CTkFrame(
            parent,
            fg_color="rgba(255, 255, 255, 0.08)",
            width=280,
            corner_radius=0
        )
        sidebar.pack(side="left", fill="y", padx=(0, 0))
        sidebar.pack_propagate(False)
        
        # Navigation items
        nav_items = [
            ("🔓", "Bypasses", "bypasses"),
            ("🛠️", "Tools", "tools"), 
            ("⚙️", "Settings", "settings")
        ]
        
        for icon, text, section in nav_items:
            nav_frame = ctk.CTkFrame(sidebar, fg_color="transparent", height=60)
            nav_frame.pack(fill="x", padx=15, pady=5)
            nav_frame.pack_propagate(False)
            
            item = ctk.CTkButton(
                nav_frame,
                text=f"   {icon}  {text}",
                font=ctk.CTkFont(size=14, weight="bold"),
                fg_color="transparent",
                hover_color="rgba(255, 255, 255, 0.15)",
                text_color="#2d3748",
                anchor="w",
                height=50,
                corner_radius=12
            )
            item.pack(fill="both", expand=True, padx=10, pady=5)
            
            if text == "Bypasses":
                # Sub-items for bypasses
                sub_items = [
                    ("🌐", "Linewize", "2 Methods"),
                    ("🛡️", "Securly", "Soon"),
                    ("🔒", "GoGuardian", "Soon")
                ]
                
                sub_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
                sub_frame.pack(fill="x", padx=30, pady=5)
                
                for sub_icon, sub_text, badge_text in sub_items:
                    sub_item_frame = ctk.CTkFrame(sub_frame, fg_color="transparent", height=45)
                    sub_item_frame.pack(fill="x", pady=2)
                    sub_item_frame.pack_propagate(False)
                    
                    sub_item = ctk.CTkButton(
                        sub_item_frame,
                        text=f"   {sub_icon}  {sub_text}",
                        font=ctk.CTkFont(size=12),
                        fg_color="transparent",
                        hover_color="rgba(255, 255, 255, 0.1)",
                        text_color="#4a5568",
                        anchor="w",
                        height=40,
                        corner_radius=10
                    )
                    sub_item.pack(side="left", fill="x", expand=True, padx=5)
                    
                    # Badge
                    badge = ctk.CTkLabel(
                        sub_item_frame,
                        text=badge_text,
                        font=ctk.CTkFont(size=10, weight="bold"),
                        text_color="white",
                        fg_color="rgba(255, 255, 255, 0.15)",
                        corner_radius=6,
                        width=60
                    )
                    badge.pack(side="right", padx=5)
    
    def create_main_area(self, parent):
        # Main content area with glass effect
        main_area = ctk.CTkFrame(
            parent,
            fg_color="rgba(255, 255, 255, 0.05)",
            corner_radius=0
        )
        main_area.pack(side="left", fill="both", expand=True)
        
        # Content container
        content_container = ctk.CTkScrollableFrame(
            main_area,
            fg_color="transparent",
            corner_radius=0
        )
        content_container.pack(fill="both", expand=True, padx=40, pady=40)
        
        # Section header
        header_frame = ctk.CTkFrame(content_container, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 35))
        
        title = ctk.CTkLabel(
            header_frame,
            text="Linewize Bypasses",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color="#2d3748"
        )
        title.pack(side="left")
        
        badge = ctk.CTkLabel(
            header_frame,
            text="Active",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="white",
            fg_color="linear-gradient(135deg, #667eea, #764ba2)",
            corner_radius=10
        )
        badge.pack(side="left", padx=20, pady=5)
        
        # Method cards
        self.create_method_card(
            content_container,
            "Method 1: Google Translate Bypass",
            "Working",
            "success",
            "Enter any blocked URL to bypass through Google Translate proxy:",
            "🚀 Bypass Now",
            True
        )
        
        self.create_method_card(
            content_container,
            "Method 2: Advanced Proxy", 
            "Beta",
            "warning",
            "Advanced proxy method with enhanced stealth features (coming soon):",
            "🔧 Launch Proxy",
            False
        )
    
    def create_method_card(self, parent, title, badge_text, badge_type, description, button_text, has_input):
        # Card frame with glass effect
        card = ctk.CTkFrame(
            parent,
            fg_color="rgba(255, 255, 255, 0.12)",
            corner_radius=20,
            border_width=1,
            border_color="rgba(255, 255, 255, 0.18)"
        )
        card.pack(fill="x", pady=15)
        
        # Card content
        card_content = ctk.CTkFrame(card, fg_color="transparent")
        card_content.pack(fill="x", padx=35, pady=35)
        
        # Card header
        header = ctk.CTkFrame(card_content, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))
        
        title_label = ctk.CTkLabel(
            header,
            text=title,
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#2d3748"
        )
        title_label.pack(side="left")
        
        # Badge with different colors
        if badge_type == "success":
            badge_color = "linear-gradient(135deg, #4CAF50, #45a049)"
        else:  # warning
            badge_color = "linear-gradient(135deg, #FF9800, #F57C00)"
            
        badge = ctk.CTkLabel(
            header,
            text=badge_text,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="white",
            fg_color=badge_color,
            corner_radius=8
        )
        badge.pack(side="right")
        
        # Description
        desc_label = ctk.CTkLabel(
            card_content,
            text=description,
            font=ctk.CTkFont(size=15),
            text_color="#4a5568",
            wraplength=600
        )
        desc_label.pack(fill="x", pady=(0, 25))
        
        if has_input:
            # Input area for first method
            input_frame = ctk.CTkFrame(card_content, fg_color="transparent")
            input_frame.pack(fill="x", pady=(0, 20))
            
            # Input container with icon
            input_container = ctk.CTkFrame(input_frame, fg_color="transparent")
            input_container.pack(fill="x", side="left", expand=True, padx=(0, 20))
            
            # Input field with glass effect
            self.url_entry = ctk.CTkEntry(
                input_container,
                placeholder_text="https://example.com",
                height=50,
                font=ctk.CTkFont(size=16),
                fg_color="rgba(255, 255, 255, 0.12)",
                border_color="rgba(255, 255, 255, 0.25)",
                text_color="#2d3748",
                placeholder_text_color="rgba(255, 255, 255, 0.6)"
            )
            self.url_entry.pack(fill="x")
            
            # Bypass button with gradient
            bypass_btn = ctk.CTkButton(
                input_frame,
                text=button_text,
                command=self.bypass_url,
                height=50,
                font=ctk.CTkFont(size=16, weight="bold"),
                fg_color="linear-gradient(135deg, #667eea, #764ba2)",
                hover_color="linear-gradient(135deg, #5a6fd8, #6a4ba8)",
                text_color="white",
                corner_radius=14
            )
            bypass_btn.pack(side="right")
            
            # Footer info
            footer = ctk.CTkLabel(
                card_content,
                text="✓ Encrypted connection • ✓ Fast • ✓ Reliable",
                font=ctk.CTkFont(size=13),
                text_color="rgba(255, 255, 255, 0.7)"
            )
            footer.pack(anchor="w")
        else:
            # Just button for second method
            placeholder_btn = ctk.CTkButton(
                card_content,
                text=button_text,
                height=50,
                font=ctk.CTkFont(size=16, weight="bold"),
                fg_color="linear-gradient(135deg, #6c757d, #495057)",
                hover_color="linear-gradient(135deg, #5a6268, #3d444b)",
                text_color="white",
                corner_radius=14,
                state="disabled"
            )
            placeholder_btn.pack(fill="x", pady=(0, 15))
            
            # Footer info
            footer = ctk.CTkLabel(
                card_content,
                text="⏳ Under development • Enhanced stealth",
                font=ctk.CTkFont(size=13),
                text_color="rgba(255, 255, 255, 0.7)"
            )
            footer.pack(anchor="w")
    
    def animate_main_gui(self):
        # Smooth entrance animation
        self.main_container.configure(fg_color="rgba(255, 255, 255, 0.8)")
        self.after(50, lambda: self.main_container.configure(fg_color="rgba(255, 255, 255, 0.9)"))
        self.after(100, lambda: self.main_container.configure(fg_color="rgba(255, 255, 255, 0.95)"))
        self.after(150, lambda: self.main_container.configure(fg_color="white"))
    
    def bypass_url(self):
        url = self.url_entry.get().strip()
        if not url:
            # Shake animation for empty input
            self.animate_shake(self.url_entry)
            return
        
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        bypass_url = f"https://translate.google.com/translate?sl=auto&tl=en&u={quote(url)}"
        webbrowser.open(bypass_url)
    
    def animate_shake(self, widget):
        original_x = widget.winfo_x()
        for i in range(5):
            new_x = original_x + (5 if i % 2 == 0 else -5)
            widget.place(x=new_x)
            self.update()
            time.sleep(0.05)
        widget.place(x=original_x)
    
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
    try:
        app = BypassApp()
        app.attributes('-alpha', 0.95)
        app.after(1000, lambda: app.attributes('-alpha', 1.0))
        app.mainloop()
    except Exception as e:
        print(f"Error: {e}")
        input("Press Enter to exit...")
