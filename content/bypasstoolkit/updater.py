import sys
import subprocess
import os
import json
import time
import requests
import psutil
import logging
import threading
from datetime import datetime

# Setup logging
def setup_logging():
    """Setup comprehensive logging"""
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    log_file = os.path.join(log_dir, f'updater_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logging.info("=" * 50)
    logging.info("Sigmi Hub Updater Started")
    logging.info("=" * 50)

# Call setup_logging at the start
setup_logging()

def install_webview():
    """Install webview with proper error handling"""
    logging.info("Installing pywebview...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pywebview"])
        logging.info("Successfully installed pywebview")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to install pywebview via pip: {e}")
        return False

# Try to import webview, install if not available
try:
    import webview
    logging.info("Successfully imported webview")
except ImportError:
    logging.warning("Webview not found. Installing...")
    if install_webview():
        try:
            import webview
            logging.info("Successfully installed and imported webview!")
        except ImportError:
            logging.error("Failed to install webview.")
            sys.exit(1)
    else:
        logging.error("Could not install webview.")
        sys.exit(1)

# Simple theme configuration
THEMES = {
    'sunset': {
        'background': 'linear-gradient(135deg, #fef3c7 0%, #fbbf24 100%)',
        'primary': '#dc2626',
        'secondary': '#ea580c',
        'text': '#451a03',
        'text_secondary': '#92400e',
        'glass': 'rgba(255, 255, 255, 0.3)',
    }
}

SETTINGS_FILE = 'bypass_settings.json'
ONLINE_FILE_URL = "https://raw.githubusercontent.com/SenturyHanderserson/SigmiForCCGS/refs/heads/main/content/bypasstoolkit/BypassGUI.py"

def load_settings():
    """Load settings from file with proper defaults"""
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r') as f:
                settings = json.load(f)
                theme = settings.get('theme', 'sunset')
                return THEMES.get(theme, THEMES['sunset'])
    except Exception as e:
        logging.error(f"Error loading settings: {e}")
    
    return THEMES['sunset']

def get_current_version():
    """Get current version from local BypassGUI.py"""
    try:
        if not os.path.exists('BypassGUI.py'):
            logging.error("BypassGUI.py not found in current directory")
            return 'v1.0'
            
        with open('BypassGUI.py', 'r', encoding='utf-8') as f:
            content = f.read()
            for line in content.split('\n'):
                if 'VERSION = ' in line:
                    version_line = line.split('=')[1].strip()
                    version = version_line.split('#')[0].strip().strip("'\"")
                    logging.info(f"Found local version: {version}")
                    return version
    except Exception as e:
        logging.error(f"Error reading current version: {e}")
    return 'v1.0'

def get_online_version_and_content():
    """Get version and full content from online BypassGUI.py"""
    logging.info(f"Fetching online file from: {ONLINE_FILE_URL}")
    try:
        response = requests.get(ONLINE_FILE_URL, timeout=30)
        
        if response.status_code == 200:
            content = response.text
            logging.debug(f"Received content length: {len(content)} characters")
            
            # Extract version from online content
            for line in content.split('\n'):
                if 'VERSION = ' in line:
                    version_line = line.split('=')[1].strip()
                    version = version_line.split('#')[0].strip().strip("'\"")
                    logging.info(f"Found online version: {version}")
                    return {
                        'version': version,
                        'content': content
                    }
            return None
        else:
            logging.error(f"Failed to download online file. Status: {response.status_code}")
            return None
    except Exception as e:
        logging.error(f"Error getting online version: {e}")
        return None

def check_for_updates():
    """Check if updates are available by comparing versions"""
    logging.info("Starting update check")
    try:
        current_version = get_current_version()
        logging.info(f"Current version: {current_version}")
        
        online_data = get_online_version_and_content()
        if not online_data:
            logging.warning("Could not fetch online data")
            return {
                'available': False,
                'current_version': current_version,
                'online_version': 'Unknown',
                'error': 'Could not fetch online version'
            }
        
        online_version = online_data['version']
        logging.info(f"Online version: {online_version}")
        
        if online_version != current_version:
            logging.info(f"Update available: {current_version} -> {online_version}")
            return {
                'available': True,
                'current_version': current_version,
                'online_version': online_version,
                'online_content': online_data['content']
            }
        else:
            logging.info("No update available - versions are the same")
            return {
                'available': False,
                'current_version': current_version,
                'online_version': online_version
            }
    except Exception as e:
        error_msg = f"Update check failed: {str(e)}"
        logging.error(error_msg)
        return {
            'available': False,
            'error': error_msg
        }

def terminate_processes():
    """Terminate running GUI processes"""
    logging.info("Terminating running GUI processes")
    try:
        current_pid = os.getpid()
        
        # Terminate python processes running the GUI
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['pid'] == current_pid:
                    continue
                    
                if proc.info['cmdline']:
                    cmdline = ' '.join(proc.info['cmdline']).lower()
                    if ('bypassgui.py' in cmdline or 'guilauncher.vbs' in cmdline):
                        logging.info(f"Terminating process: {proc.info['name']} (PID: {proc.info['pid']})")
                        try:
                            proc.terminate()
                            logging.info(f"Successfully terminated process {proc.info['pid']}")
                        except:
                            logging.debug(f"Process {proc.info['pid']} already terminated")
            except:
                pass
        
        # Wait for processes to terminate
        time.sleep(2)
        return True
    except Exception as e:
        logging.error(f"Error terminating processes: {e}")
        return False

def perform_update_with_progress(progress_callback=None):
    """Perform the update with progress reporting"""
    logging.info("Starting update process with progress tracking")
    
    def update_progress(stage, percentage, message):
        if progress_callback:
            progress_callback(stage, percentage, message)
        logging.info(f"Update progress: {stage} - {percentage}% - {message}")
    
    try:
        update_progress('checking', 0, "Checking for updates...")
        
        # First check for updates to get the online content
        update_info = check_for_updates()
        if not update_info.get('available'):
            update_progress('error', 0, "No update available to perform")
            return False
        
        online_content = update_info.get('online_content')
        if not online_content:
            update_progress('error', 0, "No online content available")
            return False
        
        update_progress('terminating', 20, "Terminating existing processes...")
        
        # Terminate existing processes first
        if not terminate_processes():
            update_progress('error', 20, "Failed to terminate processes")
            return False
        
        update_progress('backup', 40, "Creating backup...")
        
        # Create backup of current file
        if os.path.exists('BypassGUI.py'):
            try:
                with open('BypassGUI.py', 'r', encoding='utf-8') as f:
                    backup_content = f.read()
                with open('BypassGUI.py.backup', 'w', encoding='utf-8') as f:
                    f.write(backup_content)
                update_progress('backup', 50, "Backup created successfully")
            except Exception as e:
                logging.warning(f"Could not create backup: {e}")
        
        update_progress('writing', 60, "Writing new version...")
        
        # Write new content to file
        try:
            with open('BypassGUI.py', 'w', encoding='utf-8') as f:
                f.write(online_content)
            update_progress('writing', 80, "New version written successfully")
        except Exception as e:
            update_progress('error', 60, f"Failed to write new version: {e}")
            return False
        
        update_progress('verifying', 90, "Verifying installation...")
        
        # Verify the download
        new_version = get_current_version()
        if new_version == update_info.get('online_version'):
            update_progress('complete', 100, "Update completed successfully!")
            time.sleep(1)
            return True
        else:
            update_progress('error', 90, "Version mismatch - update failed")
            return False
            
    except Exception as e:
        error_msg = f"Update failed: {str(e)}"
        update_progress('error', 0, error_msg)
        logging.error(error_msg)
        return False

def restart_main_app():
    """Restart the main application"""
    logging.info("Restarting main application")
    try:
        time.sleep(1)
        
        # Launch main app via VBS wrapper
        if os.path.exists('GUILauncher.vbs'):
            logging.info("Launching via GUILauncher.vbs")
            subprocess.Popen(['wscript.exe', 'GUILauncher.vbs'], shell=False)
            return True
        else:
            # Fallback: run directly
            logging.info("Launching directly via python")
            subprocess.Popen([sys.executable, 'BypassGUI.py'], shell=False)
            return True
    except Exception as e:
        logging.error(f"Failed to restart main app: {e}")
        return False

class UpdaterAPI:
    def __init__(self):
        self.current_theme = load_settings()
        self.update_info = None
        self.is_updating = False
        logging.info("UpdaterAPI initialized")
    
    def close_app(self):
        """Close the updater"""
        logging.info("Closing updater...")
        os._exit(0)
    
    def close_window(self):
        """Close the window"""
        logging.info("Close window requested")
        self.close_app()
    
    def checkUpdates(self):
        """Check for updates"""
        logging.info("checkUpdates called from GUI")
        try:
            self.update_info = check_for_updates()
            logging.info(f"Update check result: available={self.update_info.get('available')}")
            return self.update_info
        except Exception as e:
            logging.error(f"Error in checkUpdates: {e}")
            return {'available': False, 'error': str(e)}
    
    def performUpdate(self):
        """Perform the update with progress tracking"""
        if self.is_updating:
            return {'success': False, 'error': 'Update already in progress'}
        
        self.is_updating = True
        logging.info("performUpdate called from GUI - starting update process")
        
        def update_thread():
            try:
                success = perform_update_with_progress()
                if success:
                    logging.info("Update successful, restarting main app...")
                    time.sleep(2)
                    restart_main_app()
                    self.close_app()
                else:
                    logging.error("Update failed")
                    self.is_updating = False
            except Exception as e:
                logging.error(f"Update thread error: {e}")
                self.is_updating = False
        
        # Start update in a separate thread
        thread = threading.Thread(target=update_thread)
        thread.daemon = True
        thread.start()
        
        return {'success': True, 'message': 'Update started'}
    
    def skipUpdate(self):
        """Skip update and restart main app"""
        logging.info("skipUpdate called from GUI - skipping update")
        try:
            restart_main_app()
            self.close_app()
            return {'success': True}
        except Exception as e:
            logging.error(f"Error in skipUpdate: {e}")
            return {'success': False, 'error': str(e)}

def create_updater_gui():
    """Create the updater GUI"""
    logging.info("Creating updater GUI")
    
    # Perform update check BEFORE creating window
    logging.info("Performing pre-window update check...")
    update_info = check_for_updates()
    logging.info(f"Pre-check result: available={update_info.get('available')}")
    
    current_theme = load_settings()
    current_version = get_current_version()
    
    # Determine UI state
    update_available = update_info.get('available', False)
    online_version = update_info.get('online_version', 'Unknown')
    
    # Simple HTML content
    html_content = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: Arial, sans-serif;
                background: {current_theme['background']};
                color: {current_theme['text']};
                margin: 0;
                padding: 20px;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 100vh;
            }}
            .container {{
                background: {current_theme['glass']};
                padding: 30px;
                border-radius: 15px;
                text-align: center;
                max-width: 500px;
                width: 90%;
            }}
            h1 {{
                color: {current_theme['primary']};
                margin-bottom: 20px;
            }}
            .version-info {{
                background: rgba(255,255,255,0.2);
                padding: 15px;
                border-radius: 10px;
                margin: 15px 0;
            }}
            .buttons {{
                margin: 20px 0;
            }}
            button {{
                background: {current_theme['primary']};
                color: white;
                border: none;
                padding: 12px 24px;
                margin: 5px;
                border-radius: 8px;
                cursor: pointer;
                font-size: 16px;
            }}
            button:hover {{
                opacity: 0.9;
            }}
            .progress {{
                display: none;
                margin: 20px 0;
            }}
            .progress-bar {{
                width: 100%;
                height: 20px;
                background: rgba(255,255,255,0.3);
                border-radius: 10px;
                overflow: hidden;
            }}
            .progress-fill {{
                height: 100%;
                background: {current_theme['primary']};
                width: 0%;
                transition: width 0.3s;
            }}
            .status {{
                margin: 10px 0;
                font-weight: bold;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔧 Sigmi Hub Updater</h1>
            
            <div class="version-info">
                <div>Current Version: <strong>{current_version}</strong></div>
                <div>Online Version: <strong>{online_version}</strong></div>
            </div>
            
            <div class="status" id="status">
                {'Update available!' if update_available else 'Your software is up to date!'}
            </div>
            
            <div class="buttons" id="buttons">
                {'<button onclick="startUpdate()">Update Now</button>' if update_available else ''}
                <button onclick="skipUpdate()">{'Skip Update' if update_available else 'Continue'}</button>
            </div>
            
            <div class="progress" id="progress">
                <div class="progress-bar">
                    <div class="progress-fill" id="progressFill"></div>
                </div>
                <div id="progressText">Starting update...</div>
            </div>
        </div>

        <script>
            function startUpdate() {{
                document.getElementById('buttons').style.display = 'none';
                document.getElementById('progress').style.display = 'block';
                document.getElementById('status').textContent = 'Updating...';
                
                if (window.pywebview) {{
                    pywebview.api.performUpdate().then(result => {{
                        if (!result.success) {{
                            document.getElementById('status').textContent = 'Update failed: ' + result.error;
                            document.getElementById('buttons').style.display = 'block';
                            document.getElementById('progress').style.display = 'none';
                        }}
                    }});
                }}
            }}
            
            function skipUpdate() {{
                document.getElementById('status').textContent = 'Skipping update...';
                if (window.pywebview) {{
                    pywebview.api.skipUpdate();
                }}
            }}
            
            // Simple progress simulation (real progress comes from backend)
            let progress = 0;
            function simulateProgress() {{
                if (progress < 90) {{
                    progress += 10;
                    document.getElementById('progressFill').style.width = progress + '%';
                    setTimeout(simulateProgress, 500);
                }}
            }}
            
            // Start progress simulation when update begins
            document.addEventListener('DOMContentLoaded', function() {{
                // This would be replaced with real progress updates from backend
            }});
        </script>
    </body>
    </html>
    '''
    
    try:
        logging.info("Creating webview window...")
        window = webview.create_window(
            'Sigmi Hub Updater',
            html=html_content,
            width=600,
            height=400,
            resizable=False,
            js_api=UpdaterAPI()
        )
        
        logging.info("Starting webview...")
        webview.start()
        
    except Exception as e:
        logging.error(f"Failed to create GUI: {e}")
        # Fallback to console mode
        run_console_updater()

def run_console_updater():
    """Fallback console-based updater"""
    logging.info("Falling back to console updater")
    print("=" * 50)
    print("Sigmi Hub Updater (Console Mode)")
    print("=" * 50)
    
    print("Checking for updates...")
    result = check_for_updates()
    
    if result.get('available'):
        print(f"Update available: {result['current_version']} -> {result['online_version']}")
        choice = input("Do you want to update now? (y/n): ").lower().strip()
        if choice in ['y', 'yes']:
            print("Updating...")
            if perform_update_with_progress():
                print("Update successful! Restarting main app...")
                restart_main_app()
            else:
                print("Update failed!")
        else:
            print("Skipping update...")
            restart_main_app()
    else:
        print("No updates available.")
        if result.get('error'):
            print(f"Error: {result['error']}")
        restart_main_app()

if __name__ == '__main__':
    # Always use GUI mode for now
    logging.info("Starting in GUI mode")
    create_updater_gui()
