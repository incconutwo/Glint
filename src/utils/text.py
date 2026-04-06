import re
import ctypes
import customtkinter as ctk

def strip_html_tags(text):
    if not text:
        return ""
    return re.sub(r'<[^>]+>', '', text)

def apply_win11_mica(window):
    try:
        window.update()
        hwnd = ctypes.windll.user32.GetParent(window.winfo_id())
        is_dark = ctk.get_appearance_mode() == "Dark"

        DWMWA_USE_IMMERSIVE_DARK_MODE = 20
        rendering_policy = ctypes.c_int(1 if is_dark else 0)
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE,
            ctypes.byref(rendering_policy), ctypes.sizeof(rendering_policy)
        )

        DWMWA_SYSTEMBACKDROP_TYPE = 38
        mica_value = ctypes.c_int(2)
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd, DWMWA_SYSTEMBACKDROP_TYPE,
            ctypes.byref(mica_value), ctypes.sizeof(mica_value)
        )

        class MARGINS(ctypes.Structure):
            _fields_ = [("cxLeftWidth", ctypes.c_int), ("cxRightWidth", ctypes.c_int),
                        ("cyTopHeight", ctypes.c_int), ("cyBottomHeight", ctypes.c_int)]
        margins = MARGINS(-1, -1, -1, -1)
        ctypes.windll.dwmapi.DwmExtendFrameIntoClientArea(hwnd, ctypes.byref(margins))

        mica_color = "#000001" if is_dark else "#FFFFFE"
        window.configure(fg_color=mica_color)
        window.config(bg=mica_color)
        window.wm_attributes("-transparentcolor", mica_color)
    except Exception as e:
        print(f"Mica error: {e}")