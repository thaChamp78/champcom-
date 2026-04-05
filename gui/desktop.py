"""
ChampCom Desktop Environment - The main OS-within-OS interface
"""
import tkinter as tk
from tkinter import ttk
import time
import os

from gui.taskbar import Taskbar
from gui.window_manager import WindowManager


class Desktop:
    """The main desktop environment - OS within an OS."""

    BG_COLOR = "#1a1a2e"
    ACCENT_COLOR = "#16213e"
    TEXT_COLOR = "#e0e0e0"
    HIGHLIGHT_COLOR = "#0f3460"
    ACTIVE_COLOR = "#533483"

    def __init__(self, engine):
        self.engine = engine
        self.root = tk.Tk()
        self.root.title("ChampCom OS")
        self.root.configure(bg=self.BG_COLOR)

        # Get screen size and set window
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        w = min(int(engine.config.get("app.width", 1280)), sw)
        h = min(int(engine.config.get("app.height", 720)), sh)
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")
        self.root.minsize(800, 600)

        # Style
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self._configure_styles()

        # Window manager
        self.wm = WindowManager(self)

        # Build layout
        self._build_desktop()
        self._build_taskbar()
        self._place_desktop_icons()

        # Status update loop
        self._update_clock()

    def _configure_styles(self):
        self.style.configure("Dark.TFrame", background=self.BG_COLOR)
        self.style.configure("Taskbar.TFrame", background=self.ACCENT_COLOR)
        self.style.configure("Dark.TLabel",
                             background=self.BG_COLOR,
                             foreground=self.TEXT_COLOR,
                             font=("Segoe UI", 10))
        self.style.configure("Title.TLabel",
                             background=self.ACCENT_COLOR,
                             foreground=self.TEXT_COLOR,
                             font=("Segoe UI", 10, "bold"))
        self.style.configure("Icon.TLabel",
                             background=self.BG_COLOR,
                             foreground=self.TEXT_COLOR,
                             font=("Segoe UI", 9))
        self.style.configure("Dark.TButton",
                             background=self.HIGHLIGHT_COLOR,
                             foreground=self.TEXT_COLOR,
                             font=("Segoe UI", 9),
                             borderwidth=0,
                             padding=5)
        self.style.map("Dark.TButton",
                       background=[("active", self.ACTIVE_COLOR)])

    def _build_desktop(self):
        self.desktop_frame = tk.Canvas(
            self.root,
            bg=self.BG_COLOR,
            highlightthickness=0
        )
        self.desktop_frame.pack(fill=tk.BOTH, expand=True)

        # Right-click context menu
        self.context_menu = tk.Menu(self.root, tearoff=0,
                                    bg=self.ACCENT_COLOR,
                                    fg=self.TEXT_COLOR,
                                    activebackground=self.ACTIVE_COLOR)
        self.context_menu.add_command(label="New Folder",
                                      command=lambda: self._open_app("file_manager"))
        self.context_menu.add_command(label="Terminal",
                                      command=lambda: self._open_app("terminal"))
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Settings",
                                      command=lambda: self._open_app("settings"))
        self.context_menu.add_command(label="About ChampCom",
                                      command=self._show_about)

        self.desktop_frame.bind("<Button-3>", self._show_context_menu)

    def _build_taskbar(self):
        self.taskbar = Taskbar(self)

    def _place_desktop_icons(self):
        icons = [
            ("Files", "file_manager", 50, 30),
            ("Terminal", "terminal", 50, 120),
            ("Editor", "text_editor", 50, 210),
            ("Media", "media_player", 50, 300),
            ("Browser", "browser", 50, 390),
            ("AI Chat", "ai_chat", 50, 480),
            ("Settings", "settings", 160, 30),
        ]
        # Icon symbols (using Unicode)
        symbols = {
            "file_manager": "\U0001F4C1",
            "terminal": "\U0001F4BB",
            "text_editor": "\U0001F4DD",
            "media_player": "\U0001F3B5",
            "browser": "\U0001F310",
            "ai_chat": "\U0001F916",
            "settings": "\u2699\uFE0F",
        }

        for name, app_id, x, y in icons:
            frame = tk.Frame(self.desktop_frame, bg=self.BG_COLOR, cursor="hand2")

            symbol = symbols.get(app_id, "\U0001F4E6")
            icon_label = tk.Label(frame, text=symbol, font=("Segoe UI", 28),
                                  bg=self.BG_COLOR, fg=self.TEXT_COLOR)
            icon_label.pack()

            text_label = tk.Label(frame, text=name, font=("Segoe UI", 9),
                                  bg=self.BG_COLOR, fg=self.TEXT_COLOR)
            text_label.pack()

            frame.bind("<Double-Button-1>", lambda e, a=app_id: self._open_app(a))
            icon_label.bind("<Double-Button-1>", lambda e, a=app_id: self._open_app(a))
            text_label.bind("<Double-Button-1>", lambda e, a=app_id: self._open_app(a))

            self.desktop_frame.create_window(x, y, window=frame, anchor="nw")

    def _open_app(self, app_id):
        from gui.apps.file_manager import FileManagerApp
        from gui.apps.terminal import TerminalApp
        from gui.apps.text_editor import TextEditorApp
        from gui.apps.media_player import MediaPlayerApp
        from gui.apps.browser import BrowserApp
        from gui.apps.ai_chat import AIChatApp
        from gui.apps.settings import SettingsApp

        apps = {
            "file_manager": ("Files", FileManagerApp),
            "terminal": ("Terminal", TerminalApp),
            "text_editor": ("Text Editor", TextEditorApp),
            "media_player": ("Media Player", MediaPlayerApp),
            "browser": ("Browser", BrowserApp),
            "ai_chat": ("AI Chat", AIChatApp),
            "settings": ("Settings", SettingsApp),
        }

        if app_id in apps:
            title, app_class = apps[app_id]
            win = self.wm.create_window(title, 600, 400)
            app_class(win, self.engine)

    def _show_context_menu(self, event):
        self.context_menu.post(event.x_root, event.y_root)

    def _show_about(self):
        win = self.wm.create_window("About ChampCom", 400, 300)
        frame = tk.Frame(win, bg=self.BG_COLOR)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text="\U0001F3AE", font=("Segoe UI", 48),
                 bg=self.BG_COLOR, fg=self.TEXT_COLOR).pack(pady=10)
        tk.Label(frame, text="ChampCom OS", font=("Segoe UI", 18, "bold"),
                 bg=self.BG_COLOR, fg=self.TEXT_COLOR).pack()
        tk.Label(frame, text="Version 1.0.0", font=("Segoe UI", 11),
                 bg=self.BG_COLOR, fg="#888").pack()
        tk.Label(frame, text="Operating System Within an Operating System",
                 font=("Segoe UI", 10),
                 bg=self.BG_COLOR, fg=self.TEXT_COLOR).pack(pady=5)
        tk.Label(frame, text="Built by thaChamp78",
                 font=("Segoe UI", 10),
                 bg=self.BG_COLOR, fg=self.ACTIVE_COLOR).pack(pady=10)

    def _update_clock(self):
        self.taskbar.update_clock()
        self.root.after(1000, self._update_clock)

    def run(self):
        self.root.mainloop()

    def shutdown(self):
        self.root.quit()
