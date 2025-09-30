import threading
import pyautogui
import keyboard
import time
import random
import json
import http.server
import socketserver
from http.server import BaseHTTPRequestHandler
import signal
import sys

class AutoClickerBackend:
    def __init__(self):
        self.running = False
        self.mode = "click"
        self.custom_key = None
        self.click_interval = 0.05
        self.jitter_enabled = True
        self.jitter_amount = 0.5
        self.human_like = True
        
        # Web server for API
        self.web_port = 8080
        self.web_thread = None
        self.web_server = None
        
        # Statistics
        self.action_count = 0
        self.session_start_time = 0
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        print("🎮 Auto Clicker Pro - Backend Server")
        print("=" * 50)
        print("🌐 Web Interface: https://senturyhanderserson.github.io/SigmiForCCGS/content/autoclickerinterface.html")
        print("🔗 API Server: http://localhost:8080")
        print("🎮 Hotkeys: F6 (Start/Stop), F7 (Emergency Stop)")
        print("=" * 50)

    def start_web_server(self):
        """Start a simple HTTP server to serve the status API"""
        try:
            class AutoClickerHandler(BaseHTTPRequestHandler):
                def __init__(self, *args, **kwargs):
                    self.app = None
                    super().__init__(*args, **kwargs)
                
                def do_OPTIONS(self):
                    # Handle preflight requests
                    self.send_response(200)
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
                    self.send_header('Access-Control-Allow-Headers', 'Content-Type, Accept, Origin')
                    self.send_header('Access-Control-Max-Age', '86400')
                    self.end_headers()
                
                def do_GET(self):
                    if self.path == '/status.json':
                        # Serve status JSON
                        try:
                            status_data = {
                                "running": self.app.running,
                                "mode": self.app.mode,
                                "interval": self.app.click_interval,
                                "actions": self.app.action_count,
                                "session_time": int(time.time() - self.app.session_start_time) if self.app.running else 0,
                                "jitter_enabled": self.app.jitter_enabled,
                                "human_like": self.app.human_like
                            }
                            
                            self.send_response(200)
                            self.send_header('Content-type', 'application/json')
                            self.send_header('Access-Control-Allow-Origin', '*')
                            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
                            self.send_header('Pragma', 'no-cache')
                            self.send_header('Expires', '0')
                            self.end_headers()
                            self.wfile.write(json.dumps(status_data).encode('utf-8'))
                        except Exception as e:
                            print(f"❌ Error serving status: {e}")
                            self.send_error(500, "Internal Server Error")
                    else:
                        self.send_response(404)
                        self.end_headers()
                
                def do_POST(self):
                    if self.path == '/command':
                        try:
                            content_length = int(self.headers.get('Content-Length', 0))
                            if content_length == 0:
                                self.send_error(400, "No data received")
                                return
                                
                            post_data = self.rfile.read(content_length)
                            data = json.loads(post_data.decode('utf-8'))
                            print(f"🔧 Received command: {data}")
                            
                            # Handle different commands
                            command = data.get('command')
                            if command == 'start_stop':
                                self.app.toggle_running()
                            elif command == 'set_mode':
                                self.app.mode = data.get('mode', 'click')
                                print(f"📝 Mode set to: {self.app.mode}")
                            elif command == 'set_interval':
                                interval = data.get('interval')
                                if interval is not None:
                                    self.app.click_interval = max(0.01, float(interval))
                                    print(f"⚡ Interval set to: {self.app.click_interval:.2f}s")
                            elif command == 'set_jitter':
                                self.app.jitter_enabled = bool(data.get('enabled', True))
                                print(f"🎯 Jitter {'enabled' if self.app.jitter_enabled else 'disabled'}")
                            elif command == 'set_human_like':
                                self.app.human_like = bool(data.get('enabled', True))
                                print(f"🤖 Human-like behavior {'enabled' if self.app.human_like else 'disabled'}")
                            elif command == 'set_custom_key':
                                self.app.custom_key = data.get('key')
                                self.app.mode = "custom"
                                print(f"🔑 Custom key set to: {self.app.custom_key}")
                            
                            self.send_response(200)
                            self.send_header('Content-type', 'application/json')
                            self.send_header('Access-Control-Allow-Origin', '*')
                            self.end_headers()
                            response_data = json.dumps({"status": "success", "command": command})
                            self.wfile.write(response_data.encode('utf-8'))
                            
                        except json.JSONDecodeError as e:
                            print(f"❌ JSON decode error: {e}")
                            self.send_error(400, "Invalid JSON")
                        except Exception as e:
                            print(f"❌ Error handling command: {e}")
                            self.send_error(500, "Internal Server Error")
                    else:
                        self.send_response(404)
                        self.end_headers()
                
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
            self.web_server.allow_reuse_address = True
            self.web_thread = threading.Thread(target=self.web_server.serve_forever)
            self.web_thread.daemon = True
            self.web_thread.start()
            print(f"✅ Web server started on port {self.web_port}")
            print("📡 Waiting for web interface connections...")
            
        except Exception as e:
            print(f"❌ Failed to start web server: {e}")
            print("💡 Please make sure port 8080 is available")
            return False
        return True

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
            # Start auto clicker in a separate thread
            self.clicker_thread = threading.Thread(target=self.auto_clicker, daemon=True)
            self.clicker_thread.start()
        else:
            print("🛑 AUTO CLICKER STOPPED")

    def emergency_stop(self):
        """Immediately stop the auto clicker"""
        if self.running:
            self.running = False
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

    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\n🛑 Received shutdown signal ({signum})...")
        self.shutdown()

    def shutdown(self):
        """Clean shutdown"""
        print("🛑 Shutting down Auto Clicker...")
        self.running = False
        if self.web_server:
            self.web_server.shutdown()
            self.web_server.server_close()
            print("✅ Web server stopped")
        print("✅ Auto Clicker closed successfully")
        sys.exit(0)

    def run(self):
        """Main application loop"""
        if not self.start_web_server():
            return
        
        self.setup_hotkeys()
        
        print("\n" + "="*50)
        print("✅ Backend server is running!")
        print("💡 Press Ctrl+C to stop the application")
        print("="*50 + "\n")
        
        try:
            # Keep the main thread alive
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.shutdown()

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
    
    # Create and run the backend
    backend = AutoClickerBackend()
    backend.run()

if __name__ == "__main__":
    main()
