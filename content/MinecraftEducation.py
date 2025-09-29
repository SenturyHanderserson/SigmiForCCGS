import tkinter as tk
from tkinter import ttk, messagebox
import threading
import pyautogui
import keyboard
import time
import random
import os
import json

class ModernAutoClicker:
    def __init__(self, root):
        self.root = root
        self.running = False
        self.mode = tk.StringVar(value="click")
        self.custom_key = None
        self.custom_hook = None
        self.click_interval = tk.DoubleVar(value=0.1)
        self.jitter_enabled = tk.BooleanVar(value=True)
        self.jitter_amount = tk.DoubleVar(value=0.5)
        self.human_like = tk.BooleanVar(value=True)
        
        # Set window title to appear as Minecraft Education Edition
        self.root.title("Minecraft: Education Edition - Classroom Tools")
        self.root.geometry("800x600")
        self.root.configure(bg='#1a1a2e')
        self.root.resizable(True, True)
        
        # Make window always stay on top
        self.root.attributes('-topmost', True)
        
        # Load configuration
        self.load_config()
        
        # Setup the UI
        self.setup_ui()
        
        # Start background thread for hotkey listening
        threading.Thread(target=self.listen_hotkeys, daemon=True).start()
        
        # Statistics
        self.action_count = 0
        self.session_start_time = 0

    def setup_ui(self):
        """Create a stunning glassmorphism UI"""
        # Main container
        self.main_frame = tk.Frame(self.root, bg='#1a1a2e')
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header with Minecraft-like styling
        self.header_frame = tk.Frame(self.main_frame, bg='#16213e', height=80)
        self.header_frame.pack(fill=tk.X, pady=(0, 20))
        self.header_frame.pack_propagate(False)
        
        # Minecraft-like title
        self.title_label = tk.Label(
            self.header_frame, 
            text="Minecraft: Education Edition", 
            font=('Arial', 18, 'bold'), 
            bg='#16213e', 
            fg='#4cc9f0'
        )
        self.title_label.pack(side=tk.LEFT, padx=20, pady=20)
        
        # Status indicator
        self.status_indicator = tk.Label(
            self.header_frame, 
            text="● READY", 
            font=('Arial', 12, 'bold'), 
            bg='#16213e', 
            fg='#4ade80'
        )
        self.status_indicator.pack(side=tk.RIGHT, padx=20, pady=20)
        
        # Content area
        self.content_frame = tk.Frame(self.main_frame, bg='rgba(255,255,255,0.1)')
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Controls
        self.controls_frame = self.create_glass_frame(self.content_frame, "Activity Controls")
        self.controls_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Right panel - Settings
        self.settings_frame = self.create_glass_frame(self.content_frame, "Lesson Settings")
        self.settings_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Fill the frames
        self.setup_controls()
        self.setup_settings()
        
        # Footer
        self.footer_frame = tk.Frame(self.main_frame, bg='rgba(0,0,0,0.2)', height=40)
        self.footer_frame.pack(fill=tk.X, pady=(20, 0))
        self.footer_frame.pack_propagate(False)
        
        self.footer_label = tk.Label(
            self.footer_frame, 
            text="Minecraft Education Edition - Classroom Tools v2.4.5 | Press F6 to Start/Stop | F7 for Emergency Stop", 
            font=('Arial', 9), 
            bg='rgba(0,0,0,0.2)', 
            fg='#a5b4cb'
        )
        self.footer_label.pack(pady=10)

    def create_glass_frame(self, parent, title):
        """Create a glassmorphism-styled frame"""
        frame = tk.Frame(parent, bg='rgba(255,255,255,0.1)')
        
        # Title bar
        title_frame = tk.Frame(frame, bg='rgba(255,255,255,0.15)', height=40)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame, 
            text=title, 
            font=('Arial', 12, 'bold'), 
            bg='rgba(255,255,255,0.15)', 
            fg='white'
        )
        title_label.pack(side=tk.LEFT, padx=15, pady=10)
        
        # Content area
        content = tk.Frame(frame, bg='rgba(255,255,255,0.05)')
        content.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        return frame

    def setup_controls(self):
        """Setup the controls section"""
        content = self.controls_frame.winfo_children()[1]
        
        # Mode selection
        mode_frame = tk.Frame(content, bg='rgba(255,255,255,0.05)')
        mode_frame.pack(fill=tk.X, padx=15, pady=15)
        
        mode_label = tk.Label(
            mode_frame, 
            text="Select Activity Type:", 
            font=('Arial', 11, 'bold'), 
            bg='rgba(255,255,255,0.05)', 
            fg='white'
        )
        mode_label.pack(anchor='w', pady=(0, 10))
        
        # Radio buttons
        self.create_radio_button(mode_frame, "Left Click (Basic Interaction)", "click")
        self.create_radio_button(mode_frame, "Right Click (Advanced Interaction)", "right_click")
        self.create_radio_button(mode_frame, "Space Bar (Jump Action)", "space")
        self.create_radio_button(mode_frame, "Custom Key (Special Action)", "custom")
        
        # Custom key selection
        custom_key_frame = tk.Frame(content, bg='rgba(255,255,255,0.05)')
        custom_key_frame.pack(fill=tk.X, padx=15, pady=10)
        
        self.select_key_button = tk.Button(
            custom_key_frame,
            text="Select Custom Key",
            command=self.select_key,
            bg='#3b82f6',
            fg='white',
            font=('Arial', 9),
            relief='flat',
            padx=15,
            pady=5
        )
        self.select_key_button.pack(pady=5)
        
        self.key_info_label = tk.Label(
            custom_key_frame, 
            text="No key selected", 
            font=('Arial', 9), 
            bg='rgba(255,255,255,0.05)', 
            fg='#a5b4cb'
        )
        self.key_info_label.pack(pady=5)
        
        # Control buttons
        button_frame = tk.Frame(content, bg='rgba(255,255,255,0.05)')
        button_frame.pack(fill=tk.X, padx=15, pady=20)
        
        self.start_button = tk.Button(
            button_frame,
            text="START ACTIVITY (F6)",
            command=self.toggle_running,
            bg='#4ade80',
            fg='white',
            font=('Arial', 10, 'bold'),
            relief='flat',
            padx=20,
            pady=10,
            width=20
        )
        self.start_button.pack(pady=10)
        
        self.emergency_button = tk.Button(
            button_frame,
            text="STOP ACTIVITY (F7)",
            command=self.emergency_stop,
            bg='#ef4444',
            fg='white',
            font=('Arial', 10, 'bold'),
            relief='flat',
            padx=20,
            pady=10,
            width=20
        )
        self.emergency_button.pack(pady=5)

    def setup_settings(self):
        """Setup the settings section"""
        content = self.settings_frame.winfo_children()[1]
        
        # Click interval
        interval_frame = tk.Frame(content, bg='rgba(255,255,255,0.05)')
        interval_frame.pack(fill=tk.X, padx=15, pady=15)
        
        interval_label = tk.Label(
            interval_frame, 
            text=f"Activity Speed: {self.click_interval.get()}s", 
            font=('Arial', 11, 'bold'), 
            bg='rgba(255,255,255,0.05)', 
            fg='white'
        )
        interval_label.pack(anchor='w', pady=(0, 10))
        
        interval_scale = tk.Scale(
            interval_frame,
            from_=0.05,
            to=2.0,
            resolution=0.05,
            orient=tk.HORIZONTAL,
            variable=self.click_interval,
            command=lambda v: interval_label.config(text=f"Activity Speed: {float(v):.2f}s"),
            bg='rgba(255,255,255,0.05)',
            fg='white',
            highlightbackground='rgba(255,255,255,0.1)',
            troughcolor='#4cc9f0',
            length=200
        )
        interval_scale.set(self.click_interval.get())
        interval_scale.pack(fill=tk.X, pady=5)
        
        # Human-like options
        human_frame = tk.Frame(content, bg='rgba(255,255,255,0.05)')
        human_frame.pack(fill=tk.X, padx=15, pady=15)
        
        human_label = tk.Label(
            human_frame, 
            text="Natural Behavior Settings:", 
            font=('Arial', 11, 'bold'), 
            bg='rgba(255,255,255,0.05)', 
            fg='white'
        )
        human_label.pack(anchor='w', pady=(0, 10))
        
        tk.Checkbutton(
            human_frame,
            text="Enable Natural Movement",
            variable=self.jitter_enabled,
            bg='rgba(255,255,255,0.05)',
            fg='white',
            selectcolor='#1a1a2e',
            font=('Arial', 9),
            anchor='w'
        ).pack(fill=tk.X, pady=2)
        
        tk.Checkbutton(
            human_frame,
            text="Random Timing Variations",
            variable=self.human_like,
            bg='rgba(255,255,255,0.05)',
            fg='white',
            selectcolor='#1a1a2e',
            font=('Arial', 9),
            anchor='w'
        ).pack(fill=tk.X, pady=2)
        
        # Stats display
        stats_frame = tk.Frame(content, bg='rgba(255,255,255,0.05)')
        stats_frame.pack(fill=tk.X, padx=15, pady=15)
        
        stats_label = tk.Label(
            stats_frame, 
            text="Session Statistics:", 
            font=('Arial', 11, 'bold'), 
            bg='rgba(255,255,255,0.05)', 
            fg='white'
        )
        stats_label.pack(anchor='w', pady=(0, 10))
        
        self.clicks_label = tk.Label(
            stats_frame, 
            text="Actions performed: 0", 
            font=('Arial', 9), 
            bg='rgba(255,255,255,0.05)', 
            fg='#a5b4cb'
        )
        self.clicks_label.pack(anchor='w')
        
        self.session_time_label = tk.Label(
            stats_frame, 
            text="Session time: 0s", 
            font=('Arial', 9), 
            bg='rgba(255,255,255,0.05)', 
            fg='#a5b4cb'
        )
        self.session_time_label.pack(anchor='w')

    def create_radio_button(self, parent, text, value):
        """Create a radio button"""
        radio = tk.Radiobutton(
            parent,
            text=text,
            variable=self.mode,
            value=value,
            bg='rgba(255,255,255,0.05)',
            fg='white',
            selectcolor='#1a1a2e',
            font=('Arial', 9),
            anchor='w'
        )
        radio.pack(fill=tk.X, pady=2)

    def select_key(self):
        """Allow user to select a custom key"""
        self.key_info_label.config(text="Press any key to select it...", fg='#4cc9f0')
        
        if self.custom_hook is not None:
            keyboard.unhook(self.custom_hook)
            self.custom_hook = None

        def on_key_press(event):
            self.custom_key = event.name
            self.key_info_label.config(text=f"Selected key: {self.custom_key}", fg='#4ade80')
            keyboard.unhook(self.custom_hook)
            self.custom_hook = None

        self.custom_hook = keyboard.on_press(on_key_press)

    def toggle_running(self):
        """Toggle the running state"""
        self.running = not self.running
        
        if self.running:
            self.status_indicator.config(text="● ACTIVITY RUNNING", fg='#f59e0b')
            self.start_button.config(text="STOP ACTIVITY (F6)", bg='#f59e0b')
            # Start the autoclicker
            threading.Thread(target=self.auto_clicker, daemon=True).start()
            # Start session timer
            self.session_start_time = time.time()
            threading.Thread(target=self.update_session_stats, daemon=True).start()
        else:
            self.status_indicator.config(text="● READY", fg='#4ade80')
            self.start_button.config(text="START ACTIVITY (F6)", bg='#4ade80')

    def emergency_stop(self):
        """Immediately stop the auto clicker"""
        self.running = False
        self.status_indicator.config(text="● STOPPED", fg='#ef4444')
        self.start_button.config(text="START ACTIVITY (F6)", bg='#4ade80')
        messagebox.showinfo("Activity Stopped", "Classroom activity has been stopped!")

    def listen_hotkeys(self):
        """Listen for hotkeys in a background thread"""
        keyboard.add_hotkey('F6', self.toggle_running)
        keyboard.add_hotkey('F7', self.emergency_stop)
        
        while True:
            time.sleep(1)

    def auto_clicker(self):
        """Main auto clicker loop with human-like behavior"""
        self.action_count = 0
        
        while self.running:
            mode = self.mode.get()
            
            # Add human-like randomness to timing
            interval = self.click_interval.get()
            if self.human_like.get():
                interval = max(0.05, interval + random.uniform(-0.03, 0.03))
            
            # Add jitter to mouse position if enabled
            if self.jitter_enabled.get() and mode in ["click", "right_click"]:
                current_x, current_y = pyautogui.position()
                jitter_x = random.uniform(-self.jitter_amount.get(), self.jitter_amount.get())
                jitter_y = random.uniform(-self.jitter_amount.get(), self.jitter_amount.get())
                pyautogui.moveTo(current_x + jitter_x, current_y + jitter_y)
            
            # Perform the action
            if mode == "click":
                pyautogui.click()
            elif mode == "right_click":
                pyautogui.rightClick()
            elif mode == "space":
                pyautogui.press("space")
            elif mode == "custom" and self.custom_key is not None:
                pyautogui.press(self.custom_key)
            
            self.action_count += 1
            
            # Sleep for the interval
            time.sleep(interval)

    def update_session_stats(self):
        """Update session statistics"""
        start_time = self.session_start_time
        while self.running:
            elapsed = int(time.time() - start_time)
            self.session_time_label.config(text=f"Session time: {elapsed}s")
            self.clicks_label.config(text=f"Actions performed: {self.action_count}")
            time.sleep(1)

    def load_config(self):
        """Load configuration from file"""
        try:
            config_path = os.path.join(os.path.expanduser("~"), "autoclicker_config.json")
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    self.click_interval.set(config.get('click_interval', 0.1))
                    self.jitter_enabled.set(config.get('jitter_enabled', True))
                    self.jitter_amount.set(config.get('jitter_amount', 0.5))
                    self.human_like.set(config.get('human_like', True))
                    self.custom_key = config.get('custom_key', None)
        except:
            pass

    def save_config(self):
        """Save configuration to file"""
        config = {
            'click_interval': self.click_interval.get(),
            'jitter_enabled': self.jitter_enabled.get(),
            'jitter_amount': self.jitter_amount.get(),
            'human_like': self.human_like.get(),
            'custom_key': self.custom_key
        }
        
        config_path = os.path.join(os.path.expanduser("~"), "autoclicker_config.json")
        with open(config_path, 'w') as f:
            json.dump(config, f)

    def on_closing(self):
        """Handle application closing"""
        self.running = False
        self.save_config()
        self.root.destroy()

def main():
    # Check if required modules are installed
    try:
        import pyautogui
        import keyboard
    except ImportError:
        print("Required modules not installed!")
        print("Please run: pip install pyautogui keyboard")
        return
    
    root = tk.Tk()
    app = ModernAutoClicker(root)
    
    # Handle window closing
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    root.mainloop()

if __name__ == "__main__":
    main()
