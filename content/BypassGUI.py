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
        
        # Configure window
        self.title("Bypass Toolkit")
        self.geometry("950x650")
        self.resizable(True, True)
        
        # Set dark theme for glass morphism
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Remove default title bar
        self.overrideredirect(True)
        
        # Center window on screen
        self.center_window()
        
        # Variables for dragging
        self.x = 0
        self.y = 0
        
        # Create main GUI directly (skip loading screen for now)
        self.create_main_gui()
        
    def center_window(self):
        self.update_idletasks()
        width = 950
        height = 650
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"+{x}+{y}")
    
    def create_main_gui(self):
        # Main container with glass effect
        self.main_container = ctk.CTkFrame(
            self,
            fg_color="#0f0f1a",
            corner_radius=20,
            border_width=1,
            border_color="rgba(255, 255, 255, 0.1)"
        )
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create custom title bar
        self.create_title_bar()
        
        # Create main content
        self.create_main_content()
        
        # Animate entrance
        self.animate_entrance()
    
    def create_title_bar(self):
        # Title bar frame with glass effect
        title_bar = ctk.CTkFrame(
            self.main_container,
            fg_color="rgba(255, 255, 255, 0.08)",
            height=50,
            corner_radius=15
        )
        title_bar.pack(fill="x", padx=15, pady=15)
        title_bar.pack_propagate(False)
        
        # Bind dragging events
        title_bar.bind("<ButtonPress-1>", self.start_move)
        title_bar.bind("<ButtonRelease-1>", self.stop_move)
        title_bar.bind("<B1-Motion>", self.do_move)
        
        # Title with icon
        title_frame = ctk.CTkFrame(title_bar, fg_color="transparent")
        title_frame.pack(side="left", padx=20, pady=10)
        
        title_icon = ctk.CTkLabel(
            title_frame,
            text="🚀",
            font=ctk.CTkFont(size=20),
            text_color="#667eea"
        )
        title_icon.pack(side="left")
        
        title_label = ctk.CTkLabel(
            title_frame,
            text="Bypass Toolkit",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="white"
        )
        title_label.pack(side="left", padx=(10, 0))
        title_label.bind("<ButtonPress-1>", self.start_move)
        title_label.bind("<B1-Motion>", self.do_move)
        
        # Window controls
        controls_frame = ctk.CTkFrame(title_bar, fg_color="transparent")
        controls_frame.pack(side="right", padx=15, pady=10)
        
        # Minimize button with hover effects
        self.minimize_btn = ctk.CTkButton(
            controls_frame,
            text="−",
            width=30,
            height=30,
            fg_color="rgba(255, 255, 255, 0.1)",
            hover_color="rgba(255, 255, 255, 0.2)",
            text_color="white",
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self.minimize_window,
            corner_radius=8
        )
        self.minimize_btn.pack(side="left", padx=5)
        
        # Close button with hover effects
        self.close_btn = ctk.CTkButton(
            controls_frame,
            text="×",
            width=30,
            height=30,
            fg_color="rgba(255, 255, 255, 0.1)",
            hover_color="#e74c3c",
            text_color="white",
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self.quit_app,
            corner_radius=8
        )
        self.close_btn.pack(side="left", padx=5)
    
    def create_main_content(self):
        # Main content frame
        content_frame = ctk.CTkFrame(
            self.main_container,
            fg_color="transparent"
        )
        content_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Create sidebar and main area
        self.create_sidebar(content_frame)
        self.create_main_area(content_frame)
    
    def create_sidebar(self, parent):
        # Sidebar frame with glass effect
        sidebar = ctk.CTkFrame(
            parent,
            fg_color="rgba(255, 255, 255, 0.05)",
            width=250,
            corner_radius=15
        )
        sidebar.pack(side="left", fill="y", padx=(0, 15))
        sidebar.pack_propagate(False)
        
        # Navigation items
        nav_items = [
            ("🔓", "Bypasses", "bypasses"),
            ("🛠️", "Tools", "tools"), 
            ("⚙️", "Settings", "settings")
        ]
        
        for icon, text, section in nav_items:
            nav_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
            nav_frame.pack(fill="x", padx=15, pady=8)
            
            item = ctk.CTkButton(
                nav_frame,
                text=f"   {icon}  {text}",
                font=ctk.CTkFont(size=14, weight="bold"),
                fg_color="transparent",
                hover_color="rgba(255, 255, 255, 0.1)",
                text_color="rgba(255, 255, 255, 0.9)",
                anchor="w",
                height=45,
                corner_radius=10,
                command=lambda s=section: self.switch_section(s)
            )
            item.pack(fill="x", padx=5)
            
            if text == "Bypasses":
                # Sub-items for bypasses
                sub_items = [
                    ("🌐", "Linewize", "2 Methods"),
                    ("🛡️", "Securly", "Soon"),
                    ("🔒", "GoGuardian", "Soon")
                ]
                
                sub_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
                sub_frame.pack(fill="x", padx=25, pady=5)
                
                for sub_icon, sub_text, badge_text in sub_items:
                    sub_item_frame = ctk.CTkFrame(sub_frame, fg_color="transparent")
                    sub_item_frame.pack(fill="x", pady=3)
                    
                    sub_item = ctk.CTkButton(
                        sub_item_frame,
                        text=f"   {sub_icon}  {sub_text}",
                        font=ctk.CTkFont(size=12),
                        fg_color="transparent",
                        hover_color="rgba(255, 255, 255, 0.08)",
                        text_color="rgba(255, 255, 255, 0.8)",
                        anchor="w",
                        height=35,
                        corner_radius=8,
                        command=lambda st=sub_text: self.switch_subsection(st)
                    )
                    sub_item.pack(side="left", fill="x", expand=True, padx=5)
                    
                    # Badge
                    badge = ctk.CTkLabel(
                        sub_item_frame,
                        text=badge_text,
                        font=ctk.CTkFont(size=9, weight="bold"),
                        text_color="white",
                        fg_color="rgba(255, 255, 255, 0.15)",
                        corner_radius=6,
                        width=55
                    )
                    badge.pack(side="right", padx=5)
    
    def create_main_area(self, parent):
        # Main content area with glass effect
        main_area = ctk.CTkFrame(
            parent,
            fg_color="rgba(255, 255, 255, 0.05)",
            corner_radius=15
        )
        main_area.pack(side="left", fill="both", expand=True)
        
        # Content container
        self.content_container = ctk.CTkScrollableFrame(
            main_area,
            fg_color="transparent",
            corner_radius=0
        )
        self.content_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Show Linewize section by default
        self.show_linewize_section()
    
    def show_linewize_section(self):
        # Clear existing content
        for widget in self.content_container.winfo_children():
            widget.destroy()
        
        # Section header
        header_frame = ctk.CTkFrame(self.content_container, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 30))
        
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
        badge.pack(side="left", padx=15, pady=5)
        
        # Method cards
        self.create_method_card(
            "Method 1: Google Translate Bypass",
            "WORKING",
            "#4CAF50",
            "Enter any blocked URL to bypass through Google Translate proxy:",
            "🚀 Bypass Now",
            True
        )
        
        self.create_method_card(
            "Method 2: Advanced Proxy", 
            "BETA",
            "#FF9800",
            "Advanced proxy method with enhanced stealth features (coming soon):",
            "🔧 Coming Soon",
            False
        )
    
    def create_method_card(self, title, badge_text, badge_color, description, button_text, has_input):
        # Card frame with glass effect
        card = ctk.CTkFrame(
            self.content_container,
            fg_color="rgba(255, 255, 255, 0.08)",
            corner_radius=15,
            border_width=1,
            border_color="rgba(255, 255, 255, 0.12)"
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
            text_color="rgba(255, 255, 255, 0.8)",
            wraplength=600
        )
        desc_label.pack(fill="x", pady=(0, 20))
        
        if has_input:
            # Input area for first method
            input_frame = ctk.CTkFrame(card_content, fg_color="transparent")
            input_frame.pack(fill="x", pady=(0, 20))
            
            # Input container with glass effect
            input_container = ctk.CTkFrame(input_frame, fg_color="transparent")
            input_container.pack(fill="x", side="left", expand=True, padx=(0, 15))
            
            # Input field with glass effect
            self.url_entry = ctk.CTkEntry(
                input_container,
                placeholder_text="https://example.com",
                height=45,
                font=ctk.CTkFont(size=14),
                fg_color="rgba(255, 255, 255, 0.1)",
                border_color="rgba(255, 255, 255, 0.2)",
                text_color="white",
                placeholder_text_color="rgba(255, 255, 255, 0.5)"
            )
            self.url_entry.pack(fill="x")
            
            # Bypass button with gradient and hover effects
            self.bypass_btn = ctk.CTkButton(
                input_frame,
                text=button_text,
                command=self.bypass_url,
                height=45,
                font=ctk.CTkFont(size=14, weight="bold"),
                fg_color="#667eea",
                hover_color="#5a6fd8",
                text_color="white",
                corner_radius=10
            )
            self.bypass_btn.pack(side="right")
            
            # Footer info
            footer = ctk.CTkLabel(
                card_content,
                text="✓ Encrypted connection • ✓ Fast • ✓ Reliable",
                font=ctk.CTkFont(size=12),
                text_color="rgba(255, 255, 255, 0.6)"
            )
            footer.pack(anchor="w")
        else:
            # Just button for second method
            placeholder_btn = ctk.CTkButton(
                card_content,
                text=button_text,
                height=45,
                font=ctk.CTkFont(size=14, weight="bold"),
                fg_color="rgba(108, 117, 125, 0.5)",
                hover_color="rgba(108, 117, 125, 0.7)",
                text_color="white",
                corner_radius=10,
                state="disabled"
            )
            placeholder_btn.pack(fill="x", pady=(0, 10))
            
            # Footer info
            footer = ctk.CTkLabel(
                card_content,
                text="⏳ Under development • Enhanced stealth",
                font=ctk.CTkFont(size=12),
                text_color="rgba(255, 255, 255, 0.6)"
            )
            footer.pack(anchor="w")
    
    def switch_section(self, section):
        print(f"Switching to section: {section}")
        # Add section switching logic here
    
    def switch_subsection(self, subsection):
        print(f"Switching to subsection: {subsection}")
        # Add subsection switching logic here
    
    def animate_entrance(self):
        # Fade in animation
        self.attributes('-alpha', 0)
        self.update()
        
        for i in range(0, 101, 5):
            alpha = i / 100
            self.attributes('-alpha', alpha)
            self.update()
            time.sleep(0.01)
    
    def bypass_url(self):
        url = self.url_entry.get().strip()
        if not url:
            # Shake animation for empty input
            self.animate_shake(self.url_entry)
            return
        
        # Show loading state
        original_text = self.bypass_btn.cget("text")
        self.bypass_btn.configure(text="⏳ Bypassing...", state="disabled")
        self.update()
        
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        bypass_url = f"https://translate.google.com/translate?sl=auto&tl=en&u={quote(url)}"
        
        # Simulate loading delay
        self.after(1000, lambda: self.complete_bypass(bypass_url, original_text))
    
    def complete_bypass(self, bypass_url, original_text):
        webbrowser.open(bypass_url)
        # Reset button
        self.bypass_btn.configure(text=original_text, state="normal")
    
    def animate_shake(self, widget):
        original_x = widget.winfo_x()
        for i in range(6):
            offset = 5 if i % 2 == 0 else -5
            widget.place(x=original_x + offset)
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
        # Animate minimize
        for i in range(10, -1, -1):
            self.attributes('-alpha', i/10)
            self.update()
            time.sleep(0.02)
        
        self.overrideredirect(False)
        self.state('iconic')
        self.overrideredirect(True)
        
        # Restore opacity
        self.attributes('-alpha', 1.0)
    
    def quit_app(self):
        # Fade out animation
        for i in range(10, -1, -1):
            self.attributes('-alpha', i/10)
            self.update()
            time.sleep(0.03)
        self.destroy()

if __name__ == "__main__":
    try:
        app = BypassApp()
        app.mainloop()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
