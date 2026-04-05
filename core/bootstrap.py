"""
ChampCom Bootstrap - System validation and initialization
"""
import os
import sys
import platform


class Bootstrap:
    REQUIRED_DIRS = ["configs", "assets", "modules"]
    REQUIRED_FILES = ["configs/config.yaml"]

    @staticmethod
    def validate():
        print("=" * 50)
        print("  ChampCom Bootstrap Validator")
        print("=" * 50)

        # Create required directories
        for d in Bootstrap.REQUIRED_DIRS:
            os.makedirs(d, exist_ok=True)
            print(f"  [OK] Directory: {d}")

        # Create default config if missing
        if not os.path.exists("configs/config.yaml"):
            Bootstrap._create_default_config()

        # Check Python version
        v = sys.version_info
        if v.major < 3 or (v.major == 3 and v.minor < 8):
            print("  [WARN] Python 3.8+ recommended")
        else:
            print(f"  [OK] Python {v.major}.{v.minor}.{v.micro}")

        # Check tkinter
        try:
            import tkinter
            print("  [OK] tkinter available")
        except ImportError:
            print("  [FAIL] tkinter not found - GUI will not work")
            sys.exit(1)

        print(f"  [OK] Platform: {platform.system()} {platform.release()}")
        print("  [OK] Bootstrap complete")
        print("=" * 50)

    @staticmethod
    def _create_default_config():
        config = """# ChampCom Configuration
app:
  name: ChampCom
  version: 1.0.0
  fullscreen: false
  width: 1280
  height: 720
  theme: dark

ai:
  nodes: 3
  autonomy: true
  tick_rate: 2.0

network:
  host: 0.0.0.0
  port: 7777
  max_clients: 32

media:
  volume: 0.8

logging:
  level: INFO
  file: logs/champcom.log
"""
        os.makedirs("configs", exist_ok=True)
        with open("configs/config.yaml", "w") as f:
            f.write(config)
        print("  [OK] Created default config")
