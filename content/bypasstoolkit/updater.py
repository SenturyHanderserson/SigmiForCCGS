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
