# ChampCom File Manager - Author: Jordan Marzette (C)
try:
    import tkinter as tk
    from tkinter import messagebox
    HAS_TK = True
except ImportError:
    HAS_TK = False
import os, shutil, subprocess, platform
BG = "#0f172a"; ACC = "#00ff88"; TXT = "#e2e8f0"; SUB = "#1e293b"

if HAS_TK:
    class FileManager(tk.Frame):
        def __init__(s, parent, cc):
            super().__init__(parent, bg=BG)
            s.cc = cc; s.cwd = os.path.expanduser("~")
            s._build(); s._refresh()
        def _build(s):
            hdr = tk.Frame(s, bg=SUB, height=45); hdr.pack(fill=tk.X); hdr.pack_propagate(False)
            tk.Label(hdr, text="FILES", bg=SUB, fg=ACC, font=("Segoe UI", 15, "bold")).pack(side=tk.LEFT, padx=15, pady=10)
            nav = tk.Frame(s, bg=SUB); nav.pack(fill=tk.X)
            for txt, cmd in [("<", s._up), ("\u2302", s._home), ("\u21BB", s._refresh)]:
                tk.Button(nav, text=txt, bg=SUB, fg=ACC, font=("Segoe UI", 11, "bold"),
                          relief=tk.FLAT, width=3, command=cmd).pack(side=tk.LEFT, padx=2, pady=4)
            s.path_var = tk.StringVar(value=s.cwd)
            pe = tk.Entry(nav, textvariable=s.path_var, bg="#0d1117", fg=TXT,
                          insertbackground=ACC, font=("Consolas", 9), relief=tk.FLAT)
            pe.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=4)
            pe.bind("<Return>", lambda e: s._nav(s.path_var.get()))
            body = tk.Frame(s, bg=BG); body.pack(fill=tk.BOTH, expand=True)
            sb = tk.Scrollbar(body); sb.pack(side=tk.RIGHT, fill=tk.Y)
            s.lst = tk.Listbox(body, bg="#020617", fg=TXT, selectbackground=ACC, selectforeground=BG,
                               font=("Consolas", 10), relief=tk.FLAT, yscrollcommand=sb.set)
            s.lst.pack(fill=tk.BOTH, expand=True, padx=10, pady=5); sb.config(command=s.lst.yview)
            s.lst.bind("<Double-Button-1>", lambda e: s._open())
            s.info = tk.Label(s, text="", bg=SUB, fg="#94a3b8", font=("Segoe UI", 9), anchor="w")
            s.info.pack(fill=tk.X)
        def _refresh(s):
            s.lst.delete(0, tk.END); s.path_var.set(s.cwd)
            try:
                entries = sorted(os.listdir(s.cwd))
            except (PermissionError, FileNotFoundError) as e:
                s.lst.insert(tk.END, f"[ERROR] {e}"); return
            dirs = []; files = []
            for e in entries:
                if e.startswith("."): continue
                full = os.path.join(s.cwd, e)
                if os.path.isdir(full): dirs.append(e)
                else: files.append(e)
            for d in dirs: s.lst.insert(tk.END, f"[DIR] {d}")
            for f in files:
                try: sz = os.path.getsize(os.path.join(s.cwd, f))
                except OSError: sz = 0
                s.lst.insert(tk.END, f"      {f}  ({s._sz(sz)})")
            s.info.config(text=f"  {len(dirs)} dirs, {len(files)} files")
        def _sz(s, n):
            for u in ["B","KB","MB","GB"]:
                if n < 1024: return f"{n:.0f}{u}"
                n /= 1024
            return f"{n:.1f}TB"
        def _open(s):
            sel = s.lst.curselection()
            if not sel: return
            t = s.lst.get(sel[0])
            if t.startswith("[DIR]"): nm = t[6:].strip()
            else: nm = t.strip().split("  (")[0]
            full = os.path.join(s.cwd, nm)
            if os.path.isdir(full): s._nav(full)
            else: s._launch(full)
        def _launch(s, p):
            try:
                if platform.system() == "Linux": subprocess.Popen(["xdg-open", p], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                elif platform.system() == "Darwin": subprocess.Popen(["open", p])
                else: os.startfile(p)
            except Exception as e:
                messagebox.showerror("Error", str(e))
        def _nav(s, p):
            if os.path.isdir(p): s.cwd = os.path.abspath(p); s._refresh()
        def _up(s):
            par = os.path.dirname(s.cwd)
            if par != s.cwd: s._nav(par)
        def _home(s): s._nav(os.path.expanduser("~"))
        def adapt(s, ev): return {"cta": "files_adapt", "ev": ev}
        def predict(s, sig): return {"cta": "files_predict", "sig": sig}
else:
    class FileManager: pass
