"""
ChampCom Taskbar - Bottom taskbar with start menu and system tray
"""
import tkinter as tk
import time


class Taskbar:
    """Bottom taskbar with start menu, running apps, and system tray."""

    def __init__(self, desktop):
        self.desktop = desktop
        self.root = desktop.root
        self.open_windows = {}

        # Taskbar frame at bottom
        self.bar = tk.Frame(self.root, bg=desktop.ACCENT_COLOR, height=40)
        self.bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.bar.pack_propagate(False)

        # Start button
        self.start_btn = tk.Button(
            self.bar, text="\U0001F3AE ChampCom",
            bg=desktop.ACTIVE_COLOR, fg=desktop.TEXT_COLOR,
            font=("Segoe UI", 10, "bold"),
            relief=tk.FLAT, padx=10, pady=2,
            command=self._toggle_start_menu,
            activebackground=desktop.HIGHLIGHT_COLOR,
            activeforeground=desktop.TEXT_COLOR
        )
        self.start_btn.pack(side=tk.LEFT, padx=2, pady=2)

        # Running apps area
        self.apps_frame = tk.Frame(self.bar, bg=desktop.ACCENT_COLOR)
        self.apps_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # System tray (right side)
        self.tray = tk.Frame(self.bar, bg=desktop.ACCENT_COLOR)
        self.tray.pack(side=tk.RIGHT, padx=5)

        # Clock
        self.clock_label = tk.Label(
            self.tray, text="", bg=desktop.ACCENT_COLOR,
            fg=desktop.TEXT_COLOR, font=("Segoe UI", 9)
        )
        self.clock_label.pack(side=tk.RIGHT, padx=5)

        # Status indicator
        self.status_label = tk.Label(
            self.tray, text="\u25CF AI", bg=desktop.ACCENT_COLOR,
            fg="#00ff88", font=("Segoe UI", 9)
        )
        self.status_label.pack(side=tk.RIGHT, padx=3)

        # Start menu (hidden by default)
        self.start_menu = None
        self.start_menu_visible = False

    def _toggle_start_menu(self):
        if self.start_menu_visible:
            self._hide_start_menu()
        else:
            self._show_start_menu()

    def _show_start_menu(self):
        if self.start_menu:
            self.start_menu.destroy()

        d = self.desktop
        self.start_menu = tk.Frame(
            self.root, bg=d.ACCENT_COLOR,
            highlightbackground=d.HIGHLIGHT_COLOR,
            highlightthickness=1
        )

        menu_items = [
            ("\U0001F4C1  Files", "file_manager"),
            ("\U0001F4BB  Terminal", "terminal"),
            ("\U0001F4DD  Text Editor", "text_editor"),
            ("\U0001F3B5  Media Player", "media_player"),
            ("\U0001F310  Browser", "browser"),
            ("\U0001F916  AI Chat", "ai_chat"),
            ("\u2699\uFE0F  Settings", "settings"),
        ]

        for text, app_id in menu_items:
            btn = tk.Button(
                self.start_menu, text=text,
                bg=d.ACCENT_COLOR, fg=d.TEXT_COLOR,
                font=("Segoe UI", 11), anchor="w",
                relief=tk.FLAT, padx=15, pady=5,
                command=lambda a=app_id: self._launch_from_menu(a),
                activebackground=d.ACTIVE_COLOR,
                activeforeground=d.TEXT_COLOR
            )
            btn.pack(fill=tk.X)

        # Separator
        tk.Frame(self.start_menu, bg=d.HIGHLIGHT_COLOR, height=1).pack(fill=tk.X, padx=5)

        # Power options
        tk.Button(
            self.start_menu, text="\u23FB  Shutdown",
            bg=d.ACCENT_COLOR, fg="#ff6b6b",
            font=("Segoe UI", 11), anchor="w",
            relief=tk.FLAT, padx=15, pady=5,
            command=self.desktop.shutdown,
            activebackground="#ff0000",
            activeforeground="#ffffff"
        ).pack(fill=tk.X)

        # Position above taskbar
        self.start_menu.place(x=2, y=0, anchor="sw",
                              relx=0, rely=1.0)
        self.start_menu.lift()

        # Update position after rendering
        self.root.update_idletasks()
        menu_height = self.start_menu.winfo_reqheight()
        bar_height = self.bar.winfo_height()
        root_height = self.root.winfo_height()
        self.start_menu.place(x=2, y=root_height - bar_height - menu_height)

        self.start_menu_visible = True

        # Close menu when clicking elsewhere
        self.root.bind("<Button-1>", self._check_close_menu, add="+")

    def _hide_start_menu(self):
        if self.start_menu:
            self.start_menu.destroy()
            self.start_menu = None
        self.start_menu_visible = False

    def _check_close_menu(self, event):
        if self.start_menu_visible:
            widget = event.widget
            if self.start_menu and not str(widget).startswith(str(self.start_menu)):
                if widget != self.start_btn:
                    self._hide_start_menu()

    def _launch_from_menu(self, app_id):
        self._hide_start_menu()
        self.desktop._open_app(app_id)

    def add_window(self, title, window):
        """Add a running app button to the taskbar."""
        btn = tk.Button(
            self.apps_frame, text=title,
            bg=self.desktop.HIGHLIGHT_COLOR,
            fg=self.desktop.TEXT_COLOR,
            font=("Segoe UI", 9),
            relief=tk.FLAT, padx=8, pady=1,
            command=lambda: self._focus_window(window),
            activebackground=self.desktop.ACTIVE_COLOR,
            activeforeground=self.desktop.TEXT_COLOR
        )
        btn.pack(side=tk.LEFT, padx=1, pady=2)
        self.open_windows[id(window)] = btn

    def remove_window(self, window):
        """Remove app button from taskbar."""
        wid = id(window)
        if wid in self.open_windows:
            self.open_windows[wid].destroy()
            del self.open_windows[wid]

    def _focus_window(self, window):
        try:
            window.lift()
            window.focus_set()
        except tk.TclError:
            pass

    def update_clock(self):
        now = time.strftime("%I:%M %p")
        date = time.strftime("%m/%d/%Y")
        self.clock_label.config(text=f"{now}\n{date}")
