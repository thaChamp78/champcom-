"""
ChampCom Browser - Built-in web browser (opens in system browser)
"""
import tkinter as tk
import webbrowser


class BrowserApp:
    def __init__(self, parent, engine):
        self.parent = parent
        self.engine = engine
        self.history = []
        self.history_index = -1

        self._build_ui()

    def _build_ui(self):
        bg = "#1a1a2e"
        fg = "#e0e0e0"
        accent = "#16213e"

        # Navigation bar
        nav = tk.Frame(self.parent, bg=accent)
        nav.pack(fill=tk.X)

        tk.Button(nav, text="\u2190", bg=accent, fg=fg,
                  relief=tk.FLAT, font=("Segoe UI", 12),
                  command=self._back).pack(side=tk.LEFT, padx=2)
        tk.Button(nav, text="\u2192", bg=accent, fg=fg,
                  relief=tk.FLAT, font=("Segoe UI", 12),
                  command=self._forward).pack(side=tk.LEFT, padx=2)
        tk.Button(nav, text="\u2302", bg=accent, fg=fg,
                  relief=tk.FLAT, font=("Segoe UI", 12),
                  command=self._home).pack(side=tk.LEFT, padx=2)

        self.url_var = tk.StringVar(value="https://")
        self.url_entry = tk.Entry(
            nav, textvariable=self.url_var,
            bg="#0d1117", fg=fg, insertbackground=fg,
            font=("Segoe UI", 10), relief=tk.FLAT
        )
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=3)
        self.url_entry.bind("<Return>", lambda e: self._navigate())

        tk.Button(nav, text="Go", bg="#533483", fg=fg,
                  relief=tk.FLAT, font=("Segoe UI", 9),
                  command=self._navigate, padx=10).pack(side=tk.RIGHT, padx=5, pady=3)

        # Bookmarks bar
        bm_bar = tk.Frame(self.parent, bg=accent)
        bm_bar.pack(fill=tk.X)

        bookmarks = [
            ("Google", "https://www.google.com"),
            ("YouTube", "https://www.youtube.com"),
            ("GitHub", "https://github.com"),
            ("Wikipedia", "https://www.wikipedia.org"),
            ("Reddit", "https://www.reddit.com"),
        ]
        for name, url in bookmarks:
            tk.Button(bm_bar, text=name, bg=accent, fg="#888",
                      relief=tk.FLAT, font=("Segoe UI", 8),
                      command=lambda u=url: self._open_url(u),
                      padx=6).pack(side=tk.LEFT)

        # Content area
        content = tk.Frame(self.parent, bg="#0d1117")
        content.pack(fill=tk.BOTH, expand=True)

        # Info panel
        info_frame = tk.Frame(content, bg="#0d1117")
        info_frame.pack(expand=True)

        tk.Label(info_frame, text="\U0001F310", font=("Segoe UI", 48),
                 bg="#0d1117", fg=fg).pack(pady=10)
        tk.Label(info_frame, text="ChampCom Browser",
                 font=("Segoe UI", 16, "bold"),
                 bg="#0d1117", fg=fg).pack()
        tk.Label(info_frame,
                 text="Enter a URL and press Go to open in your system browser.\n"
                      "Or click a bookmark above.",
                 font=("Segoe UI", 10), bg="#0d1117", fg="#888",
                 justify=tk.CENTER).pack(pady=10)

        # Quick links
        links_frame = tk.Frame(content, bg="#0d1117")
        links_frame.pack(pady=10)

        quick_links = [
            ("Search Google", "https://www.google.com"),
            ("Watch YouTube", "https://www.youtube.com"),
            ("Browse GitHub", "https://github.com"),
        ]
        for text, url in quick_links:
            btn = tk.Button(links_frame, text=text,
                            bg="#16213e", fg=fg, relief=tk.FLAT,
                            font=("Segoe UI", 10), padx=15, pady=5,
                            command=lambda u=url: self._open_url(u))
            btn.pack(side=tk.LEFT, padx=5)

        # History panel
        history_label = tk.Label(self.parent, text="  History", bg=accent,
                                 fg=fg, font=("Segoe UI", 9, "bold"), anchor="w")
        history_label.pack(fill=tk.X)

        self.history_list = tk.Listbox(
            self.parent, bg="#0d1117", fg=fg, height=4,
            selectbackground="#533483", font=("Segoe UI", 9),
            relief=tk.FLAT
        )
        self.history_list.pack(fill=tk.X)
        self.history_list.bind("<Double-Button-1>", self._open_from_history)

    def _navigate(self):
        url = self.url_var.get().strip()
        if url and not url.startswith(("http://", "https://")):
            url = "https://" + url
        self._open_url(url)

    def _open_url(self, url):
        if not url:
            return
        self.url_var.set(url)
        self.history.append(url)
        self.history_index = len(self.history) - 1
        self.history_list.insert(0, url)
        webbrowser.open(url)

    def _back(self):
        if self.history_index > 0:
            self.history_index -= 1
            self._open_url(self.history[self.history_index])

    def _forward(self):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self._open_url(self.history[self.history_index])

    def _home(self):
        self.url_var.set("https://")

    def _open_from_history(self, event):
        sel = self.history_list.curselection()
        if sel:
            url = self.history_list.get(sel[0])
            self._open_url(url)
