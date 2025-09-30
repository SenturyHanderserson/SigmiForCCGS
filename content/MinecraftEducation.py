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
import os

class AutoClickerBackend:
    def __init__(self):
        self.running = False
        self.mode = "click"
        self.custom_key = None
        self.click_interval = 0.05
        self.jitter_enabled = True
        self.jitter_amount = 2
        self.human_like = True
        
        # Web server for API
        self.web_port = 8080
        self.web_thread = None
        self.web_server = None
        
        # Statistics
        self.action_count = 0
        self.session_start_time = 0
        
        # Thread control
        self.clicker_thread = None
        self.stop_clicker = threading.Event()
        
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
                    super().__init__(*args, **kwargs)
                
                def do_OPTIONS(self):
                    """Handle preflight CORS requests"""
                    self.send_response(200)
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
                    self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, Accept, Origin')
                    self.send_header('Access-Control-Max-Age', '86400')
                    self.end_headers()
                
                def _set_cors_headers(self):
                    """Set CORS headers for all responses"""
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
                    self.send_header('Access-Control-Allow-Headers', 'Content-Type, Accept, Origin')
                
                def do_GET(self):
                    """Handle GET requests"""
                    try:
                        if self.path == '/status.json' or self.path == '/status':
                            # Serve status JSON
                            status_data = {
                                "running": self.server.backend_app.running,
                                "mode": self.server.backend_app.mode,
                                "interval": self.server.backend_app.click_interval,
                                "actions": self.server.backend_app.action_count,
                                "session_time": int(time.time() - self.server.backend_app.session_start_time) if self.server.backend_app.running else 0,
                                "jitter_enabled": self.server.backend_app.jitter_enabled,
                                "human_like": self.server.backend_app.human_like
                            }
                            
                            self.send_response(200)
                            self.send_header('Content-type', 'application/json')
                            self._set_cors_headers()
                            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
                            self.send_header('Pragma', 'no-cache')
                            self.send_header('Expires', '0')
                            self.end_headers()
                            self.wfile.write(json.dumps(status_data).encode('utf-8'))
                            
                        elif self.path == '/shutdown':
                            # Emergency shutdown endpoint
                            self.server.backend_app.emergency_shutdown()
                            self.send_response(200)
                            self.send_header('Content-type', 'application/json')
                            self._set_cors_headers()
                            self.end_headers()
                            self.wfile.write(json.dumps({"status": "shutting_down"}).encode('utf-8'))
                            
                        else:
                            self.send_response(404)
                            self._set_cors_headers()
                            self.end_headers()
                            
                    except Exception as e:
                        print(f"❌ Error in GET handler: {e}")
                        self.send_response(500)
                        self._set_cors_headers()
                        self.end_headers()
                        self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
                
                def do_POST(self):
                    """Handle POST requests"""
                    try:
                        if self.path == '/command':
                            content_length = int(self.headers.get('Content-Length', 0))
                            if content_length == 0:
                                self.send_error(400, "No data received")
                                return
                                
                            post_data = self.rfile.read(content_length)
                            data = json.loads(post_data.decode('utf-8'))
                            print(f"🔧 Received command: {data}")
                            
                            # Handle different commands
                            command = data.get('command')
                            response_data = {"status": "success", "command": command}
                            
                            if command == 'start_stop':
                                self.server.backend_app.toggle_running()
                            elif command == 'set_mode':
                                mode = data.get('mode', 'click')
                                self.server.backend_app.mode = mode
                                print(f"📝 Mode set to: {mode}")
                            elif command == 'set_interval':
                                interval = data.get('interval')
                                if interval is not None:
                                    self.server.backend_app.click_interval = max(0.01, float(interval))
                                    print(f"⚡ Interval set to: {self.server.backend_app.click_interval:.2f}s")
                            elif command == 'set_jitter':
                                enabled = bool(data.get('enabled', True))
                                self.server.backend_app.jitter_enabled = enabled
                                print(f"🎯 Jitter {'enabled' if enabled else 'disabled'}")
                            elif command == 'set_human_like':
                                enabled = bool(data.get('enabled', True))
                                self.server.backend_app.human_like = enabled
                                print(f"🤖 Human-like behavior {'enabled' if enabled else 'disabled'}")
                            elif command == 'set_custom_key':
                                custom_key = data.get('key')
                                self.server.backend_app.custom_key = custom_key
                                self.server.backend_app.mode = "custom"
                                print(f"🔑 Custom key set to: {custom_key}")
                            elif command == 'panic_stop':
                                self.server.backend_app.panic_stop()
                            elif command == 'restart_backend':
                                self.server.backend_app.restart_backend()
                            else:
                                response_data = {"status": "error", "message": "Unknown command"}
                            
                            self.send_response(200)
                            self.send_header('Content-type', 'application/json')
                            self._set_cors_headers()
                            self.end_headers()
                            self.wfile.write(json.dumps(response_data).encode('utf-8'))
                            
                        else:
                            self.send_response(404)
                            self._set_cors_headers()
                            self.end_headers()
                            
                    except json.JSONDecodeError as e:
                        print(f"❌ JSON decode error: {e}")
                        self.send_response(400)
                        self._set_cors_headers()
                        self.end_headers()
                        self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode('utf-8'))
                    except Exception as e:
                        print(f"❌ Error in POST handler: {e}")
                        self.send_response(500)
                        self._set_cors_headers()
                        self.end_headers()
                        self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
                
                def log_message(self, format, *args):
                    # Suppress normal HTTP logging
                    pass
            
            # Create custom server class that stores backend reference
            class BackendServer(socketserver.TCPServer):
                def __init__(self, server_address, handler_class, backend_app):
                    self.backend_app = backend_app
                    self.allow_reuse_address = True
                    super().__init__(server_address, handler_class)
            
            # Start server in a separate thread
            self.web_server = BackendServer(("", self.web_port), AutoClickerHandler, self)
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
            keyboard.add_hotkey('f7', self.panic_stop)
            print("✅ Hotkeys registered: F6 (Start/Stop), F7 (Emergency Stop)")
        except Exception as e:
            print(f"❌ Failed to setup hotkeys: {e}")

    def toggle_running(self):
        """Toggle the running state"""
        if self.running:
            # Stop running
            self.running = False
            self.stop_clicker.set()
            print("🛑 AUTO CLICKER STOPPED")
        else:
            # Start running
            self.running = True
            self.stop_clicker.clear()
            self.session_start_time = time.time()
            self.action_count = 0
            # Start auto clicker in a separate thread
            self.clicker_thread = threading.Thread(target=self.auto_clicker, daemon=True)
            self.clicker_thread.start()
            print("🚀 AUTO CLICKER STARTED - Clicking at lightning speed!")

    def panic_stop(self):
        """Immediately stop everything"""
        if self.running:
            self.running = False
            self.stop_clicker.set()
            print("🚨 EMERGENCY STOP - Auto clicker disabled immediately!")

    def emergency_shutdown(self):
        """Complete emergency shutdown"""
        print("🛑 Emergency shutdown initiated...")
        self.shutdown()

    def restart_backend(self):
        """Restart the backend service"""
        print("🔄 Restarting backend service...")
        self.running = False
        self.stop_clicker.set()
        time.sleep(0.5)
        print("✅ Backend service restarted")

    def perform_action(self):
        """Perform a single click/keypress action"""
        try:
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
            return True
            
        except Exception as e:
            print(f"❌ Error performing action: {e}")
            return False

    def auto_clicker(self):
        """Main auto clicker loop with human-like behavior"""
        click_count = 0
        last_update = time.time()
        last_action_time = time.time()
        
        print(f"🎯 Starting auto-clicker with mode: {self.mode}, interval: {self.click_interval:.2f}s")
        
        while self.running and not self.stop_clicker.is_set():
            try:
                current_time = time.time()
                
                # Check if it's time for the next action
                if current_time - last_action_time >= self.click_interval:
                    # Add human-like randomness to timing
                    interval = self.click_interval
                    if self.human_like:
                        interval = max(0.01, interval * random.uniform(0.8, 1.2))
                    
                    # Perform the action
                    if self.perform_action():
                        click_count += 1
                        last_action_time = current_time
                    
                    # Small delay to prevent CPU overload
                    time.sleep(0.001)
                
                # Update console every second
                if current_time - last_update > 1.0:
                    cps = click_count / (current_time - last_update)
                    if self.running:  # Only print if still running
                        print(f"⚡ Clicking... {self.action_count} total actions | {cps:.1f} APS | Mode: {self.mode}")
                    click_count = 0
                    last_update = current_time
                
                # Small sleep to prevent busy waiting
                time.sleep(0.001)
                
            except Exception as e:
                print(f"❌ Error in auto clicker loop: {e}")
                self.running = False
                break
        
        print("✅ Auto-clicker thread stopped")

    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\n🛑 Received shutdown signal ({signum})...")
        self.shutdown()

    def shutdown(self):
        """Clean shutdown"""
        print("🛑 Shutting down Auto Clicker...")
        self.running = False
        self.stop_clicker.set()
        
        if self.clicker_thread and self.clicker_thread.is_alive():
            self.clicker_thread.join(timeout=2.0)
        
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
