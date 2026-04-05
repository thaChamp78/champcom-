"""
ChampCom Text Editor - Built-in code/text editor
"""
import tkinter as tk
from tkinter import filedialog, messagebox
import os


class TextEditorApp:
    def __init__(self, parent, engine):
        self.parent = parent
        self.engine = engine
        self.current_file = None
        self.modified = False

        self._build_ui()

    def _build_ui(self):
        bg = "#0d1117"
        fg = "#e0e0e0"
        accent = "#16213e"

        # Menu bar
        menubar = tk.Frame(self.parent, bg=accent)
        menubar.pack(fill=tk.X)

        for text, cmd in [("New", self._new), ("Open", self._open),
                          ("Save", self._save), ("Save As", self._save_as)]:
            tk.Button(menubar, text=text, bg=accent, fg=fg,
                      relief=tk.FLAT, font=("Segoe UI", 9),
                      command=cmd, padx=8).pack(side=tk.LEFT)

        # File name label
        self.file_label = tk.Label(menubar, text="[Untitled]", bg=accent,
                                   fg="#888", font=("Segoe UI", 9))
        self.file_label.pack(side=tk.RIGHT, padx=10)

        # Line numbers + text area
        edit_frame = tk.Frame(self.parent, bg=bg)
        edit_frame.pack(fill=tk.BOTH, expand=True)

        # Line numbers
        self.line_nums = tk.Text(
            edit_frame, width=5, bg="#161b22", fg="#555",
            font=("Consolas", 11), relief=tk.FLAT,
            state=tk.DISABLED, padx=4
        )
        self.line_nums.pack(side=tk.LEFT, fill=tk.Y)

        # Scrollbar
        scrollbar = tk.Scrollbar(edit_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Text area
        self.text = tk.Text(
            edit_frame, bg=bg, fg=fg,
            insertbackground="#569cd6",
            font=("Consolas", 11),
            relief=tk.FLAT, wrap=tk.NONE,
            undo=True, padx=5, pady=5,
            yscrollcommand=scrollbar.set
        )
        self.text.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self._on_scroll)

        # Syntax highlight tags
        self.text.tag_configure("keyword", foreground="#569cd6")
        self.text.tag_configure("string", foreground="#ce9178")
        self.text.tag_configure("comment", foreground="#6a9955")
        self.text.tag_configure("number", foreground="#b5cea8")

        # Bindings
        self.text.bind("<KeyRelease>", self._on_key)
        self.text.bind("<Control-s>", lambda e: self._save())
        self.text.bind("<Control-o>", lambda e: self._open())
        self.text.bind("<Control-n>", lambda e: self._new())

        # Status bar
        self.status = tk.Label(self.parent, text="Ln 1, Col 1", bg=accent,
                               fg="#888", font=("Segoe UI", 8), anchor="w")
        self.status.pack(fill=tk.X)

    def _on_scroll(self, *args):
        self.text.yview(*args)
        self.line_nums.yview(*args)

    def _on_key(self, event=None):
        self.modified = True
        self._update_line_numbers()
        self._update_status()

    def _update_line_numbers(self):
        self.line_nums.config(state=tk.NORMAL)
        self.line_nums.delete("1.0", tk.END)
        line_count = int(self.text.index("end-1c").split(".")[0])
        line_text = "\n".join(str(i) for i in range(1, line_count + 1))
        self.line_nums.insert("1.0", line_text)
        self.line_nums.config(state=tk.DISABLED)

    def _update_status(self):
        pos = self.text.index(tk.INSERT)
        line, col = pos.split(".")
        self.status.config(text=f"Ln {line}, Col {int(col) + 1}")

    def _new(self):
        if self.modified:
            if not messagebox.askyesno("New File", "Discard unsaved changes?"):
                return
        self.text.delete("1.0", tk.END)
        self.current_file = None
        self.modified = False
        self.file_label.config(text="[Untitled]")
        self._update_line_numbers()

    def _open(self):
        path = filedialog.askopenfilename(
            filetypes=[("All Files", "*.*"), ("Python", "*.py"),
                       ("Text", "*.txt"), ("Config", "*.yaml *.yml *.json")]
        )
        if not path:
            return
        try:
            with open(path, "r") as f:
                content = f.read()
            self.text.delete("1.0", tk.END)
            self.text.insert("1.0", content)
            self.current_file = path
            self.modified = False
            self.file_label.config(text=os.path.basename(path))
            self._update_line_numbers()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _save(self):
        if self.current_file:
            self._write_file(self.current_file)
        else:
            self._save_as()

    def _save_as(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("All Files", "*.*"), ("Python", "*.py"),
                       ("Text", "*.txt")]
        )
        if path:
            self._write_file(path)

    def _write_file(self, path):
        try:
            content = self.text.get("1.0", "end-1c")
            with open(path, "w") as f:
                f.write(content)
            self.current_file = path
            self.modified = False
            self.file_label.config(text=os.path.basename(path))
        except Exception as e:
            messagebox.showerror("Error", str(e))
