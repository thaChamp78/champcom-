# ChampCom AI Command Center - Author: Jordan Marzette (C)
try:
    import tkinter as tk
    HAS_TK = True
except ImportError:
    HAS_TK = False
import time, threading
BG = "#0f172a"; ACC = "#00ff88"; TXT = "#e2e8f0"; SUB = "#1e293b"

if HAS_TK:
    class CommandCenterApp(tk.Frame):
        def __init__(s, parent, cc):
            super().__init__(parent, bg=BG)
            s.cc = cc; s.history = []
            s._build()
            s._boot_msg()
        def _build(s):
            hdr = tk.Frame(s, bg=SUB, height=50); hdr.pack(fill=tk.X); hdr.pack_propagate(False)
            tk.Label(hdr, text="AI COMMAND CENTER", bg=SUB, fg=ACC, font=("Segoe UI", 15, "bold")).pack(side=tk.LEFT, padx=15, pady=12)
            s.sig = tk.Label(hdr, text="\u25CF READY", bg=SUB, fg=ACC, font=("Segoe UI", 9))
            s.sig.pack(side=tk.RIGHT, padx=15)
            body = tk.Frame(s, bg=BG); body.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
            sb = tk.Scrollbar(body); sb.pack(side=tk.RIGHT, fill=tk.Y)
            s.out = tk.Text(body, bg="#020617", fg=TXT, insertbackground=ACC,
                            font=("Consolas", 10), relief=tk.FLAT, wrap=tk.WORD,
                            state=tk.DISABLED, yscrollcommand=sb.set, padx=10, pady=8)
            s.out.pack(fill=tk.BOTH, expand=True); sb.config(command=s.out.yview)
            s.out.tag_configure("user", foreground="#60a5fa")
            s.out.tag_configure("ai", foreground=ACC)
            s.out.tag_configure("sys", foreground="#94a3b8")
            s.out.tag_configure("err", foreground="#f87171")
            inp = tk.Frame(s, bg=SUB); inp.pack(fill=tk.X, padx=15, pady=(0,10))
            tk.Label(inp, text=">", bg=SUB, fg=ACC, font=("Consolas", 14, "bold")).pack(side=tk.LEFT, padx=(8,4))
            s.ent = tk.Entry(inp, bg=SUB, fg=TXT, insertbackground=ACC, font=("Consolas", 11), relief=tk.FLAT)
            s.ent.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=8)
            s.ent.bind("<Return>", lambda e: s._send())
            tk.Button(inp, text="EXECUTE", bg=ACC, fg=BG, font=("Segoe UI", 9, "bold"),
                      relief=tk.FLAT, command=s._send, padx=15).pack(side=tk.RIGHT, padx=8)
            s.ent.focus_set()
        def _boot_msg(s):
            s._append("ChampCom AI Command Center online", "sys")
            s._append(f"Systems available: {len(s.cc.systems)}", "sys")
            s._append(f"Agents active: {len(s.cc.agents)}", "sys")
            s._append("Type a command or ask anything.\n", "sys")
        def _append(s, txt, tag="sys"):
            s.out.config(state=tk.NORMAL)
            ts = time.strftime("%H:%M:%S")
            s.out.insert(tk.END, f"[{ts}] ", "sys")
            s.out.insert(tk.END, f"{txt}\n", tag)
            s.out.see(tk.END); s.out.config(state=tk.DISABLED)
        def _send(s):
            msg = s.ent.get().strip()
            if not msg: return
            s.ent.delete(0, tk.END)
            s._append(f"> {msg}", "user")
            s.history.append(msg)
            threading.Thread(target=s._process, args=(msg,), daemon=True).start()
        def _process(s, msg):
            r = s._route(msg)
            s.after(0, s._append, r, "ai")
        def _route(s, msg):
            m = msg.lower()
            if "status" in m or "stat" in m:
                st = s.cc.stats()
                return f"Systems: {st['systems']} | Apps: {st['apps']} | Agents: {st['agents']} | Up: {st['up']:.1f}s"
            if m.startswith("list systems") or m == "ls":
                names = list(s.cc.systems.keys())[:15]
                return "First 15 systems:\n  " + "\n  ".join(names) + f"\n  ... ({len(s.cc.systems)} total)"
            if m.startswith("run "):
                nm = msg[4:].strip()
                r = s.cc.run_system(nm, "hybrid")
                return f"Result: {r}"
            if "help" in m:
                return ("Commands: status | ls | run <system> | predict <signal> | adapt <event> | help\n"
                        "Or ask anything in natural language.")
            if m.startswith("predict "):
                return str(s.cc.predict(msg[8:]))
            if m.startswith("adapt "):
                return str(s.cc.adapt(msg[6:]))
            return f"AI processed: '{msg}'. Standard: 1T x 10^18. Author: Jordan Marzette."
        def adapt(s, ev): return {"cta": "cmd_adapt", "ev": ev}
        def predict(s, sig): return {"cta": "cmd_predict", "sig": sig}
else:
    class CommandCenterApp: pass
