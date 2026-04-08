#!/usr/bin/env python3
# ChampCom INF - Master Boot Entry
# Author: Jordan Marzette (C) All Rights Reserved
import sys, os, subprocess, importlib
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

OPTIONAL = ["pywebview", "vlc", "speech_recognition", "pyttsx3"]

def _try_import(name):
    try: importlib.import_module(name); return True
    except ImportError: return False

def _install_missing():
    missing = [p for p in OPTIONAL if not _try_import(p if p != "vlc" else "vlc")]
    if missing and "--auto-install" in sys.argv:
        print(f"[BOOT] Installing: {missing}")
        pip_map = {"vlc": "python-vlc", "speech_recognition": "SpeechRecognition"}
        pkgs = [pip_map.get(m, m) for m in missing]
        subprocess.call([sys.executable, "-m", "pip", "install", "--quiet"] + pkgs)

def _banner():
    print("=" * 60)
    print("  CHAMPCOM INF - AI OPERATING SYSTEM")
    print("  Author: Jordan Marzette (C) All Rights Reserved")
    print("  Standard: 1T x 10^18 Above All")
    print("=" * 60)

def main():
    _banner()
    _install_missing()
    from champcom.runtime import ChampCom
    cc = ChampCom()
    cc.boot()
    # Load all inject batches
    from champcom.batches import load_all_batches
    load_all_batches(cc)
    cc.run()
    return 0

if __name__ == "__main__":
    sys.exit(main())
