"""
ChampCom Plugin Manager - Load and manage extension modules
"""
import os
import importlib.util
import traceback


class Plugin:
    def __init__(self, name, module):
        self.name = name
        self.module = module
        self.enabled = True

    def on_init(self, engine):
        if hasattr(self.module, "on_init"):
            self.module.on_init(engine)

    def on_tick(self, engine, dt):
        if hasattr(self.module, "on_tick"):
            self.module.on_tick(engine, dt)

    def on_shutdown(self, engine):
        if hasattr(self.module, "on_shutdown"):
            self.module.on_shutdown(engine)


class PluginManager:
    def __init__(self):
        self.plugins = {}

    def discover(self, directory="modules"):
        """Scan directory for .py plugin files."""
        if not os.path.isdir(directory):
            return
        for filename in os.listdir(directory):
            if filename.endswith(".py") and not filename.startswith("_"):
                name = filename[:-3]
                path = os.path.join(directory, filename)
                self.load(name, path)

    def load(self, name, path):
        try:
            spec = importlib.util.spec_from_file_location(name, path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            self.plugins[name] = Plugin(name, module)
            print(f"  [PLUGIN] Loaded: {name}")
        except Exception:
            print(f"  [PLUGIN] Failed to load: {name}")
            traceback.print_exc()

    def init_all(self, engine):
        for plugin in self.plugins.values():
            if plugin.enabled:
                plugin.on_init(engine)

    def tick_all(self, engine, dt):
        for plugin in self.plugins.values():
            if plugin.enabled:
                plugin.on_tick(engine, dt)

    def shutdown_all(self, engine):
        for plugin in self.plugins.values():
            if plugin.enabled:
                plugin.on_shutdown(engine)

    def list_plugins(self):
        return [(p.name, p.enabled) for p in self.plugins.values()]

    def toggle(self, name):
        if name in self.plugins:
            self.plugins[name].enabled = not self.plugins[name].enabled
