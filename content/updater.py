import urllib.request
import os
import hashlib

def get_remote_file_hash(url):
    try:
        with urllib.request.urlopen(url) as response:
            content = response.read()
            return hashlib.md5(content).hexdigest()
    except:
        return None

def get_local_file_hash(filepath):
    try:
        with open(filepath, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except:
        return None

def check_for_updates():
    install_path = os.path.join(os.getenv('LOCALAPPDATA'), 'BypassToolkit')
    main_app_path = os.path.join(install_path, 'BypassGUI.py')
    
    remote_url = 'https://raw.githubusercontent.com/SenturyHanderserson/SigmiForCCGS/refs/heads/main/content/BypassGUI.py'
    
    local_hash = get_local_file_hash(main_app_path)
    remote_hash = get_remote_file_hash(remote_url)
    
    if local_hash and remote_hash and local_hash != remote_hash:
        print("Update available!")
        return 1 
    else:
        print("No updates available.")
        return 0  

if __name__ == "__main__":
    exit(check_for_updates())
