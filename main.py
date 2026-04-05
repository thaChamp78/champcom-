#!/usr/bin/env python3
"""
ChampCom - Operating System Within an Operating System
Double-click to launch. No external dependencies required.
"""
import sys
import os

# Ensure we're running from the right directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from core.bootstrap import Bootstrap
from core.engine import ChampComEngine


def main():
    Bootstrap.validate()
    engine = ChampComEngine()
    engine.init()
    engine.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
