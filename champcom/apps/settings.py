# ChampCom Settings - Author: Jordan Marzette (C)
try:
    import tkinter as tk
    HAS_TK = True
except ImportError:
    HAS_TK = False
BG = "#0f172a"; ACC = "#00ff88"; TXT = "#e2e8f0"; SUB = "#1e293b"

if HAS_TK:
    class SettingsApp(tk.Frame):
        def __init__(s, parent, cc):
            super().__init__(parent, bg=BG)
            s.cc = cc
            s.entries = {}
            s._build()
        def _build(s):
            hdr = tk.Frame(s, bg=SUB, height=50); hdr.pack(fill=tk.X); hdr.pack_propagate(False)
            tk.Label(hdr, text="SETTINGS", bg=SUB, fg=ACC, font=("Segoe UI", 16, "bold")).pack(side=tk.LEFT, padx=15, pady=12)
            body = tk.Frame(s, bg=BG); body.pack(fill=tk.BOTH, expand=True, padx=25, pady=15)
            tk.Label(body, text="General", bg=BG, fg=ACC, font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0,5))
            s._setting(body, "Theme", s.cc.cfg.get("theme", "dark"), "theme")
            s._setting(body, "Author", s.cc.cfg.get("author", "Jordan Marzette"), "author")
            s._setting(body, "Version", s.cc.cfg.get("version", "1.0.0"), "version")
            tk.Label(body, text="API Keys", bg=BG, fg=ACC, font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(15,5))
            s._setting(body, "Anthropic", s.cc.cfg.get("api_anthropic", ""), "api_anthropic", True)
            s._setting(body, "OpenAI", s.cc.cfg.get("api_openai", ""), "api_openai", True)
            tk.Label(body, text="Startup", bg=BG, fg=ACC, font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(15,5))
            s._setting(body, "Autostart App", s.cc.cfg.get("autostart", "home"), "autostart")
            s._setting(body, "Boot Agents", s.cc.cfg.get("boot_agents", "12"), "boot_agents")
            btn_frame = tk.Frame(body, bg=BG); btn_frame.pack(pady=25)
            tk.Button(btn_frame, text="SAVE", bg=ACC, fg=BG, font=("Segoe UI", 10, "bold"),
                      relief=tk.FLAT, command=s._save, padx=25, pady=6).pack(side=tk.LEFT, padx=5)
            tk.Button(btn_frame, text="RESET", bg=SUB, fg=TXT, font=("Segoe UI", 10, "bold"),
                      relief=tk.FLAT, command=s._reset, padx=25, pady=6).pack(side=tk.LEFT, padx=5)
            s.msg = tk.Label(body, text="", bg=BG, fg=ACC, font=("Segoe UI", 9))
            s.msg.pack(anchor="w")
        def _setting(s, parent, label, value, key, is_secret=False):
            f = tk.Frame(parent, bg=BG); f.pack(fill=tk.X, pady=3)
            tk.Label(f, text=label, bg=BG, fg=TXT, font=("Segoe UI", 10), width=20, anchor="w").pack(side=tk.LEFT)
            show = "*" if is_secret else None
            e = tk.Entry(f, bg="#0d1117", fg=TXT, insertbackground=ACC,
                         font=("Consolas", 10), relief=tk.FLAT, show=show)
            e.insert(0, str(value)); e.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=2)
            s.entries[key] = e
        def _save(s):
            for k, e in s.entries.items(): s.cc.cfg[k] = e.get()
            s.msg.config(text="Settings saved.")
        def _reset(s):
            for k, e in s.entries.items():
                e.delete(0, tk.END); e.insert(0, str(s.cc.cfg.get(k, "")))
            s.msg.config(text="Reset to saved values.")
        def adapt(s, ev): return {"cta": "settings_adapt", "ev": ev}
        def predict(s, sig): return {"cta": "settings_predict", "sig": sig}
else:
    class SettingsApp: pass
