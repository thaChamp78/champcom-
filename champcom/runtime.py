# ChampCom runtime - Author: Jordan Marzette (C) All Rights Reserved
import time, os, sys
from champcom.core.eco import _eco, eco_run

class ChampCom:
    def __init__(s):
        s.systems = {}; s.apps = {}; s.agents = {}; s.t0 = time.time()
        s.running = False; s.boot_complete = False; s.win = None
        s.cfg = {"author": "Jordan Marzette", "version": "1.0.0", "theme": "dark"}
        s.stats_cache = {}
    def boot(s):
        print("[BOOT] ChampCom INF runtime starting...")
        s.boot_complete = True
        print(f"[BOOT] Runtime up in {time.time()-s.t0:.3f}s")
        return {"cta": "booted", "t": time.time() - s.t0}
    def register(s, nm, cat="general"):
        if nm in s.systems: return {"cta": "skip", "nm": nm}
        s.systems[nm] = _eco(nm, cat)
        return {"cta": "registered", "nm": nm, "cat": cat}
    def register_app(s, nm, app_cls):
        s.apps[nm] = app_cls
        return {"cta": "app_registered", "nm": nm}
    def register_agent(s, nm, role):
        s.agents[nm] = {"nm": nm, "role": role, "ops": 0, "status": "idle", "last": None}
        return {"cta": "agent_registered", "nm": nm}
    def run_system(s, nm, variant="hybrid", *a, **k):
        if nm not in s.systems: return {"cta": "err", "msg": f"no system: {nm}"}
        return eco_run(s.systems[nm], variant, *a, **k)
    def adapt(s, ev):
        hits = 0
        for e in s.systems.values():
            e["hybrid"].adapt(ev); hits += 1
        return {"cta": "adapt_all", "ev": ev, "hits": hits}
    def predict(s, sig):
        for e in s.systems.values(): e["hybrid"].predict(sig)
        return {"cta": "predict_all", "sig": sig, "systems": len(s.systems)}
    def run(s):
        s.running = True
        try:
            from champcom.ui.main_window import MainWindow
            s.win = MainWindow(s)
            s.win.show()
        except Exception as e:
            print(f"[UI] GUI unavailable ({e}), running headless")
            s._headless_loop()
    def _headless_loop(s):
        print("=" * 60)
        print(f"  CHAMPCOM INF - HEADLESS MODE")
        print(f"  Systems:  {len(s.systems)}")
        print(f"  Apps:     {len(s.apps)}")
        print(f"  Agents:   {len(s.agents)}")
        print(f"  Uptime:   {time.time()-s.t0:.2f}s")
        print("=" * 60)
        print("  First 10 registered systems:")
        for i, nm in enumerate(list(s.systems.keys())[:10]):
            print(f"    {i+1}. {nm}")
        if len(s.systems) > 10:
            print(f"    ... and {len(s.systems)-10} more")
    def stats(s):
        return {"cta": "stats", "systems": len(s.systems), "apps": len(s.apps),
                "agents": len(s.agents), "up": time.time() - s.t0,
                "running": s.running, "author": s.cfg["author"]}
    def shutdown(s):
        s.running = False
        return {"cta": "shutdown", "up": time.time() - s.t0}
