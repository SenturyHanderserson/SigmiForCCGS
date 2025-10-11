import os
import requests
import sys
import time
import json
import hashlib

def get_current_version():
    """Get current version from BypassGUI.py"""
    try:
        with open('BypassGUI.py', 'r', encoding='utf-8') as f:
            content = f.read()
            for line in content.split('\n'):
                if 'VERSION = ' in line:
                    return line.split('=')[1].strip().strip("'\"")
    except:
        pass
    return 'v1 beta'

def get_online_version():
    """Get version from online source"""
    try:
        online_url = "https://raw.githubusercontent.com/SenturyHanderserson/SigmiForCCGS/refs/heads/main/content/bypasstoolkit/BypassGUI.py"
        response = requests.get(online_url, timeout=30)
        if response.status_code == 200:
            for line in response.text.split('\n'):
                if 'VERSION = ' in line:
                    return line.split('=')[1].strip().strip("'\"")
    except:
        pass
    return None

def check_for_updates():
    """Check if updates are available"""
    try:
        current_version = get_current_version()
        online_version = get_online_version()
        
        if online_version and online_version != current_version:
            return {
                'available': True,
                'current_version': current_version,
                'online_version': online_version
            }
        else:
            return {
                'available': False,
                'current_version': current_version,
                'online_version': online_version
            }
    except Exception as e:
        return {
            'available': False,
            'error': str(e)
        }

def perform_update():
    """Perform the update by downloading new version"""
    try:
        print("Starting update process...")
        
        # Get the online content
        online_url = "https://raw.githubusercontent.com/SenturyHanderserson/SigmiForCCGS/refs/heads/main/content/bypasstoolkit/BypassGUI.py"
        response = requests.get(online_url, timeout=30)
        
        if response.status_code == 200:
            online_content = response.text
            
            # Create backup of current file
            if os.path.exists('BypassGUI.py'):
                backup_content = ''
                with open('BypassGUI.py', 'r', encoding='utf-8') as f:
                    backup_content = f.read()
                
                # Write backup
                with open('BypassGUI.py.backup', 'w', encoding='utf-8') as f:
                    f.write(backup_content)
            
            # Write new content to file
            with open('BypassGUI.py', 'w', encoding='utf-8') as f:
                f.write(online_content)
            
            print("Update successful!")
            return True
        else:
            print(f"Failed to download update. Status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Update failed: {e}")
        return False

def restart_application():
    """Restart the main application"""
    try:
        print("Restarting application...")
        time.sleep(2)
        
        # Restart the application
        python = sys.executable
        os.execl(python, python, 'BypassGUI.py')
    except Exception as e:
        print(f"Failed to restart application: {e}")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == '--check':
            # Check for updates and return result as JSON
            result = check_for_updates()
            print(json.dumps(result))
        elif sys.argv[1] == '--update':
            # Perform the update
            if perform_update():
                restart_application()
            else:
                print("Update failed. Please try again.")
                time.sleep(5)
    else:
        # Default behavior - check and update if available
        print("Checking for updates...")
        result = check_for_updates()
        
        if result.get('available'):
            print(f"Update available: {result['current_version']} -> {result['online_version']}")
            print("Performing update...")
            if perform_update():
                restart_application()
            else:
                print("Update failed.")
                time.sleep(5)
        else:
            print("No updates available.")
            if result.get('error'):
                print(f"Error: {result['error']}")
            time.sleep(3)
