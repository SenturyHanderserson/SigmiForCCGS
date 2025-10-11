import urllib.request
import os
import hashlib
import sys

def get_remote_file_hash(url):
    try:
        with urllib.request.urlopen(url) as response:
            content = response.read()
            return hashlib.md5(content).hexdigest()
    except Exception as e:
        print(f"Error checking remote: {e}")
        return None

def get_local_file_hash(filepath):
    try:
        with open(filepath, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except Exception as e:
        print(f"Error checking local: {e}")
        return None

def check_for_updates():
    install_path = os.path.join(os.getenv('LOCALAPPDATA'), 'BypassToolkit')
    main_app_path = os.path.join(install_path, 'BypassGUI.py')
    
    # Only check if file exists
    if not os.path.exists(main_app_path):
        print("No local installation found.")
        return 0
    
    remote_url = 'https://raw.githubusercontent.com/SenturyHanderserson/SigmiForCCGS/refs/heads/main/content/BypassGUI.py'
    
    local_hash = get_local_file_hash(main_app_path)
    remote_hash = get_remote_file_hash(remote_url)
    
    print(f"Local hash: {local_hash}")
    print(f"Remote hash: {remote_hash}")
    
    if local_hash and remote_hash and local_hash != remote_hash:
        print("Update available!")
        return 1
    else:
        print("No updates available.")
        return 0

if __name__ == "__main__":
    exit(check_for_updates())
