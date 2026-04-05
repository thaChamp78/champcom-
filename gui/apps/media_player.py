"""
ChampCom Media Player App - GUI for media playback
"""
import tkinter as tk
from tkinter import filedialog
import os


class MediaPlayerApp:
    def __init__(self, parent, engine):
        self.parent = parent
        self.engine = engine
        self.player = engine.media_player
        self.playlist = []
        self.current_index = -1

        self._build_ui()

    def _build_ui(self):
        bg = "#1a1a2e"
        fg = "#e0e0e0"
        accent = "#16213e"

        # Album art / Now playing area
        display = tk.Frame(self.parent, bg="#0d1117", height=150)
        display.pack(fill=tk.X)
        display.pack_propagate(False)

        self.now_playing = tk.Label(
            display, text="\U0001F3B5\n\nNo media loaded",
            bg="#0d1117", fg=fg,
            font=("Segoe UI", 14), justify=tk.CENTER
        )
        self.now_playing.pack(expand=True)

        # Controls
        controls = tk.Frame(self.parent, bg=accent)
        controls.pack(fill=tk.X, pady=2)

        btn_style = {"bg": accent, "fg": fg, "relief": tk.FLAT,
                     "font": ("Segoe UI", 14), "padx": 10}

        tk.Button(controls, text="\u23EE", command=self._prev,
                  **btn_style).pack(side=tk.LEFT, padx=5)
        self.play_btn = tk.Button(controls, text="\u25B6", command=self._play,
                                  **btn_style)
        self.play_btn.pack(side=tk.LEFT, padx=5)
        tk.Button(controls, text="\u23F9", command=self._stop,
                  **btn_style).pack(side=tk.LEFT, padx=5)
        tk.Button(controls, text="\u23ED", command=self._next,
                  **btn_style).pack(side=tk.LEFT, padx=5)

        # Volume
        vol_frame = tk.Frame(controls, bg=accent)
        vol_frame.pack(side=tk.RIGHT, padx=10)
        tk.Label(vol_frame, text="\U0001F50A", bg=accent, fg=fg,
                 font=("Segoe UI", 10)).pack(side=tk.LEFT)
        self.volume = tk.Scale(vol_frame, from_=0, to=100, orient=tk.HORIZONTAL,
                               bg=accent, fg=fg, troughcolor="#0d1117",
                               highlightthickness=0, length=100,
                               showvalue=False)
        self.volume.set(80)
        self.volume.pack(side=tk.LEFT)

        # Playlist area
        playlist_label = tk.Label(self.parent, text="  Playlist", bg=accent,
                                  fg=fg, font=("Segoe UI", 9, "bold"), anchor="w")
        playlist_label.pack(fill=tk.X)

        list_frame = tk.Frame(self.parent, bg=bg)
        list_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.playlist_box = tk.Listbox(
            list_frame, bg="#0d1117", fg=fg,
            selectbackground="#533483",
            font=("Segoe UI", 10), relief=tk.FLAT,
            yscrollcommand=scrollbar.set
        )
        self.playlist_box.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.playlist_box.yview)
        self.playlist_box.bind("<Double-Button-1>", lambda e: self._play_selected())

        # Bottom toolbar
        toolbar = tk.Frame(self.parent, bg=accent)
        toolbar.pack(fill=tk.X)

        tk.Button(toolbar, text="+ Add Files", bg=accent, fg=fg,
                  relief=tk.FLAT, font=("Segoe UI", 9),
                  command=self._add_files).pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="Clear", bg=accent, fg=fg,
                  relief=tk.FLAT, font=("Segoe UI", 9),
                  command=self._clear_playlist).pack(side=tk.LEFT, padx=5)

    def _add_files(self):
        files = filedialog.askopenfilenames(
            filetypes=[
                ("Media Files", "*.mp3 *.wav *.ogg *.flac *.mp4 *.avi *.mkv *.webm"),
                ("Audio", "*.mp3 *.wav *.ogg *.flac *.m4a"),
                ("Video", "*.mp4 *.avi *.mkv *.mov *.webm"),
                ("All Files", "*.*")
            ]
        )
        for f in files:
            self.playlist.append(f)
            self.playlist_box.insert(tk.END, f"  {os.path.basename(f)}")

    def _play(self):
        if self.playlist and self.current_index < 0:
            self.current_index = 0
        if 0 <= self.current_index < len(self.playlist):
            path = self.playlist[self.current_index]
            self.player.play(path)
            self.now_playing.config(
                text=f"\U0001F3B5\n\n{os.path.basename(path)}"
            )
            self.play_btn.config(text="\u23F8")
            self.playlist_box.selection_clear(0, tk.END)
            self.playlist_box.selection_set(self.current_index)

    def _play_selected(self):
        sel = self.playlist_box.curselection()
        if sel:
            self.current_index = sel[0]
            self._play()

    def _stop(self):
        self.player.stop()
        self.play_btn.config(text="\u25B6")
        self.now_playing.config(text="\U0001F3B5\n\nStopped")

    def _next(self):
        if self.playlist:
            self.current_index = (self.current_index + 1) % len(self.playlist)
            self._play()

    def _prev(self):
        if self.playlist:
            self.current_index = (self.current_index - 1) % len(self.playlist)
            self._play()

    def _clear_playlist(self):
        self.playlist.clear()
        self.playlist_box.delete(0, tk.END)
        self.current_index = -1
        self._stop()
