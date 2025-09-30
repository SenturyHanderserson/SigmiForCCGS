import tkinter as tk
from tkinter import ttk, messagebox
import threading
import pyautogui
import keyboard
import time
import random
import os
import json
import http.server
import socketserver
import webbrowser
import socket

class ModernAutoClicker:
    def __init__(self, root):
        self.root = root
        self.running = False
        self.mode = "click"
        self.custom_key = None
        self.click_interval = 0.05  # Faster default
        self.jitter_enabled = True
        self.jitter_amount = 0.5
        self.human_like = True
        
        # Web server for HTML interface
        self.web_port = 8080
        self.web_thread = None
        self.web_server = None
        
        # Set window title
        self.root.title("Minecraft: Education Edition - Classroom Tools")
        self.root.geometry("400x200")
        self.root.configure(bg='#1a1a2e')
        
        # Start web server
        self.start_web_server()
        
        # Open web interface
        webbrowser.open(f"http://localhost:{self.web_port}")
        
        # Setup hotkeys
        self.setup_hotkeys()
        
        # Statistics
        self.action_count = 0
        self.session_start_time = 0

    def start_web_server(self):
        """Start a simple HTTP server to serve the HTML interface"""
        try:
            # Create a simple HTTP handler
            handler = http.server.SimpleHTTPRequestHandler
            
            # Change to the autoclicker directory
            os.chdir("autoclicker")
            
            # Start server in a separate thread
            self.web_server = socketserver.TCPServer(("", self.web_port), handler)
            self.web_thread = threading.Thread(target=self.web_server.serve_forever)
            self.web_thread.daemon = True
            self.web_thread.start()
            print(f"Web interface available at http://localhost:{self.web_port}")
        except Exception as e:
            print(f"Failed to start web server: {e}")

    def setup_hotkeys(self):
        """Setup global hotkeys"""
        keyboard.add_hotkey('f6', self.toggle_running)
        keyboard.add_hotkey('f7', self.emergency_stop)

    def toggle_running(self):
        """Toggle the running state"""
        self.running = not self.running
        
        if self.running:
            print("Auto clicker STARTED")
            self.session_start_time = time.time()
            threading.Thread(target=self.auto_clicker, daemon=True).start()
            threading.Thread(target=self.update_web_interface, daemon=True).start()
        else:
            print("Auto clicker STOPPED")

    def emergency_stop(self):
        """Immediately stop the auto clicker"""
        self.running = False
        print("EMERGENCY STOP - Auto clicker disabled")

    def auto_clicker(self):
        """Main auto clicker loop with human-like behavior"""
        self.action_count = 0
        
        while self.running:
            # Add human-like randomness to timing
            interval = self.click_interval
            if self.human_like:
                interval = max(0.02, interval + random.uniform(-0.01, 0.01))  # Faster variations
            
            # Add jitter to mouse position if enabled
            if self.jitter_enabled and self.mode in ["click", "right_click"]:
                current_x, current_y = pyautogui.position()
                jitter_x = random.uniform(-self.jitter_amount, self.jitter_amount)
                jitter_y = random.uniform(-self.jitter_amount, self.jitter_amount)
                pyautogui.moveTo(current_x + jitter_x, current_y + jitter_y)
            
            # Perform the action
            if self.mode == "click":
                pyautogui.click()
            elif self.mode == "right_click":
                pyautogui.rightClick()
            elif self.mode == "space":
                pyautogui.press("space")
            elif self.mode == "custom" and self.custom_key is not None:
                pyautogui.press(self.custom_key)
            
            self.action_count += 1
            
            # Sleep for the interval (much faster now)
            time.sleep(interval)

    def update_web_interface(self):
        """Update status file for web interface"""
        while self.running:
            try:
                status_data = {
                    "running": self.running,
                    "mode": self.mode,
                    "interval": self.click_interval,
                    "actions": self.action_count,
                    "session_time": int(time.time() - self.session_start_time) if self.running else 0,
                    "jitter_enabled": self.jitter_enabled,
                    "human_like": self.human_like
                }
                
                # Write status to a file that the HTML can read
                with open("autoclicker/status.json", "w") as f:
                    json.dump(status_data, f)
                    
            except Exception as e:
                print(f"Error updating web interface: {e}")
            
            time.sleep(0.5)

    def handle_web_command(self, command, data):
        """Handle commands from the web interface"""
        if command == "start_stop":
            self.toggle_running()
        elif command == "set_mode":
            self.mode = data.get("mode", "click")
        elif command == "set_interval":
            self.click_interval = max(0.01, float(data.get("interval", 0.05)))
        elif command == "set_jitter":
            self.jitter_enabled = bool(data.get("enabled", True))
        elif command == "set_human_like":
            self.human_like = bool(data.get("enabled", True))
        elif command == "set_custom_key":
            self.custom_key = data.get("key")

    def on_closing(self):
        """Handle application closing"""
        self.running = False
        if self.web_server:
            self.web_server.shutdown()
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
    
    # Create minimal tkinter window (hidden)
    root = tk.Tk()
    root.withdraw()  # Hide the tkinter window
    
    app = ModernAutoClicker(root)
    
    # Handle window closing
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    print("Auto Clicker is running in the background!")
    print("Web interface: http://localhost:8080")
    print("Hotkeys: F6 to start/stop, F7 for emergency stop")
    print("Press Ctrl+C in terminal to exit")
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        app.on_closing()

if __name__ == "__main__":
    main()
