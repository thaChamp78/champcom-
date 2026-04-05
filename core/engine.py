"""
ChampCom Engine - The main engine that wires everything together
"""
import time
import threading

from core.config import Config
from core.ecs import ECS, Entity
from core.plugin_manager import PluginManager
from ai.brain import Brain, Autonomy
from ai.agents import create_default_agents
from network.replication import Replication
from network.prediction import Prediction
from render.graph import RenderGraph
from media.player import MediaPlayer


class ChampComEngine:
    """The master engine - initializes and connects all subsystems."""

    def __init__(self):
        # Core systems
        self.config = Config()
        self.ecs = ECS()
        self.plugins = PluginManager()

        # AI
        self.brain = Brain()
        self.autonomy = Autonomy(self.brain)

        # Network
        self.replication = Replication()
        self.prediction = Prediction()

        # Render
        self.render_graph = RenderGraph()

        # Media
        self.media_player = MediaPlayer()

        # State
        self.running = False
        self.tick_count = 0
        self.start_time = None

    def init(self):
        """Initialize all subsystems."""
        print("\n[ENGINE] Initializing ChampCom Engine...")

        # Load config
        self.config.load("configs/config.yaml")
        print("  [OK] Config loaded")

        # Initialize AI nodes
        agents = create_default_agents()
        for agent in agents:
            self.brain.add_node(agent)
        print(f"  [OK] AI Brain initialized ({len(agents)} nodes)")

        # Setup ECS with some default entities
        system_entity = self.ecs.create("system")
        self.ecs.add(system_entity, "transform", [0, 0, 0])
        self.ecs.add(system_entity, "info", {"name": "ChampCom", "type": "system"})
        print(f"  [OK] ECS initialized")

        # Setup render graph
        self.render_graph.add_pass("ui_update", lambda: None)
        print("  [OK] Render graph initialized")

        # Discover plugins
        self.plugins.discover("modules")
        self.plugins.init_all(self)
        print("  [OK] Plugin system initialized")

        # Start autonomy if enabled
        if self.config.get("ai.autonomy", True):
            tick_rate = self.config.get("ai.tick_rate", 2.0)
            self.autonomy.tick_rate = float(tick_rate)
            self.autonomy.start()
            print("  [OK] AI Autonomy started")

        self.start_time = time.time()
        print("[ENGINE] ChampCom Engine ready.\n")

    def run(self):
        """Start the GUI desktop environment."""
        self.running = True

        # Start background tick thread
        tick_thread = threading.Thread(target=self._tick_loop, daemon=True)
        tick_thread.start()

        # Launch the desktop GUI (blocks until closed)
        from gui.desktop import Desktop
        self.desktop = Desktop(self)
        self.desktop.run()

        # Cleanup on exit
        self.shutdown()

    def _tick_loop(self):
        """Background engine tick for ECS, network, etc."""
        last = time.time()
        while self.running:
            now = time.time()
            dt = now - last
            if dt > 0.1:
                dt = 0.033
            last = now

            # Update ECS
            self.ecs.update_transforms(dt)

            # Network replication
            snaps = self.replication.capture(self.ecs)
            self.prediction.push(snaps)

            # Render graph
            self.render_graph.execute()

            # Plugin ticks
            self.plugins.tick_all(self, dt)

            self.tick_count += 1
            time.sleep(0.033)  # ~30 ticks per second

    def shutdown(self):
        """Clean shutdown of all systems."""
        print("\n[ENGINE] Shutting down...")
        self.running = False
        self.autonomy.stop()
        self.plugins.shutdown_all(self)
        print("[ENGINE] ChampCom shutdown complete.")

    def get_uptime(self):
        if self.start_time:
            return time.time() - self.start_time
        return 0
