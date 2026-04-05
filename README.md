# ChampCom

**Operating System Within an Operating System**

A fully operational desktop environment that runs as a standalone Python application. Double-click `main.py` to launch.

## Quick Start

```bash
python main.py
```

**Windows:** Double-click `scripts/build.bat`
**Linux/Mac:** Run `bash scripts/build.sh`

## Requirements

- Python 3.8+
- tkinter (included with Python on most systems)
- No other dependencies needed

### Install tkinter if missing:
```bash
# Ubuntu/Debian
sudo apt install python3-tk

# Fedora
sudo dnf install python3-tkinter

# macOS (comes with Python from python.org)
# Windows (comes with Python installer - make sure to check "tcl/tk" during install)
```

## Built-in Apps

| App | Description |
|-----|-------------|
| **File Manager** | Browse, create, delete files and folders |
| **Terminal** | Full command-line interface with history |
| **Text Editor** | Code editor with line numbers and syntax support |
| **Media Player** | Audio/video player with playlist |
| **Browser** | Web browser (opens in system browser) |
| **AI Chat** | Chat with the built-in AI brain |
| **Settings** | Configure all system settings |

## Core Systems

- **ECS (Entity Component System)** - Data-driven entity management
- **AI Brain** - Multi-node AI with Planner, Executor, Analyzer, Responder
- **Render Graph** - Pass-based rendering pipeline
- **Network Replication** - State sync with prediction/rollback
- **Plugin Manager** - Extensible module system
- **Config System** - YAML-like configuration

## Extending with Plugins

Drop `.py` files into the `modules/` directory. See `modules/example_plugin.py` for the template.

## Project Structure

```
champcom-/
├── main.py                  # Entry point
├── setup.py                 # Install script
├── requirements.txt         # Dependencies (none needed)
├── configs/
│   └── config.yaml          # System configuration
├── core/
│   ├── bootstrap.py         # System validation
│   ├── config.py            # Config parser
│   ├── ecs.py               # Entity Component System
│   ├── engine.py            # Main engine
│   └── plugin_manager.py    # Plugin loader
├── ai/
│   ├── brain.py             # AI brain + autonomy
│   └── agents.py            # Specialized agents
├── network/
│   ├── replication.py       # State sync
│   └── prediction.py        # Client prediction
├── render/
│   └── graph.py             # Render pass graph
├── media/
│   └── player.py            # Media playback
├── gui/
│   ├── desktop.py           # Desktop environment
│   ├── taskbar.py           # Taskbar + start menu
│   ├── window_manager.py    # Window management
│   └── apps/                # Built-in applications
│       ├── file_manager.py
│       ├── terminal.py
│       ├── text_editor.py
│       ├── media_player.py
│       ├── browser.py
│       ├── ai_chat.py
│       └── settings.py
├── assets/                  # Media assets
├── modules/                 # Plugin directory
│   └── example_plugin.py
└── scripts/
    ├── build.sh             # Linux/Mac launcher
    └── build.bat            # Windows launcher
```

## Built by [thaChamp78](https://github.com/thaChamp78)
