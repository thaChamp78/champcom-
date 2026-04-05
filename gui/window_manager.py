"""
ChampCom Window Manager - Draggable, resizable application windows
"""
import tkinter as tk


class ManagedWindow(tk.Toplevel):
    """A draggable, resizable application window within ChampCom."""

    def __init__(self, desktop, title, width, height):
        super().__init__(desktop.root)
        self.desktop = desktop
        self.title_text = title

        # Window setup
        self.overrideredirect(False)
        self.title(title)
        self.geometry(f"{width}x{height}")
        self.configure(bg=desktop.BG_COLOR)
        self.minsize(300, 200)

        # Center on parent
        self.update_idletasks()
        px = desktop.root.winfo_x()
        py = desktop.root.winfo_y()
        pw = desktop.root.winfo_width()
        ph = desktop.root.winfo_height()
        x = px + (pw - width) // 2
        y = py + (ph - height) // 2
        self.geometry(f"+{x}+{y}")

        # Title bar
        self.titlebar = tk.Frame(self, bg=desktop.ACCENT_COLOR, height=30)
        self.titlebar.pack(fill=tk.X)
        self.titlebar.pack_propagate(False)

        # Title label
        tk.Label(
            self.titlebar, text=f"  {title}",
            bg=desktop.ACCENT_COLOR, fg=desktop.TEXT_COLOR,
            font=("Segoe UI", 9, "bold"), anchor="w"
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Window buttons
        btn_frame = tk.Frame(self.titlebar, bg=desktop.ACCENT_COLOR)
        btn_frame.pack(side=tk.RIGHT)

        # Minimize
        tk.Button(
            btn_frame, text="\u2500", width=3,
            bg=desktop.ACCENT_COLOR, fg=desktop.TEXT_COLOR,
            font=("Segoe UI", 8), relief=tk.FLAT,
            command=self._minimize,
            activebackground=desktop.HIGHLIGHT_COLOR
        ).pack(side=tk.LEFT)

        # Maximize
        tk.Button(
            btn_frame, text="\u25A1", width=3,
            bg=desktop.ACCENT_COLOR, fg=desktop.TEXT_COLOR,
            font=("Segoe UI", 8), relief=tk.FLAT,
            command=self._toggle_maximize,
            activebackground=desktop.HIGHLIGHT_COLOR
        ).pack(side=tk.LEFT)

        # Close
        tk.Button(
            btn_frame, text="\u2715", width=3,
            bg=desktop.ACCENT_COLOR, fg=desktop.TEXT_COLOR,
            font=("Segoe UI", 8), relief=tk.FLAT,
            command=self._close,
            activebackground="#e74c3c"
        ).pack(side=tk.LEFT)

        # Content area
        self.content = tk.Frame(self, bg=desktop.BG_COLOR)
        self.content.pack(fill=tk.BOTH, expand=True)

        # Track state
        self.maximized = False
        self._normal_geo = None

        # Register in taskbar
        desktop.taskbar.add_window(title, self)

        # Handle close via window manager
        self.protocol("WM_DELETE_WINDOW", self._close)

    def _minimize(self):
        self.withdraw()

    def _toggle_maximize(self):
        if self.maximized:
            if self._normal_geo:
                self.geometry(self._normal_geo)
            self.maximized = False
        else:
            self._normal_geo = self.geometry()
            pw = self.desktop.root.winfo_width()
            ph = self.desktop.root.winfo_height()
            px = self.desktop.root.winfo_x()
            py = self.desktop.root.winfo_y()
            self.geometry(f"{pw}x{ph-40}+{px}+{py}")
            self.maximized = True

    def _close(self):
        self.desktop.taskbar.remove_window(self)
        self.desktop.wm.unregister(self)
        self.destroy()


class WindowManager:
    """Manages all open application windows."""

    def __init__(self, desktop):
        self.desktop = desktop
        self.windows = []

    def create_window(self, title, width=600, height=400):
        win = ManagedWindow(self.desktop, title, width, height)
        self.windows.append(win)
        return win.content

    def unregister(self, window):
        self.windows = [w for w in self.windows if w is not window]

    def close_all(self):
        for win in list(self.windows):
            try:
                win._close()
            except tk.TclError:
                pass

    def get_window_count(self):
        return len(self.windows)
