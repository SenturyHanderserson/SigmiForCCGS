import pywebview
import threading
import time
import json
import os
from flask import Flask, render_template_string, request, jsonify

# Create Flask app to serve our HTML/CSS/JS
app = Flask(__name__)

# Theme configuration
THEMES = {
    'white': {
        'name': 'Frost Glass',
        'background': 'linear-gradient(135deg, rgba(255, 255, 255, 0.85) 0%, rgba(255, 255, 255, 0.95) 100%)',
        'primary': '#7877C6',
        'secondary': '#FF6B6B',
        'text': '#333',
        'text_secondary': '#555',
        'border': 'rgba(255, 255, 255, 0.8)',
        'accent_glow': 'rgba(120, 119, 198, 0.08)'
    },
    'blue': {
        'name': 'Ocean Glass',
        'background': 'linear-gradient(135deg, rgba(100, 125, 220, 0.85) 0%, rgba(80, 100, 200, 0.95) 100%)',
        'primary': '#4FC3F7',
        'secondary': '#29B6F6',
        'text': '#FFFFFF',
        'text_secondary': 'rgba(255, 255, 255, 0.9)',
        'border': 'rgba(255, 255, 255, 0.2)',
        'accent_glow': 'rgba(79, 195, 247, 0.15)'
    },
    'purple': {
        'name': 'Royal Glass',
        'background': 'linear-gradient(135deg, rgba(120, 80, 200, 0.85) 0%, rgba(100, 60, 180, 0.95) 100%)',
        'primary': '#BA68C8',
        'secondary': '#AB47BC',
        'text': '#FFFFFF',
        'text_secondary': 'rgba(255, 255, 255, 0.9)',
        'border': 'rgba(255, 255, 255, 0.2)',
        'accent_glow': 'rgba(186, 104, 200, 0.15)'
    },
    'black': {
        'name': 'Obsidian Glass',
        'background': 'linear-gradient(135deg, rgba(30, 30, 40, 0.95) 0%, rgba(20, 20, 30, 0.98) 100%)',
        'primary': '#BB86FC',
        'secondary': '#03DAC6',
        'text': '#FFFFFF',
        'text_secondary': 'rgba(255, 255, 255, 0.8)',
        'border': 'rgba(255, 255, 255, 0.1)',
        'accent_glow': 'rgba(187, 134, 252, 0.15)'
    }
}

# Settings storage
SETTINGS_FILE = 'bypass_settings.json'

def load_settings():
    """Load settings from file"""
    default_settings = {
        'theme': 'white',
        'window_position': {'x': 100, 'y': 100},
        'window_size': {'width': 1000, 'height': 700}
    }
    
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    
    return default_settings

def save_settings(settings):
    """Save settings to file"""
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=2)
    except Exception as e:
        print(f"Error saving settings: {e}")

# Load initial settings
current_settings = load_settings()

def get_html_content():
    """Generate HTML content with current theme"""
    current_theme = THEMES[current_settings['theme']]
    
    return f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bypass Toolkit</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: transparent;
            color: {current_theme['text']};
            overflow: hidden;
            height: 100vh;
            user-select: none;
        }}

        .app-container {{
            width: 100vw;
            height: 100vh;
            background: {current_theme['background']};
            backdrop-filter: blur(40px) saturate(200%);
            -webkit-backdrop-filter: blur(40px) saturate(200%);
            border: 1px solid {current_theme['border']};
            display: flex;
            flex-direction: column;
            position: relative;
            box-shadow: 
                0 25px 50px rgba(0, 0, 0, 0.1),
                0 0 0 1px rgba(255, 255, 255, 0.1),
                inset 0 1px 0 rgba(255, 255, 255, 0.1);
        }}

        .app-container::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: 
                radial-gradient(circle at 20% 80%, {current_theme['accent_glow']} 0%, transparent 50%),
                radial-gradient(circle at 80% 20%, rgba(255, 107, 107, 0.05) 0%, transparent 50%);
            pointer-events: none;
            z-index: -1;
        }}

        /* Title Bar */
        .title-bar {{
            height: 60px;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(20px);
            border-bottom: 1px solid {current_theme['border']};
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 25px;
            position: relative;
            cursor: move;
        }}

        .title-bar::after {{
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            height: 1px;
            background: linear-gradient(90deg, 
                transparent 0%, 
                rgba(255, 255, 255, 0.2) 50%, 
                transparent 100%);
        }}

        .title-content {{
            display: flex;
            align-items: center;
            gap: 15px;
        }}

        .title-icon {{
            font-size: 24px;
            filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
        }}

        .title-text {{
            font-size: 20px;
            font-weight: 700;
            background: linear-gradient(135deg, {current_theme['primary']}, {current_theme['secondary']});
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }}

        .window-controls {{
            display: flex;
            gap: 12px;
        }}

        .control-btn {{
            width: 32px;
            height: 32px;
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid {current_theme['border']};
            border-radius: 8px;
            color: {current_theme['text']};
            font-size: 18px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        }}

        .control-btn:hover {{
            background: rgba(255, 255, 255, 0.2);
            transform: scale(1.1);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }}

        .close-btn:hover {{
            background: rgba(255, 107, 107, 0.2);
            border-color: rgba(255, 107, 107, 0.3);
            color: #FF6B6B;
        }}

        /* Main Content */
        .main-content {{
            flex: 1;
            display: flex;
            overflow: hidden;
        }}

        /* Sidebar */
        .sidebar {{
            width: 280px;
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(20px);
            border-right: 1px solid {current_theme['border']};
            padding: 30px 0;
            display: flex;
            flex-direction: column;
        }}

        .nav-section {{
            margin-bottom: 20px;
        }}

        .nav-item {{
            padding: 16px 30px;
            color: {current_theme['text_secondary']};
            cursor: pointer;
            transition: all 0.4s ease;
            display: flex;
            align-items: center;
            font-weight: 600;
            border-left: 4px solid transparent;
            position: relative;
            margin: 5px 15px;
            border-radius: 12px;
        }}

        .nav-glow {{
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(135deg, {current_theme['accent_glow']}, transparent);
            border-radius: 12px;
            opacity: 0;
            transition: opacity 0.3s ease;
        }}

        .nav-item:hover {{
            background: rgba(255, 255, 255, 0.1);
            color: {current_theme['text']};
            border-left-color: {current_theme['primary']};
            transform: translateX(5px);
        }}

        .nav-item:hover .nav-glow {{
            opacity: 1;
        }}

        .nav-item.active {{
            background: linear-gradient(135deg, {current_theme['accent_glow']}, transparent);
            color: {current_theme['primary']};
            border-left-color: {current_theme['primary']};
            box-shadow: 0 8px 25px {current_theme['accent_glow']};
        }}

        .nav-icon {{
            margin-right: 15px;
            font-size: 18px;
        }}

        .nav-subitems {{
            margin-left: 30px;
            margin-top: 10px;
        }}

        .nav-subitem {{
            padding: 14px 20px;
            color: {current_theme['text_secondary']};
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            font-size: 14px;
            border-left: 3px solid transparent;
            border-radius: 10px;
            margin: 4px 0;
            justify-content: space-between;
            position: relative;
        }}

        .nav-subitem:hover {{
            background: rgba(255, 255, 255, 0.05);
            color: {current_theme['primary']};
            transform: translateX(8px);
        }}

        .nav-subitem.active {{
            background: linear-gradient(135deg, {current_theme['accent_glow']}, transparent);
            color: {current_theme['primary']};
            border-left-color: {current_theme['primary']};
        }}

        .nav-badge {{
            background: {current_theme['accent_glow']};
            padding: 4px 8px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 600;
            color: {current_theme['primary']};
        }}

        /* Content Area */
        .content-area {{
            flex: 1;
            padding: 40px;
            overflow-y: auto;
        }}

        .content-section {{
            display: none;
        }}

        .content-section.active {{
            display: block;
            animation: fadeIn 0.4s ease;
        }}

        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(15px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        .section-header {{
            display: flex;
            align-items: center;
            gap: 20px;
            margin-bottom: 35px;
        }}

        h2 {{
            font-size: 32px;
            color: {current_theme['text']};
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
            font-weight: 700;
        }}

        .section-badge {{
            background: linear-gradient(135deg, {current_theme['primary']}, {current_theme['secondary']});
            padding: 8px 16px;
            border-radius: 10px;
            font-size: 12px;
            font-weight: 700;
            color: white;
            box-shadow: 0 4px 15px {current_theme['accent_glow']};
        }}

        /* Method Cards */
        .method-card {{
            background: linear-gradient(135deg, 
                rgba(255, 255, 255, 0.1) 0%, 
                rgba(255, 255, 255, 0.05) 100%);
            backdrop-filter: blur(20px);
            border: 1px solid {current_theme['border']};
            border-radius: 20px;
            padding: 35px;
            margin-bottom: 30px;
            transition: all 0.4s ease;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.08);
            position: relative;
            overflow: hidden;
        }}

        .method-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
            transition: left 0.8s ease;
        }}

        .method-card:hover::before {{
            left: 100%;
        }}

        .method-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 25px 50px rgba(0, 0, 0, 0.12);
            border-color: {current_theme['primary']};
        }}

        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }}

        h3 {{
            font-size: 22px;
            color: {current_theme['text']};
            text-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
            font-weight: 600;
        }}

        .method-badge {{
            padding: 6px 12px;
            border-radius: 8px;
            font-size: 11px;
            font-weight: 700;
            color: white;
        }}

        .method-badge.success {{
            background: linear-gradient(135deg, #4CAF50, #45a049);
            box-shadow: 0 4px 15px rgba(76, 175, 80, 0.2);
        }}

        .method-badge.warning {{
            background: linear-gradient(135deg, #FF9800, #F57C00);
            box-shadow: 0 4px 15px rgba(255, 152, 0, 0.2);
        }}

        p {{
            color: {current_theme['text_secondary']};
            line-height: 1.7;
            margin-bottom: 25px;
            font-size: 15px;
        }}

        .input-group {{
            display: flex;
            gap: 20px;
            margin: 30px 0;
            align-items: center;
        }}

        .input-container {{
            flex: 1;
            position: relative;
        }}

        .url-input {{
            width: 100%;
            padding: 18px 20px 18px 50px;
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid {current_theme['border']};
            border-radius: 14px;
            color: {current_theme['text']};
            font-size: 16px;
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.05);
        }}

        .url-input::placeholder {{
            color: {current_theme['text_secondary']};
        }}

        .url-input:focus {{
            outline: none;
            background: rgba(255, 255, 255, 0.15);
            border-color: {current_theme['primary']};
            box-shadow: 0 0 0 3px {current_theme['accent_glow']},
                        0 12px 35px rgba(0, 0, 0, 0.08);
        }}

        .input-icon {{
            position: absolute;
            left: 20px;
            top: 50%;
            transform: translateY(-50%);
            font-size: 18px;
            color: {current_theme['text_secondary']};
        }}

        .bypass-button, .placeholder-button {{
            padding: 18px 35px;
            background: linear-gradient(135deg, {current_theme['primary']}, {current_theme['secondary']});
            border: none;
            border-radius: 14px;
            color: white;
            font-size: 16px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
            box-shadow: 0 8px 25px {current_theme['accent_glow']};
            min-width: 140px;
        }}

        .button-glow {{
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
            transition: left 0.6s;
        }}

        .bypass-button:hover .button-glow, .placeholder-button:hover .button-glow {{
            left: 100%;
        }}

        .bypass-button:hover, .placeholder-button:hover {{
            transform: translateY(-3px);
            box-shadow: 0 15px 35px {current_theme['accent_glow']};
        }}

        .bypass-button:active, .placeholder-button:active {{
            transform: translateY(0);
            box-shadow: 0 5px 20px {current_theme['accent_glow']};
        }}

        .placeholder-button {{
            background: linear-gradient(135deg, #9e9e9e, #757575);
            box-shadow: 0 8px 25px rgba(158, 158, 158, 0.3);
        }}

        .placeholder-button:hover {{
            box-shadow: 0 15px 35px rgba(158, 158, 158, 0.4);
        }}

        .card-footer {{
            margin-top: 20px;
            padding-top: 15px;
            border-top: 1px solid {current_theme['border']};
        }}

        .info-text {{
            color: {current_theme['text_secondary']};
            font-size: 13px;
        }}

        /* Settings Page */
        .settings-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 25px;
            margin-top: 30px;
        }}

        .setting-group {{
            background: linear-gradient(135deg, 
                rgba(255, 255, 255, 0.1) 0%, 
                rgba(255, 255, 255, 0.05) 100%);
            backdrop-filter: blur(20px);
            border: 1px solid {current_theme['border']};
            border-radius: 20px;
            padding: 30px;
            transition: all 0.3s ease;
        }}

        .setting-group:hover {{
            transform: translateY(-3px);
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
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
            border: 2px solid {current_theme['border']};
            border-radius: 15px;
            cursor: pointer;
            transition: all 0.3s ease;
            text-align: center;
            background: rgba(255, 255, 255, 0.05);
            position: relative;
        }}

        .theme-option:hover {{
            transform: scale(1.05);
            border-color: {current_theme['primary']};
        }}

        .theme-option.active {{
            border-color: {current_theme['primary']};
            box-shadow: 0 0 0 2px {current_theme['accent_glow']};
        }}

        .theme-option.active::after {{
            content: '✓';
            position: absolute;
            top: 10px;
            right: 10px;
            background: {current_theme['primary']};
            color: white;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            font-size: 14px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        .theme-preview {{
            width: 100%;
            height: 60px;
            border-radius: 10px;
            margin-bottom: 10px;
            border: 1px solid {current_theme['border']};
        }}

        .theme-name {{
            font-weight: 600;
            color: {current_theme['text']};
        }}

        /* Theme Transition */
        .theme-transition {{
            animation: themeChange 0.5s ease-in-out;
        }}

        @keyframes themeChange {{
            0% {{ opacity: 1; }}
            50% {{ opacity: 0.7; }}
            100% {{ opacity: 1; }}
        }}

        /* Scrollbar */
        .content-area::-webkit-scrollbar {{
            width: 10px;
        }}

        .content-area::-webkit-scrollbar-track {{
            background: rgba(255, 255, 255, 0.05);
            border-radius: 5px;
        }}

        .content-area::-webkit-scrollbar-thumb {{
            background: linear-gradient(135deg, {current_theme['primary']}, {current_theme['secondary']});
            border-radius: 5px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }}

        .content-area::-webkit-scrollbar-thumb:hover {{
            background: linear-gradient(135deg, {current_theme['secondary']}, {current_theme['primary']});
        }}

        /* Animations */
        @keyframes shake {{
            0%, 100% {{ transform: translateX(0); }}
            25% {{ transform: translateX(-10px); }}
            75% {{ transform: translateX(10px); }}
        }}

        .shake {{
            animation: shake 0.5s ease-in-out;
        }}

        @keyframes fadeIn {{
            from {{ 
                opacity: 0; 
                transform: translateY(20px); 
            }}
            to {{ 
                opacity: 1; 
                transform: translateY(0); 
            }}
        }}

        .fade-in {{
            animation: fadeIn 0.6s ease-out;
        }}

        /* Loading Animation */
        .button-loader {{
            display: none;
        }}

        .spinner {{
            width: 20px;
            height: 20px;
            border: 2px solid transparent;
            border-top: 2px solid white;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }}

        .bypass-button.loading .button-text {{
            display: none;
        }}

        .bypass-button.loading .button-loader {{
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}

        /* Coming Soon */
        .coming-soon {{
            text-align: center;
            padding: 60px 40px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 20px;
            border: 2px dashed {current_theme['border']};
        }}

        .coming-soon-icon {{
            font-size: 60px;
            margin-bottom: 20px;
            filter: drop-shadow(0 4px 8px rgba(0,0,0,0.1));
        }}
    </style>
</head>
<body>
    <div class="app-container fade-in">
        <!-- Title Bar -->
        <div class="title-bar" id="titleBar">
            <div class="title-content">
                <div class="title-icon">🚀</div>
                <div class="title-text">Bypass Toolkit</div>
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
                        <span class="nav-icon">🔓</span>
                        Bypasses
                        <span class="nav-glow"></span>
                    </div>
                    <div class="nav-subitems">
                        <div class="nav-subitem active" data-subsection="linewize">
                            <div>
                                <span class="nav-icon">🌐</span>
                                Linewize
                            </div>
                            <span class="nav-badge">2 Methods</span>
                        </div>
                        <div class="nav-subitem" data-subsection="securly">
                            <div>
                                <span class="nav-icon">🛡️</span>
                                Securly
                            </div>
                            <span class="nav-badge">Soon</span>
                        </div>
                        <div class="nav-subitem" data-subsection="goguardian">
                            <div>
                                <span class="nav-icon">🔒</span>
                                GoGuardian
                            </div>
                            <span class="nav-badge">Soon</span>
                        </div>
                    </div>
                </div>
                <div class="nav-section">
                    <div class="nav-item" data-section="tools">
                        <span class="nav-icon">🛠️</span>
                        Tools
                        <span class="nav-glow"></span>
                    </div>
                </div>
                <div class="nav-section">
                    <div class="nav-item" data-section="settings">
                        <span class="nav-icon">⚙️</span>
                        Settings
                        <span class="nav-glow"></span>
                    </div>
                </div>
            </div>

            <!-- Content Area -->
            <div class="content-area">
                <!-- Bypasses Section -->
                <div class="content-section active" id="bypasses-section">
                    <div class="subsection active" id="linewize-subsection">
                        <div class="section-header">
                            <h2>Linewize Bypasses</h2>
                            <div class="section-badge">Active</div>
                        </div>

                        <!-- Method 1 Card -->
                        <div class="method-card">
                            <div class="card-header">
                                <h3>Method 1: Google Translate Bypass</h3>
                                <div class="method-badge success">Working</div>
                            </div>
                            <p>Enter any blocked URL to bypass through Google Translate proxy:</p>
                            <div class="input-group">
                                <div class="input-container">
                                    <input type="text" id="urlInput" placeholder="https://example.com" class="url-input">
                                    <span class="input-icon">🔗</span>
                                </div>
                                <button class="bypass-button" id="bypassBtn">
                                    <span class="button-text">Bypass Now</span>
                                    <span class="button-loader">
                                        <div class="spinner"></div>
                                    </span>
                                    <span class="button-glow"></span>
                                </button>
                            </div>
                            <div class="card-footer">
                                <span class="info-text">✓ Encrypted connection • ✓ Fast • ✓ Reliable</span>
                            </div>
                        </div>

                        <!-- Method 2 Card -->
                        <div class="method-card">
                            <div class="card-header">
                                <h3>Method 2: Advanced Proxy</h3>
                                <div class="method-badge warning">Beta</div>
                            </div>
                            <p>Advanced proxy method with enhanced stealth features (coming soon):</p>
                            <button class="placeholder-button">
                                <span class="button-text">Launch Proxy</span>
                                <span class="button-glow"></span>
                            </button>
                            <div class="card-footer">
                                <span class="info-text">⏳ Under development • Enhanced stealth</span>
                            </div>
                        </div>
                    </div>

                    <div class="subsection" id="securly-subsection">
                        <div class="section-header">
                            <h2>Securly Bypasses</h2>
                            <div class="section-badge">Coming Soon</div>
                        </div>
                        <div class="coming-soon">
                            <div class="coming-soon-icon">🚧</div>
                            <h3>Under Construction</h3>
                            <p>Bypass methods for Securly filter will be available soon.</p>
                        </div>
                    </div>

                    <div class="subsection" id="goguardian-subsection">
                        <div class="section-header">
                            <h2>GoGuardian Bypasses</h2>
                            <div class="section-badge">Coming Soon</div>
                        </div>
                        <div class="coming-soon">
                            <div class="coming-soon-icon">🔧</div>
                            <h3>Work in Progress</h3>
                            <p>Bypass methods for GoGuardian filter are being developed.</p>
                        </div>
                    </div>
                </div>

                <!-- Tools Section -->
                <div class="content-section" id="tools-section">
                    <div class="section-header">
                        <h2>Tools</h2>
                        <div class="section-badge">Utilities</div>
                    </div>
                    <div class="coming-soon">
                        <div class="coming-soon-icon">🔧</div>
                        <h3>Tools Coming Soon</h3>
                        <p>Additional tools and utilities will be available here soon.</p>
                    </div>
                </div>

                <!-- Settings Section -->
                <div class="content-section" id="settings-section">
                    <div class="section-header">
                        <h2>Settings</h2>
                        <div class="section-badge">Preferences</div>
                    </div>
                    
                    <div class="settings-grid">
                        <div class="setting-group">
                            <div class="setting-title">
                                <span>🎨</span> Theme Preferences
                            </div>
                            <div class="theme-options">
                                <div class="theme-option {'active' if current_settings['theme'] == 'white' else ''}" data-theme="white">
                                    <div class="theme-preview" style="background: linear-gradient(135deg, rgba(255, 255, 255, 0.85) 0%, rgba(255, 255, 255, 0.95) 100%); border: 1px solid rgba(255, 255, 255, 0.8);"></div>
                                    <div class="theme-name">Frost Glass</div>
                                </div>
                                <div class="theme-option {'active' if current_settings['theme'] == 'blue' else ''}" data-theme="blue">
                                    <div class="theme-preview" style="background: linear-gradient(135deg, rgba(100, 125, 220, 0.85) 0%, rgba(80, 100, 200, 0.95) 100%); border: 1px solid rgba(255, 255, 255, 0.2);"></div>
                                    <div class="theme-name">Ocean Glass</div>
                                </div>
                                <div class="theme-option {'active' if current_settings['theme'] == 'purple' else ''}" data-theme="purple">
                                    <div class="theme-preview" style="background: linear-gradient(135deg, rgba(120, 80, 200, 0.85) 0%, rgba(100, 60, 180, 0.95) 100%); border: 1px solid rgba(255, 255, 255, 0.2);"></div>
                                    <div class="theme-name">Royal Glass</div>
                                </div>
                                <div class="theme-option {'active' if current_settings['theme'] == 'black' else ''}" data-theme="black">
                                    <div class="theme-preview" style="background: linear-gradient(135deg, rgba(30, 30, 40, 0.95) 0%, rgba(20, 20, 30, 0.98) 100%); border: 1px solid rgba(255, 255, 255, 0.1);"></div>
                                    <div class="theme-name">Obsidian Glass</div>
                                </div>
                            </div>
                        </div>

                        <div class="setting-group">
                            <div class="setting-title">
                                <span>💾</span> Application Settings
                            </div>
                            <p style="margin-bottom: 20px; color: {current_theme['text_secondary']};">
                                Customize your bypass toolkit experience.
                            </p>
                            <button class="bypass-button" style="width: 100%;" onclick="resetSettings()">
                                <span class="button-text">Reset to Defaults</span>
                                <span class="button-glow"></span>
                            </button>
                        </div>

                        <div class="setting-group">
                            <div class="setting-title">
                                <span>ℹ️</span> About
                            </div>
                            <p style="color: {current_theme['text_secondary']}; line-height: 1.6;">
                                <strong>Bypass Toolkit v2.0</strong><br>
                                Advanced web filtering bypass utility<br>
                                With multi-theme glass morphism design<br>
                                Built with security and privacy in mind
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Current settings
        let currentSettings = {json.dumps(current_settings)};

        // Handle bypass functionality
        function handleBypass() {{
            const urlInput = document.getElementById('urlInput');
            const bypassBtn = document.getElementById('bypassBtn');
            const url = urlInput.value.trim();
            
            if (!url) {{
                urlInput.classList.add('shake');
                setTimeout(() => urlInput.classList.remove('shake'), 500);
                return;
            }}

            // Show loading state
            bypassBtn.classList.add('loading');
            
            setTimeout(() => {{
                let destination = url;
                if (!/^https?:\\/\\//i.test(destination)) {{
                    destination = "https://" + destination;
                }}
                
                const bypassUrl = `https://translate.google.com/translate?sl=auto&tl=en&u=${{encodeURIComponent(destination)}}`;
                window.open(bypassUrl, '_blank');
                
                // Reset button state
                bypassBtn.classList.remove('loading');
            }}, 1500);
        }}

        // Navigation functionality
        function setupNavigation() {{
            const navItems = document.querySelectorAll('.nav-item');
            const navSubitems = document.querySelectorAll('.nav-subitem');
            const contentSections = document.querySelectorAll('.content-section');
            const subsections = document.querySelectorAll('.subsection');

            // Main navigation
            navItems.forEach(item => {{
                item.addEventListener('click', () => {{
                    const section = item.getAttribute('data-section');
                    
                    // Update active states
                    navItems.forEach(nav => nav.classList.remove('active'));
                    item.classList.add('active');
                    
                    contentSections.forEach(content => content.classList.remove('active'));
                    document.getElementById(`${{section}}-section`).classList.add('active');
                }});
            }});

            // Sub-navigation
            navSubitems.forEach(item => {{
                item.addEventListener('click', () => {{
                    const subsection = item.getAttribute('data-subsection');
                    
                    // Update active states
                    navSubitems.forEach(nav => nav.classList.remove('active'));
                    item.classList.add('active');
                    
                    subsections.forEach(sub => sub.classList.remove('active'));
                    document.getElementById(`${{subsection}}-subsection`).classList.add('active');
                }});
            }});
        }}

        // Theme functionality with auto-refresh
        function setupThemes() {{
            const themeOptions = document.querySelectorAll('.theme-option');
            
            themeOptions.forEach(option => {{
                option.addEventListener('click', async () => {{
                    const theme = option.getAttribute('data-theme');
                    
                    // Show loading state
                    const appContainer = document.querySelector('.app-container');
                    appContainer.classList.add('theme-transition');
                    
                    // Update active state
                    themeOptions.forEach(opt => opt.classList.remove('active'));
                    option.classList.add('active');
                    
                    // Save theme preference
                    currentSettings.theme = theme;
                    
                    try {{
                        // Save settings via API
                        if (window.pywebview) {{
                            await pywebview.api.save_settings(currentSettings);
                        }} else {{
                            // Fallback for browser testing
                            localStorage.setItem('bypassSettings', JSON.stringify(currentSettings));
                        }}
                        
                        // Wait a moment for the animation, then refresh
                        setTimeout(() => {{
                            window.location.reload();
                        }}, 300);
                        
                    }} catch (error) {{
                        console.error('Failed to save settings:', error);
                        // Still refresh even if save fails
                        setTimeout(() => {{
                            window.location.reload();
                        }}, 300);
                    }}
                }});
            }});
        }}

        // Settings management
        async function saveSettings() {{
            try {{
                if (window.pywebview) {{
                    await pywebview.api.save_settings(currentSettings);
                }} else {{
                    // Fallback for browser testing
                    localStorage.setItem('bypassSettings', JSON.stringify(currentSettings));
                }}
                return true;
            }} catch (error) {{
                console.error('Failed to save settings:', error);
                return false;
            }}
        }}

        function resetSettings() {{
            if (confirm('Are you sure you want to reset all settings to defaults?')) {{
                currentSettings = {{
                    theme: 'white',
                    window_position: {{x: 100, y: 100}},
                    window_size: {{width: 1000, height: 700}}
                }};
                
                // Show transition and reload
                const appContainer = document.querySelector('.app-container');
                appContainer.classList.add('theme-transition');
                
                setTimeout(async () => {{
                    await saveSettings();
                    window.location.reload();
                }}, 300);
            }}
        }}

        // Dragging functionality
        function setupDragging() {{
            let isDragging = false;
            let currentX, currentY, initialX, initialY, xOffset = 0, yOffset = 0;
            const titleBar = document.getElementById('titleBar');

            titleBar.addEventListener("mousedown", dragStart);
            document.addEventListener("mousemove", drag);
            document.addEventListener("mouseup", dragEnd);

            function dragStart(e) {{
                initialX = e.clientX - xOffset;
                initialY = e.clientY - yOffset;

                if (e.target === titleBar || titleBar.contains(e.target)) {{
                    isDragging = true;
                }}
            }}

            function drag(e) {{
                if (isDragging) {{
                    e.preventDefault();
                    currentX = e.clientX - initialX;
                    currentY = e.clientY - initialY;

                    xOffset = currentX;
                    yOffset = currentY;

                    // In webview environment, use API to move window
                    if (window.pywebview) {{
                        pywebview.api.move_window(currentX, currentY);
                    }}
                }}
            }}

            function dragEnd(e) {{
                initialX = currentX;
                initialY = currentY;
                isDragging = false;
                
                // Save window position
                currentSettings.window_position = {{x: currentX, y: currentY}};
                saveSettings();
            }}
        }}

        // Initialize everything when page loads
        document.addEventListener('DOMContentLoaded', function() {{
            // Set up event listeners
            document.getElementById('bypassBtn').addEventListener('click', handleBypass);
            document.getElementById('urlInput').addEventListener('keypress', function(e) {{
                if (e.key === 'Enter') handleBypass();
            }});

            // Initialize components
            setupNavigation();
            setupThemes();
            setupDragging();
        }});

        // Close app function for WebView
        window.closeApp = function() {{
            if (window.pywebview) {{
                pywebview.api.close_app();
            }} else {{
                window.close();
            }}
        }};

        // Hover effects for cards
        document.querySelectorAll('.method-card').forEach(card => {{
            card.addEventListener('mouseenter', function() {{
                this.style.transform = 'translateY(-5px)';
            }});
            
            card.addEventListener('mouseleave', function() {{
                this.style.transform = 'translateY(0)';
            }});
        }});
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return get_html_content()

@app.route('/api/save_settings', methods=['POST'])
def api_save_settings():
    global current_settings
    try:
        new_settings = request.get_json()
        current_settings.update(new_settings)
        save_settings(current_settings)
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

class BypassAPI:
    def close_app(self):
        """Close the application"""
        print("Closing application...")
        import os
        os._exit(0)
    
    def move_window(self, x, y):
        """Move the window - placeholder for actual implementation"""
        # In pywebview, window movement is handled automatically when easy_drag=True
        pass
    
    def save_settings(self, settings):
        """Save settings from JavaScript"""
        global current_settings
        current_settings = settings
        save_settings(settings)
        return {'status': 'success'}

def run_flask():
    """Run Flask server in background"""
    app.run(host='127.0.0.1', port=4785, debug=False, use_reloader=False)

def create_window():
    """Create the WebView2 window"""
    # Start Flask server
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    time.sleep(2)  # Give server more time to start
    
    # Load window position from settings
    settings = load_settings()
    x = settings['window_position']['x']
    y = settings['window_position']['y']
    width = settings['window_size']['width']
    height = settings['window_size']['height']
    
    try:
        # Create WebView2 window
        window = pywebview.create_window(
            'Bypass Toolkit',
            'http://127.0.0.1:4785/',
            x=x, y=y, width=width, height=height,
            resizable=True,
            frameless=True,
            easy_drag=True,  # Enable easy dragging
            js_api=BypassAPI()
        )
        
        pywebview.start()
    except Exception as e:
        print(f"Error creating window: {e}")
        print("Make sure you have pywebview installed: pip install pywebview")
        print("On Windows, you might need: pip install pywebview[winforms] or pywebview[cef]")

if __name__ == '__main__':
    create_window()
