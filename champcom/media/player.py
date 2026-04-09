# ChampCom Media Player - Author: Jordan Marzette (C)
try:
    import tkinter as tk
    from tkinter import filedialog
    HAS_TK = True
except ImportError:
    HAS_TK = False
try:
    import vlc
    HAS_VLC = True
except ImportError:
    HAS_VLC = False
import os
BG = "#0f172a"; ACC = "#00ff88"; TXT = "#e2e8f0"; SUB = "#1e293b"

if HAS_TK:
    class MediaPlayer(tk.Frame):
        def __init__(s, parent, cc):
            super().__init__(parent, bg=BG)
            s.cc = cc; s.playlist = []; s.idx = -1
            s.vlc_inst = vlc.Instance() if HAS_VLC else None
            s.player = s.vlc_inst.media_player_new() if HAS_VLC else None
            s._build()
        def _build(s):
            hdr = tk.Frame(s, bg=SUB, height=50); hdr.pack(fill=tk.X); hdr.pack_propagate(False)
            tk.Label(hdr, text="MEDIA", bg=SUB, fg=ACC, font=("Segoe UI", 16, "bold")).pack(side=tk.LEFT, padx=15, pady=12)
            engine = "VLC" if HAS_VLC else "System (install python-vlc for full features)"
            tk.Label(hdr, text=engine, bg=SUB, fg="#94a3b8", font=("Segoe UI", 9)).pack(side=tk.RIGHT, padx=15)
            disp = tk.Frame(s, bg="#020617", height=200); disp.pack(fill=tk.X); disp.pack_propagate(False)
            s.art = tk.Label(disp, text="\u266B", bg="#020617", fg=ACC, font=("Segoe UI", 72))
            s.art.pack(expand=True)
            s.title_lbl = tk.Label(s, text="No media loaded", bg=BG, fg=TXT, font=("Segoe UI", 12, "bold"))
            s.title_lbl.pack(pady=(10,2))
            s.time_lbl = tk.Label(s, text="00:00 / 00:00", bg=BG, fg="#94a3b8", font=("Consolas", 9))
            s.time_lbl.pack()
            ctrl = tk.Frame(s, bg=BG); ctrl.pack(pady=10)
            for txt, cmd in [("\u23EE", s._prev), ("\u25B6", s._play), ("\u23F8", s._pause),
                             ("\u23F9", s._stop), ("\u23ED", s._next)]:
                tk.Button(ctrl, text=txt, bg=SUB, fg=ACC, font=("Segoe UI", 16),
                          relief=tk.FLAT, width=3, command=cmd).pack(side=tk.LEFT, padx=4)
            vf = tk.Frame(s, bg=BG); vf.pack(pady=5)
            tk.Label(vf, text="VOL", bg=BG, fg=TXT, font=("Segoe UI", 9)).pack(side=tk.LEFT)
            s.vol = tk.Scale(vf, from_=0, to=100, orient=tk.HORIZONTAL, bg=BG, fg=ACC,
                             troughcolor=SUB, highlightthickness=0, length=200, showvalue=False,
                             command=s._set_vol)
            s.vol.set(70); s.vol.pack(side=tk.LEFT, padx=8)
            tk.Label(s, text="Playlist", bg=BG, fg=ACC, font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=15, pady=(10,2))
            plf = tk.Frame(s, bg=BG); plf.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
            sb = tk.Scrollbar(plf); sb.pack(side=tk.RIGHT, fill=tk.Y)
            s.lst = tk.Listbox(plf, bg="#020617", fg=TXT, selectbackground=ACC, selectforeground=BG,
                               font=("Consolas", 9), relief=tk.FLAT, yscrollcommand=sb.set, height=8)
            s.lst.pack(fill=tk.BOTH, expand=True); sb.config(command=s.lst.yview)
            s.lst.bind("<Double-Button-1>", lambda e: s._play_selected())
            bf = tk.Frame(s, bg=BG); bf.pack(pady=6)
            tk.Button(bf, text="+ ADD", bg=SUB, fg=ACC, font=("Segoe UI", 9, "bold"),
                      relief=tk.FLAT, command=s._add, padx=15).pack(side=tk.LEFT, padx=3)
            tk.Button(bf, text="CLEAR", bg=SUB, fg=TXT, font=("Segoe UI", 9),
                      relief=tk.FLAT, command=s._clear, padx=15).pack(side=tk.LEFT, padx=3)
        def _add(s):
            fs = filedialog.askopenfilenames(title="Add Media",
                filetypes=[("Media","*.mp3 *.wav *.ogg *.flac *.mp4 *.mkv *.avi *.webm *.m4a"),("All","*.*")])
            for f in fs:
                s.playlist.append(f)
                s.lst.insert(tk.END, os.path.basename(f))
        def _play(s):
            if not s.playlist: return
            if s.idx < 0: s.idx = 0
            s._load_track()
            if HAS_VLC and s.player: s.player.play()
        def _play_selected(s):
            sel = s.lst.curselection()
            if sel: s.idx = sel[0]; s._play()
        def _load_track(s):
            if 0 <= s.idx < len(s.playlist):
                p = s.playlist[s.idx]
                s.title_lbl.config(text=os.path.basename(p))
                if HAS_VLC and s.player:
                    s.player.set_media(s.vlc_inst.media_new(p))
                s.lst.selection_clear(0, tk.END); s.lst.selection_set(s.idx)
        def _pause(s):
            if HAS_VLC and s.player: s.player.pause()
        def _stop(s):
            if HAS_VLC and s.player: s.player.stop()
            s.title_lbl.config(text="Stopped")
        def _next(s):
            if s.playlist:
                s.idx = (s.idx + 1) % len(s.playlist); s._play()
        def _prev(s):
            if s.playlist:
                s.idx = (s.idx - 1) % len(s.playlist); s._play()
        def _clear(s):
            s.playlist.clear(); s.lst.delete(0, tk.END); s._stop()
        def _set_vol(s, v):
            if HAS_VLC and s.player: s.player.audio_set_volume(int(v))
        def adapt(s, ev): return {"cta": "media_adapt", "ev": ev}
        def predict(s, sig): return {"cta": "media_predict", "sig": sig}
else:
    class MediaPlayer: pass
