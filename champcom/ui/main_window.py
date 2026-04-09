# ChampCom Main Window - Author: Jordan Marzette (C)
try:
    import tkinter as tk
    from tkinter import ttk
    HAS_TK = True
except ImportError:
    HAS_TK = False

BG = "#0f172a"; ACC = "#00ff88"; TXT = "#e2e8f0"; SUB = "#1e293b"; HI = "#334155"

class MainWindow:
    def __init__(s, cc):
        if not HAS_TK: raise ImportError("tkinter required for GUI mode")
        s.cc = cc
        s.root = tk.Tk()
        s.root.title("CHAMPCOM INF - AI Operating System")
        s.root.geometry("1400x860")
        s.root.configure(bg=BG)
        s.root.minsize(1024, 680)
        s.current_app = None
        s.sidebar_buttons = {}
        s._build_ui()
    def _build_ui(s):
        s._build_top_bar()
        s._build_body()
        s._build_status_bar()
    def _build_top_bar(s):
        bar = tk.Frame(s.root, bg=SUB, height=55)
        bar.pack(fill=tk.X); bar.pack_propagate(False)
        tk.Label(bar, text="CHAMPCOM", bg=SUB, fg=ACC, font=("Segoe UI", 18, "bold")).pack(side=tk.LEFT, padx=15)
        tk.Label(bar, text="INF", bg=SUB, fg=TXT, font=("Segoe UI", 10)).pack(side=tk.LEFT)
        s.status_dot = tk.Label(bar, text="  \u25cf ONLINE", bg=SUB, fg=ACC, font=("Segoe UI", 10, "bold"))
        s.status_dot.pack(side=tk.LEFT, padx=20)
        tk.Label(bar, text="(C) Jordan Marzette | All Rights Reserved", bg=SUB, fg="#94a3b8", font=("Segoe UI", 9)).pack(side=tk.RIGHT, padx=15)
    def _build_body(s):
        body = tk.Frame(s.root, bg=BG)
        body.pack(fill=tk.BOTH, expand=True)
        s.sidebar = tk.Frame(body, bg=SUB, width=85)
        s.sidebar.pack(side=tk.LEFT, fill=tk.Y); s.sidebar.pack_propagate(False)
        s.content = tk.Frame(body, bg=BG)
        s.content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        s._build_sidebar()
    def _build_sidebar(s):
        icons = [("home","HOME","\u2302"), ("launcher","APPS","\u25A6"), ("browser","WEB","\u2B58"),
                 ("media","MEDIA","\u25B6"), ("streaming","STRM","\u25A0"), ("emulator","GAME","\u2756"),
                 ("command","AI","\u2699"), ("agents","BOTS","\u2726"), ("social","SOCL","\u2665"),
                 ("files","FILE","\u25A3"), ("voice","VOX","\u25C9"), ("settings","SET","\u25CE")]
        for nm, lbl, sym in icons:
            f = tk.Frame(s.sidebar, bg=SUB)
            f.pack(fill=tk.X, pady=2)
            b = tk.Button(f, text=sym, bg=SUB, fg=ACC, font=("Segoe UI", 18),
                          relief=tk.FLAT, bd=0, activebackground=HI, activeforeground=ACC,
                          command=lambda n=nm: s.open_app(n))
            b.pack(fill=tk.X, pady=(5,0))
            tk.Label(f, text=lbl, bg=SUB, fg=TXT, font=("Segoe UI", 7)).pack()
            s.sidebar_buttons[nm] = b
    def _build_status_bar(s):
        bar = tk.Frame(s.root, bg=SUB, height=26)
        bar.pack(fill=tk.X, side=tk.BOTTOM); bar.pack_propagate(False)
        s.status_lbl = tk.Label(bar, text="Ready", bg=SUB, fg=TXT, font=("Segoe UI", 9))
        s.status_lbl.pack(side=tk.LEFT, padx=10)
        s.sys_lbl = tk.Label(bar, text="", bg=SUB, fg=ACC, font=("Segoe UI", 9))
        s.sys_lbl.pack(side=tk.RIGHT, padx=10)
        s._update_status()
    def _update_status(s):
        st = s.cc.stats()
        s.sys_lbl.config(text=f"Systems: {st['systems']} | Apps: {st['apps']} | Agents: {st['agents']} | Up: {st['up']:.0f}s")
        s.root.after(1000, s._update_status)
    def open_app(s, nm):
        for w in s.content.winfo_children(): w.destroy()
        s.status_lbl.config(text=f"App: {nm}")
        if nm == "home":
            _HomeApp(s.content, s.cc).pack(fill=tk.BOTH, expand=True)
            return
        if nm in s.cc.apps:
            try:
                app = s.cc.apps[nm](s.content, s.cc)
                app.pack(fill=tk.BOTH, expand=True)
                s.current_app = app
            except Exception as e:
                s._error_view(f"App '{nm}' failed to load: {e}")
        else:
            s._error_view(f"App '{nm}' not registered")
    def _error_view(s, msg):
        for w in s.content.winfo_children(): w.destroy()
        tk.Label(s.content, text="\u26A0", bg=BG, fg="#fbbf24", font=("Segoe UI", 48)).pack(pady=20)
        tk.Label(s.content, text=msg, bg=BG, fg=TXT, font=("Segoe UI", 12)).pack()
    def show(s):
        s.open_app("home")
        s.root.mainloop()
    def adapt(s, ev): return {"cta": "win_adapt", "ev": ev}
    def predict(s, sig): return {"cta": "win_predict", "sig": sig}

if HAS_TK:
    class _HomeApp(tk.Frame):
        def __init__(s, parent, cc):
            super().__init__(parent, bg=BG)
            s.cc = cc
            s._build()
        def _build(s):
            tk.Label(s, text="CHAMPCOM INF", bg=BG, fg=ACC, font=("Segoe UI", 36, "bold")).pack(pady=(40,5))
            tk.Label(s, text="AI Operating System \u2014 1T \u00D7 10\u00B9\u2078 Standard", bg=BG, fg=TXT, font=("Segoe UI", 13)).pack()
            tk.Label(s, text="(C) Jordan Marzette | All Rights Reserved", bg=BG, fg="#94a3b8", font=("Segoe UI", 10)).pack(pady=5)
            st = s.cc.stats()
            stats = tk.Frame(s, bg=BG); stats.pack(pady=30)
            for lbl, val, col in [("Systems Online", st["systems"], ACC), ("Apps", st["apps"], "#3b82f6"),
                                    ("Agents", st["agents"], "#a855f7"), ("Uptime", f"{st['up']:.0f}s", "#fbbf24")]:
                c = tk.Frame(stats, bg=SUB, padx=30, pady=20); c.pack(side=tk.LEFT, padx=10)
                tk.Label(c, text=str(val), bg=SUB, fg=col, font=("Segoe UI", 26, "bold")).pack()
                tk.Label(c, text=lbl, bg=SUB, fg=TXT, font=("Segoe UI", 10)).pack()
            tk.Label(s, text="Select an app from the sidebar to begin", bg=BG, fg="#94a3b8", font=("Segoe UI", 11)).pack(pady=20)
        def adapt(s, ev): return {"cta": "home_adapt", "ev": ev}
        def predict(s, sig): return {"cta": "home_predict", "sig": sig}
