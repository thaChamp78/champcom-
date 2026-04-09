# ChampCom Emulator - Author: Jordan Marzette (C)
try:
    import tkinter as tk
    from tkinter import filedialog
    HAS_TK = True
except ImportError:
    HAS_TK = False
import os, subprocess, platform, shutil
BG = "#0f172a"; ACC = "#00ff88"; TXT = "#e2e8f0"; SUB = "#1e293b"
EMUS = [("RetroArch","retroarch"),("Dolphin","dolphin-emu"),("PCSX2","pcsx2"),
        ("RPCS3","rpcs3"),("PPSSPP","ppsspp"),("mGBA","mgba"),
        ("DuckStation","duckstation"),("Ryujinx","ryujinx"),("Citra","citra"),
        ("Snes9x","snes9x")]

if HAS_TK:
    class EmulatorApp(tk.Frame):
        def __init__(s, parent, cc):
            super().__init__(parent, bg=BG)
            s.cc = cc; s.rom = None
            s._build()
        def _build(s):
            hdr = tk.Frame(s, bg=SUB, height=50); hdr.pack(fill=tk.X); hdr.pack_propagate(False)
            tk.Label(hdr, text="CHAMPPLAY", bg=SUB, fg=ACC, font=("Segoe UI", 16, "bold")).pack(side=tk.LEFT, padx=15, pady=10)
            body = tk.Frame(s, bg=BG); body.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
            tk.Label(body, text="Installed Emulators", bg=BG, fg=ACC, font=("Segoe UI", 13, "bold")).pack(anchor="w")
            s.status = tk.Label(body, text="Scanning...", bg=BG, fg=TXT, font=("Segoe UI", 9))
            s.status.pack(anchor="w", pady=5)
            s.emu_frame = tk.Frame(body, bg=BG); s.emu_frame.pack(fill=tk.X, pady=5)
            s._scan()
            rf = tk.Frame(body, bg=BG); rf.pack(fill=tk.X, pady=(20,5))
            tk.Label(rf, text="ROM File:", bg=BG, fg=ACC, font=("Segoe UI", 11, "bold")).pack(anchor="w")
            rl = tk.Frame(rf, bg=BG); rl.pack(fill=tk.X, pady=3)
            s.rom_var = tk.StringVar()
            tk.Entry(rl, textvariable=s.rom_var, bg="#0d1117", fg=TXT, insertbackground=ACC,
                     font=("Consolas", 9), relief=tk.FLAT).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,6), pady=3)
            tk.Button(rl, text="BROWSE", bg=SUB, fg=ACC, font=("Segoe UI", 9),
                      relief=tk.FLAT, command=s._browse, padx=15).pack(side=tk.RIGHT)
            tk.Label(body, text="(User-owned ROMs only)", bg=BG, fg="#94a3b8", font=("Segoe UI", 8)).pack(anchor="w")
            s.launch_status = tk.Label(body, text="", bg=BG, fg="#94a3b8", font=("Segoe UI", 9))
            s.launch_status.pack(anchor="w", pady=10)
        def _scan(s):
            found = []
            for nm, bin in EMUS:
                if shutil.which(bin): found.append((nm, bin))
            if not found:
                tk.Label(s.emu_frame, text="No emulators detected in PATH",
                         bg=BG, fg="#fbbf24", font=("Segoe UI", 9)).pack(anchor="w")
                s.status.config(text=f"0 of {len(EMUS)} emulators installed")
                return
            s.status.config(text=f"{len(found)} emulators detected")
            for nm, bin in found:
                b = tk.Button(s.emu_frame, text=nm, bg=SUB, fg=ACC, font=("Segoe UI", 10),
                              relief=tk.FLAT, width=15, command=lambda x=bin, n=nm: s._launch(x, n))
                b.pack(side=tk.LEFT, padx=3, pady=3)
        def _browse(s):
            p = filedialog.askopenfilename(title="Select ROM",
                filetypes=[("ROM files","*.nes *.smc *.sfc *.gba *.gb *.n64 *.iso *.cso *.chd *.cue *.nds *.3ds *.zip"),("All","*.*")])
            if p: s.rom_var.set(p); s.rom = p
        def _launch(s, bin, nm):
            args = [bin]
            if s.rom and os.path.exists(s.rom): args.append(s.rom)
            try:
                subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                s.launch_status.config(text=f"Launched: {nm}")
            except Exception as e:
                s.launch_status.config(text=f"Error: {e}")
        def adapt(s, ev): return {"cta": "emu_adapt", "ev": ev}
        def predict(s, sig): return {"cta": "emu_predict", "sig": sig}
else:
    class EmulatorApp: pass
