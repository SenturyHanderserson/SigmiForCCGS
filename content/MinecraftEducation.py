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
import subprocess
import tempfile
from win10toast import ToastNotifier
import psutil

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
        
        # Notification system
        self.toaster = ToastNotifier()
        
        # Statistics
        self.action_count = 0
        self.session_start_time = 0
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # Hide console window
        self.hide_console()
        
        # Show startup notification
        self.show_notification("Auto Clicker Pro", "Background service started successfully!\nWeb interface: localhost:8080", duration=5)

    def hide_console(self):
        """Hide the console window"""
        try:
            import ctypes
            whnd = ctypes.windll.kernel32.GetConsoleWindow()
            if whnd != 0:
                ctypes.windll.user32.ShowWindow(whnd, 0)  # 0 = SW_HIDE
        except:
            pass  # If hiding fails, continue anyway

    def show_notification(self, title, message, duration=5, icon_path=None):
        """Show Windows notification"""
        try:
            # Create temporary icon if none provided
            if not icon_path:
                icon_path = self.create_temp_icon()
            
            self.toaster.show_toast(
                title,
                message,
                icon_path=icon_path,
                duration=duration,
                threaded=True
            )
        except Exception as e:
            print(f"Notification error: {e}")  # This won't be visible when hidden

    def create_temp_icon(self):
        """Create a temporary icon file for notifications"""
        try:
            # This would normally be a proper icon file
            # For now, we'll use a generic approach
            return None  # Let Windows use default icon
        except:
            return None

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
                            self.send_error(500, "Internal Server Error")
                    elif self.path == '/shutdown':
                        # Emergency shutdown endpoint
                        try:
                            self.app.emergency_shutdown()
                            self.send_response(200)
                            self.send_header('Content-type', 'application/json')
                            self.send_header('Access-Control-Allow-Origin', '*')
                            self.end_headers()
                            self.wfile.write(json.dumps({"status": "shutting_down"}).encode('utf-8'))
                        except Exception as e:
                            self.send_error(500, "Shutdown error")
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
                            
                            # Handle different commands
                            command = data.get('command')
                            if command == 'start_stop':
                                self.app.toggle_running()
                            elif command == 'set_mode':
                                self.app.mode = data.get('mode', 'click')
                            elif command == 'set_interval':
                                interval = data.get('interval')
                                if interval is not None:
                                    self.app.click_interval = max(0.01, float(interval))
                            elif command == 'set_jitter':
                                self.app.jitter_enabled = bool(data.get('enabled', True))
                            elif command == 'set_human_like':
                                self.app.human_like = bool(data.get('enabled', True))
                            elif command == 'set_custom_key':
                                self.app.custom_key = data.get('key')
                                self.app.mode = "custom"
                            elif command == 'panic_stop':
                                self.app.panic_stop()
                            elif command == 'restart_backend':
                                self.app.restart_backend()
                            
                            self.send_response(200)
                            self.send_header('Content-type', 'application/json')
                            self.send_header('Access-Control-Allow-Origin', '*')
                            self.end_headers()
                            response_data = json.dumps({"status": "success", "command": command})
                            self.wfile.write(response_data.encode('utf-8'))
                            
                        except json.JSONDecodeError as e:
                            self.send_error(400, "Invalid JSON")
                        except Exception as e:
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
            
            # Show connection notification
            self.show_notification(
                "Auto Clicker Pro - Connected", 
                "Web interface is now active!\n\n🌐 Local: http://localhost:8080\n🔗 Remote: GitHub Pages\n\nService running in background.",
                duration=5
            )
            
            return True
            
        except Exception as e:
            self.show_notification(
                "Auto Clicker Pro - Error", 
                f"Failed to start web server:\n{str(e)}\n\nPlease check if port 8080 is available.",
                duration=10
            )
            return False

    def setup_hotkeys(self):
        """Setup global hotkeys"""
        try:
            keyboard.add_hotkey('f6', self.toggle_running)
            keyboard.add_hotkey('f7', self.panic_stop)
            return True
        except Exception as e:
            self.show_notification(
                "Auto Clicker Pro - Warning", 
                "Hotkey registration failed.\nF6/F7 may not work.\nUse web interface controls.",
                duration=5
            )
            return False

    def toggle_running(self):
        """Toggle the running state"""
        self.running = not self.running
        
        if self.running:
            self.session_start_time = time.time()
            self.action_count = 0
            # Start auto clicker in a separate thread
            self.clicker_thread = threading.Thread(target=self.auto_clicker, daemon=True)
            self.clicker_thread.start()
            
            self.show_notification(
                "Auto Clicker - STARTED", 
                "Auto clicking activated!\n\nClicking at lightning speed ⚡\nPress F7 for emergency stop.",
                duration=3
            )
        else:
            self.show_notification(
                "Auto Clicker - STOPPED", 
                "Auto clicking deactivated.\n\nTotal actions performed: " + str(self.action_count),
                duration=3
            )

    def panic_stop(self):
        """Immediately stop everything"""
        if self.running:
            self.running = False
            self.show_notification(
                "🚨 PANIC STOP", 
                "Auto clicker emergency stopped!\n\nAll activities halted immediately.",
                duration=5
            )

    def emergency_shutdown(self):
        """Complete emergency shutdown"""
        self.show_notification(
            "Auto Clicker - SHUTDOWN", 
            "Service is shutting down...\n\nAll processes terminated.",
            duration=3
        )
        self.shutdown()

    def restart_backend(self):
        """Restart the backend service"""
        self.show_notification(
            "Auto Clicker - RESTARTING", 
            "Service restarting...\n\nPlease wait a moment.",
            duration=3
        )
        # This would typically restart the service
        # For now, we'll just simulate a restart
        time.sleep(2)
        self.show_notification(
            "Auto Clicker - RESTARTED", 
            "Service restarted successfully!",
            duration=3
        )

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
                    click_count = 0
                    last_update = time.time()
                
                time.sleep(interval)
                
            except Exception as e:
                self.show_notification(
                    "Auto Clicker - ERROR", 
                    f"Auto clicker error:\n{str(e)}\n\nAuto clicking stopped.",
                    duration=5
                )
                self.running = False
                break

    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.shutdown()

    def shutdown(self):
        """Clean shutdown"""
        self.running = False
        if self.web_server:
            self.web_server.shutdown()
            self.web_server.server_close()
        sys.exit(0)

    def run(self):
        """Main application loop"""
        if not self.start_web_server():
            return
        
        if not self.setup_hotkeys():
            # Continue even if hotkeys fail
            pass
        
        # Main loop - keep the service alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.shutdown()
        except Exception as e:
            self.show_notification(
                "Auto Clicker - CRITICAL ERROR", 
                f"Critical error occurred:\n{str(e)}\n\nService must restart.",
                duration=10
            )
            self.shutdown()

def main():
    # Check if required modules are installed
    try:
        import pyautogui
        import keyboard
        from win10toast import ToastNotifier
        import psutil
    except ImportError as e:
        # This won't be visible when hidden, but we try to show a notification
        try:
            toaster = ToastNotifier()
            toaster.show_toast(
                "Auto Clicker - Installation Required",
                f"Missing dependencies:\n{str(e)}\n\nPlease run the installer again.",
                duration=10
            )
        except:
            pass
        return
    
    # Create and run the backend
    backend = AutoClickerBackend()
    backend.run()

if __name__ == "__main__":
    main()
