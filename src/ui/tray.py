import threading
import pystray
from PIL import Image
import config
from config import save_settings

_root_ref = None

def set_root(root):
    global _root_ref
    _root_ref = root

def create_image():
    image = Image.new('RGB', (64, 64), color=(46, 46, 46))
    pixels = image.load()
    for i in range(16, 48):
        for j in range(16, 48):
            pixels[i, j] = (76, 175, 80)
    return image

def quit_app(icon, item):
    import os
    icon.stop()
    os._exit(0)

def toggle_enabled(icon, item):
    config.APP_ENABLED = not config.APP_ENABLED
    save_settings()

def toggle_instant_mode(icon, item):
    config.INSTANT_MODE = not config.INSTANT_MODE
    save_settings()

def change_api_key(icon, item):
    from src.ui.dialogs import show_api_key_dialog
    if _root_ref:
        _root_ref.after(0, show_api_key_dialog)

def setup_tray(root):
    set_root(root)
    image = create_image()
    menu = pystray.Menu(
        pystray.MenuItem('Grammar Fixer (Running)', lambda _: None, enabled=False),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem('Enabled', toggle_enabled, checked=lambda item: config.APP_ENABLED),
        pystray.MenuItem('Instant Mode', toggle_instant_mode, checked=lambda item: config.INSTANT_MODE),
        pystray.MenuItem('Change API Key', change_api_key),
        pystray.MenuItem('Quit', quit_app)
    )
    icon = pystray.Icon("Aicorrection", image, "AI Correction", menu)
    icon.run()