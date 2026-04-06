import threading
import queue
import pyperclip
import keyboard
import customtkinter as ctk

import config
from config import load_settings
from src.api.client import correction_queue, init_client, process_text_and_api
from src.ui.dialogs import show_api_key_dialog, show_prompt_input_window, set_root as dialogs_set_root
from src.ui.diff_window import show_diff_window, apply_replacement_direct, set_root as diff_set_root
from src.ui.tray import setup_tray, set_root as tray_set_root

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

load_settings()
init_client()

# Hidden root window
root = ctk.CTk()
root.withdraw()

# Give all UI modules a reference to root
dialogs_set_root(root)
diff_set_root(root)
tray_set_root(root)

# Start system tray
threading.Thread(target=setup_tray, args=(root,), daemon=True).start()

def ui_loop():
    try:
        original_clipboard, original_text, corrected_text, is_html, mode = correction_queue.get_nowait()

        if mode == "api_key_missing":
            show_api_key_dialog()
        elif mode == "ask_prompt":
            show_prompt_input_window(original_clipboard, original_text, is_html)
        else:
            if config.INSTANT_MODE:
                if original_text != corrected_text:
                    threading.Thread(
                        target=apply_replacement_direct,
                        args=(original_clipboard, corrected_text, is_html)
                    ).start()
                else:
                    pyperclip.copy(original_clipboard)
            else:
                show_diff_window(original_clipboard, original_text, corrected_text, is_html, mode)
    except queue.Empty:
        pass
    root.after(100, ui_loop)

print(f"Grammar Fixer started. Model: {config.MODEL}")
print("Ctrl+Alt+G = Fix | Ctrl+Alt+A = Answer | Ctrl+Alt+S = Summarize | Ctrl+Alt+P = Custom")

keyboard.add_hotkey('ctrl+alt+g', lambda: threading.Thread(target=process_text_and_api, kwargs={"mode": "correction"}).start())
keyboard.add_hotkey('ctrl+alt+a', lambda: threading.Thread(target=process_text_and_api, kwargs={"mode": "answer"}).start())
keyboard.add_hotkey('ctrl+alt+s', lambda: threading.Thread(target=process_text_and_api, kwargs={"mode": "summarize"}).start())
keyboard.add_hotkey('ctrl+alt+p', lambda: threading.Thread(target=process_text_and_api, kwargs={"mode": "ask_prompt"}).start())

root.after(100, ui_loop)

if not config.GROQ_API_KEY:
    root.after(500, show_api_key_dialog)

root.mainloop()