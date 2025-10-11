import sys
import subprocess
import os
import json
import webbrowser
import requests
from urllib.parse import quote

def install_webview():
    """Install webview with proper error handling"""
    print("Installing pywebview...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pywebview"])
        return True
    except subprocess.CalledProcessError:
        print("Failed to install pywebview via pip.")
        return False

# Try to import webview, install if not available
try:
    import webview
except ImportError:
    print("Webview not found. Installing...")
    if install_webview():
        try:
            import webview
            print("Successfully installed and imported webview!")
        except ImportError:
            print("Failed to install webview.")
            sys.exit(1)
    else:
        print("Could not install webview.")
        sys.exit(1)

# Theme Configuration
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
        'hover_shadow': '0 35px 60px rgba(0, 0, 0, 0.15)'
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
        'hover_shadow': '0 35px 60px rgba(0, 0, 0, 0.4)'
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
        'hover_shadow': '0 35px 60px rgba(251, 191, 36, 0.3)'
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
        'hover_shadow': '0 35px 60px rgba(59, 130, 246, 0.25)'
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
        'hover_shadow': '0 35px 60px rgba(139, 92, 246, 0.35)'
    }
}

# Settings storage
SETTINGS_FILE = 'bypass_settings.json'
VERSION = 'v1 beta'

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
                # Ensure all required keys exist and theme is valid
                for key in default_settings:
                    if key not in loaded_settings:
                        loaded_settings[key] = default_settings[key]
                
                # Validate theme
                if loaded_settings.get('theme') not in THEMES:
                    loaded_settings['theme'] = default_settings['theme']
                    
                return loaded_settings
    except Exception as e:
        print(f"Error loading settings: {e}")
    
    return default_settings

def save_settings(settings):
    """Save settings to file"""
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=2)
    except Exception as e:
        print(f"Error saving settings: {e}")

def check_for_updates():
    """Check if updates are available from GitHub"""
    try:
        # Get current file path
        current_file = __file__
        
        # Get online version
        online_url = "https://raw.githubusercontent.com/SenturyHanderserson/SigmiForCCGS/refs/heads/main/content/bypasstoolkit/BypassGUI.py"
        response = requests.get(online_url, timeout=10)
        
        if response.status_code == 200:
            online_content = response.text
            
            # Read current file
            with open(current_file, 'r', encoding='utf-8') as f:
                current_content = f.read()
            
            # Simple comparison (you might want to parse version numbers properly)
            if online_content != current_content:
                # Extract version from online content
                online_version = "v1.1"  # Default assumption
                for line in online_content.split('\n'):
                    if 'VERSION = ' in line:
                        online_version = line.split('=')[1].strip().strip("'\"")
                        break
                
                return {
                    'available': True,
                    'online_version': online_version,
                    'online_content': online_content
                }
        
        return {'available': False}
        
    except Exception as e:
        print(f"Update check failed: {e}")
        return {'available': False, 'error': str(e)}

def perform_update(online_content):
    """Perform the update by creating updater script"""
    try:
        # Create updater script
        updater_script = '''
import os
import requests
import sys
import time

def update_app():
    """Update the application with new content"""
    try:
        # Get the online content
        online_url = "https://raw.githubusercontent.com/SenturyHanderserson/SigmiForCCGS/refs/heads/main/content/bypasstoolkit/BypassGUI.py"
        response = requests.get(online_url, timeout=30)
        
        if response.status_code == 200:
            online_content = response.text
            
            # Write new content to file
            current_file = __file__.replace('updater.py', 'BypassGUI.py')
            with open(current_file, 'w', encoding='utf-8') as f:
                f.write(online_content)
            
            print("Update successful! Restarting application...")
            time.sleep(2)
            
            # Restart the application
            python = sys.executable
            os.execl(python, python, current_file)
        else:
            print("Failed to download update")
            
    except Exception as e:
        print(f"Update failed: {e}")

if __name__ == '__main__':
    update_app()
'''.strip()
        
        # Write updater script
        with open('updater.py', 'w') as f:
            f.write(updater_script)
        
        # Run updater
        subprocess.Popen([sys.executable, 'updater.py'])
        
        # Close current app
        sys.exit(0)
        
    except Exception as e:
        print(f"Update initiation failed: {e}")
        return False

class BypassAPI:
    def __init__(self):
        self.settings = load_settings()
    
    def close_app(self):
        """Close the application"""
        print("Closing application...")
        import os
        os._exit(0)
    
    def changeTheme(self, theme):
        """Change application theme"""
        self.settings['theme'] = theme
        save_settings(self.settings)
        return {'status': 'theme_changed', 'theme': theme}
    
    def restart_app(self):
        """Restart the application to apply theme changes"""
        print("Restarting application...")
        python = sys.executable
        os.execl(python, python, *sys.argv)
    
    def checkUpdates(self):
        """Check for updates"""
        try:
            result = check_for_updates()
            return result
        except Exception as e:
            return {'available': False, 'error': str(e)}
    
    def performUpdate(self):
        """Perform the update"""
        try:
            result = check_for_updates()
            if result['available']:
                success = perform_update(result['online_content'])
                return {'success': success}
            return {'success': False, 'error': 'No update available'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

def create_webview_app():
    """Create the WebView window with enhanced styling"""
    settings = load_settings()
    
    # Safe theme access with validation
    theme_name = settings.get('theme', 'frost')
    if theme_name not in THEMES:
        theme_name = 'frost'
    current_theme = THEMES[theme_name]
    
    # Safe access with defaults
    x = settings.get('window_position', {}).get('x', 100)
    y = settings.get('window_position', {}).get('y', 100)
    width = settings.get('window_size', {}).get('width', 1200)
    height = settings.get('window_size', {}).get('height', 800)
    
    # HTML content with embedded CSS
    html_content = f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Sigmi Hub</title>
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
                overflow: hidden;
                height: 100vh;
                user-select: none;
            }}
            
            /* Loading Overlay */
            .loading-overlay {{
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: {current_theme['background']};
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                z-index: 9999;
                backdrop-filter: blur(20px);
            }}
            
            .loading-spinner {{
                width: 60px;
                height: 60px;
                border: 4px solid {current_theme['glass_border']};
                border-top: 4px solid {current_theme['primary']};
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin-bottom: 20px;
            }}
            
            .loading-text {{
                font-size: 18px;
                font-weight: 600;
                color: {current_theme['text']};
                background: linear-gradient(135deg, {current_theme['primary']}, {current_theme['secondary']});
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }}
            
            .loading-subtext {{
                font-size: 14px;
                color: {current_theme['text_secondary']};
                margin-top: 10px;
            }}
            
            @keyframes spin {{
                0% {{ transform: rotate(0deg); }}
                100% {{ transform: rotate(360deg); }}
            }}
            
            .app-container {{
                width: 100vw;
                height: 100vh;
                display: flex;
                flex-direction: column;
                backdrop-filter: blur(40px);
                position: relative;
                opacity: 0;
                transition: opacity 0.5s ease-in-out;
            }}
            
            .app-container.loaded {{
                opacity: 1;
            }}
            
            /* Title Bar */
            .title-bar {{
                height: 60px;
                background: {current_theme['glass']};
                backdrop-filter: blur(30px);
                border-bottom: 1px solid {current_theme['glass_border']};
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 0 25px;
                cursor: move;
                box-shadow: {current_theme['shadow']};
            }}
            
            .title-content {{
                display: flex;
                align-items: center;
                gap: 15px;
            }}
            
            .title-icon {{
                font-size: 24px;
                animation: float 3s ease-in-out infinite;
            }}
            
            @keyframes float {{
                0%, 100% {{ transform: translateY(0px); }}
                50% {{ transform: translateY(-5px); }}
            }}
            
            .title-text {{
                font-size: 20px;
                font-weight: 700;
                background: linear-gradient(135deg, {current_theme['primary']}, {current_theme['secondary']});
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }}
            
            .window-controls {{
                display: flex;
                gap: 12px;
            }}
            
            .control-btn {{
                width: 32px;
                height: 32px;
                background: {current_theme['glass']};
                border: 1px solid {current_theme['glass_border']};
                border-radius: 8px;
                color: {current_theme['text']};
                font-size: 18px;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            }}
            
            .control-btn:hover {{
                background: {current_theme['primary']};
                color: white;
                transform: translateY(-2px);
                box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
            }}
            
            .main-content {{
                flex: 1;
                display: flex;
                overflow: hidden;
            }}
            
            /* Sidebar */
            .sidebar {{
                width: 280px;
                background: {current_theme['glass']};
                backdrop-filter: blur(30px);
                border-right: 1px solid {current_theme['glass_border']};
                padding: 30px 0;
                display: flex;
                flex-direction: column;
            }}
            
            .nav-section {{
                margin-bottom: 20px;
            }}
            
            .nav-item {{
                padding: 16px 25px;
                color: {current_theme['text_secondary']};
                cursor: pointer;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                display: flex;
                align-items: center;
                font-weight: 600;
                border-left: 4px solid transparent;
                margin: 5px 15px;
                border-radius: 12px;
            }}
            
            .nav-item:hover {{
                background: rgba(255, 255, 255, 0.2);
                color: {current_theme['text']};
                transform: translateX(5px);
            }}
            
            .nav-item.active {{
                background: rgba(255, 255, 255, 0.25);
                color: {current_theme['primary']};
                border-left-color: {current_theme['primary']};
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
            }}
            
            .nav-icon {{
                margin-right: 15px;
                font-size: 18px;
                transition: transform 0.3s ease;
            }}
            
            .nav-item:hover .nav-icon {{
                transform: scale(1.1);
            }}
            
            .content-area {{
                flex: 1;
                padding: 40px;
                overflow-y: auto;
            }}
            
            .content-section {{
                display: none;
                animation: fadeIn 0.5s ease-in-out;
            }}
            
            .content-section.active {{
                display: block;
            }}
            
            @keyframes fadeIn {{
                from {{ opacity: 0; transform: translateY(20px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}
            
            /* Method Cards */
            .method-card {{
                background: {current_theme['glass']};
                backdrop-filter: blur(30px);
                border: 1px solid {current_theme['glass_border']};
                border-radius: 20px;
                padding: 35px;
                margin-bottom: 25px;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                box-shadow: {current_theme['shadow']};
            }}
            
            .method-card:hover {{
                transform: translateY(-5px);
                box-shadow: {current_theme['hover_shadow']};
                border-color: {current_theme['primary']};
            }}
            
            .card-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 20px;
            }}
            
            h2 {{
                font-size: 24px;
                color: {current_theme['text']};
                font-weight: 700;
            }}
            
            .method-badge {{
                padding: 6px 12px;
                border-radius: 8px;
                font-size: 12px;
                font-weight: 700;
                color: white;
            }}
            
            .method-badge.success {{
                background: linear-gradient(135deg, #10b981, #059669);
            }}
            
            .method-badge.warning {{
                background: linear-gradient(135deg, #f59e0b, #d97706);
            }}
            
            p {{
                color: {current_theme['text_secondary']};
                line-height: 1.6;
                margin-bottom: 25px;
                font-size: 15px;
            }}
            
            .input-group {{
                display: flex;
                gap: 20px;
                margin: 25px 0;
                align-items: center;
            }}
            
            .input-container {{
                flex: 1;
                position: relative;
            }}
            
            .url-input {{
                width: 100%;
                padding: 16px 20px 16px 50px;
                background: rgba(255, 255, 255, 0.15);
                border: 1px solid {current_theme['glass_border']};
                border-radius: 12px;
                color: {current_theme['text']};
                font-size: 16px;
                transition: all 0.3s ease;
                backdrop-filter: blur(10px);
            }}
            
            .url-input:focus {{
                outline: none;
                border-color: {current_theme['primary']};
                box-shadow: 0 0 0 3px {current_theme['primary']}20;
                transform: translateY(-2px);
            }}
            
            .input-icon {{
                position: absolute;
                left: 20px;
                top: 50%;
                transform: translateY(-50%);
                font-size: 18px;
                color: {current_theme['text_secondary']};
            }}
            
            .bypass-button {{
                padding: 16px 32px;
                background: linear-gradient(135deg, {current_theme['primary']}, {current_theme['secondary']});
                border: none;
                border-radius: 12px;
                color: white;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                position: relative;
                overflow: hidden;
            }}
            
            .bypass-button:hover {{
                transform: translateY(-3px);
                box-shadow: 0 10px 25px {current_theme['primary']}40;
            }}
            
            .bypass-button:active {{
                transform: translateY(-1px);
            }}
            
            .card-footer {{
                margin-top: 20px;
                padding-top: 15px;
                border-top: 1px solid {current_theme['glass_border']};
            }}
            
            .info-text {{
                color: {current_theme['text_secondary']};
                font-size: 13px;
            }}
            
            /* Settings */
            .settings-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 25px;
                margin-top: 30px;
            }}
            
            .setting-group {{
                background: {current_theme['glass']};
                backdrop-filter: blur(30px);
                border: 1px solid {current_theme['glass_border']};
                border-radius: 20px;
                padding: 30px;
                transition: all 0.3s ease;
                box-shadow: {current_theme['shadow']};
            }}
            
            .setting-group:hover {{
                transform: translateY(-3px);
                box-shadow: {current_theme['hover_shadow']};
            }}
            
            .setting-title {{
                font-size: 18px;
                font-weight: 600;
                margin-bottom: 20px;
                color: {current_theme['text']};
                display: flex;
                align-items: center;
                gap: 10px;
            }}
            
            .theme-options {{
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 15px;
            }}
            
            .theme-option {{
                padding: 20px;
                border: 2px solid {current_theme['glass_border']};
                border-radius: 15px;
                cursor: pointer;
                transition: all 0.3s ease;
                text-align: center;
                background: rgba(255, 255, 255, 0.1);
            }}
            
            .theme-option:hover {{
                transform: scale(1.05);
                border-color: {current_theme['primary']};
            }}
            
            .theme-option.active {{
                border-color: {current_theme['primary']};
                box-shadow: 0 0 0 2px {current_theme['primary']}20;
            }}
            
            .theme-preview {{
                width: 100%;
                height: 60px;
                border-radius: 10px;
                margin-bottom: 10px;
                border: 1px solid {current_theme['glass_border']};
            }}
            
            .theme-name {{
                font-weight: 600;
                color: {current_theme['text']};
                font-size: 14px;
            }}
            
            /* Tools Section */
            .tools-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-top: 30px;
            }}
            
            .tool-card {{
                background: {current_theme['glass']};
                backdrop-filter: blur(30px);
                border: 1px solid {current_theme['glass_border']};
                border-radius: 15px;
                padding: 25px;
                text-align: center;
                transition: all 0.3s ease;
                cursor: pointer;
            }}
            
            .tool-card:hover {{
                transform: translateY(-5px);
                box-shadow: {current_theme['hover_shadow']};
            }}
            
            .tool-icon {{
                font-size: 32px;
                margin-bottom: 15px;
            }}
            
            /* Update Modal */
            .update-modal {{
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.5);
                display: none;
                justify-content: center;
                align-items: center;
                z-index: 10000;
            }}
            
            .update-modal.active {{
                display: flex;
            }}
            
            .update-content {{
                background: {current_theme['glass']};
                backdrop-filter: blur(40px);
                border: 1px solid {current_theme['glass_border']};
                border-radius: 20px;
                padding: 40px;
                max-width: 500px;
                width: 90%;
                text-align: center;
                box-shadow: {current_theme['shadow']};
            }}
            
            .update-icon {{
                font-size: 48px;
                margin-bottom: 20px;
            }}
            
            .update-buttons {{
                display: flex;
                gap: 15px;
                justify-content: center;
                margin-top: 25px;
            }}
            
            .update-button {{
                padding: 12px 24px;
                border: none;
                border-radius: 10px;
                font-size: 14px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
            }}
            
            .update-confirm {{
                background: linear-gradient(135deg, #10b981, #059669);
                color: white;
            }}
            
            .update-cancel {{
                background: {current_theme['glass']};
                border: 1px solid {current_theme['glass_border']};
                color: {current_theme['text']};
            }}
            
            /* Scrollbar */
            .content-area::-webkit-scrollbar {{
                width: 8px;
            }}
            
            .content-area::-webkit-scrollbar-track {{
                background: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
            }}
            
            .content-area::-webkit-scrollbar-thumb {{
                background: linear-gradient(135deg, {current_theme['primary']}, {current_theme['secondary']});
                border-radius: 10px;
            }}
        </style>
    </head>
    <body>
        <!-- Loading Overlay -->
        <div class="loading-overlay" id="loadingOverlay">
            <div class="loading-spinner"></div>
            <div class="loading-text">Sigmi Hub</div>
            <div class="loading-subtext">Loading...</div>
        </div>

        <!-- Update Modal -->
        <div class="update-modal" id="updateModal">
            <div class="update-content">
                <div class="update-icon">🚀</div>
                <h2 style="margin-bottom: 15px; color: {current_theme['text']};">Update Available!</h2>
                <p style="color: {current_theme['text_secondary']}; margin-bottom: 10px;" id="updateMessage">
                    A new version is available for download.
                </p>
                <p style="color: {current_theme['text_secondary']}; font-size: 14px;">
                    The application will restart to complete the update.
                </p>
                <div class="update-buttons">
                    <button class="update-button update-confirm" onclick="confirmUpdate()">Update Now</button>
                    <button class="update-button update-cancel" onclick="closeUpdateModal()">Later</button>
                </div>
            </div>
        </div>

        <div class="app-container" id="appContainer">
            <!-- Title Bar -->
            <div class="title-bar" id="titleBar">
                <div class="title-content">
                    <div class="title-icon">🚀</div>
                    <div class="title-text">Sigmi Hub</div>
                </div>
                <div class="window-controls">
                    <button class="control-btn close-btn" onclick="window.closeApp()">×</button>
                </div>
            </div>

            <!-- Main Content -->
            <div class="main-content">
                <!-- Sidebar -->
                <div class="sidebar">
                    <div class="nav-section">
                        <div class="nav-item active" data-section="bypasses">
                            <span class="nav-icon">🌐</span>
                            URL Bypass
                        </div>
                        <div class="nav-item" data-section="tools">
                            <span class="nav-icon">🛠️</span>
                            Tools
                        </div>
                        <div class="nav-item" data-section="settings">
                            <span class="nav-icon">⚙️</span>
                            Settings
                        </div>
                    </div>
                </div>

                <!-- Content Area -->
                <div class="content-area">
                    <!-- Bypasses Section -->
                    <div class="content-section active" id="bypasses-section">
                        <div class="method-card">
                            <div class="card-header">
                                <h2>Google Translate Bypass</h2>
                                <div class="method-badge success">Working</div>
                            </div>
                            <p>Access blocked websites through Google Translate's proxy service. Simple and effective.</p>
                            
                            <div class="input-group">
                                <div class="input-container">
                                    <input type="text" id="urlInput" placeholder="https://example.com" class="url-input">
                                    <span class="input-icon">🔗</span>
                                </div>
                                <button class="bypass-button" id="bypassBtn">Bypass Now</button>
                            </div>
                            
                            <div class="card-footer">
                                <span class="info-text">✓ Fast • ✓ Reliable • ✓ No installation required</span>
                            </div>
                        </div>

                        <div class="method-card">
                            <div class="card-header">
                                <h2>Alternative Methods</h2>
                                <div class="method-badge warning">Coming Soon</div>
                            </div>
                            <p>Additional bypass methods and proxy services will be available in future updates.</p>
                            <button class="bypass-button" style="background: linear-gradient(135deg, {current_theme['accent']}, {current_theme['secondary']}); opacity: 0.7;" disabled>
                                Available Soon
                            </button>
                        </div>
                    </div>

                    <!-- Tools Section -->
                    <div class="content-section" id="tools-section">
                        <h2 style="margin-bottom: 25px; color: {current_theme['text']};">Utility Tools</h2>
                        <div class="tools-grid">
                            <div class="tool-card">
                                <div class="tool-icon">🔍</div>
                                <h3>URL Checker</h3>
                                <p style="color: {current_theme['text_secondary']}; font-size: 14px; margin-top: 10px;">Check if a website is accessible</p>
                            </div>
                            <div class="tool-card">
                                <div class="tool-icon">📊</div>
                                <h3>Connection Test</h3>
                                <p style="color: {current_theme['text_secondary']}; font-size: 14px; margin-top: 10px;">Test your connection speed</p>
                            </div>
                            <div class="tool-card">
                                <div class="tool-icon">🛡️</div>
                                <h3>Security Scan</h3>
                                <p style="color: {current_theme['text_secondary']}; font-size: 14px; margin-top: 10px;">Basic security checks</p>
                            </div>
                        </div>
                    </div>

                    <!-- Settings Section -->
                    <div class="content-section" id="settings-section">
                        <h2 style="margin-bottom: 25px; color: {current_theme['text']};">Preferences</h2>
                        
                        <div class="settings-grid">
                            <div class="setting-group">
                                <div class="setting-title">
                                    <span>🎨</span> Theme Settings
                                </div>
                                <div class="theme-options">
                                    <div class="theme-option {'active' if settings.get('theme') == 'frost' else ''}" data-theme="frost">
                                        <div class="theme-preview" style="background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);"></div>
                                        <div class="theme-name">Frost Glass</div>
                                    </div>
                                    <div class="theme-option {'active' if settings.get('theme') == 'midnight' else ''}" data-theme="midnight">
                                        <div class="theme-preview" style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);"></div>
                                        <div class="theme-name">Midnight Glass</div>
                                    </div>
                                    <div class="theme-option {'active' if settings.get('theme') == 'sunset' else ''}" data-theme="sunset">
                                        <div class="theme-preview" style="background: linear-gradient(135deg, #fef3c7 0%, #fbbf24 100%);"></div>
                                        <div class="theme-name">Sunset Glass</div>
                                    </div>
                                    <div class="theme-option {'active' if settings.get('theme') == 'ocean' else ''}" data-theme="ocean">
                                        <div class="theme-preview" style="background: linear-gradient(135deg, #dbeafe 0%, #93c5fd 100%);"></div>
                                        <div class="theme-name">Ocean Glass</div>
                                    </div>
                                    <div class="theme-option {'active' if settings.get('theme') == 'purple' else ''}" data-theme="purple">
                                        <div class="theme-preview" style="background: linear-gradient(135deg, #a78bfa 0%, #7c3aed 50%, #5b21b6 100%);"></div>
                                        <div class="theme-name">Purple Haze</div>
                                    </div>
                                </div>
                            </div>

                            <div class="setting-group">
                                <div class="setting-title">
                                    <span>⚡</span> Application
                                </div>
                                <p style="color: {current_theme['text_secondary']}; margin-bottom: 20px; line-height: 1.6;">
                                    Sigmi Hub {VERSION}<br>
                                    Simple and effective web bypass utility
                                </p>
                                <button class="bypass-button" style="width: 100%;" onclick="checkForUpdates()">
                                    Check for Updates
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script>
            let updateAvailable = false;
            let onlineVersion = '';

            // Loading screen management
            function hideLoadingScreen() {{
                const loadingOverlay = document.getElementById('loadingOverlay');
                const appContainer = document.getElementById('appContainer');
                
                // Add fade out animation to loading screen
                loadingOverlay.style.opacity = '0';
                loadingOverlay.style.transition = 'opacity 0.5s ease-in-out';
                
                // Show main app with fade in
                appContainer.classList.add('loaded');
                
                // Remove loading overlay after animation
                setTimeout(() => {{
                    loadingOverlay.style.display = 'none';
                }}, 500);
            }}

            // Theme switching with loading screen
            function showThemeLoadingScreen(themeName) {{
                const loadingOverlay = document.getElementById('loadingOverlay');
                const loadingText = loadingOverlay.querySelector('.loading-text');
                const loadingSubtext = loadingOverlay.querySelector('.loading-subtext');
                
                // Update loading text
                loadingText.textContent = 'Switching Theme';
                loadingSubtext.textContent = `Applying ${{themeName}} theme...`;
                
                // Show loading screen
                loadingOverlay.style.display = 'flex';
                loadingOverlay.style.opacity = '1';
                
                // Hide main app
                document.getElementById('appContainer').classList.remove('loaded');
            }}

            // Update modal functions
            function showUpdateModal(version) {{
                const modal = document.getElementById('updateModal');
                const message = document.getElementById('updateMessage');
                message.textContent = `Version ${{version}} is ready to update!`;
                modal.classList.add('active');
            }}

            function closeUpdateModal() {{
                const modal = document.getElementById('updateModal');
                modal.classList.remove('active');
            }}

            function confirmUpdate() {{
                if (window.pywebview) {{
                    pywebview.api.performUpdate();
                }}
                closeUpdateModal();
            }}

            // Bypass functionality
            document.getElementById('bypassBtn').addEventListener('click', function() {{
                const urlInput = document.getElementById('urlInput');
                const url = urlInput.value.trim();
                
                if (!url) {{
                    urlInput.style.animation = 'shake 0.5s ease-in-out';
                    setTimeout(() => urlInput.style.animation = '', 500);
                    return;
                }}

                let destination = url;
                if (!/^https?:\\/\\//i.test(destination)) {{
                    destination = "https://" + destination;
                }}
                
                const bypassUrl = `https://translate.google.com/translate?sl=auto&tl=en&u=${{encodeURIComponent(destination)}}`;
                window.open(bypassUrl, '_blank');
            }});

            // Navigation
            function setupNavigation() {{
                const navItems = document.querySelectorAll('.nav-item');
                const contentSections = document.querySelectorAll('.content-section');
                
                navItems.forEach(item => {{
                    item.addEventListener('click', function() {{
                        const section = this.getAttribute('data-section');
                        
                        // Update active states
                        navItems.forEach(nav => nav.classList.remove('active'));
                        this.classList.add('active');
                        
                        contentSections.forEach(content => content.classList.remove('active'));
                        document.getElementById(`${{section}}-section`).classList.add('active');
                    }});
                }});
            }}

            // Theme switching
            function setupThemes() {{
                const themeOptions = document.querySelectorAll('.theme-option');
                
                themeOptions.forEach(option => {{
                    option.addEventListener('click', function() {{
                        const theme = this.getAttribute('data-theme');
                        const themeName = this.querySelector('.theme-name').textContent;
                        
                        // Show loading screen
                        showThemeLoadingScreen(themeName);
                        
                        // Update active state
                        themeOptions.forEach(opt => opt.classList.remove('active'));
                        this.classList.add('active');
                        
                        // Save theme and reload with delay to show loading screen
                        if (window.pywebview) {{
                            pywebview.api.changeTheme(theme);
                            setTimeout(() => {{
                                if (window.pywebview) {{
                                    pywebview.api.restart_app();
                                }}
                            }}, 1500); // Show loading screen for 1.5 seconds
                        }}
                    }});
                }});
            }}

            // Update checking
            function checkForUpdates() {{
                const button = event.target;
                const originalText = button.textContent;
                
                button.textContent = 'Checking...';
                button.disabled = true;
                
                if (window.pywebview) {{
                    pywebview.api.checkUpdates().then(result => {{
                        if (result.available) {{
                            showUpdateModal(result.online_version);
                        }} else {{
                            button.textContent = 'Up to date ✓';
                            setTimeout(() => {{
                                button.textContent = originalText;
                                button.disabled = false;
                            }}, 2000);
                        }}
                    }});
                }} else {{
                    setTimeout(() => {{
                        button.textContent = 'Up to date ✓';
                        setTimeout(() => {{
                            button.textContent = originalText;
                            button.disabled = false;
                        }}, 2000);
                    }}, 1500);
                }}
            }}

            // Initialize
            document.addEventListener('DOMContentLoaded', function() {{
                // Set up event listeners
                document.getElementById('urlInput').addEventListener('keypress', function(e) {{
                    if (e.key === 'Enter') document.getElementById('bypassBtn').click();
                }});
                
                // Initialize components
                setupNavigation();
                setupThemes();
                
                // Add shake animation
                const style = document.createElement('style');
                style.textContent = `
                    @keyframes shake {{
                        0%, 100% {{ transform: translateX(0); }}
                        25% {{ transform: translateX(-8px); }}
                        75% {{ transform: translateX(8px); }}
                    }}
                `;
                document.head.appendChild(style);
                
                // Hide loading screen after everything is loaded
                setTimeout(hideLoadingScreen, 1000);
            }});

            // Close app function
            window.closeApp = function() {{
                if (window.pywebview) {{
                    pywebview.api.close_app();
                }}
            }};
        </script>
    </body>
    </html>
    '''
    
    # Create webview window with icon support
    try:
        # Try to find icon file in the same directory
        icon_path = None
        possible_icons = ['icon.ico', 'app.ico', 'logo.ico', 'icon.png', 'app.png', 'logo.png']
        
        for icon_file in possible_icons:
            if os.path.exists(icon_file):
                icon_path = icon_file
                break
        
        window = webview.create_window(
            'Sigmi Hub',
            html=html_content,
            x=x, y=y, width=width, height=height,
            resizable=True,
            frameless=True,
            easy_drag=True,
            js_api=BypassAPI()
        )
        
    except Exception as e:
        print(f"Error creating window: {e}")
        sys.exit(1)
    
    def on_closed():
        try:
            settings = load_settings()
            geometry = window.get_position()
            size = window.get_size()
            settings['window_position'] = {'x': geometry[0], 'y': geometry[1]}
            settings['window_size'] = {'width': size[0], 'height': size[1]}
            save_settings(settings)
        except Exception as e:
            print(f"Error saving window position: {e}")
    
    window.events.closed += on_closed
    webview.start()

def main():
    """Main entry point"""
    print(f"Starting Sigmi Hub {VERSION}...")
    create_webview_app()

if __name__ == '__main__':
    main()
