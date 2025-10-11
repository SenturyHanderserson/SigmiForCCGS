import webview
import threading
import time
import sys
import os
from flask import Flask, render_template_string

# Create Flask app to serve our HTML/CSS/JS
app = Flask(__name__)

# Our complete HTML with CSS and JavaScript
HTML_CONTENT = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bypass Toolkit</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: transparent;
            color: #333;
            overflow: hidden;
            height: 100vh;
            user-select: none;
        }

        .app-container {
            width: 100vw;
            height: 100vh;
            background: linear-gradient(135deg, 
                rgba(255, 255, 255, 0.85) 0%, 
                rgba(255, 255, 255, 0.95) 100%);
            backdrop-filter: blur(40px) saturate(200%);
            -webkit-backdrop-filter: blur(40px) saturate(200%);
            border: 1px solid rgba(255, 255, 255, 0.8);
            display: flex;
            flex-direction: column;
            position: relative;
            box-shadow: 
                0 25px 50px rgba(0, 0, 0, 0.1),
                0 0 0 1px rgba(255, 255, 255, 0.9),
                inset 0 1px 0 rgba(255, 255, 255, 0.8);
        }

        .app-container::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: 
                radial-gradient(circle at 20% 80%, rgba(120, 119, 198, 0.08) 0%, transparent 50%),
                radial-gradient(circle at 80% 20%, rgba(255, 107, 107, 0.05) 0%, transparent 50%);
            pointer-events: none;
            z-index: -1;
        }

        /* Title Bar */
        .title-bar {
            height: 60px;
            background: rgba(255, 255, 255, 0.7);
            backdrop-filter: blur(20px);
            border-bottom: 1px solid rgba(255, 255, 255, 0.8);
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 25px;
            -webkit-app-region: drag;
            position: relative;
        }

        .title-bar::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            height: 1px;
            background: linear-gradient(90deg, 
                transparent 0%, 
                rgba(0, 0, 0, 0.1) 50%, 
                transparent 100%);
        }

        .title-content {
            display: flex;
            align-items: center;
            gap: 15px;
        }

        .title-icon {
            font-size: 24px;
            filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
        }

        .title-text {
            font-size: 20px;
            font-weight: 700;
            background: linear-gradient(135deg, #7877C6, #FF6B6B);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }

        .window-controls {
            display: flex;
            gap: 12px;
            -webkit-app-region: no-drag;
        }

        .control-btn {
            width: 32px;
            height: 32px;
            background: rgba(255, 255, 255, 0.6);
            border: 1px solid rgba(0, 0, 0, 0.1);
            border-radius: 8px;
            color: #555;
            font-size: 18px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        }

        .control-btn:hover {
            background: rgba(255, 255, 255, 0.9);
            transform: scale(1.1);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }

        .close-btn:hover {
            background: rgba(255, 107, 107, 0.2);
            border-color: rgba(255, 107, 107, 0.3);
            color: #FF6B6B;
        }

        /* Main Content */
        .main-content {
            flex: 1;
            display: flex;
            overflow: hidden;
        }

        /* Sidebar */
        .sidebar {
            width: 280px;
            background: rgba(255, 255, 255, 0.5);
            backdrop-filter: blur(20px);
            border-right: 1px solid rgba(0, 0, 0, 0.05);
            padding: 30px 0;
            display: flex;
            flex-direction: column;
        }

        .nav-section {
            margin-bottom: 20px;
        }

        .nav-item {
            padding: 16px 30px;
            color: #555;
            cursor: pointer;
            transition: all 0.4s ease;
            display: flex;
            align-items: center;
            font-weight: 600;
            border-left: 4px solid transparent;
            position: relative;
            margin: 5px 15px;
            border-radius: 12px;
        }

        .nav-glow {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(135deg, rgba(120, 119, 198, 0.1), transparent);
            border-radius: 12px;
            opacity: 0;
            transition: opacity 0.3s ease;
        }

        .nav-item:hover {
            background: rgba(120, 119, 198, 0.08);
            color: #7877C6;
            border-left-color: rgba(120, 119, 198, 0.3);
            transform: translateX(5px);
        }

        .nav-item:hover .nav-glow {
            opacity: 1;
        }

        .nav-item.active {
            background: linear-gradient(135deg, rgba(120, 119, 198, 0.15), rgba(255, 107, 107, 0.08));
            color: #7877C6;
            border-left-color: #7877C6;
            box-shadow: 0 8px 25px rgba(120, 119, 198, 0.15);
        }

        .nav-icon {
            margin-right: 15px;
            font-size: 18px;
        }

        .nav-subitems {
            margin-left: 30px;
            margin-top: 10px;
        }

        .nav-subitem {
            padding: 14px 20px;
            color: #666;
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
        }

        .nav-subitem:hover {
            background: rgba(120, 119, 198, 0.05);
            color: #7877C6;
            transform: translateX(8px);
        }

        .nav-subitem.active {
            background: linear-gradient(135deg, rgba(120, 119, 198, 0.12), rgba(120, 119, 198, 0.05));
            color: #7877C6;
            border-left-color: #7877C6;
        }

        .nav-badge {
            background: rgba(120, 119, 198, 0.1);
            padding: 4px 8px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 600;
            color: #7877C6;
        }

        /* Content Area */
        .content-area {
            flex: 1;
            padding: 40px;
            overflow-y: auto;
        }

        .section-header {
            display: flex;
            align-items: center;
            gap: 20px;
            margin-bottom: 35px;
        }

        h2 {
            font-size: 32px;
            color: #333;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
            font-weight: 700;
        }

        .section-badge {
            background: linear-gradient(135deg, #7877C6, #FF6B6B);
            padding: 8px 16px;
            border-radius: 10px;
            font-size: 12px;
            font-weight: 700;
            color: white;
            box-shadow: 0 4px 15px rgba(120, 119, 198, 0.3);
        }

        /* Method Cards */
        .method-card {
            background: linear-gradient(135deg, 
                rgba(255, 255, 255, 0.7) 0%, 
                rgba(255, 255, 255, 0.5) 100%);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.8);
            border-radius: 20px;
            padding: 35px;
            margin-bottom: 30px;
            transition: all 0.4s ease;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.08);
            position: relative;
            overflow: hidden;
        }

        .method-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.6), transparent);
            transition: left 0.8s ease;
        }

        .method-card:hover::before {
            left: 100%;
        }

        .method-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 25px 50px rgba(0, 0, 0, 0.12);
            border-color: rgba(255, 255, 255, 0.9);
        }

        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }

        h3 {
            font-size: 22px;
            color: #333;
            text-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
            font-weight: 600;
        }

        .method-badge {
            padding: 6px 12px;
            border-radius: 8px;
            font-size: 11px;
            font-weight: 700;
            color: white;
        }

        .method-badge.success {
            background: linear-gradient(135deg, #4CAF50, #45a049);
            box-shadow: 0 4px 15px rgba(76, 175, 80, 0.2);
        }

        .method-badge.warning {
            background: linear-gradient(135deg, #FF9800, #F57C00);
            box-shadow: 0 4px 15px rgba(255, 152, 0, 0.2);
        }

        p {
            color: #555;
            line-height: 1.7;
            margin-bottom: 25px;
            font-size: 15px;
        }

        .input-group {
            display: flex;
            gap: 20px;
            margin: 30px 0;
            align-items: center;
        }

        .input-container {
            flex: 1;
            position: relative;
        }

        .url-input {
            width: 100%;
            padding: 18px 20px 18px 50px;
            background: rgba(255, 255, 255, 0.8);
            border: 1px solid rgba(0, 0, 0, 0.1);
            border-radius: 14px;
            color: #333;
            font-size: 16px;
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.05);
        }

        .url-input::placeholder {
            color: #999;
        }

        .url-input:focus {
            outline: none;
            background: rgba(255, 255, 255, 0.95);
            border-color: rgba(120, 119, 198, 0.5);
            box-shadow: 0 0 0 3px rgba(120, 119, 198, 0.1),
                        0 12px 35px rgba(0, 0, 0, 0.08);
        }

        .input-icon {
            position: absolute;
            left: 20px;
            top: 50%;
            transform: translateY(-50%);
            font-size: 18px;
            color: #999;
        }

        .bypass-button, .placeholder-button {
            padding: 18px 35px;
            background: linear-gradient(135deg, #7877C6 0%, #FF6B6B 100%);
            border: none;
            border-radius: 14px;
            color: white;
            font-size: 16px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
            box-shadow: 0 8px 25px rgba(120, 119, 198, 0.3);
            min-width: 140px;
        }

        .button-glow {
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
            transition: left 0.6s;
        }

        .bypass-button:hover .button-glow, .placeholder-button:hover .button-glow {
            left: 100%;
        }

        .bypass-button:hover, .placeholder-button:hover {
            transform: translateY(-3px);
            box-shadow: 0 15px 35px rgba(120, 119, 198, 0.4);
        }

        .bypass-button:active, .placeholder-button:active {
            transform: translateY(0);
            box-shadow: 0 5px 20px rgba(120, 119, 198, 0.3);
        }

        .placeholder-button {
            background: linear-gradient(135deg, #9e9e9e 0%, #757575 100%);
            box-shadow: 0 8px 25px rgba(158, 158, 158, 0.3);
        }

        .placeholder-button:hover {
            box-shadow: 0 15px 35px rgba(158, 158, 158, 0.4);
        }

        .card-footer {
            margin-top: 20px;
            padding-top: 15px;
            border-top: 1px solid rgba(0, 0, 0, 0.05);
        }

        .info-text {
            color: #777;
            font-size: 13px;
        }

        /* Scrollbar */
        .content-area::-webkit-scrollbar {
            width: 10px;
        }

        .content-area::-webkit-scrollbar-track {
            background: rgba(255, 255, 255, 0.5);
            border-radius: 5px;
        }

        .content-area::-webkit-scrollbar-thumb {
            background: linear-gradient(135deg, #7877C6, #FF6B6B);
            border-radius: 5px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }

        .content-area::-webkit-scrollbar-thumb:hover {
            background: linear-gradient(135deg, #FF6B6B, #7877C6);
        }

        /* Animations */
        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            25% { transform: translateX(-10px); }
            75% { transform: translateX(10px); }
        }

        .shake {
            animation: shake 0.5s ease-in-out;
        }

        @keyframes fadeIn {
            from { 
                opacity: 0; 
                transform: translateY(20px); 
            }
            to { 
                opacity: 1; 
                transform: translateY(0); 
            }
        }

        .fade-in {
            animation: fadeIn 0.6s ease-out;
        }

        /* Loading Animation */
        .button-loader {
            display: none;
        }

        .spinner {
            width: 20px;
            height: 20px;
            border: 2px solid transparent;
            border-top: 2px solid white;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }

        .bypass-button.loading .button-text {
            display: none;
        }

        .bypass-button.loading .button-loader {
            display: flex;
            align-items: center;
            justify-content: center;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="app-container fade-in">
        <!-- Title Bar -->
        <div class="title-bar">
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
                    <div class="nav-item active">
                        <span class="nav-icon">🔓</span>
                        Bypasses
                        <span class="nav-glow"></span>
                    </div>
                    <div class="nav-subitems">
                        <div class="nav-subitem active">
                            <div>
                                <span class="nav-icon">🌐</span>
                                Linewize
                            </div>
                            <span class="nav-badge">2 Methods</span>
                        </div>
                        <div class="nav-subitem">
                            <div>
                                <span class="nav-icon">🛡️</span>
                                Securly
                            </div>
                            <span class="nav-badge">Soon</span>
                        </div>
                        <div class="nav-subitem">
                            <div>
                                <span class="nav-icon">🔒</span>
                                GoGuardian
                            </div>
                            <span class="nav-badge">Soon</span>
                        </div>
                    </div>
                </div>
                <div class="nav-section">
                    <div class="nav-item">
                        <span class="nav-icon">🛠️</span>
                        Tools
                        <span class="nav-glow"></span>
                    </div>
                </div>
                <div class="nav-section">
                    <div class="nav-item">
                        <span class="nav-icon">⚙️</span>
                        Settings
                        <span class="nav-glow"></span>
                    </div>
                </div>
            </div>

            <!-- Content Area -->
            <div class="content-area">
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
        </div>
    </div>

    <script>
        // Handle bypass functionality
        function handleBypass() {
            const urlInput = document.getElementById('urlInput');
            const bypassBtn = document.getElementById('bypassBtn');
            const url = urlInput.value.trim();
            
            if (!url) {
                urlInput.classList.add('shake');
                setTimeout(() => urlInput.classList.remove('shake'), 500);
                return;
            }

            // Show loading state
            bypassBtn.classList.add('loading');
            
            setTimeout(() => {
                let destination = url;
                if (!/^https?:\/\//i.test(destination)) {
                    destination = "https://" + destination;
                }
                
                const bypassUrl = `https://translate.google.com/translate?sl=auto&tl=en&u=${encodeURIComponent(destination)}`;
                window.open(bypassUrl, '_blank');
                
                // Reset button state
                bypassBtn.classList.remove('loading');
            }, 1500);
        }

        // Handle Enter key in input
        document.getElementById('urlInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                handleBypass();
            }
        });

        // Add click event to bypass button
        document.getElementById('bypassBtn').addEventListener('click', handleBypass);

        // Navigation functionality
        document.querySelectorAll('.nav-item, .nav-subitem').forEach(item => {
            item.addEventListener('click', function() {
                // Remove active class from all items
                document.querySelectorAll('.nav-item, .nav-subitem').forEach(i => {
                    i.classList.remove('active');
                });
                // Add active class to clicked item
                this.classList.add('active');
            });
        });

        // Close app function for WebView
        window.closeApp = function() {
            if (window.pywebview) {
                pywebview.api.close_app();
            } else {
                window.close();
            }
        };

        // Hover effects
        document.querySelectorAll('.method-card').forEach(card => {
            card.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-5px)';
            });
            
            card.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0)';
            });
        });

        // Dragging functionality for the entire window
        let isDragging = false;
        let currentX;
        let currentY;
        let initialX;
        let initialY;
        let xOffset = 0;
        let yOffset = 0;

        const titleBar = document.querySelector('.title-bar');

        titleBar.addEventListener("mousedown", dragStart);
        document.addEventListener("mousemove", drag);
        document.addEventListener("mouseup", dragEnd);

        function dragStart(e) {
            initialX = e.clientX - xOffset;
            initialY = e.clientY - yOffset;

            if (e.target === titleBar || titleBar.contains(e.target)) {
                isDragging = true;
            }
        }

        function drag(e) {
            if (isDragging) {
                e.preventDefault();
                currentX = e.clientX - initialX;
                currentY = e.clientY - initialY;

                xOffset = currentX;
                yOffset = currentY;

                // In a webview environment, we'd need to use the API to move the window
                if (window.pywebview) {
                    pywebview.api.move_window(currentX, currentY);
                }
            }
        }

        function dragEnd(e) {
            initialX = currentX;
            initialY = currentY;
            isDragging = false;
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_CONTENT)

class BypassAPI:
    def close_app(self):
        """Close the application"""
        print("Closing application...")
        # This will be called from JavaScript
        import os
        os._exit(0)
    
    def move_window(self, x, y):
        """Move the window - placeholder for actual implementation"""
        # In a real implementation, this would use the webview API to move the window
        pass

def run_flask():
    """Run Flask server in background"""
    app.run(host='127.0.0.1', port=4785, debug=False)

def create_window():
    """Create the WebView2 window"""
    # Start Flask server
    threading.Thread(target=run_flask, daemon=True).start()
    time.sleep(1)  # Give server time to start
    
    # Create WebView2 window
    window = webview.create_window(
        'Bypass Toolkit',
        'http://127.0.0.1:4785/',
        width=1000,
        height=700,
        resizable=True,
        frameless=True,
        easy_drag=True,  # Enable easy dragging
        js_api=BypassAPI()
    )
    
    webview.start()

if __name__ == '__main__':
    create_window()
