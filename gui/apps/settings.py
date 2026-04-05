"""
ChampCom Settings App - System configuration interface
"""
import tkinter as tk
from tkinter import ttk, messagebox


class SettingsApp:
    def __init__(self, parent, engine):
        self.parent = parent
        self.engine = engine
        self.config = engine.config

        self._build_ui()

    def _build_ui(self):
        bg = "#1a1a2e"
        fg = "#e0e0e0"
        accent = "#16213e"

        # Left sidebar - categories
        sidebar = tk.Frame(self.parent, bg=accent, width=150)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="\u2699 Settings",
                 bg=accent, fg=fg,
                 font=("Segoe UI", 12, "bold")).pack(pady=10)

        categories = [
            ("General", self._show_general),
            ("Display", self._show_display),
            ("AI", self._show_ai),
            ("Network", self._show_network),
            ("Plugins", self._show_plugins),
            ("About", self._show_about),
        ]

        for name, cmd in categories:
            btn = tk.Button(sidebar, text=f"  {name}", bg=accent, fg=fg,
                            relief=tk.FLAT, font=("Segoe UI", 10),
                            anchor="w", command=cmd, padx=10,
                            activebackground="#533483",
                            activeforeground=fg)
            btn.pack(fill=tk.X, pady=1)

        # Right content area
        self.content = tk.Frame(self.parent, bg=bg)
        self.content.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Show general by default
        self._show_general()

    def _clear_content(self):
        for w in self.content.winfo_children():
            w.destroy()

    def _make_section(self, title):
        self._clear_content()
        bg = "#1a1a2e"
        fg = "#e0e0e0"

        tk.Label(self.content, text=title, bg=bg, fg=fg,
                 font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=15, pady=10)
        tk.Frame(self.content, bg="#333", height=1).pack(fill=tk.X, padx=15)

        frame = tk.Frame(self.content, bg=bg)
        frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        return frame

    def _make_setting(self, parent, label, value, row):
        bg = "#1a1a2e"
        fg = "#e0e0e0"

        tk.Label(parent, text=label, bg=bg, fg=fg,
                 font=("Segoe UI", 10)).grid(row=row, column=0,
                                              sticky="w", pady=5, padx=5)
        entry = tk.Entry(parent, bg="#0d1117", fg=fg,
                         insertbackground=fg, font=("Segoe UI", 10),
                         relief=tk.FLAT, width=30)
        entry.insert(0, str(value))
        entry.grid(row=row, column=1, sticky="w", pady=5, padx=5)
        return entry

    def _show_general(self):
        frame = self._make_section("General Settings")
        bg = "#1a1a2e"
        fg = "#e0e0e0"

        self.app_name = self._make_setting(
            frame, "App Name:", self.config.get("app.name", "ChampCom"), 0)
        self.app_version = self._make_setting(
            frame, "Version:", self.config.get("app.version", "1.0.0"), 1)
        self.log_level = self._make_setting(
            frame, "Log Level:", self.config.get("logging.level", "INFO"), 2)

        tk.Button(frame, text="Save", bg="#533483", fg=fg,
                  relief=tk.FLAT, font=("Segoe UI", 10),
                  command=self._save_general, padx=20).grid(
            row=3, column=0, columnspan=2, pady=15)

    def _save_general(self):
        self.config.set("app.name", self.app_name.get())
        self.config.set("app.version", self.app_version.get())
        self.config.set("logging.level", self.log_level.get())
        self.config.save("configs/config.yaml")
        messagebox.showinfo("Settings", "General settings saved.")

    def _show_display(self):
        frame = self._make_section("Display Settings")
        fg = "#e0e0e0"

        self.width_entry = self._make_setting(
            frame, "Width:", self.config.get("app.width", 1280), 0)
        self.height_entry = self._make_setting(
            frame, "Height:", self.config.get("app.height", 720), 1)

        tk.Button(frame, text="Save", bg="#533483", fg=fg,
                  relief=tk.FLAT, font=("Segoe UI", 10),
                  command=self._save_display, padx=20).grid(
            row=3, column=0, columnspan=2, pady=15)

    def _save_display(self):
        try:
            self.config.set("app.width", int(self.width_entry.get()))
            self.config.set("app.height", int(self.height_entry.get()))
            self.config.save("configs/config.yaml")
            messagebox.showinfo("Settings", "Display settings saved. Restart to apply.")
        except ValueError:
            messagebox.showerror("Error", "Width/Height must be numbers.")

    def _show_ai(self):
        frame = self._make_section("AI Settings")
        bg = "#1a1a2e"
        fg = "#e0e0e0"

        self.ai_nodes = self._make_setting(
            frame, "AI Nodes:", self.config.get("ai.nodes", 3), 0)
        self.ai_tick = self._make_setting(
            frame, "Tick Rate (s):", self.config.get("ai.tick_rate", 2.0), 1)

        # Show active nodes
        tk.Label(frame, text="\nActive AI Nodes:", bg=bg, fg=fg,
                 font=("Segoe UI", 10, "bold")).grid(
            row=2, column=0, columnspan=2, sticky="w", pady=5)

        row = 3
        for name, node in self.engine.brain.nodes.items():
            tk.Label(frame, text=f"  \u25CF {name} ({node.role})",
                     bg=bg, fg="#00ff88",
                     font=("Segoe UI", 9)).grid(
                row=row, column=0, columnspan=2, sticky="w")
            row += 1

        tk.Button(frame, text="Save", bg="#533483", fg=fg,
                  relief=tk.FLAT, font=("Segoe UI", 10),
                  command=self._save_ai, padx=20).grid(
            row=row, column=0, columnspan=2, pady=15)

    def _save_ai(self):
        try:
            self.config.set("ai.nodes", int(self.ai_nodes.get()))
            self.config.set("ai.tick_rate", float(self.ai_tick.get()))
            self.config.save("configs/config.yaml")
            messagebox.showinfo("Settings", "AI settings saved.")
        except ValueError:
            messagebox.showerror("Error", "Invalid values.")

    def _show_network(self):
        frame = self._make_section("Network Settings")
        fg = "#e0e0e0"

        self.net_host = self._make_setting(
            frame, "Host:", self.config.get("network.host", "0.0.0.0"), 0)
        self.net_port = self._make_setting(
            frame, "Port:", self.config.get("network.port", 7777), 1)
        self.net_max = self._make_setting(
            frame, "Max Clients:", self.config.get("network.max_clients", 32), 2)

        tk.Button(frame, text="Save", bg="#533483", fg=fg,
                  relief=tk.FLAT, font=("Segoe UI", 10),
                  command=self._save_network, padx=20).grid(
            row=3, column=0, columnspan=2, pady=15)

    def _save_network(self):
        self.config.set("network.host", self.net_host.get())
        try:
            self.config.set("network.port", int(self.net_port.get()))
            self.config.set("network.max_clients", int(self.net_max.get()))
        except ValueError:
            messagebox.showerror("Error", "Port and Max Clients must be numbers.")
            return
        self.config.save("configs/config.yaml")
        messagebox.showinfo("Settings", "Network settings saved.")

    def _show_plugins(self):
        frame = self._make_section("Plugins")
        bg = "#1a1a2e"
        fg = "#e0e0e0"

        plugins = self.engine.plugins.list_plugins()
        if not plugins:
            tk.Label(frame, text="No plugins installed.\n\n"
                     "Place .py files in the 'modules/' directory\n"
                     "to add plugins.",
                     bg=bg, fg="#888", font=("Segoe UI", 10),
                     justify=tk.LEFT).pack(anchor="w")
        else:
            for name, enabled in plugins:
                pf = tk.Frame(frame, bg=bg)
                pf.pack(fill=tk.X, pady=2)
                status = "\u25CF" if enabled else "\u25CB"
                color = "#00ff88" if enabled else "#888"
                tk.Label(pf, text=f"{status} {name}", bg=bg, fg=color,
                         font=("Segoe UI", 10)).pack(side=tk.LEFT)
                tk.Button(pf, text="Toggle", bg="#16213e", fg=fg,
                          relief=tk.FLAT, font=("Segoe UI", 8),
                          command=lambda n=name: self._toggle_plugin(n)).pack(
                    side=tk.RIGHT)

    def _toggle_plugin(self, name):
        self.engine.plugins.toggle(name)
        self._show_plugins()

    def _show_about(self):
        frame = self._make_section("About ChampCom")
        bg = "#1a1a2e"
        fg = "#e0e0e0"

        tk.Label(frame, text="\U0001F3AE", font=("Segoe UI", 48),
                 bg=bg, fg=fg).pack(pady=5)
        tk.Label(frame, text="ChampCom OS",
                 font=("Segoe UI", 18, "bold"),
                 bg=bg, fg=fg).pack()
        tk.Label(frame, text="Version 1.0.0",
                 font=("Segoe UI", 11), bg=bg, fg="#888").pack()
        tk.Label(frame, text="\nOperating System Within an Operating System\n"
                 "\nBuilt-in Apps: File Manager, Terminal, Text Editor,\n"
                 "Media Player, Browser, AI Chat, Settings\n"
                 "\nCore Systems: ECS, AI Brain, Render Graph,\n"
                 "Network Replication, Plugin Manager",
                 font=("Segoe UI", 10), bg=bg, fg=fg,
                 justify=tk.CENTER).pack(pady=10)
        tk.Label(frame, text="Built by thaChamp78",
                 font=("Segoe UI", 10, "bold"),
                 bg=bg, fg="#533483").pack(pady=5)
