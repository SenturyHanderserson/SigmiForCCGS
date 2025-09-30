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
        
        # Set window title (hidden)
        self.root.title("Minecraft: Education Edition - Classroom Tools")
        self.root.withdraw()  # Hide the window
        
        # Start web server
        self.start_web_server()
        
        # Open web interface
        webbrowser.open(f"http://localhost:{self.web_port}")
        
        # Setup hotkeys
        self.setup_hotkeys()
        
        # Statistics
        self.action_count = 0
        self.session_start_time = 0
        
        print("Auto Clicker Pro - Purple Glassmorphism Edition")
        print("=" * 50)

    def start_web_server(self):
        """Start a simple HTTP server to serve the HTML interface"""
        try:
            # Check if we're already in the autoclicker directory
            current_dir = os.getcwd()
            if not current_dir.endswith('autoclicker'):
                # Try to change to autoclicker directory if it exists
                if os.path.exists('autoclicker'):
                    os.chdir('autoclicker')
                else:
                    print("AutoClicker directory not found. Starting in current directory.")
            
            # Create a custom handler to serve our files
            class AutoClickerHandler(http.server.SimpleHTTPRequestHandler):
                def do_POST(self):
                    if self.path == '/command':
                        content_length = int(self.headers['Content-Length'])
                        post_data = self.rfile.read(content_length)
                        try:
                            data = json.loads(post_data.decode())
                            # Handle the command (you can add command processing here)
                            print(f"Received command: {data}")
                            
                            self.send_response(200)
                            self.send_header('Content-type', 'application/json')
                            self.end_headers()
                            self.wfile.write(json.dumps({"status": "success"}).encode())
                        except Exception as e:
                            self.send_response(500)
                            self.end_headers()
                    else:
                        super().do_POST()
            
            # Start server in a separate thread
            self.web_server = socketserver.TCPServer(("", self.web_port), AutoClickerHandler)
            self.web_thread = threading.Thread(target=self.web_server.serve_forever)
            self.web_thread.daemon = True
            self.web_thread.start()
            print(f"✅ Web interface: http://localhost:{self.web_port}")
            print("✅ Purple glassmorphism UI is ready!")
            
        except Exception as e:
            print(f"❌ Failed to start web server: {e}")
            print("💡 Running in basic mode without web interface")

    def setup_hotkeys(self):
        """Setup global hotkeys"""
        try:
            keyboard.add_hotkey('f6', self.toggle_running)
            keyboard.add_hotkey('f7', self.emergency_stop)
            print("✅ Hotkeys registered: F6 (Start/Stop), F7 (Emergency Stop)")
        except Exception as e:
            print(f"❌ Failed to setup hotkeys: {e}")

    def toggle_running(self):
        """Toggle the running state"""
        self.running = not self.running
        
        if self.running:
            print("🚀 AUTO CLICKER STARTED - Clicking at lightning speed!")
            self.session_start_time = time.time()
            self.action_count = 0
            threading.Thread(target=self.auto_clicker, daemon=True).start()
            threading.Thread(target=self.update_web_interface, daemon=True).start()
        else:
            print("🛑 AUTO CLICKER STOPPED")

    def emergency_stop(self):
        """Immediately stop the auto clicker"""
        if self.running:
            self.running = False
            print("🚨 EMERGENCY STOP - Auto clicker disabled immediately!")

    def auto_clicker(self):
        """Main auto clicker loop with human-like behavior - SUPER FAST"""
        click_count = 0
        last_update = time.time()
        
        while self.running:
            try:
                # Add human-like randomness to timing
                interval = self.click_interval
                if self.human_like:
                    interval = max(0.01, interval + random.uniform(-0.005, 0.005))  # Very fast variations
                
                # Add jitter to mouse position if enabled
                if self.jitter_enabled and self.mode in ["click", "right_click"]:
                    current_x, current_y = pyautogui.position()
                    jitter_x = random.uniform(-self.jitter_amount, self.jitter_amount)
                    jitter_y = random.uniform(-self.jitter_amount, self.jitter_amount)
                    pyautogui.moveTo(current_x + jitter_x, current_y + jitter_y)
                
                # Perform the action - ULTRA FAST
                if self.mode == "click":
                    pyautogui.click()
                elif self.mode == "right_click":
                    pyautogui.rightClick()
                elif self.mode == "space":
                    pyautogui.press("space")
                elif self.mode == "custom" and self.custom_key is not None:
                    pyautogui.press(self.custom_key)
                
                self.action_count += 1
                click_count += 1
                
                # Update console every 100 clicks
                if time.time() - last_update > 1.0:  # Update every second
                    cps = click_count / (time.time() - last_update)
                    print(f"⚡ Clicking... {self.action_count} total clicks | {cps:.1f} CPS")
                    click_count = 0
                    last_update = time.time()
                
                # Sleep for the interval (VERY FAST)
                time.sleep(interval)
                
            except Exception as e:
                print(f"❌ Error in auto clicker: {e}")
                break

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
                with open("status.json", "w") as f:
                    json.dump(status_data, f)
                    
            except Exception as e:
                print(f"⚠️ Error updating web interface: {e}")
            
            time.sleep(0.1)  # Update very frequently for real-time feel

    def on_closing(self):
        """Handle application closing"""
        print("\n🛑 Shutting down Auto Clicker...")
        self.running = False
        if self.web_server:
            self.web_server.shutdown()
            print("✅ Web server stopped")
        self.root.destroy()
        print("✅ Auto Clicker closed successfully")

def main():
    # Check if required modules are installed
    try:
        import pyautogui
        import keyboard
    except ImportError:
        print("❌ Required modules not installed!")
        print("💡 Please run: pip install pyautogui keyboard")
        input("Press Enter to exit...")
        return
    
    # Create tkinter root
    root = tk.Tk()
    
    try:
        app = ModernAutoClicker(root)
        
        # Handle window closing
        root.protocol("WM_DELETE_WINDOW", app.on_closing)
        
        print("\n" + "="*50)
        print("🎮 CONTROLS:")
        print("   F6 - Start/Stop Auto Clicker")
        print("   F7 - Emergency Stop")
        print("   Web Interface - http://localhost:8080")
        print("="*50)
        print("💡 The web interface features:")
        print("   • Purple glassmorphism design")
        print("   • Real-time status updates") 
        print("   • Ultra-fast clicking (0.01s - 1.0s)")
        print("   • Human-like behavior options")
        print("   • Live click counter & session timer")
        print("="*50)
        print("⏳ Auto Clicker is running in the background...")
        print("   Press Ctrl+C in this window to exit")
        print("="*50 + "\n")
        
        # Keep the application running
        root.mainloop()
        
    except KeyboardInterrupt:
        print("\n🛑 Received interrupt signal...")
        if 'app' in locals():
            app.on_closing()
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
