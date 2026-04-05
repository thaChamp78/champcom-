"""
Example ChampCom Plugin

Place .py files in the modules/ directory to extend ChampCom.
Each plugin can implement these functions:

    on_init(engine)    - Called when the engine starts
    on_tick(engine, dt) - Called every engine tick (~30/sec)
    on_shutdown(engine) - Called when the engine shuts down
"""

PLUGIN_NAME = "Example Plugin"
PLUGIN_VERSION = "1.0.0"


def on_init(engine):
    print(f"  [PLUGIN] {PLUGIN_NAME} v{PLUGIN_VERSION} initialized")


def on_tick(engine, dt):
    pass  # Called every tick - add your logic here


def on_shutdown(engine):
    print(f"  [PLUGIN] {PLUGIN_NAME} shutting down")
