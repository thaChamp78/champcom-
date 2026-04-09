# ChampCom eco factory - 4-variant pattern
# Author: Jordan Marzette (C) All Rights Reserved
import time
AUTHOR = "Jordan Marzette"

class _Base:
    def __init__(s, nm, cat="general"):
        s.nm = nm; s.cat = cat; s.t0 = time.time(); s.ops = 0; s.st = "ready"; s.mem = []
    def adapt(s, ev):
        s.ops += 1; s.mem.append(("adapt", ev))
        return {"cta": "adapt", "nm": s.nm, "ev": ev, "ops": s.ops}
    def predict(s, sig):
        s.ops += 1; s.mem.append(("predict", sig))
        return {"cta": "predict", "nm": s.nm, "sig": sig, "conf": 0.87, "ops": s.ops}
    def run(s, *a, **k):
        s.ops += 1
        return {"cta": "run", "nm": s.nm, "st": s.st, "ops": s.ops}
    def info(s):
        return {"cta": "info", "nm": s.nm, "cat": s.cat, "ops": s.ops, "up": time.time()-s.t0}
    def exec(s, payload):
        s.ops += 1
        return {"cta": "exec", "nm": s.nm, "payload": payload, "ok": True}

class Core(_Base):
    def __init__(s, nm, cat="core"):
        super().__init__(nm, cat); s.variant = "core"
    def run(s, *a, **k):
        r = super().run(*a, **k); r["variant"] = "core"; r["mode"] = "stable"; return r

class Counter(_Base):
    def __init__(s, nm, cat="counter"):
        super().__init__(nm, cat); s.variant = "counter"
    def run(s, *a, **k):
        r = super().run(*a, **k); r["variant"] = "counter"; r["inverse"] = True; return r

class Balanced(_Base):
    def __init__(s, nm, cat="balanced"):
        super().__init__(nm, cat); s.variant = "balanced"
    def run(s, *a, **k):
        r = super().run(*a, **k); r["variant"] = "balanced"; r["equilibrium"] = 0.5; return r

class Hybrid(_Base):
    def __init__(s, nm, cat="hybrid"):
        super().__init__(nm, cat); s.variant = "hybrid"; s.author = AUTHOR
    def run(s, *a, **k):
        r = super().run(*a, **k); r["variant"] = "hybrid"; r["author"] = s.author; r["sovereign"] = True; return r

def _eco(nm, cat="general"):
    return {
        "core": Core(nm, cat),
        "counter": Counter(nm, cat),
        "balanced": Balanced(nm, cat),
        "hybrid": Hybrid(nm, cat),
        "nm": nm, "cat": cat,
    }

def eco_run(eco, variant="hybrid", *a, **k):
    if variant in eco: return eco[variant].run(*a, **k)
    return {"cta": "err", "msg": f"variant {variant} not found"}

def eco_info(eco):
    return {"cta": "info", "nm": eco.get("nm"), "cat": eco.get("cat"),
            "variants": [v for v in ("core","counter","balanced","hybrid") if v in eco]}
