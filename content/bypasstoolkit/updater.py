import os
import sys

os.environ['PYWEBVIEW_DISABLE_ACCESSIBILITY'] = '1'
os.environ['PYWEBVIEW_DISABLE_DPI_AWARENESS'] = '1'

if sys.platform == 'win32':
    os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '0'
    os.environ['QT_SCALE_FACTOR'] = '1'

import subprocess
import json
import time
import requests
import psutil
import logging
import threading
from datetime import datetime

def setup_logging():
    """Setup minimal logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

setup_logging()

def install_webview():
    """Install webview with proper error handling"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pywebview"])
        return True
    except subprocess.CalledProcessError:
        return False

try:
    import webview
except ImportError:
    if install_webview():
        try:
            import webview
        except ImportError:
            sys.exit(1)
    else:
        sys.exit(1)

THEMES = {
    'frost': {
        'name': 'Frost Glass',
        'background': 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)',
        'primary': '#3b82f6',
        'secondary': '#8b5cf6',
        'accent': '#06b6d4',
        'text': '#1e293b',
        'text_secondary': '#64748b',
        'glass': 'rgba(255, 255, 255, 0.25)',
        'glass_border': 'rgba(255, 255, 255, 0.4)',
        'shadow': '0 25px 50px rgba(0, 0, 0, 0.1)',
        'hover_shadow': '0 35px 60px rgba(0, 0, 0, 0.15)',
        'topbar_bg': 'rgba(255, 255, 255, 0.9)'
    },
    'midnight': {
        'name': 'Midnight Glass',
        'background': 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)',
        'primary': '#818cf8',
        'secondary': '#f472b6',
        'accent': '#2dd4bf',
        'text': '#f1f5f9',
        'text_secondary': '#94a3b8',
        'glass': 'rgba(30, 41, 59, 0.4)',
        'glass_border': 'rgba(255, 255, 255, 0.1)',
        'shadow': '0 25px 50px rgba(0, 0, 0, 0.3)',
        'hover_shadow': '0 35px 60px rgba(0, 0, 0, 0.4)',
        'topbar_bg': 'rgba(15, 23, 42, 0.9)'
    },
    'sunset': {
        'name': 'Sunset Glass',
        'background': 'linear-gradient(135deg, #fef3c7 0%, #fbbf24 100%)',
        'primary': '#dc2626',
        'secondary': '#ea580c',
        'accent': '#d97706',
        'text': '#451a03',
        'text_secondary': '#92400e',
        'glass': 'rgba(255, 255, 255, 0.3)',
        'glass_border': 'rgba(255, 255, 255, 0.5)',
        'shadow': '0 25px 50px rgba(251, 191, 36, 0.2)',
        'hover_shadow': '0 35px 60px rgba(251, 191, 36, 0.3)',
        'topbar_bg': 'rgba(254, 243, 199, 0.9)'
    },
    'ocean': {
        'name': 'Ocean Glass',
        'background': 'linear-gradient(135deg, #dbeafe 0%, #93c5fd 100%)',
        'primary': '#1d4ed8',
        'secondary': '#7e22ce',
        'accent': '#0ea5e9',
        'text': '#1e3a8a',
        'text_secondary': '#475569',
        'glass': 'rgba(255, 255, 255, 0.3)',
        'glass_border': 'rgba(255, 255, 255, 0.5)',
        'shadow': '0 25px 50px rgba(59, 130, 246, 0.15)',
        'hover_shadow': '0 35px 60px rgba(59, 130, 246, 0.25)',
        'topbar_bg': 'rgba(219, 234, 254, 0.9)'
    },
    'purple': {
        'name': 'Purple Haze',
        'background': 'linear-gradient(135deg, #a78bfa 0%, #7c3aed 50%, #5b21b6 100%)',
        'primary': '#f0abfc',
        'secondary': '#c4b5fd',
        'accent': '#a78bfa',
        'text': '#faf5ff',
        'text_secondary': '#ddd6fe',
        'glass': 'rgba(168, 85, 247, 0.2)',
        'glass_border': 'rgba(192, 132, 252, 0.3)',
        'shadow': '0 25px 50px rgba(139, 92, 246, 0.25)',
        'hover_shadow': '0 35px 60px rgba(139, 92, 246, 0.35)',
        'topbar_bg': 'rgba(139, 92, 246, 0.9)'
    }
}

SETTINGS_FILE = 'bypass_settings.json'
ONLINE_FILE_URL = "https://raw.githubusercontent.com/SenturyHanderserson/SigmiForCCGS/refs/heads/main/content/bypasstoolkit/BypassGUI.py"

def load_settings():
    """Load settings from file with proper defaults"""
    default_settings = {
        'theme': 'frost',
        'window_position': {'x': 100, 'y': 100},
        'window_size': {'width': 1200, 'height': 800}
    }
    
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r') as f:
                loaded_settings = json.load(f)
                for key in default_settings:
                    if key not in loaded_settings:
                        loaded_settings[key] = default_settings[key]
                
                if loaded_settings.get('theme') not in THEMES:
                    loaded_settings['theme'] = default_settings['theme']
                    
                return loaded_settings
    except Exception:
        pass
    
    return default_settings

def get_current_version():
    """Get current version from local BypassGUI.py"""
    try:
        if not os.path.exists('BypassGUI.py'):
            return 'v1.0'
            
        with open('BypassGUI.py', 'r', encoding='utf-8') as f:
            content = f.read()
            for line in content.split('\n'):
                if 'VERSION = ' in line:
                    version_line = line.split('=')[1].strip()
                    version = version_line.split('#')[0].strip().strip("'\"")
                    return version
    except Exception:
        pass
    return 'v1.0'

def get_online_version_and_content():
    """Get version and full content from online BypassGUI.py"""
    try:
        response = requests.get(ONLINE_FILE_URL, timeout=30)
        
        if response.status_code == 200:
            content = response.text
            for line in content.split('\n'):
                if 'VERSION = ' in line:
                    version_line = line.split('=')[1].strip()
                    version = version_line.split('#')[0].strip().strip("'\"")
                    return {
                        'version': version,
                        'content': content
                    }
    except Exception:
        pass
    return None

def check_for_updates():
    """Check if updates are available by comparing versions"""
    try:
        current_version = get_current_version()
        online_data = get_online_version_and_content()
        
        if not online_data:
            return {
                'available': False,
                'current_version': current_version,
                'online_version': 'Unknown',
                'error': 'Could not fetch online version'
            }
        
        online_version = online_data['version']
        
        if online_version != current_version:
            return {
                'available': True,
                'current_version': current_version,
                'online_version': online_version,
                'online_content': online_data['content']
            }
        else:
            return {
                'available': False,
                'current_version': current_version,
                'online_version': online_version
            }
    except Exception:
        return {
            'available': False,
            'error': 'Update check failed'
        }

def terminate_processes():
    """Terminate running GUI processes"""
    try:
        current_pid = os.getpid()
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['pid'] == current_pid:
                    continue
                    
                if proc.info['cmdline']:
                    cmdline = ' '.join(proc.info['cmdline']).lower()
                    if ('bypassgui.py' in cmdline or 'guilauncher.vbs' in cmdline):
                        try:
                            proc.terminate()
                        except:
                            pass
            except:
                pass
        
        time.sleep(2)
        return True
    except Exception:
        return False

def restart_main_app():
    """Restart the main application"""
    try:
        time.sleep(1)
        if os.path.exists('GUILauncher.vbs'):
            subprocess.Popen(['wscript.exe', 'GUILauncher.vbs'], shell=False)
        else:
            subprocess.Popen([sys.executable, 'BypassGUI.py'], shell=False)
        return True
    except Exception:
        return False

class UpdaterAPI:
    def __init__(self):
        self.update_info = None
        self.is_updating = False
        self.window = None
        self.settings = load_settings()
    
    def close_app(self):
        """Close the updater"""
        os._exit(0)
    
    def close_window(self):
        """Close the window"""
        self.close_app()
    
    def checkUpdates(self):
        """Check for updates"""
        try:
            self.update_info = check_for_updates()
            return self.update_info
        except Exception:
            return {'available': False, 'error': 'Check failed'}
    
    def performUpdate(self):
        """Perform the update with progress tracking"""
        if self.is_updating:
            return {'success': False, 'error': 'Update in progress'}
        
        self.is_updating = True
        
        def update_progress(stage, percentage, message):
            """Update progress in the UI"""
            try:
                if self.window:
                    js_code = f"""
                    if (typeof updateProgress === 'function') {{
                        updateProgress("{stage}", {percentage}, "{message}");
                    }}
                    """
                    self.window.evaluate_js(js_code)
            except Exception:
                pass
        
        def update_thread():
            try:
                # Stage 1: Checking
                update_progress('checking', 10, "Checking for updates...")
                time.sleep(0.5)
                
                update_info = check_for_updates()
                if not update_info.get('available'):
                    update_progress('error', 0, "No update available")
                    self.is_updating = False
                    return
                
                online_content = update_info.get('online_content')
                if not online_content:
                    update_progress('error', 0, "No online content available")
                    self.is_updating = False
                    return
                
                # Stage 2: Preparing
                update_progress('terminating', 30, "Preparing for update...")
                time.sleep(0.5)
                
                if not terminate_processes():
                    update_progress('error', 30, "Failed to prepare system")
                    self.is_updating = False
                    return
                
                # Stage 3: Downloading
                update_progress('writing', 60, "Downloading new version...")
                time.sleep(1)
                
                try:
                    with open('BypassGUI.py', 'w', encoding='utf-8') as f:
                        f.write(online_content)
                    update_progress('writing', 80, "New version installed!")
                except Exception:
                    update_progress('error', 60, "Installation failed")
                    self.is_updating = False
                    return
                
                # Stage 4: Finalizing
                update_progress('verifying', 90, "Finalizing...")
                time.sleep(0.5)
                
                new_version = get_current_version()
                if new_version == update_info.get('online_version'):
                    update_progress('complete', 100, "Update completed successfully!")
                    time.sleep(1.5)
                    restart_main_app()
                    self.close_app()
                else:
                    update_progress('error', 90, "Verification failed")
                    self.is_updating = False
                    
            except Exception:
                update_progress('error', 0, "Update process failed")
                self.is_updating = False
        
        thread = threading.Thread(target=update_thread)
        thread.daemon = True
        thread.start()
        
        return {'success': True, 'message': 'Update started'}
    
    def skipUpdate(self):
        """Skip update and restart main app"""
        try:
            restart_main_app()
            self.close_app()
            return {'success': True}
        except Exception:
            return {'success': False, 'error': 'Skip failed'}

def create_updater_gui():
    """Create the beautiful updater GUI"""
    # Load settings and theme
    settings = load_settings()
    theme_name = settings.get('theme', 'frost')
    if theme_name not in THEMES:
        theme_name = 'frost'
    current_theme = THEMES[theme_name]
    
    # Perform update check before creating window
    update_info = check_for_updates()
    current_version = get_current_version()
    
    # Determine UI state
    update_available = update_info.get('available', False)
    online_version = update_info.get('online_version', 'Unknown')
    
    # Beautiful HTML content with glass morphism and custom topbar
    html_content = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Sigmi Hub Updater</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
            
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Inter', sans-serif;
                background: {current_theme['background']};
                color: {current_theme['text']};
                height: 100vh;
                overflow: hidden;
                display: flex;
                flex-direction: column;
            }}
            
            /* Custom Topbar */
            .topbar {{
                background: {current_theme['topbar_bg']};
                backdrop-filter: blur(20px);
                border-bottom: 1px solid {current_theme['glass_border']};
                height: 40px;
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 0 15px;
                -webkit-app-region: drag;
                user-select: none;
                position: relative;
                z-index: 1000;
            }}
            
            .topbar-title {{
                color: {current_theme['text']};
                font-size: 14px;
                font-weight: 600;
                display: flex;
                align-items: center;
                gap: 8px;
            }}
            
            .topbar-icon {{
                font-size: 16px;
            }}
            
            .topbar-controls {{
                display: flex;
                gap: 8px;
                -webkit-app-region: no-drag;
            }}
            
            .topbar-btn {{
                background: none;
                border: none;
                color: {current_theme['text_secondary']};
                font-size: 16px;
                width: 30px;
                height: 30px;
                border-radius: 6px;
                display: flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                transition: all 0.2s ease;
            }}
            
            .topbar-btn:hover {{
                background: rgba(255, 255, 255, 0.1);
                color: {current_theme['text']};
            }}
            
            .close-btn:hover {{
                background: rgba(239, 68, 68, 0.3);
                color: #fff;
            }}
            
            .blur-bg {{
                position: fixed;
                top: -50%;
                left: -50%;
                width: 200%;
                height: 200%;
                background: {current_theme['background']};
                filter: blur(40px);
                z-index: -1;
            }}
            
            .content {{
                flex: 1;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
                overflow: auto;
            }}
            
            .glass-container {{
                background: {current_theme['glass']};
                backdrop-filter: blur(20px);
                border: 1px solid {current_theme['glass_border']};
                border-radius: 20px;
                padding: 40px;
                box-shadow: {current_theme['shadow']};
                text-align: center;
                max-width: 500px;
                width: 100%;
                animation: slideUp 0.6s ease-out;
            }}
            
            @keyframes slideUp {{
                from {{ 
                    opacity: 0;
                    transform: translateY(30px) scale(0.95);
                }}
                to {{ 
                    opacity: 1;
                    transform: translateY(0) scale(1);
                }}
            }}
            
            .icon {{
                font-size: 64px;
                margin-bottom: 20px;
                animation: float 3s ease-in-out infinite;
                filter: drop-shadow(0 10px 20px rgba(0,0,0,0.1));
            }}
            
            @keyframes float {{
                0%, 100% {{ transform: translateY(0px); }}
                50% {{ transform: translateY(-10px); }}
            }}
            
            h1 {{
                font-size: 28px;
                font-weight: 700;
                margin-bottom: 8px;
                background: linear-gradient(135deg, {current_theme['primary']}, {current_theme['secondary']});
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }}
            
            .subtitle {{
                color: {current_theme['text_secondary']};
                font-size: 16px;
                margin-bottom: 30px;
                font-weight: 400;
            }}
            
            .version-card {{
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border: 1px solid {current_theme['glass_border']};
                border-radius: 16px;
                padding: 20px;
                margin: 20px 0;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            
            .version-item {{
                text-align: center;
                flex: 1;
            }}
            
            .version-label {{
                color: {current_theme['text_secondary']};
                font-size: 12px;
                font-weight: 500;
                margin-bottom: 4px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            
            .version-value {{
                color: {current_theme['text']};
                font-size: 18px;
                font-weight: 600;
            }}
            
            .status-badge {{
                display: inline-block;
                padding: 8px 16px;
                background: {current_theme['primary'] if update_available else '#10b981'};
                border-radius: 20px;
                font-size: 14px;
                font-weight: 600;
                margin: 10px 0;
                animation: pulse 2s infinite;
            }}
            
            @keyframes pulse {{
                0%, 100% {{ opacity: 1; }}
                50% {{ opacity: 0.7; }}
            }}
            
            .buttons {{
                display: flex;
                gap: 12px;
                margin: 25px 0;
                justify-content: center;
            }}
            
            .btn {{
                padding: 14px 28px;
                border: none;
                border-radius: 12px;
                font-size: 15px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                min-width: 140px;
                position: relative;
                overflow: hidden;
            }}
            
            .btn::before {{
                content: '';
                position: absolute;
                top: 0;
                left: -100%;
                width: 100%;
                height: 100%;
                background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
                transition: left 0.5s;
            }}
            
            .btn:hover::before {{
                left: 100%;
            }}
            
            .btn-primary {{
                background: linear-gradient(135deg, {current_theme['primary']}, {current_theme['secondary']});
                color: white;
                box-shadow: 0 4px 15px {current_theme['primary']}30;
            }}
            
            .btn-primary:hover {{
                transform: translateY(-2px);
                box-shadow: 0 8px 25px {current_theme['primary']}40;
            }}
            
            .btn-secondary {{
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid {current_theme['glass_border']};
                color: {current_theme['text']};
            }}
            
            .btn-secondary:hover {{
                background: rgba(255, 255, 255, 0.15);
                transform: translateY(-2px);
            }}
            
            .progress-container {{
                display: none;
                margin: 25px 0;
                animation: fadeIn 0.5s ease-out;
            }}
            
            @keyframes fadeIn {{
                from {{ opacity: 0; }}
                to {{ opacity: 1; }}
            }}
            
            .progress-header {{
                font-size: 18px;
                font-weight: 600;
                margin-bottom: 15px;
                color: {current_theme['text']};
            }}
            
            .progress-bar-container {{
                width: 100%;
                height: 8px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                overflow: hidden;
                margin-bottom: 15px;
                position: relative;
            }}
            
            .progress-bar {{
                height: 100%;
                background: linear-gradient(90deg, {current_theme['primary']}, {current_theme['accent']});
                border-radius: 10px;
                width: 0%;
                transition: width 0.4s cubic-bezier(0.4, 0, 0.2, 1);
                position: relative;
                overflow: hidden;
            }}
            
            .progress-bar::after {{
                content: '';
                position: absolute;
                top: 0;
                left: -100%;
                width: 100%;
                height: 100%;
                background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
                animation: shimmer 2s infinite;
            }}
            
            @keyframes shimmer {{
                0% {{ left: -100%; }}
                100% {{ left: 100%; }}
            }}
            
            .progress-info {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-top: 10px;
            }}
            
            .progress-text {{
                color: {current_theme['text_secondary']};
                font-size: 14px;
                font-weight: 500;
            }}
            
            .progress-percentage {{
                color: {current_theme['accent']};
                font-size: 16px;
                font-weight: 700;
            }}
            
            .skipping-container {{
                display: none;
                flex-direction: column;
                align-items: center;
                gap: 20px;
                margin: 25px 0;
                animation: fadeIn 0.5s ease-out;
            }}
            
            .spinner {{
                width: 40px;
                height: 40px;
                border: 3px solid {current_theme['glass_border']};
                border-top: 3px solid {current_theme['primary']};
                border-radius: 50%;
                animation: spin 1s linear infinite;
            }}
            
            @keyframes spin {{
                0% {{ transform: rotate(0deg); }}
                100% {{ transform: rotate(360deg); }}
            }}
        </style>
    </head>
    <body>
        <!-- Custom Topbar -->
        <div class="topbar">
            <div class="topbar-title">
                <span class="topbar-icon">🚀</span>
                Sigmi Hub Updater
            </div>
            <div class="topbar-controls">
                <button class="topbar-btn close-btn" onclick="closeWindow()">×</button>
            </div>
        </div>
        
        <div class="blur-bg"></div>
        
        <div class="content">
            <div class="glass-container">
                <div class="icon">🚀</div>
                <h1>Sigmi Hub Updater</h1>
                <div class="subtitle">Keep your software up to date</div>
                
                <div class="version-card">
                    <div class="version-item">
                        <div class="version-label">Current Version</div>
                        <div class="version-value">{current_version}</div>
                    </div>
                    <div class="version-item">
                        <div class="version-label">Latest Version</div>
                        <div class="version-value">{online_version}</div>
                    </div>
                </div>
                
                <div class="status-badge" id="statusBadge">
                    {'Update Available!' if update_available else 'Up to Date!'}
                </div>
                
                <div class="buttons" id="buttons">
                    {'<button class="btn btn-primary" onclick="startUpdate()">Update Now</button>' if update_available else ''}
                    <button class="btn btn-secondary" onclick="skipUpdate()">{'Skip Update' if update_available else 'Launch App'}</button>
                </div>
                
                <div class="progress-container" id="progressContainer">
                    <div class="progress-header" id="progressHeader">Updating Sigmi Hub</div>
                    <div class="progress-bar-container">
                        <div class="progress-bar" id="progressBar"></div>
                    </div>
                    <div class="progress-info">
                        <div class="progress-text" id="progressText">Initializing update...</div>
                        <div class="progress-percentage" id="progressPercentage">0%</div>
                    </div>
                </div>
                
                <div class="skipping-container" id="skippingContainer">
                    <div class="spinner"></div>
                    <div class="progress-text">Launching application...</div>
                </div>
            </div>
        </div>

        <script>
            // Window control functions
            function closeWindow() {{
                if (window.pywebview) {{
                    pywebview.api.close_window();
                }}
            }}
            
            function startUpdate() {{
                document.getElementById('buttons').style.display = 'none';
                document.getElementById('progressContainer').style.display = 'block';
                document.getElementById('statusBadge').textContent = 'Updating...';
                document.getElementById('statusBadge').style.background = '{current_theme['primary']}';
                
                if (window.pywebview) {{
                    pywebview.api.performUpdate().then(result => {{
                        if (!result.success) {{
                            showError('Update failed. Please try again.');
                        }}
                    }}).catch(error => {{
                        showError('Update error occurred.');
                    }});
                }}
            }}
            
            function skipUpdate() {{
                document.getElementById('buttons').style.display = 'none';
                document.getElementById('skippingContainer').style.display = 'flex';
                document.getElementById('statusBadge').textContent = 'Launching...';
                
                if (window.pywebview) {{
                    pywebview.api.skipUpdate();
                }}
            }}
            
            function showError(message) {{
                document.getElementById('progressText').textContent = message;
                document.getElementById('progressText').style.color = '#ef4444';
                document.getElementById('statusBadge').textContent = 'Update Failed';
                document.getElementById('statusBadge').style.background = '#ef4444';
                document.getElementById('buttons').style.display = 'flex';
            }}
            
            // Handle progress updates from backend
            window.updateProgress = function(stage, percentage, message) {{
                const progressBar = document.getElementById('progressBar');
                const progressText = document.getElementById('progressText');
                const progressPercentage = document.getElementById('progressPercentage');
                const progressHeader = document.getElementById('progressHeader');
                
                // Smooth percentage animation
                progressBar.style.width = percentage + '%';
                progressPercentage.textContent = percentage + '%';
                progressText.textContent = message;
                
                // Update header based on stage
                const stageTitles = {{
                    'checking': 'Checking for updates',
                    'terminating': 'Preparing system',
                    'writing': 'Installing update',
                    'verifying': 'Finalizing',
                    'complete': 'Update Complete!',
                    'error': 'Update Failed'
                }};
                
                progressHeader.textContent = stageTitles[stage] || 'Updating Sigmi Hub';
                
                // Visual feedback for completion
                if (percentage === 100) {{
                    progressBar.style.background = 'linear-gradient(90deg, #10b981, {current_theme['accent']})';
                    document.getElementById('statusBadge').textContent = 'Update Complete!';
                    document.getElementById('statusBadge').style.background = '#10b981';
                }}
            }};
        </script>
    </body>
    </html>
    '''
    
    try:
        api = UpdaterAPI()
        
        window = webview.create_window(
            'Sigmi Hub Updater',
            html=html_content,
            width=550,
            height=650,
            resizable=False,
            js_api=api,
            frameless=True,
            easy_drag=True
        )
        
        api.window = window
        
        webview.start()
        
    except Exception as e:
        try:
            restart_main_app()
        except:
            pass

if __name__ == '__main__':
    create_updater_gui()
