import threading
import difflib
import tkinter as tk
import pyperclip
import keyboard
import customtkinter as ctk
from src.utils.text import strip_html_tags, apply_win11_mica
from src.clipboard.manager import set_clipboard_html

_root_ref = None

def set_root(root):
    global _root_ref
    _root_ref = root

def apply_replacement_direct(original_clipboard, corrected_text, is_html):
    if is_html:
        set_clipboard_html(corrected_text)
    else:
        pyperclip.copy(corrected_text)
    keyboard.press_and_release('ctrl+v')
    import time; time.sleep(0.4)
    pyperclip.copy(original_clipboard)

def show_diff_window(original_clipboard, original_text, corrected_text, is_html, mode):
    if original_text == corrected_text:
        pyperclip.copy(original_clipboard)
        return

    titles = {
        "answer": "Review Answer",
        "summarize": "Review Summary",
        "custom": "Review Custom Result"
    }
    window_title = titles.get(mode, "Review Correction")

    top = ctk.CTkToplevel(_root_ref)
    top.title(window_title)
    top.attributes("-topmost", True)
    apply_win11_mica(top)

    w, h = 700, 500
    x = int(top.winfo_screenwidth() / 2 - w / 2)
    y = int(top.winfo_screenheight() / 2 - h / 2)
    top.geometry(f"{w}x{h}+{x}+{y}")

    custom_font = ("Segoe UI Variable Display", 13)
    label_text = titles.get(mode, "Review Changes")

    ctk.CTkLabel(top, text=label_text,
                 font=("Segoe UI Variable Display", 16, "bold"),
                 bg_color="transparent").pack(pady=(20, 10))

    def on_accept(event=None):
        top.destroy()
        threading.Thread(
            target=apply_replacement_direct,
            args=(original_clipboard, corrected_text, is_html)
        ).start()

    def on_reject(event=None):
        top.destroy()
        pyperclip.copy(original_clipboard)

    btn_frame = ctk.CTkFrame(top, fg_color="transparent")
    btn_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=20)
    bf = ("Segoe UI Variable Display", 12)

    ctk.CTkButton(btn_frame, text="✓ Accept", font=bf, fg_color="#0078D4",
                  hover_color="#106EBE", text_color="white", corner_radius=8,
                  width=100, command=on_accept).pack(side=tk.RIGHT, padx=5)
    ctk.CTkButton(btn_frame, text="✕ Cancel", font=bf,
                  fg_color=("#E5E5E5", "#333333"), hover_color=("#CCCCCC", "#444444"),
                  text_color=("#111111", "white"), corner_radius=8,
                  width=100, command=on_reject).pack(side=tk.RIGHT, padx=5)

    content_frame = ctk.CTkFrame(top, fg_color="transparent")
    content_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=(10, 20))
    content_frame.grid_columnconfigure(0, weight=1)
    content_frame.grid_rowconfigure(1, weight=1)

    box_bg = ("#FFFFFF", "#1E1E1E")
    is_dark = ctk.get_appearance_mode() == "Dark"
    bg_del = "#4A1C1A" if is_dark else "#FFD6D6"
    fg_del = "#FFB3B3" if is_dark else "#B30000"
    bg_ins = "#1A4A22" if is_dark else "#D6FFD6"
    fg_ins = "#B3FFB3" if is_dark else "#006600"
    fg_eq  = "#E0E0E0" if is_dark else "#111111"

    if mode == "answer":
        text_after = ctk.CTkTextbox(content_frame, wrap=tk.WORD, font=custom_font,
                                    fg_color=box_bg, border_width=1,
                                    border_color=("#AAAAAA", "#333333"),
                                    text_color=("#111111", "#E0E0E0"), corner_radius=8)
        text_after.grid(row=1, column=0, sticky="nsew")
        text_after.insert(tk.END, strip_html_tags(corrected_text))
        text_after.configure(state="disabled")
    else:
        content_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(content_frame, text="Original",
                     font=("Segoe UI Variable Display", 13, "bold"),
                     text_color=("#333333", "#CCCCCC")).grid(row=0, column=0, pady=(0,5), sticky="w")
        ctk.CTkLabel(content_frame, text="Corrected",
                     font=("Segoe UI Variable Display", 13, "bold"),
                     text_color=("#333333", "#CCCCCC")).grid(row=0, column=1, pady=(0,5), sticky="w", padx=(10,0))

        text_before = ctk.CTkTextbox(content_frame, wrap=tk.WORD, font=custom_font,
                                     fg_color=box_bg, border_width=1,
                                     border_color=("#AAAAAA", "#333333"),
                                     text_color=("#111111", "#E0E0E0"), corner_radius=8)
        text_before.grid(row=1, column=0, sticky="nsew", padx=(0, 5))

        text_after = ctk.CTkTextbox(content_frame, wrap=tk.WORD, font=custom_font,
                                    fg_color=box_bg, border_width=1,
                                    border_color=("#AAAAAA", "#333333"),
                                    text_color=("#111111", "#E0E0E0"), corner_radius=8)
        text_after.grid(row=1, column=1, sticky="nsew", padx=(5, 0))

        for t in (text_before, text_after):
            t.tag_config('delete', background=bg_del, foreground=fg_del, overstrike=True)
            t.tag_config('insert', background=bg_ins, foreground=fg_ins)
            t.tag_config('equal', foreground=fg_eq)

        disp_orig = strip_html_tags(original_text)
        disp_corr = strip_html_tags(corrected_text)
        matcher = difflib.SequenceMatcher(None, disp_orig, disp_corr)

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                text_before.insert(tk.END, disp_orig[i1:i2], 'equal')
                text_after.insert(tk.END, disp_corr[j1:j2], 'equal')
            elif tag == 'delete':
                text_before.insert(tk.END, disp_orig[i1:i2], 'delete')
            elif tag == 'insert':
                text_after.insert(tk.END, disp_corr[j1:j2], 'insert')
            elif tag == 'replace':
                text_before.insert(tk.END, disp_orig[i1:i2], 'delete')
                text_after.insert(tk.END, disp_corr[j1:j2], 'insert')

        text_before.configure(state="disabled")
        text_after.configure(state="disabled")

    top.bind('<Return>', on_accept)
    top.bind('<Escape>', on_reject)
    top.focus_force()