# ChampCom batches package - Jordan Marzette (C) All Rights Reserved
# Auto-discovers and loads every batch_*.py module containing a load(cc) callable.
import os
import importlib
import pkgutil

__all__ = ["load_all_batches", "batch_count", "module_count"]


def _discover():
    pkg_dir = os.path.dirname(os.path.abspath(__file__))
    for _, name, _ in pkgutil.iter_modules([pkg_dir]):
        if name.startswith("batch_"):
            yield name


def load_all_batches(cc):
    """Load every batch module and register its components with the ChampCom runtime."""
    results = []
    total = 0
    loaded_batches = 0
    for name in sorted(_discover()):
        mod = importlib.import_module(f"champcom.batches.{name}")
        if hasattr(mod, "load"):
            r = mod.load(cc)
            if isinstance(r, dict):
                total += r.get("count", 0)
                loaded_batches += 1
                results.append(r)
    print(f"[BATCHES] Loaded {loaded_batches} batch files, {total} modules registered")
    return {"cta": "all_batches_loaded", "batches": loaded_batches, "modules": total, "details": results}


def batch_count():
    return sum(1 for _ in _discover())


def module_count():
    """Sum of MODULES in every batch file without actually registering."""
    total = 0
    for name in _discover():
        mod = importlib.import_module(f"champcom.batches.{name}")
        total += len(getattr(mod, "MODULES", ()))
    return total
