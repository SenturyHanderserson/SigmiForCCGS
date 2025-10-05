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

        self.web_port = 8080
        self.web_thread = None
        self.web_server = None

        self.action_count = 0
        self.session_start_time = 0
        self.start_time = time.time()

        self.clicker_thread = None
        self.stop_clicker = threading.Event()

        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)


    # - Web Server -
    def start_web_server(self):
        try:
            class AutoClickerHandler(BaseHTTPRequestHandler):
                def _set_cors_headers(self):
                    """Set CORS headers for all responses"""
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
                    self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, Accept, Origin, X-Requested-With')
                    self.send_header('Access-Control-Allow-Credentials', 'true')
                    self.send_header('Access-Control-Max-Age', '86400')

                def do_OPTIONS(self):
                    """Handle preflight CORS requests"""
                    self.send_response(200)
                    self._set_cors_headers()
                    self.end_headers()

                def do_GET(self):
                    """Handle GET requests"""
                    try:
                        self.send_response(200)
                        self.send_header('Content-type', 'application/json')
                        self._set_cors_headers()
                        
                        if self.path.startswith('/status') or self.path.startswith('/status.json'):
                            status_data = self.server.backend_app.get_status()
                            self.end_headers()
                            self.wfile.write(json.dumps(status_data).encode('utf-8'))
                        else:
                            status_data = self.server.backend_app.get_status()
                            self.end_headers()
                            self.wfile.write(json.dumps(status_data).encode('utf-8'))
                            
                    except Exception as e:
                        print(f"❌ Error in GET handler: {e}")
                        self.send_response(500)
                        self.send_header('Content-type', 'application/json')
                        self._set_cors_headers()
                        self.end_headers()
                        error_response = {"status": "error", "message": str(e)}
                        self.wfile.write(json.dumps(error_response).encode('utf-8'))

                def do_POST(self):
                    """Handle POST requests"""
                    try:
                        if self.path == '/command' or self.path.startswith('/command?'):
                            content_length = int(self.headers.get('Content-Length', 0))
                            post_data = b''
                            
                            if content_length > 0:
                                post_data = self.rfile.read(content_length)
                                data = json.loads(post_data.decode('utf-8'))
                            else:
                                data = {}
                                
                            print(f"🔧 Received command: {data}")

                            app = self.server.backend_app
                            cmd = data.get("command")
                            
                            response_data = app.handle_command(cmd, data)
                            
                            self.send_response(200)
                            self.send_header('Content-type', 'application/json')
                            self._set_cors_headers()
                            self.end_headers()
                            self.wfile.write(json.dumps(response_data).encode("utf-8"))
                        else:
                            self.send_response(404)
                            self.send_header('Content-type', 'application/json')
                            self._set_cors_headers()
                            self.end_headers()
                            error_response = {"status": "error", "message": "Endpoint not found"}
                            self.wfile.write(json.dumps(error_response).encode("utf-8"))
                    except Exception as e:
                        print(f"❌ Error in POST handler: {e}")
                        self.send_response(500)
                        self.send_header('Content-type', 'application/json')
                        self._set_cors_headers()
                        error_response = {"status": "error", "message": str(e)}
                        self.end_headers()
                        self.wfile.write(json.dumps(error_response).encode("utf-8"))

                def log_message(self, format, *args):
                    """Silence default request logs"""
                    return

            class BackendServer(socketserver.TCPServer):
                def __init__(self, addr, handler, app):
                    self.backend_app = app
                    self.allow_reuse_address = True
                    super().__init__(addr, handler)

            for attempt in range(3):
                try:
                    self.web_server = BackendServer(("", self.web_port), AutoClickerHandler, self)
                    self.web_thread = threading.Thread(target=self.web_server.serve_forever, daemon=True)
                    self.web_thread.start()
                    return True
                except OSError as e:
                    if "Address already in use" in str(e):
                        print(f"⚠️ Port {self.web_port} in use, trying port {self.web_port + 1}")
                        self.web_port += 1
                    else:
                        raise e
                        
            print(f"❌ Failed to start web server after multiple attempts")
            return False
            
        except Exception as e:
            print(f"❌ Failed to start web server: {e}")
            return False

    # - Command Handler -
    def handle_command(self, command, data):
        """Handle all commands from the web interface"""
        response_data = {"status": "ok"}
        
        try:
            if command == "toggle_running":
                self.toggle_running()
                response_data["message"] = f"Auto-clicker {'started' if self.running else 'stopped'}"
                response_data["running"] = self.running
            elif command == "panic_stop":
                was_running = self.running
                self.panic_stop()
                response_data["message"] = "Emergency stop activated"
                response_data["running"] = self.running
                
            elif command == "set_mode":
                mode = data.get("mode", "click")
                self.set_mode(mode)
                response_data["message"] = f"Mode set to {mode}"
                response_data["mode"] = self.mode
                
            elif command == "set_interval":
                interval = float(data.get("interval", 0.05))
                self.set_interval(interval)
                response_data["message"] = f"Interval set to {interval}s"
                response_data["interval"] = self.click_interval
                
            elif command == "set_jitter":
                enabled = bool(data.get("enabled", True))
                self.set_jitter(enabled)
                response_data["message"] = f"Jitter {'enabled' if enabled else 'disabled'}"
                response_data["jitter_enabled"] = self.jitter_enabled
                
            elif command == "set_human_like":
                enabled = bool(data.get("enabled", True))
                self.set_human_like(enabled)
                response_data["message"] = f"Human-like mode {'enabled' if enabled else 'disabled'}"
                response_data["human_like"] = self.human_like
                
            elif command == "set_custom_key":
                key = data.get("key")
                self.set_custom_key(key)
                response_data["message"] = f"Custom key set to '{key}'"
                response_data["mode"] = self.mode
                
            elif command == "debug_windows_key":
                self.debug_windows_key()
                response_data["message"] = "Windows key pressed"
                
            elif command == "debug_single_click":
                self.debug_single_click()
                response_data["message"] = "Single click performed"
                
            elif command == "restart":
                response_data["message"] = "Restart command received"
                # coming soon ig
                
            elif command == "shutdown":
                response_data["message"] = "Shutdown command received"
                # coming soon ig
                
            else:
                response_data = {"status": "error", "message": f"Unknown command: {command}"}
                print(f"⚠️ Unknown command: {command}")
                
        except Exception as e:
            response_data = {"status": "error", "message": f"Error executing command: {str(e)}"}
            print(f"❌ Error handling command {command}: {e}")
            
        return response_data

    # -Control Functions -
    def set_mode(self, mode):
        """Set the click mode"""
        valid_modes = ["click", "right_click", "space", "custom"]
        if mode in valid_modes:
            self.mode = mode
            self.perform_action()
        else:
            print(f"❌ Invalid mode: {mode}")

    def set_interval(self, interval):
        """Set the click interval - allow much smaller values for higher CPS"""
        self.click_interval = max(0.005, min(2.0, interval))

    def set_jitter(self, enabled):
        """Enable or disable mouse jitter"""
        self.jitter_enabled = enabled

    def set_human_like(self, enabled):
        """Enable or disable human-like timing"""
        self.human_like = enabled

    def set_custom_key(self, key):
        """Set custom key for custom mode"""
        if key:
            self.custom_key = key
            self.mode = "custom"
            self.perform_action()
        else:
            print("❌ No custom key provided")

    def toggle_running(self):
        """Toggle the auto-clicker state (for F6 hotkey and web interface)"""
        if self.running:
            self.stop_auto_clicker()
        else:
            self.start_auto_clicker()

    def start_auto_clicker(self):
        """Start the auto-clicker"""
        if not self.running:
            self.running = True
            self.stop_clicker.clear()
            self.session_start_time = time.time()
            self.action_count = 0
            self.clicker_thread = threading.Thread(target=self.auto_clicker_loop, daemon=True)
            self.clicker_thread.start()

    def stop_auto_clicker(self):
        """Stop the auto-clicker"""
        if self.running:
            self.running = False
            self.stop_clicker.set()
            print("🛑 Auto-clicker stopped")

    def panic_stop(self):
        """Emergency stop"""
        was_running = self.running
        self.running = False
        self.stop_clicker.set()
        if was_running:
            print("🚨 Emergency stop activated")
        else:
            print("ℹ️  Panic stop pressed but auto-clicker was not running")

    # - Debug Functions -
    def debug_windows_key(self):
        """Press Windows key for debugging"""
        pyautogui.press("win")
        print("✅ Windows key pressed successfully")

    def debug_single_click(self):
        """Perform single click for debugging"""
        pyautogui.click()
        print("✅ Single click performed")

    # -Core Auto-Clicker Logic -
    def perform_action(self):
        """Perform a single action based on current mode"""
        try:
            if self.mode == "click":
                if self.jitter_enabled:
                    x, y = pyautogui.position()
                    offset_x = random.randint(-self.jitter_amount, self.jitter_amount)
                    offset_y = random.randint(-self.jitter_amount, self.jitter_amount)
                    pyautogui.click(x + offset_x, y + offset_y)
                else:
                    pyautogui.click()
                    
            elif self.mode == "right_click":
                if self.jitter_enabled:
                    x, y = pyautogui.position()
                    offset_x = random.randint(-self.jitter_amount, self.jitter_amount)
                    offset_y = random.randint(-self.jitter_amount, self.jitter_amount)
                    pyautogui.rightClick(x + offset_x, y + offset_y)
                else:
                    pyautogui.rightClick()
                    
            elif self.mode == "space":
                pyautogui.press("space")
                
            elif self.mode == "custom" and self.custom_key:
                pyautogui.press(self.custom_key)
                
            self.action_count += 1
            
            return True
            
        except Exception as e:
            print(f"❌ Error performing action: {e}")
            return False

    def auto_clicker_loop(self):
        """Main auto-clicker loop - optimized for high CPS"""
        last_time = time.time()
        
        while self.running and not self.stop_clicker.is_set():
            try:
                now = time.time()
                
                if self.human_like and self.click_interval >= 0.02:
                    interval = self.click_interval * random.uniform(0.8, 1.2)
                else:
                    interval = self.click_interval
                
                if now - last_time >= interval:
                    self.perform_action()
                    last_time = now
                    
                time.sleep(0.001)
                
            except Exception as e:
                print(f"❌ Error in auto-clicker loop: {e}")
                break
                

    # - Status and Utility Functions -
    def get_status(self):
        """Get current status for web interface"""
        if self.running:
            session_time = int(time.time() - self.session_start_time)
        else:
            session_time = 0
            
        return {
            "running": self.running,
            "mode": self.mode,
            "interval": self.click_interval,
            "actions": self.action_count,
            "session_time": session_time,
            "jitter_enabled": self.jitter_enabled,
            "human_like": self.human_like,
            "uptime": int(time.time() - self.start_time)
        }

    def verify_state(self):
        """Verify that the current state is consistent"""
        if self.running and (self.clicker_thread is None or not self.clicker_thread.is_alive()):
            print("⚠️ Running flag true but thread not alive — restarting thread")
            self.clicker_thread = threading.Thread(target=self.auto_clicker_loop, daemon=True)
            self.clicker_thread.start()

    # - Hotkey Setup -  more coming soon gonna make it so you can change the key
    def setup_hotkeys(self):
        """Setup global hotkeys"""
        try:
            # F6 toggles start/stop
            keyboard.add_hotkey("f6", self.hotkey_toggle)
        except Exception as e:
            print(f"❌ Failed to setup hotkeys: {e}")

    def hotkey_toggle(self):
        """Handle F6 hotkey with status update"""
        self.toggle_running()

    # - Signal Handling -
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"🛑 Received signal {signum}, shutting down...")
        self.running = False
        self.stop_clicker.set()
        if self.web_server:
            self.web_server.shutdown()
            self.web_server.server_close()
        sys.exit(0)

    # - Main Looping Logic -
    def run(self):
        """Main application loop"""
        if not self.start_web_server():
            print("❌ Failed to start web server, exiting...")
            return
        
        self.setup_hotkeys()
        
        def state_check():
            while True:
                self.verify_state()
                time.sleep(5)
        
        state_thread = threading.Thread(target=state_check, daemon=True)
        state_thread.start()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutting down...")
            self.signal_handler(signal.SIGINT, None)


if __name__ == "__main__":
    pyautogui.FAILSAFE = False
    pyautogui.PAUSE = 0
    
    AutoClickerBackend().run()

