# ChampCom App Launcher - Author: Jordan Marzette (C)
try:
    import tkinter as tk
    HAS_TK = True
except ImportError:
    HAS_TK = False
BG = "#0f172a"; ACC = "#00ff88"; TXT = "#e2e8f0"; SUB = "#1e293b"

if HAS_TK:
    class AppLauncher(tk.Frame):
        def __init__(s, parent, cc):
            super().__init__(parent, bg=BG)
            s.cc = cc
            s._build()
        def _build(s):
            tk.Label(s, text="APPS", bg=BG, fg=ACC, font=("Segoe UI", 24, "bold")).pack(pady=15)
            grid = tk.Frame(s, bg=BG); grid.pack(pady=10)
            apps = [("Browser","browser","\u2B58"), ("Media","media","\u25B6"), ("Streaming","streaming","\u25A0"),
                    ("Emulator","emulator","\u2756"), ("AI Center","command","\u2699"), ("Agents","agents","\u2726"),
                    ("Social","social","\u2665"), ("Files","files","\u25A3"), ("Voice","voice","\u25C9"),
                    ("Settings","settings","\u25CE")]
            for i, (nm, key, sym) in enumerate(apps):
                r, c = divmod(i, 5)
                f = tk.Frame(grid, bg=SUB, width=140, height=140); f.grid(row=r, column=c, padx=10, pady=10)
                f.pack_propagate(False)
                b = tk.Button(f, text=sym, bg=SUB, fg=ACC, font=("Segoe UI", 38), relief=tk.FLAT, bd=0,
                              activebackground="#334155", command=lambda k=key: s._launch(k))
                b.pack(expand=True)
                tk.Label(f, text=nm, bg=SUB, fg=TXT, font=("Segoe UI", 10)).pack(pady=5)
        def _launch(s, nm):
            if s.cc.win: s.cc.win.open_app(nm)
        def adapt(s, ev): return {"cta": "launcher_adapt", "ev": ev}
        def predict(s, sig): return {"cta": "launcher_predict", "sig": sig}
else:
    class AppLauncher: pass
