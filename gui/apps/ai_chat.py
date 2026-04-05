"""
ChampCom AI Chat - Interactive chat with the AI brain
"""
import tkinter as tk
import time
import threading


class AIChatApp:
    def __init__(self, parent, engine):
        self.parent = parent
        self.engine = engine
        self.brain = engine.brain

        self._build_ui()
        self._append_msg("system", "ChampCom AI online. Type a message to chat.")
        self._append_msg("system", f"Active nodes: {', '.join(self.brain.nodes.keys())}")

    def _build_ui(self):
        bg = "#1a1a2e"
        fg = "#e0e0e0"
        accent = "#16213e"

        # Header with AI status
        header = tk.Frame(self.parent, bg=accent)
        header.pack(fill=tk.X)

        tk.Label(header, text="\U0001F916 ChampCom AI",
                 bg=accent, fg=fg,
                 font=("Segoe UI", 11, "bold")).pack(side=tk.LEFT, padx=10, pady=5)

        self.status_dot = tk.Label(header, text="\u25CF Online",
                                   bg=accent, fg="#00ff88",
                                   font=("Segoe UI", 9))
        self.status_dot.pack(side=tk.RIGHT, padx=10)

        # Mode selector
        mode_frame = tk.Frame(self.parent, bg=accent)
        mode_frame.pack(fill=tk.X)

        tk.Label(mode_frame, text="Mode:", bg=accent, fg="#888",
                 font=("Segoe UI", 8)).pack(side=tk.LEFT, padx=5)

        self.mode_var = tk.StringVar(value="chat")
        modes = [("Chat", "chat"), ("Plan", "plan"), ("Analyze", "analyze"), ("Execute", "execute")]
        for text, val in modes:
            tk.Radiobutton(mode_frame, text=text, variable=self.mode_var,
                           value=val, bg=accent, fg=fg,
                           selectcolor="#533483",
                           activebackground=accent,
                           font=("Segoe UI", 8)).pack(side=tk.LEFT, padx=3)

        # Chat display
        chat_frame = tk.Frame(self.parent, bg=bg)
        chat_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(chat_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.chat = tk.Text(
            chat_frame, bg="#0d1117", fg=fg,
            font=("Segoe UI", 10), relief=tk.FLAT,
            wrap=tk.WORD, state=tk.DISABLED,
            yscrollcommand=scrollbar.set, padx=10, pady=5
        )
        self.chat.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.chat.yview)

        # Tags for styling
        self.chat.tag_configure("user", foreground="#569cd6")
        self.chat.tag_configure("ai", foreground="#00ff88")
        self.chat.tag_configure("system", foreground="#888888")
        self.chat.tag_configure("timestamp", foreground="#555555")

        # Input area
        input_frame = tk.Frame(self.parent, bg=accent)
        input_frame.pack(fill=tk.X)

        self.input_entry = tk.Entry(
            input_frame, bg="#0d1117", fg=fg,
            insertbackground=fg, font=("Segoe UI", 10),
            relief=tk.FLAT
        )
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
        self.input_entry.focus_set()
        self.input_entry.bind("<Return>", self._on_send)

        tk.Button(input_frame, text="Send", bg="#533483", fg=fg,
                  relief=tk.FLAT, font=("Segoe UI", 9),
                  command=self._on_send, padx=15).pack(side=tk.RIGHT, padx=5, pady=5)

        # Quick actions
        actions_frame = tk.Frame(self.parent, bg=accent)
        actions_frame.pack(fill=tk.X)

        quick_actions = [
            ("Status", "system status"),
            ("Help", "help"),
            ("Memory", "show memory"),
            ("Clear", None),
        ]
        for text, cmd in quick_actions:
            if cmd is None:
                tk.Button(actions_frame, text=text, bg=accent, fg="#888",
                          relief=tk.FLAT, font=("Segoe UI", 8),
                          command=self._clear_chat, padx=5).pack(side=tk.LEFT, padx=2)
            else:
                tk.Button(actions_frame, text=text, bg=accent, fg="#888",
                          relief=tk.FLAT, font=("Segoe UI", 8),
                          command=lambda c=cmd: self._send_message(c),
                          padx=5).pack(side=tk.LEFT, padx=2)

    def _on_send(self, event=None):
        msg = self.input_entry.get().strip()
        if not msg:
            return
        self.input_entry.delete(0, tk.END)
        self._send_message(msg)

    def _send_message(self, msg):
        self._append_msg("user", msg)

        # Process in background thread
        threading.Thread(target=self._process, args=(msg,), daemon=True).start()

    def _process(self, msg):
        mode = self.mode_var.get()
        try:
            if mode == "chat":
                response = self.brain.chat(msg)
            elif mode == "plan":
                results = self.brain.process(msg, "Planner")
                response = results[0] if results else "No planner available."
            elif mode == "analyze":
                results = self.brain.process(msg, "Analyzer")
                response = results[0] if results else "No analyzer available."
            elif mode == "execute":
                results = self.brain.process(msg, "Executor")
                response = results[0] if results else "No executor available."
            else:
                response = self.brain.chat(msg)

            # Handle special commands
            if msg.lower() == "show memory":
                memory = self.brain.get_memory(5)
                response = "Recent memory:\n"
                for m in memory:
                    response += f"  - {m['context'][:50]}...\n"

            self.parent.after(0, self._append_msg, "ai", response)
        except Exception as e:
            self.parent.after(0, self._append_msg, "system", f"Error: {e}")

    def _append_msg(self, sender, text):
        self.chat.config(state=tk.NORMAL)

        timestamp = time.strftime("%H:%M")
        self.chat.insert(tk.END, f"[{timestamp}] ", "timestamp")

        if sender == "user":
            self.chat.insert(tk.END, "You: ", "user")
        elif sender == "ai":
            self.chat.insert(tk.END, "AI: ", "ai")
        else:
            self.chat.insert(tk.END, "System: ", "system")

        self.chat.insert(tk.END, f"{text}\n\n")
        self.chat.see(tk.END)
        self.chat.config(state=tk.DISABLED)

    def _clear_chat(self):
        self.chat.config(state=tk.NORMAL)
        self.chat.delete("1.0", tk.END)
        self.chat.config(state=tk.DISABLED)
        self._append_msg("system", "Chat cleared.")
