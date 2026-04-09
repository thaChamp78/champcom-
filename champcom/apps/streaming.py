# ChampCom Streaming - Author: Jordan Marzette (C)
try:
    import tkinter as tk
    HAS_TK = True
except ImportError:
    HAS_TK = False
try:
    import vlc
    HAS_VLC = True
except ImportError:
    HAS_VLC = False
import webbrowser, threading
BG = "#0f172a"; ACC = "#00ff88"; TXT = "#e2e8f0"; SUB = "#1e293b"
SITES = [("YouTube","https://youtube.com"),("Twitch","https://twitch.tv"),
         ("Netflix","https://netflix.com"),("Disney+","https://disneyplus.com"),
         ("Hulu","https://hulu.com"),("Prime","https://primevideo.com"),
         ("HBO","https://max.com"),("Apple TV","https://tv.apple.com"),
         ("Paramount","https://paramountplus.com"),("Peacock","https://peacocktv.com")]

if HAS_TK:
    class StreamingApp(tk.Frame):
        def __init__(s, parent, cc):
            super().__init__(parent, bg=BG)
            s.cc = cc; s.player = None
            s._build()
        def _build(s):
            hdr = tk.Frame(s, bg=SUB, height=50); hdr.pack(fill=tk.X); hdr.pack_propagate(False)
            tk.Label(hdr, text="CHAMPSTREAM", bg=SUB, fg=ACC, font=("Segoe UI", 16, "bold")).pack(side=tk.LEFT, padx=15, pady=10)
            engine = "VLC" if HAS_VLC else "System"
            tk.Label(hdr, text=f"Engine: {engine}", bg=SUB, fg=TXT, font=("Segoe UI", 9)).pack(side=tk.RIGHT, padx=15)
            body = tk.Frame(s, bg=BG); body.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            tk.Label(body, text="Streaming Services", bg=BG, fg=ACC, font=("Segoe UI", 14, "bold")).pack(anchor="w")
            grid = tk.Frame(body, bg=BG); grid.pack(fill=tk.X, pady=10)
            for i, (nm, u) in enumerate(SITES):
                r, c = divmod(i, 5)
                b = tk.Button(grid, text=nm, bg=SUB, fg=ACC, font=("Segoe UI", 11, "bold"),
                              relief=tk.FLAT, width=14, height=3, activebackground="#334155",
                              command=lambda x=u: s._open(x))
                b.grid(row=r, column=c, padx=6, pady=6)
            tk.Label(body, text="Local Video Playback", bg=BG, fg=ACC, font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(20,5))
            lf = tk.Frame(body, bg=BG); lf.pack(fill=tk.X)
            s.path_var = tk.StringVar()
            tk.Entry(lf, textvariable=s.path_var, bg="#0d1117", fg=TXT, insertbackground=ACC,
                     font=("Consolas", 10), relief=tk.FLAT).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,6), pady=3)
            tk.Button(lf, text="PLAY", bg=ACC, fg=BG, font=("Segoe UI", 9, "bold"),
                      relief=tk.FLAT, command=s._play_local, padx=20).pack(side=tk.RIGHT)
            s.status = tk.Label(body, text="", bg=BG, fg="#94a3b8", font=("Segoe UI", 9))
            s.status.pack(anchor="w", pady=10)
        def _open(s, u):
            s.status.config(text=f"Opening: {u}")
            webbrowser.open(u)
        def _play_local(s):
            p = s.path_var.get().strip()
            if not p: return
            if HAS_VLC:
                try:
                    inst = vlc.Instance(); s.player = inst.media_player_new()
                    s.player.set_media(inst.media_new(p)); s.player.play()
                    s.status.config(text=f"Playing (VLC): {p}")
                except Exception as e:
                    s.status.config(text=f"VLC error: {e}")
            else:
                import os, platform, subprocess
                try:
                    if platform.system() == "Linux": subprocess.Popen(["xdg-open", p])
                    elif platform.system() == "Darwin": subprocess.Popen(["open", p])
                    else: os.startfile(p)
                    s.status.config(text=f"Playing (system): {p}")
                except Exception as e:
                    s.status.config(text=f"Error: {e}")
        def adapt(s, ev): return {"cta": "stream_adapt", "ev": ev}
        def predict(s, sig): return {"cta": "stream_predict", "sig": sig}
else:
    class StreamingApp: pass
