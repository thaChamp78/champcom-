# ChampCom Browser - Author: Jordan Marzette (C)
try:
    import tkinter as tk
    HAS_TK = True
except ImportError:
    HAS_TK = False
try:
    import webview
    HAS_WV = True
except ImportError:
    HAS_WV = False
import webbrowser, threading
BG = "#0f172a"; ACC = "#00ff88"; TXT = "#e2e8f0"; SUB = "#1e293b"

if HAS_TK:
    class BrowserApp(tk.Frame):
        def __init__(s, parent, cc):
            super().__init__(parent, bg=BG)
            s.cc = cc; s.current_url = "https://www.google.com"
            s.history = []; s.hi = -1
            s._build()
        def _build(s):
            nav = tk.Frame(s, bg=SUB); nav.pack(fill=tk.X, pady=(0,1))
            for txt, cmd in [("<", s._back), (">", s._fwd), ("\u21BB", s._reload), ("\u2302", s._home)]:
                tk.Button(nav, text=txt, bg=SUB, fg=ACC, font=("Segoe UI", 12, "bold"),
                          relief=tk.FLAT, width=3, command=cmd, activebackground="#334155").pack(side=tk.LEFT, padx=2, pady=4)
            s.url = tk.Entry(nav, bg="#0d1117", fg=TXT, insertbackground=ACC, font=("Segoe UI", 10), relief=tk.FLAT)
            s.url.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=4)
            s.url.insert(0, s.current_url)
            s.url.bind("<Return>", lambda e: s._go())
            tk.Button(nav, text="GO", bg=ACC, fg=BG, font=("Segoe UI", 9, "bold"),
                      relief=tk.FLAT, command=s._go, padx=15).pack(side=tk.RIGHT, padx=5, pady=4)
            bm = tk.Frame(s, bg=SUB); bm.pack(fill=tk.X, pady=(0,1))
            for nm, u in [("Google","https://google.com"), ("YouTube","https://youtube.com"),
                          ("GitHub","https://github.com"), ("Wiki","https://wikipedia.org"),
                          ("News","https://news.google.com")]:
                tk.Button(bm, text=nm, bg=SUB, fg="#94a3b8", font=("Segoe UI", 8), relief=tk.FLAT,
                          command=lambda x=u: s._goto(x)).pack(side=tk.LEFT, padx=4, pady=2)
            body = tk.Frame(s, bg=BG); body.pack(fill=tk.BOTH, expand=True)
            engine = "Chromium (pywebview)" if HAS_WV else "System browser (fallback)"
            tk.Label(body, text="\u2B58", bg=BG, fg=ACC, font=("Segoe UI", 72)).pack(pady=40)
            tk.Label(body, text="ChampCom Browser", bg=BG, fg=ACC, font=("Segoe UI", 22, "bold")).pack()
            tk.Label(body, text=f"Engine: {engine}", bg=BG, fg=TXT, font=("Segoe UI", 11)).pack(pady=5)
            tk.Label(body, text="Enter a URL above and click GO to open", bg=BG, fg="#94a3b8", font=("Segoe UI", 10)).pack(pady=15)
            if not HAS_WV:
                tk.Label(body, text="Install pywebview for embedded Chromium: pip install pywebview",
                         bg=BG, fg="#fbbf24", font=("Segoe UI", 9)).pack(pady=5)
        def _go(s):
            u = s.url.get().strip()
            if u and not u.startswith(("http://", "https://")): u = "https://" + u
            s._goto(u)
        def _goto(s, u):
            if not u: return
            s.current_url = u; s.url.delete(0, tk.END); s.url.insert(0, u)
            s.history.append(u); s.hi = len(s.history) - 1
            if HAS_WV:
                threading.Thread(target=lambda: webview.create_window("ChampCom Web", u), daemon=True).start()
            else:
                webbrowser.open(u)
        def _back(s):
            if s.hi > 0: s.hi -= 1; s._goto(s.history[s.hi])
        def _fwd(s):
            if s.hi < len(s.history) - 1: s.hi += 1; s._goto(s.history[s.hi])
        def _reload(s): s._goto(s.current_url)
        def _home(s): s._goto("https://www.google.com")
        def adapt(s, ev): return {"cta": "browser_adapt", "ev": ev}
        def predict(s, sig): return {"cta": "browser_predict", "sig": sig}
else:
    class BrowserApp: pass
