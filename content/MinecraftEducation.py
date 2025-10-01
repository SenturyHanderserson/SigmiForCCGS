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
        self.jitter_amount = 2
        self.human_like = True

        self.web_port = 8080
        self.web_thread = None
        self.web_server = None

        self.action_count = 0
        self.session_start_time = 0

        self.clicker_thread = None
        self.stop_clicker = threading.Event()

        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        print("🎮 Auto Clicker Pro - Backend Server")
        print("=" * 50)
        print("🌐 API Server: http://localhost:8080")
        print("🎮 Hotkeys: F6 (Start/Stop), F7 (Emergency Stop)")
        print("🔧 Debug: Windows key test available via web interface")
        print("=" * 50)

    # ------------------- Web Server -------------------
    def start_web_server(self):
        try:
            class AutoClickerHandler(BaseHTTPRequestHandler):
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
                    self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
                    self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, Accept, Origin')
                    self.send_header('Access-Control-Allow-Credentials', 'true')

                def do_GET(self):
                    """Handle GET requests"""
                    try:
                        if self.path in ['/status.json', '/status']:
                            status_data = {
                                "running": self.server.backend_app.running,
                                "mode": self.server.backend_app.mode,
                                "interval": self.server.backend_app.click_interval,
                                "actions": self.server.backend_app.action_count,
                                "session_time": int(time.time() - self.server.backend_app.session_start_time)
                                if self.server.backend_app.running else 0,
                                "jitter_enabled": self.server.backend_app.jitter_enabled,
                                "human_like": self.server.backend_app.human_like
                            }
                            self.send_response(200)
                            self.send_header('Content-type', 'application/json')
                            self._set_cors_headers()
                            self.end_headers()
                            self.wfile.write(json.dumps(status_data).encode('utf-8'))
                        else:
                            self.send_response(404)
                            self._set_cors_headers()
                            self.end_headers()
                    except Exception as e:
                        print(f"❌ Error in GET handler: {e}")
                        self.send_response(500)
                        self._set_cors_headers()
                        self.end_headers()

                def do_POST(self):
                    """Handle POST requests"""
                    try:
                        if self.path == '/command':
                            # Handle CORS preflight
                            if self.headers.get('Origin'):
                                self._set_cors_headers()
                            
                            content_length = int(self.headers.get('Content-Length', 0))
                            if content_length > 0:
                                post_data = self.rfile.read(content_length)
                                data = json.loads(post_data.decode('utf-8'))
                            else:
                                data = {}
                                
                            print(f"🔧 Received command: {data}")

                            app = self.server.backend_app
                            cmd = data.get("command")
                            before_state = {
                                "running": app.running,
                                "mode": app.mode,
                                "interval": app.click_interval,
                            }
                            print(f"📊 State before command: {before_state}")

                            response_data = {"status": "ok"}
                            
                            # Handle debug commands
                            if cmd == "debug_windows_key":
                                print("🪟 DEBUG: Pressing Windows key")
                                pyautogui.press("win")
                                print("✅ Windows key pressed successfully")
                                response_data["message"] = "Windows key pressed"
                                
                            elif cmd == "debug_single_click":
                                print("🖱️ DEBUG: Performing single click")
                                pyautogui.click()
                                print("✅ Single click performed")
                                response_data["message"] = "Single click performed"
                                
                            # Original commands
                            elif cmd == "start_stop":
                                app.toggle_running()
                                response_data["message"] = "Toggled running state"
                            elif cmd == "set_mode":
                                app.mode = data.get("mode", "click")
                                print(f"📝 Mode set to: {app.mode}")
                                app.perform_action()  # force one action
                                response_data["message"] = f"Mode set to {app.mode}"
                            elif cmd == "set_interval":
                                app.click_interval = max(0.01, float(data.get("interval", 0.05)))
                                print(f"⚡ Interval updated to: {app.click_interval}")
                                response_data["message"] = f"Interval set to {app.click_interval}"
                            elif cmd == "set_jitter":
                                app.jitter_enabled = bool(data.get("enabled", True))
                                print(f"🎯 Jitter {app.jitter_enabled}")
                                response_data["message"] = f"Jitter set to {app.jitter_enabled}"
                            elif cmd == "set_human_like":
                                app.human_like = bool(data.get("enabled", True))
                                print(f"🤖 Human-like {app.human_like}")
                                response_data["message"] = f"Human-like set to {app.human_like}"
                            elif cmd == "set_custom_key":
                                app.custom_key = data.get("key")
                                app.mode = "custom"
                                print(f"🔑 Custom key = {app.custom_key}")
                                app.perform_action()
                                response_data["message"] = f"Custom key set to {app.custom_key}"
                            elif cmd == "panic_stop":
                                app.panic_stop()
                                response_data["message"] = "Panic stop activated"
                            elif cmd == "restart":
                                print("🔄 Restart command received")
                                response_data["message"] = "Restart command received"
                            elif cmd == "shutdown":
                                print("🔌 Shutdown command received")
                                response_data["message"] = "Shutdown command received"
                            else:
                                print(f"⚠️ Unknown command {cmd}")
                                response_data = {"status": "error", "message": f"Unknown command: {cmd}"}

                            app.verify_state(cmd)

                            after_state = {
                                "running": app.running,
                                "mode": app.mode,
                                "interval": app.click_interval,
                            }
                            print(f"📊 State after command: {after_state}")

                            self.send_response(200)
                            self.send_header('Content-type', 'application/json')
                            self._set_cors_headers()
                            self.end_headers()
                            self.wfile.write(json.dumps(response_data).encode("utf-8"))
                        else:
                            self.send_response(404)
                            self._set_cors_headers()
                            self.end_headers()
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

            self.web_server = BackendServer(("", self.web_port), AutoClickerHandler, self)
            print(f"🚀 Starting web server on port {self.web_port}...")
            self.web_thread = threading.Thread(target=self.web_server.serve_forever, daemon=True)
            self.web_thread.start()
            print(f"✅ Web server started successfully on http://localhost:{self.web_port}")
            return True
        except Exception as e:
            print(f"❌ Failed to start web server: {e}")
            return False

    # ------------------- Controls -------------------
    def setup_hotkeys(self):
        try:
            keyboard.add_hotkey("f6", self.toggle_running)
            keyboard.add_hotkey("f7", self.panic_stop)
            print("✅ Hotkeys registered: F6 (Start/Stop), F7 (Panic Stop)")
        except Exception as e:
            print(f"❌ Failed to setup hotkeys: {e}")

    def toggle_running(self):
        if self.running:
            self.running = False
            self.stop_clicker.set()
            print("🛑 Auto-clicker stopped")
        else:
            self.running = True
            self.stop_clicker.clear()
            self.session_start_time = time.time()
            self.action_count = 0
            self.clicker_thread = threading.Thread(target=self.auto_clicker, daemon=True)
            self.clicker_thread.start()
            print("🚀 Auto-clicker started")

    def panic_stop(self):
        self.running = False
        self.stop_clicker.set()
        print("🚨 Emergency stop activated")

    def perform_action(self):
        try:
            if self.mode == "click":
                pyautogui.click()
            elif self.mode == "right_click":
                pyautogui.rightClick()
            elif self.mode == "space":
                pyautogui.press("space")
            elif self.mode == "custom" and self.custom_key:
                pyautogui.press(self.custom_key)
            self.action_count += 1
            print(f"✅ Action performed ({self.mode}) - Total: {self.action_count}")
            return True
        except Exception as e:
            print(f"❌ perform_action error: {e}")
            return False

    def auto_clicker(self):
        last_time = time.time()
        print("🔄 Auto-clicker thread started")
        while self.running and not self.stop_clicker.is_set():
            try:
                now = time.time()
                interval = self.click_interval * random.uniform(0.8, 1.2) if self.human_like else self.click_interval
                if now - last_time >= interval:
                    self.perform_action()
                    last_time = now
                time.sleep(0.001)
            except Exception as e:
                print(f"❌ Error in auto_clicker loop: {e}")
                break
        print("✅ Auto-clicker thread ended")

    def verify_state(self, cmd):
        """Verify that command actually applied"""
        if cmd == "start_stop" and self.running and (self.clicker_thread is None or not self.clicker_thread.is_alive()):
            print("⚠️ Running flag true but thread not alive — restarting thread")
            self.clicker_thread = threading.Thread(target=self.auto_clicker, daemon=True)
            self.clicker_thread.start()

    def signal_handler(self, signum, frame):
        print(f"🛑 Received signal {signum}, shutting down...")
        self.running = False
        self.stop_clicker.set()
        if self.web_server:
            print("🔌 Shutting down web server...")
            self.web_server.shutdown()
        sys.exit(0)

    def run(self):
        if not self.start_web_server():
            print("❌ Failed to start web server, exiting...")
            return
        
        self.setup_hotkeys()
        
        print("\n🎯 Auto Clicker Pro is now running!")
        print("💡 Use the web interface at http://localhost:8080")
        print("💡 Or use hotkeys: F6 (Start/Stop), F7 (Emergency Stop)")
        print("⏹️  Press Ctrl+C to exit\n")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutting down...")
            self.signal_handler(signal.SIGINT, None)


if __name__ == "__main__":
    AutoClickerBackend().run()
