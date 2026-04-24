"""
Ghost HUD — a floating, pill-shaped overlay that appears near the user's
text cursor (caret) to show AI processing status and results.

Architecture
────────────
• Platform-agnostic state machine (Working → Result / Error).
• Caret-position detection is isolated in _get_caret_position() so future
  Linux (AT-SPI) and macOS (Accessibility API) backends can be swapped in
  without touching the UI code.
• Visual effects delegate to ui_utils (Mica on Windows, plain on others).
"""

import sys
import platform
import tkinter as tk
import customtkinter as ctk

# --- Platform-specific caret detection ------------------------------------
# We wrap the import so the module loads cleanly on non-Windows systems.
_PLATFORM = platform.system()  # "Windows", "Linux", "Darwin"

if _PLATFORM == "Windows":
    try:
        import ctypes
        import ctypes.wintypes

        class _GUITHREADINFO(ctypes.Structure):
            _fields_ = [
                ("cbSize",        ctypes.wintypes.DWORD),
                ("flags",         ctypes.wintypes.DWORD),
                ("hwndActive",    ctypes.wintypes.HWND),
                ("hwndFocus",     ctypes.wintypes.HWND),
                ("hwndCapture",   ctypes.wintypes.HWND),
                ("hwndMenuOwner", ctypes.wintypes.HWND),
                ("hwndMoveSize",  ctypes.wintypes.HWND),
                ("hwndCaret",     ctypes.wintypes.HWND),
                ("rcCaret",       ctypes.wintypes.RECT),
            ]

        _HAS_WIN32_CARET = True
    except Exception:
        _HAS_WIN32_CARET = False
else:
    _HAS_WIN32_CARET = False


def _get_caret_position():
    """Return (x, y) screen coordinates near the user's text caret.

    Windows: uses GetGUIThreadInfo → rcCaret, then ClientToScreen.
    Fallback (all platforms): returns the current mouse pointer position.
    """
    if _PLATFORM == "Windows" and _HAS_WIN32_CARET:
        try:
            gui_info = _GUITHREADINFO()
            gui_info.cbSize = ctypes.sizeof(_GUITHREADINFO)
            if ctypes.windll.user32.GetGUIThreadInfo(0, ctypes.byref(gui_info)):
                hwnd_caret = gui_info.hwndCaret
                if hwnd_caret:
                    # Convert caret rect to screen coordinates
                    pt = ctypes.wintypes.POINT(
                        gui_info.rcCaret.left,
                        gui_info.rcCaret.bottom,  # bottom of the caret line
                    )
                    ctypes.windll.user32.ClientToScreen(hwnd_caret, ctypes.byref(pt))
                    return pt.x, pt.y
        except Exception:
            pass

    # --- Fallback: mouse position (works everywhere) ----------------------
    if _PLATFORM == "Windows":
        try:
            pt = ctypes.wintypes.POINT()
            ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
            return pt.x, pt.y
        except Exception:
            pass

    # Ultimate fallback — centre of primary screen (shouldn't normally hit)
    return 500, 400


# --- HUD states -----------------------------------------------------------
STATE_IDLE     = "idle"
STATE_WORKING  = "working"
STATE_RESULT   = "result"
STATE_ERROR    = "error"


class GhostHUD:
    """Singleton-style floating HUD widget.

    Usage from the main thread:
        hud = GhostHUD(root)
        hud.show_working("Fixing grammar…")
        # … later, from the UI-poll callback …
        hud.show_result(on_accept_cb, on_reject_cb, on_diff_cb, label="Done")
        hud.show_error("API timeout")
    """

    # Geometry constants
    HUD_WIDTH       = 340
    HUD_HEIGHT_SLIM = 50   # working / error state
    HUD_HEIGHT_FULL = 60   # result state (shows buttons)
    CARET_OFFSET_Y  = 22   # gap below the caret line
    SCREEN_MARGIN   = 12   # keep the HUD inside screen edges

    # Animation
    FADE_STEPS      = 8
    FADE_INTERVAL   = 25   # ms per step
    SHIMMER_INTERVAL = 80  # ms between shimmer frames

    def __init__(self, parent: ctk.CTk):
        self._parent = parent
        self._state  = STATE_IDLE

        # --- Build the toplevel window (hidden) ---------------------------
        self._win = ctk.CTkToplevel(parent)
        self._win.withdraw()
        self._win.overrideredirect(True)          # borderless
        self._win.attributes("-topmost", True)
        # Prevent the HUD from showing in the taskbar (Windows)
        if _PLATFORM == "Windows":
            self._win.attributes("-toolwindow", True)

        # --- Pill-shaped panel --------------------------------------------
        is_dark = ctk.get_appearance_mode() == "Dark"
        
        # Transparent key to hide the square corners of the toplevel
        transparent_color = "#000001" if is_dark else "#FFFFFE"
        self._win.configure(fg_color=transparent_color)
        if _PLATFORM == "Windows":
            self._win.attributes("-transparentcolor", transparent_color)

        self._bg = "#1E1E1E" if is_dark else "#F5F5F5"
        self._fg = "#E0E0E0" if is_dark else "#222222"
        self._accent   = "#0078D4"
        self._err_fg   = "#FF6B6B"

        self._panel = ctk.CTkFrame(
            self._win,
            fg_color=self._bg,
            corner_radius=16,
            border_width=1,
            border_color=("#3A3A3A" if is_dark else "#CCCCCC"),
        )
        self._panel.pack(expand=True, fill="both", padx=2, pady=2)

        # Inner layout: [icon/spinner]  [label]  [buttons …]
        self._inner = ctk.CTkFrame(self._panel, fg_color="transparent")
        self._inner.pack(expand=True, fill="both", padx=12, pady=6)

        # Spinner / status dot
        self._dot = ctk.CTkLabel(
            self._inner, text="", width=20, font=("Segoe UI Variable Display", 16),
            text_color=self._accent,
        )
        self._dot.pack(side="left", padx=(0, 6))

        # Status label
        self._label = ctk.CTkLabel(
            self._inner, text="", font=("Segoe UI Variable Display", 13),
            text_color=self._fg, anchor="w",
        )
        self._label.pack(side="left", fill="x", expand=True)

        # Action buttons (hidden until result state)
        btn_font = ("Segoe UI Variable Display", 13, "bold")
        self._btn_accept = ctk.CTkButton(
            self._inner, text="✔", width=36, height=30, corner_radius=8,
            font=btn_font, fg_color=self._accent, hover_color="#106EBE",
            text_color="white",
        )
        self._btn_reject = ctk.CTkButton(
            self._inner, text="✖", width=36, height=30, corner_radius=8,
            font=btn_font,
            fg_color=("#D0D0D0" if not is_dark else "#333333"),
            hover_color=("#BBBBBB" if not is_dark else "#444444"),
            text_color=("#333333" if not is_dark else "#CCCCCC"),
        )
        self._btn_diff = ctk.CTkButton(
            self._inner, text="↗", width=36, height=30, corner_radius=8,
            font=btn_font,
            fg_color=("#D0D0D0" if not is_dark else "#333333"),
            hover_color=("#BBBBBB" if not is_dark else "#444444"),
            text_color=("#333333" if not is_dark else "#CCCCCC"),
        )

        # Shimmer animation state
        self._shimmer_chars = ["◐", "◓", "◑", "◒"]
        self._shimmer_idx   = 0
        self._shimmer_job   = None

        # Fade animation state
        self._fade_job   = None
        self._current_alpha = 0.0

        # Auto-dismiss timer
        self._dismiss_job = None

        # Keyboard binding for the toplevel
        self._win.bind("<Escape>", lambda e: self.dismiss())

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def show_working(self, label: str = "Thinking…"):
        """Display the HUD in its 'working' shimmer state near the caret."""
        self._cancel_timers()
        self._state = STATE_WORKING

        # Position near the caret *before* showing
        self._win.update_idletasks()
        self._position_near_caret(self.HUD_HEIGHT_SLIM)

        # Configure visuals
        self._hide_buttons()
        self._label.configure(text=label, text_color=self._fg)
        self._win.geometry(f"{self.HUD_WIDTH}x{self.HUD_HEIGHT_SLIM}")

        # Start shimmer animation
        self._shimmer_idx = 0
        self._tick_shimmer()

        # Fade in
        self._fade_in()

    def show_result(self, on_accept, on_reject, on_diff=None,
                    label: str = "Ready"):
        """Transition the HUD to 'result' with action buttons."""
        self._cancel_timers()
        self._state = STATE_RESULT

        # Stop shimmer
        self._dot.configure(text="✦")

        # Label
        self._label.configure(text=label, text_color=self._fg)

        # Wire callbacks & show buttons
        self._btn_accept.configure(command=lambda: self._on_action(on_accept))
        self._btn_reject.configure(command=lambda: self._on_action(on_reject))

        # Keyboard bindings
        self._win.bind("<Return>", lambda e: self._on_action(on_accept))
        self._win.bind("<KP_Enter>", lambda e: self._on_action(on_accept))
        self._win.bind("<Escape>", lambda e: self._on_action(on_reject))

        self._btn_reject.pack(side="right", padx=(2, 0))
        if on_diff:
            self._btn_diff.configure(command=lambda: self._on_action(on_diff))
            self._btn_diff.pack(side="right", padx=(2, 0))
        self._btn_accept.pack(side="right", padx=(2, 0))

        # Resize to full height
        self._win.geometry(f"{self.HUD_WIDTH}x{self.HUD_HEIGHT_FULL}")

        # If the HUD isn't visible yet (edge case), fade it in
        if self._current_alpha < 0.8:
            self._fade_in()
            
        # Briefly take focus so Enter/Escape work immediately
        self._win.focus_force()

        # Auto-dismiss after 15 seconds if the user ignores it
        self._dismiss_job = self._win.after(15000, self.dismiss)

    def show_error(self, label: str = "Error", auto_dismiss_ms: int = 4000):
        """Flash an error state, then auto-dismiss."""
        self._cancel_timers()
        self._state = STATE_ERROR

        self._hide_buttons()
        self._dot.configure(text="⚠")
        self._label.configure(text=label, text_color=self._err_fg)
        self._win.geometry(f"{self.HUD_WIDTH}x{self.HUD_HEIGHT_SLIM}")

        if self._current_alpha < 0.8:
            self._position_near_caret(self.HUD_HEIGHT_SLIM)
            self._fade_in()

        self._dismiss_job = self._win.after(auto_dismiss_ms, self.dismiss)

    def dismiss(self, immediate: bool = False):
        """Fade out and hide the HUD."""
        self._cancel_timers()
        if self._state == STATE_IDLE:
            return
        self._state = STATE_IDLE
        
        # Unbind result keys
        self._win.unbind("<Return>")
        self._win.unbind("<KP_Enter>")
        # Restore default escape behavior
        self._win.bind("<Escape>", lambda e: self.dismiss())

        if immediate:
            self._current_alpha = 0.0
            self._win.attributes("-alpha", 0.0)
            self._win.withdraw()
        else:
            self._fade_out()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _on_action(self, callback):
        """Run a callback and dismiss the HUD."""
        self.dismiss(immediate=True)
        if callback:
            callback()

    def _hide_buttons(self):
        for btn in (self._btn_accept, self._btn_reject, self._btn_diff):
            btn.pack_forget()

    def _position_near_caret(self, hud_height):
        """Place the HUD below the caret, clamped inside the screen."""
        self._win.update_idletasks()
        cx, cy = _get_caret_position()

        # Offset: centered horizontally, just below the caret vertically
        x = cx - self.HUD_WIDTH // 2
        y = cy + self.CARET_OFFSET_Y

        # Clamp to screen bounds
        try:
            sw = self._win.winfo_screenwidth()
            sh = self._win.winfo_screenheight()
        except Exception:
            sw, sh = 1920, 1080

        x = max(self.SCREEN_MARGIN, min(x, sw - self.HUD_WIDTH - self.SCREEN_MARGIN))
        # If the HUD would go below the screen, show it *above* the caret
        if y + hud_height + self.SCREEN_MARGIN > sh:
            y = cy - hud_height - self.CARET_OFFSET_Y
        y = max(self.SCREEN_MARGIN, y)

        self._win.geometry(f"+{x}+{y}")

    # --- Shimmer animation ------------------------------------------------

    def _tick_shimmer(self):
        if self._state != STATE_WORKING:
            return
        char = self._shimmer_chars[self._shimmer_idx % len(self._shimmer_chars)]
        self._dot.configure(text=char)
        self._shimmer_idx += 1
        self._shimmer_job = self._win.after(self.SHIMMER_INTERVAL, self._tick_shimmer)

    # --- Fade animations --------------------------------------------------

    def _fade_in(self):
        self._win.deiconify()
        self._current_alpha = 0.0
        self._win.attributes("-alpha", 0.0)
        self._step_fade(target=0.95, step=0.95 / self.FADE_STEPS)

    def _fade_out(self):
        self._step_fade(target=0.0, step=-(self._current_alpha / max(self.FADE_STEPS, 1)))

    def _step_fade(self, target, step):
        if self._fade_job:
            self._win.after_cancel(self._fade_job)
            self._fade_job = None

        self._current_alpha += step
        done = (step > 0 and self._current_alpha >= target) or \
               (step < 0 and self._current_alpha <= target)
        if done:
            self._current_alpha = target
        self._current_alpha = max(0.0, min(1.0, self._current_alpha))

        try:
            self._win.attributes("-alpha", self._current_alpha)
        except tk.TclError:
            return  # window destroyed

        if done:
            if target == 0.0:
                self._win.withdraw()
            return

        self._fade_job = self._win.after(self.FADE_INTERVAL,
                                         lambda: self._step_fade(target, step))

    # --- Timer management -------------------------------------------------

    def _cancel_timers(self):
        for attr in ("_shimmer_job", "_fade_job", "_dismiss_job"):
            job = getattr(self, attr, None)
            if job:
                try:
                    self._win.after_cancel(job)
                except Exception:
                    pass
                setattr(self, attr, None)
