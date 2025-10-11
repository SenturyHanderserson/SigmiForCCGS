import urllib.request
import os
import hashlib
import sys

def get_remote_file_content(url):
    """Get remote file content"""
    try:
        with urllib.request.urlopen(url) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        print(f"Error checking remote: {e}")
        return None

def get_local_file_content(filepath):
    """Get local file content"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error checking local: {e}")
        return None

def check_for_updates():
    """Check if updates are available"""
    install_path = os.path.join(os.getenv('LOCALAPPDATA'), 'BypassToolkit')
    main_app_path = os.path.join(install_path, 'BypassGUI.py')
    
    # Only check if file exists
    if not os.path.exists(main_app_path):
        print("No local installation found.")
        return 0
    
    remote_url = 'https://raw.githubusercontent.com/SenturyHanderserson/SigmiForCCGS/refs/heads/main/content/BypassGUI.py'
    
    local_content = get_local_file_content(main_app_path)
    remote_content = get_remote_file_content(remote_url)
    
    if local_content and remote_content:
        # Simple content comparison (you could use version numbers instead)
        local_hash = hashlib.md5(local_content.encode()).hexdigest()
        remote_hash = hashlib.md5(remote_content.encode()).hexdigest()
        
        print(f"Local version hash: {local_hash[:8]}...")
        print(f"Remote version hash: {remote_hash[:8]}...")
        
        if local_hash != remote_hash:
            print("Update available!")
            return 1
        else:
            print("No updates available.")
            return 0
    else:
        print("Could not check for updates.")
        return 0

if __name__ == "__main__":
    exit_code = check_for_updates()
    sys.exit(exit_code)
