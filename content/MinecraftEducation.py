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
        
        print("🎮 Auto Clicker Pro - Web Edition")
        print("=" * 50)
        print("🌐 Web Interface: https://senturyhanderserson.github.io/SigmiForCCGS/content/autoclickerinterface.html")
        print("🔗 Local Interface: http://localhost:8080")
        print("=" * 50)

    def setup_gui(self):
        """Setup the main GUI with embedded browser"""
        self.root.title("Auto Clicker Pro - Backend Server")
        self.root.geometry("1000x700")
        self.root.configure(bg='#1a1a2e')
        
        # Create main frame
        main_frame = tk.Frame(self.root, bg='#1a1a2e')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        header_frame = tk.Frame(main_frame, bg='#16213e', height=80)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame, 
            text="Auto Clicker Pro - Backend Server", 
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
        
        # Info panel
        info_frame = tk.Frame(main_frame, bg='#2d3748', height=100)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        info_frame.pack_propagate(False)
        
        info_text = tk.Text(
            info_frame,
            bg='#2d3748',
            fg='white',
            font=('Arial', 10),
            wrap=tk.WORD,
            height=4
        )
        info_text.pack(fill=tk.BOTH, padx=10, pady=10)
        info_text.insert(tk.END, "🚀 Auto Clicker Pro is running!\n\n")
        info_text.insert(tk.END, "🌐 Web Interface: https://senturyhanderserson.github.io/SigmiForCCGS/content/autoclickerinterface.html\n")
        info_text.insert(tk.END, "🔗 Local URL: http://localhost:8080\n")
        info_text.insert(tk.END, "🎮 Hotkeys: F6 (Start/Stop), F7 (Emergency Stop)\n\n")
        info_text.insert(tk.END, "💡 The web interface will automatically connect to this backend.")
        info_text.config(state=tk.DISABLED)
        
        # Create embedded browser frame
        browser_frame = tk.Frame(main_frame, bg='#2d3748')
        browser_frame.pack(fill=tk.BOTH, expand=True)
        
        try:
            # Try to use tkinterweb for embedded browser
            self.browser = HtmlFrame(browser_frame)
            self.browser.pack(fill=tk.BOTH, expand=True)
            # Load the web interface
            self.root.after(1000, self.load_web_interface)
        except Exception as e:
            print(f"❌ Could not load embedded browser: {e}")
            print("💡 The web interface is available at the URL above")
            
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
            status_text.insert(tk.END, "✅ Backend Server Running\n\n")
            status_text.insert(tk.END, "Open your web browser and visit:\n")
            status_text.insert(tk.END, "https://senturyhanderserson.github.io/SigmiForCCGS/content/autoclickerinterface.html\n\n")
            status_text.insert(tk.END, "The web interface will automatically detect this backend.\n\n")
            status_text.insert(tk.END, "Status: READY - Waiting for web interface connection...")
            status_text.config(state=tk.DISABLED)
            self.status_text = status_text

    def load_web_interface(self):
        """Load the web interface into the embedded browser"""
        try:
            # Load the GitHub Pages interface
            self.browser.load_url("https://senturyhanderserson.github.io/SigmiForCCGS/content/autoclickerinterface.html")
            print("✅ Web interface loaded in embedded browser")
        except Exception as e:
            print(f"❌ Could not load web interface: {e}")
            # Fallback to local server
            try:
                self.browser.load_url(f"http://localhost:{self.web_port}/")
            except:
                print("💡 Please visit the web interface manually using the URL above")

    def start_web_server(self):
        """Start a simple HTTP server to serve the status API"""
        try:
            # Create a custom handler for API endpoints
            class AutoClickerHandler(http.server.SimpleHTTPRequestHandler):
                def __init__(self, *args, **kwargs):
                    self.app = None
                    super().__init__(*args, **kwargs)
                
                def do_GET(self):
                    if self.path == '/status.json':
                        # Serve status JSON
                        try:
                            status_data = {
                                "running": self.app.running if self.app else False,
                                "mode": self.app.mode if self.app else "click",
                                "interval": self.app.click_interval if self.app else 0.05,
                                "actions": self.app.action_count if self.app else 0,
                                "session_time": int(time.time() - self.app.session_start_time) if self.app and self.app.running else 0,
                                "jitter_enabled": self.app.jitter_enabled if self.app else True,
                                "human_like": self.app.human_like if self.app else True
                            }
                            
                            self.send_response(200)
                            self.send_header('Content-type', 'application/json')
                            self.send_header('Access-Control-Allow-Origin', '*')
                            self.end_headers()
                            self.wfile.write(json.dumps(status_data).encode())
                        except Exception as e:
                            self.send_response(500)
                            self.end_headers()
                    else:
                        # Serve other files normally
                        super().do_GET()
                
                def do_POST(self):
                    if self.path == '/command':
                        content_length = int(self.headers['Content-Length'])
                        post_data = self.rfile.read(content_length)
                        try:
                            data = json.loads(post_data.decode())
                            print(f"🔧 Received command: {data}")
                            
                            # Handle different commands
                            if hasattr(self, 'app') and self.app:
                                if data.get('command') == 'start_stop':
                                    self.app.toggle_running()
                                elif data.get('command') == 'set_mode':
                                    self.app.mode = data.get('mode', 'click')
                                    print(f"📝 Mode set to: {self.app.mode}")
                                elif data.get('command') == 'set_interval':
                                    interval = data.get('interval')
                                    if interval is not None:
                                        self.app.click_interval = max(0.01, float(interval))
                                        print(f"⚡ Interval set to: {self.app.click_interval:.2f}s")
                                elif data.get('command') == 'set_jitter':
                                    self.app.jitter_enabled = bool(data.get('enabled', True))
                                    print(f"🎯 Jitter {'enabled' if self.app.jitter_enabled else 'disabled'}")
                                elif data.get('command') == 'set_human_like':
                                    self.app.human_like = bool(data.get('enabled', True))
                                    print(f"🤖 Human-like behavior {'enabled' if self.app.human_like else 'disabled'}")
                                elif data.get('command') == 'set_custom_key':
                                    self.app.custom_key = data.get('key')
                                    self.app.mode = "custom"
                                    print(f"🔑 Custom key set to: {self.app.custom_key}")
                            
                            self.send_response(200)
                            self.send_header('Content-type', 'application/json')
                            self.send_header('Access-Control-Allow-Origin', '*')
                            self.end_headers()
                            self.wfile.write(json.dumps({"status": "success"}).encode())
                        except Exception as e:
                            print(f"❌ Error handling command: {e}")
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
            print("📡 Waiting for web interface connections...")
            
        except Exception as e:
            print(f"❌ Failed to start web server: {e}")
            print("💡 Please make sure port 8080 is available")

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
        """Main auto clicker loop with human-like behavior"""
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
        print("🌐 WEB INTERFACE:")
        print("   https://senturyhanderserson.github.io/SigmiForCCGS/content/autoclickerinterface.html")
        print("="*50)
        print("💡 The web interface will automatically connect to this backend")
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
