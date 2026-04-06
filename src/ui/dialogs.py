import threading
import pyperclip
import customtkinter as ctk
import webbrowser
import config
from src.utils.text import apply_win11_mica
from src.api.client import update_api_key, run_custom_api

_root_ref = None

def set_root(root):
    global _root_ref
    _root_ref = root

def show_prompt_input_window(original_clipboard, original_text, is_html):
    top = ctk.CTkToplevel(_root_ref)
    top.title("Custom AI Prompt")
    top.attributes("-topmost", True)
    apply_win11_mica(top)

    w, h = 500, 160
    x = int(top.winfo_screenwidth() / 2 - w / 2)
    y = int(top.winfo_screenheight() / 2 - h / 2)
    top.geometry(f"{w}x{h}+{x}+{y}")

    ctk.CTkLabel(top, text="What should I do with this text?",
                 font=("Segoe UI Variable Display", 14, "bold"),
                 bg_color="transparent").pack(pady=10)

    entry = ctk.CTkEntry(top, font=("Segoe UI Variable Display", 12), width=460,
                         fg_color=("#FFFFFF", "#1E1E1E"), border_width=1,
                         border_color=("#AAAAAA", "#555555"),
                         text_color=("#111111", "#E0E0E0"), corner_radius=8)
    entry.pack(pady=5, padx=20)
    entry.focus()

    def on_submit(event=None):
        user_prompt = entry.get().strip()
        top.destroy()
        if user_prompt:
            threading.Thread(
                target=run_custom_api,
                args=(original_clipboard, original_text, is_html, user_prompt)
            ).start()
        else:
            pyperclip.copy(original_clipboard)

    def on_cancel(event=None):
        top.destroy()
        pyperclip.copy(original_clipboard)

    top.bind('<Return>', on_submit)
    top.bind('<Escape>', on_cancel)


def show_api_key_dialog():
    top = ctk.CTkToplevel(_root_ref)
    top.title("Settings")
    top.attributes("-topmost", True)
    apply_win11_mica(top)

    w, h = 500, 160
    x = int(top.winfo_screenwidth() / 2 - w / 2)
    y = int(top.winfo_screenheight() / 2 - h / 2)
    top.geometry(f"{w}x{h}+{x}+{y}")

    ctk.CTkLabel(top, text="Enter Groq API Key:",
                 font=("Segoe UI Variable Display", 14, "bold"),
                 bg_color="transparent").pack(pady=(15, 5))

    entry = ctk.CTkEntry(top, font=("Segoe UI Variable Display", 12), width=460,
                         fg_color=("#FFFFFF", "#1E1E1E"), border_width=1,
                         border_color=("#AAAAAA", "#555555"),
                         text_color=("#111111", "#E0E0E0"), corner_radius=8, show="*")
    entry.pack(pady=5, padx=20)
    if config.GROQ_API_KEY:
        entry.insert(0, config.GROQ_API_KEY)
    entry.focus()

    def on_submit(event=None):
        new_key = entry.get().strip()
        if new_key:
            update_api_key(new_key)
        top.destroy()

    def on_cancel(event=None):
        top.destroy()

    btn_frame = ctk.CTkFrame(top, fg_color="transparent")
    btn_frame.pack(pady=(15, 10))
    bf = ("Segoe UI Variable Display", 12)

    ctk.CTkButton(btn_frame, text="Save", font=bf, fg_color="#0078D4",
                  hover_color="#106EBE", text_color="white", corner_radius=8,
                  width=100, command=on_submit).pack(side=ctk.LEFT, padx=10)
    ctk.CTkButton(btn_frame, text="Get API Key", font=bf,
                  fg_color=("#E5E5E5", "#333333"), hover_color=("#CCCCCC", "#444444"),
                  text_color=("#111111", "white"), corner_radius=8, width=100,
                  command=lambda: webbrowser.open("https://console.groq.com/keys")
                  ).pack(side=ctk.LEFT, padx=10)
    ctk.CTkButton(btn_frame, text="Cancel", font=bf, fg_color="transparent",
                  border_width=1, border_color=("#AAAAAA", "#333333"),
                  text_color=("#333333", "#AAAAAA"), hover_color=("#E5E5E5", "#222222"),
                  corner_radius=8, width=100, command=on_cancel).pack(side=ctk.LEFT, padx=10)

    top.bind('<Return>', on_submit)
    top.bind('<Escape>', on_cancel)