"""
ChampCom Terminal - Built-in command-line interface
"""
import tkinter as tk
import subprocess
import threading
import os
import platform


class TerminalApp:
    def __init__(self, parent, engine):
        self.parent = parent
        self.engine = engine
        self.cwd = os.path.expanduser("~")
        self.history = []
        self.history_index = -1

        self._build_ui()
        self._print_welcome()

    def _build_ui(self):
        # Terminal output
        self.output = tk.Text(
            self.parent,
            bg="#0d1117", fg="#00ff88",
            insertbackground="#00ff88",
            font=("Consolas", 10),
            relief=tk.FLAT, wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.output.pack(fill=tk.BOTH, expand=True)

        # Configure tags for colored output
        self.output.tag_configure("prompt", foreground="#569cd6")
        self.output.tag_configure("error", foreground="#f44747")
        self.output.tag_configure("info", foreground="#888888")
        self.output.tag_configure("success", foreground="#00ff88")

        # Input frame
        input_frame = tk.Frame(self.parent, bg="#0d1117")
        input_frame.pack(fill=tk.X)

        self.prompt_label = tk.Label(
            input_frame, text="$ ",
            bg="#0d1117", fg="#569cd6",
            font=("Consolas", 10)
        )
        self.prompt_label.pack(side=tk.LEFT)

        self.input_entry = tk.Entry(
            input_frame,
            bg="#0d1117", fg="#00ff88",
            insertbackground="#00ff88",
            font=("Consolas", 10),
            relief=tk.FLAT
        )
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.input_entry.focus_set()
        self.input_entry.bind("<Return>", self._on_enter)
        self.input_entry.bind("<Up>", self._history_up)
        self.input_entry.bind("<Down>", self._history_down)

    def _print_welcome(self):
        self._append(f"ChampCom Terminal v1.0 [{platform.system()}]\n", "info")
        self._append(f"Type 'help' for available commands.\n\n", "info")

    def _append(self, text, tag=None):
        self.output.config(state=tk.NORMAL)
        if tag:
            self.output.insert(tk.END, text, tag)
        else:
            self.output.insert(tk.END, text)
        self.output.see(tk.END)
        self.output.config(state=tk.DISABLED)

    def _on_enter(self, event):
        cmd = self.input_entry.get().strip()
        self.input_entry.delete(0, tk.END)

        if not cmd:
            return

        self.history.append(cmd)
        self.history_index = len(self.history)

        self._append(f"$ {cmd}\n", "prompt")
        self._execute(cmd)

    def _execute(self, cmd):
        parts = cmd.split()
        command = parts[0].lower()

        # Built-in commands
        if command == "help":
            self._cmd_help()
        elif command == "clear" or command == "cls":
            self.output.config(state=tk.NORMAL)
            self.output.delete("1.0", tk.END)
            self.output.config(state=tk.DISABLED)
        elif command == "cd":
            self._cmd_cd(parts[1] if len(parts) > 1 else "~")
        elif command == "pwd":
            self._append(f"{self.cwd}\n")
        elif command == "exit" or command == "quit":
            self._append("Goodbye!\n", "info")
        elif command == "sysinfo":
            self._cmd_sysinfo()
        elif command == "champcom":
            self._cmd_champcom(parts[1:])
        else:
            # Run system command
            threading.Thread(target=self._run_system_cmd, args=(cmd,),
                             daemon=True).start()

    def _cmd_help(self):
        help_text = """Available Commands:
  help          Show this help
  clear/cls     Clear terminal
  cd <path>     Change directory
  pwd           Print working directory
  sysinfo       Show system information
  champcom      ChampCom system commands
  exit          Close terminal

  Any other command is executed as a system command.
"""
        self._append(help_text, "info")

    def _cmd_cd(self, path):
        if path == "~":
            path = os.path.expanduser("~")
        elif not os.path.isabs(path):
            path = os.path.join(self.cwd, path)

        path = os.path.abspath(path)
        if os.path.isdir(path):
            self.cwd = path
            self._append(f"{self.cwd}\n")
        else:
            self._append(f"No such directory: {path}\n", "error")

    def _cmd_sysinfo(self):
        import sys
        info = f"""System Information:
  Platform:  {platform.system()} {platform.release()}
  Machine:   {platform.machine()}
  Python:    {sys.version.split()[0]}
  CWD:       {self.cwd}
  User:      {os.environ.get('USER', os.environ.get('USERNAME', 'unknown'))}
"""
        self._append(info, "info")

    def _cmd_champcom(self, args):
        if not args:
            self._append("Usage: champcom <status|ecs|ai|config>\n", "info")
            return

        sub = args[0]
        if sub == "status":
            self._append("ChampCom Engine: RUNNING\n", "success")
            self._append(f"  ECS Entities: {self.engine.ecs.count()}\n")
            self._append(f"  AI Nodes: {len(self.engine.brain.nodes)}\n")
            self._append(f"  Plugins: {len(self.engine.plugins.plugins)}\n")
        elif sub == "ecs":
            self._append(f"ECS Entities: {self.engine.ecs.count()}\n")
            for comp_type in self.engine.ecs.components:
                count = len(self.engine.ecs.components[comp_type])
                self._append(f"  {comp_type}: {count} components\n")
        elif sub == "ai":
            for name, node in self.engine.brain.nodes.items():
                self._append(f"  [{node.role}] {name}\n")
        elif sub == "config":
            self._append(f"Config data:\n")
            self._print_dict(self.engine.config.data, "  ")
        else:
            self._append(f"Unknown subcommand: {sub}\n", "error")

    def _print_dict(self, d, prefix=""):
        for k, v in d.items():
            if isinstance(v, dict):
                self._append(f"{prefix}{k}:\n")
                self._print_dict(v, prefix + "  ")
            else:
                self._append(f"{prefix}{k}: {v}\n")

    def _run_system_cmd(self, cmd):
        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True,
                cwd=self.cwd, timeout=30
            )
            if result.stdout:
                self.parent.after(0, self._append, result.stdout)
            if result.stderr:
                self.parent.after(0, self._append, result.stderr, "error")
        except subprocess.TimeoutExpired:
            self.parent.after(0, self._append, "Command timed out.\n", "error")
        except Exception as e:
            self.parent.after(0, self._append, f"Error: {e}\n", "error")

    def _history_up(self, event):
        if self.history and self.history_index > 0:
            self.history_index -= 1
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, self.history[self.history_index])

    def _history_down(self, event):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, self.history[self.history_index])
        else:
            self.history_index = len(self.history)
            self.input_entry.delete(0, tk.END)
