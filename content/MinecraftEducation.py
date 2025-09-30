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
from tkinterweb import HtmlFrame  # This will embed the browser

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
        
        # Set up the main window with embedded browser
        self.setup_gui()
        
        # Start web server
        self.start_web_server()
        
        # Setup hotkeys
        self.setup_hotkeys()
        
        # Statistics
        self.action_count = 0
        self.session_start_time = 0
        
        print("Auto Clicker Pro - Purple Glassmorphism Edition")
        print("=" * 50)

    def setup_gui(self):
        """Setup the main GUI with embedded browser"""
        self.root.title("Minecraft: Education Edition - Classroom Tools")
        self.root.geometry("1200x800")
        self.root.configure(bg='#1a1a2e')
        
        # Create main frame
        main_frame = tk.Frame(self.root, bg='#1a1a2e')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        header_frame = tk.Frame(main_frame, bg='#16213e', height=60)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame, 
            text="Minecraft: Education Edition - Classroom Tools", 
            font=('Arial', 16, 'bold'), 
            bg='#16213e', 
            fg='#4cc9f0'
        )
        title_label.pack(side=tk.LEFT, padx=20, pady=15)
        
        status_label = tk.Label(
            header_frame, 
            text="● READY", 
            font=('Arial', 12, 'bold'), 
            bg='#16213e', 
            fg='#4ade80'
        )
        status_label.pack(side=tk.RIGHT, padx=20, pady=15)
        self.status_label = status_label
        
        # Create embedded browser frame
        browser_frame = tk.Frame(main_frame, bg='#2d3748')
        browser_frame.pack(fill=tk.BOTH, expand=True)
        
        try:
            # Try to use tkinterweb for embedded browser
            self.browser = HtmlFrame(browser_frame)
            self.browser.pack(fill=tk.BOTH, expand=True)
            # Load the HTML interface
            self.root.after(1000, self.load_html_interface)
        except Exception as e:
            print(f"❌ Could not load embedded browser: {e}")
            print("💡 Install tkinterweb: pip install tkinterweb")
            
            # Fallback: Simple status display
            fallback_frame = tk.Frame(browser_frame, bg='#2d3748')
            fallback_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            status_text = tk.Text(
                fallback_frame, 
                bg='#2d3748', 
                fg='white', 
                font=('Arial', 12),
                wrap=tk.WORD
            )
            status_text.pack(fill=tk.BOTH, expand=True)
            status_text.insert(tk.END, "Auto Clicker Pro is running!\n\n")
            status_text.insert(tk.END, "Hotkeys:\n")
            status_text.insert(tk.END, "• F6 - Start/Stop Auto Clicker\n")
            status_text.insert(tk.END, "• F7 - Emergency Stop\n\n")
            status_text.insert(tk.END, "Status: READY\n")
            status_text.config(state=tk.DISABLED)
            self.status_text = status_text

    def load_html_interface(self):
        """Load the HTML interface into the embedded browser"""
        try:
            # First try to load via the web server to ensure all assets load
            self.browser.load_url(f"http://localhost:{self.web_port}/")
            print("✅ HTML interface loaded from web server")
        except Exception as e:
            print(f"❌ Could not load HTML interface: {e}")

    def start_web_server(self):
        """Start a simple HTTP server to serve the HTML interface"""
        try:
            # Create a custom handler to serve our files and handle commands
            class AutoClickerHandler(http.server.SimpleHTTPRequestHandler):
                def __init__(self, *args, **kwargs):
                    self.app = None
                    super().__init__(*args, **kwargs)
                
                def do_GET(self):
                    # Serve files from current directory
                    if self.path == '/':
                        self.path = '/interface.html'
                    
                    # Set proper MIME types for CSS and JS
                    if self.path.endswith('.css'):
                        self.send_header('Content-Type', 'text/css')
                    elif self.path.endswith('.js'):
                        self.send_header('Content-Type', 'application/javascript')
                    
                    # Serve the file
                    try:
                        super().do_GET()
                    except Exception as e:
                        print(f"Error serving {self.path}: {e}")
                
                def do_POST(self):
                    if self.path == '/command':
                        content_length = int(self.headers['Content-Length'])
                        post_data = self.rfile.read(content_length)
                        try:
                            data = json.loads(post_data.decode())
                            print(f"Received command: {data}")
                            
                            # Handle different commands
                            if hasattr(self, 'app') and self.app:
                                if data.get('command') == 'start_stop':
                                    self.app.toggle_running()
                                elif data.get('command') == 'set_mode':
                                    self.app.mode = data.get('mode', 'click')
                                elif data.get('command') == 'set_interval':
                                    interval = data.get('interval')
                                    if interval is not None:
                                        self.app.click_interval = max(0.01, float(interval))
                                elif data.get('command') == 'set_jitter':
                                    self.app.jitter_enabled = bool(data.get('enabled', True))
                                elif data.get('command') == 'set_human_like':
                                    self.app.human_like = bool(data.get('enabled', True))
                            
                            self.send_response(200)
                            self.send_header('Content-type', 'application/json')
                            self.send_header('Access-Control-Allow-Origin', '*')
                            self.end_headers()
                            self.wfile.write(json.dumps({"status": "success"}).encode())
                        except Exception as e:
                            print(f"Error handling command: {e}")
                            self.send_response(500)
                            self.end_headers()
                    else:
                        super().do_POST()
                
                def log_message(self, format, *args):
                    # Suppress normal HTTP logging
                    pass
            
            # Create the server with reference to this app instance
            def handler(*args, **kwargs):
                h = AutoClickerHandler(*args, **kwargs)
                h.app = self
                return h
            
            # Start server in a separate thread
            self.web_server = socketserver.TCPServer(("", self.web_port), handler)
            self.web_thread = threading.Thread(target=self.web_server.serve_forever)
            self.web_thread.daemon = True
            self.web_thread.start()
            print(f"✅ Web server started on port {self.web_port}")
            
        except Exception as e:
            print(f"❌ Failed to start web server: {e}")
            print("💡 Running without web interface")

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
            if hasattr(self, 'status_label'):
                self.status_label.config(text="● RUNNING", fg='#f59e0b')
            self.session_start_time = time.time()
            self.action_count = 0
            threading.Thread(target=self.auto_clicker, daemon=True).start()
            threading.Thread(target=self.update_web_interface, daemon=True).start()
        else:
            print("🛑 AUTO CLICKER STOPPED")
            if hasattr(self, 'status_label'):
                self.status_label.config(text="● READY", fg='#4ade80')

    def emergency_stop(self):
        """Immediately stop the auto clicker"""
        if self.running:
            self.running = False
            if hasattr(self, 'status_label'):
                self.status_label.config(text="● STOPPED", fg='#ef4444')
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
                    interval = max(0.01, interval + random.uniform(-0.005, 0.005))
                
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
                click_count += 1
                
                # Update console every second
                if time.time() - last_update > 1.0:
                    cps = click_count / (time.time() - last_update)
                    print(f"⚡ Clicking... {self.action_count} total clicks | {cps:.1f} CPS")
                    click_count = 0
                    last_update = time.time()
                
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
            
            time.sleep(0.1)

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
    
    # Try to install tkinterweb if not available
    try:
        from tkinterweb import HtmlFrame
    except ImportError:
        print("📦 Installing tkinterweb for embedded browser...")
        try:
            import subprocess
            subprocess.check_call(["pip", "install", "tkinterweb"])
            from tkinterweb import HtmlFrame
            print("✅ tkinterweb installed successfully")
        except Exception as e:
            print(f"❌ Could not install tkinterweb: {e}")
            print("💡 The app will run with basic interface")
    
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
        print("="*50)
        print("💡 Features:")
        print("   • Embedded purple glassmorphism interface")
        print("   • Ultra-fast clicking (0.01s - 1.0s)")
        print("   • Human-like behavior options")
        print("   • Live click counter & session timer")
        print("="*50 + "\n")
        
        # Start the GUI
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
