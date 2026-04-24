import os
import sys
import json
from pathlib import Path

try:
    import winreg
    HAS_WINREG = True
except ImportError:
    HAS_WINREG = False

def set_startup_registry(enabled):
    """ Adds or removes the app from the Windows Registry Run key """
    if not HAS_WINREG:
        return

    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    app_name = "Glint"
    
    # Determine the execution path
    if getattr(sys, 'frozen', False):
        # Running as compiled exe
        current_path = sys.executable
    else:
        # Running as python script
        # Note: We use pythonw.exe to ensure it runs without a console window
        pythonw = sys.executable.replace("python.exe", "pythonw.exe")
        # Use sys.argv[0] to get the main script path even if called from a submodule
        main_script = os.path.abspath(sys.argv[0])
        current_path = f'"{pythonw}" "{main_script}"'

    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
        if enabled:
            winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, current_path)
        else:
            try:
                winreg.DeleteValue(key, app_name)
            except FileNotFoundError:
                pass # Already gone
        winreg.CloseKey(key)
    except Exception as e:
        print(f"Registry update error: {e}")

def load_settings(config_file):
    if config_file.exists():
        try:
            with open(config_file, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading settings: {e}")
    return {}

def save_settings(config_file, data):
    try:
        with open(config_file, "w") as f:
            json.dump(data, f)
    except Exception as e:
        print(f"Error saving settings: {e}")
