"""
ChampCom File Manager - Browse and manage files
"""
import tkinter as tk
from tkinter import ttk, messagebox
import os
import shutil
import subprocess
import platform


class FileManagerApp:
    def __init__(self, parent, engine):
        self.parent = parent
        self.engine = engine
        self.current_path = os.path.expanduser("~")

        self._build_ui()
        self._refresh()

    def _build_ui(self):
        bg = "#1a1a2e"
        fg = "#e0e0e0"
        accent = "#16213e"

        # Toolbar
        toolbar = tk.Frame(self.parent, bg=accent)
        toolbar.pack(fill=tk.X)

        tk.Button(toolbar, text="\u2190 Back", bg=accent, fg=fg,
                  relief=tk.FLAT, command=self._go_up,
                  font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="\u2302 Home", bg=accent, fg=fg,
                  relief=tk.FLAT, command=self._go_home,
                  font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="\u21BB Refresh", bg=accent, fg=fg,
                  relief=tk.FLAT, command=self._refresh,
                  font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=2)

        # Path bar
        self.path_var = tk.StringVar(value=self.current_path)
        self.path_entry = tk.Entry(toolbar, textvariable=self.path_var,
                                   bg="#0d1117", fg=fg, insertbackground=fg,
                                   font=("Consolas", 9), relief=tk.FLAT)
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=3)
        self.path_entry.bind("<Return>", lambda e: self._navigate(self.path_var.get()))

        # File list with scrollbar
        list_frame = tk.Frame(self.parent, bg=bg)
        list_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.file_list = tk.Listbox(
            list_frame, bg="#0d1117", fg=fg,
            selectbackground="#533483", selectforeground="#ffffff",
            font=("Consolas", 10), relief=tk.FLAT,
            yscrollcommand=scrollbar.set
        )
        self.file_list.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.file_list.yview)

        self.file_list.bind("<Double-Button-1>", self._on_double_click)
        self.file_list.bind("<Button-3>", self._context_menu)

        # Status bar
        self.status = tk.Label(self.parent, text="", bg=accent, fg="#888",
                               font=("Segoe UI", 8), anchor="w")
        self.status.pack(fill=tk.X)

        # Context menu
        self.ctx_menu = tk.Menu(self.parent, tearoff=0, bg=accent, fg=fg)
        self.ctx_menu.add_command(label="Open", command=self._open_selected)
        self.ctx_menu.add_command(label="Delete", command=self._delete_selected)
        self.ctx_menu.add_separator()
        self.ctx_menu.add_command(label="New Folder", command=self._new_folder)
        self.ctx_menu.add_command(label="New File", command=self._new_file)

    def _refresh(self):
        self.file_list.delete(0, tk.END)
        self.path_var.set(self.current_path)

        try:
            entries = sorted(os.listdir(self.current_path))
        except PermissionError:
            self.file_list.insert(tk.END, "[Permission Denied]")
            return

        dirs = []
        files = []
        for entry in entries:
            if entry.startswith("."):
                continue
            full = os.path.join(self.current_path, entry)
            if os.path.isdir(full):
                dirs.append(entry)
            else:
                files.append(entry)

        for d in dirs:
            self.file_list.insert(tk.END, f"\U0001F4C1 {d}")
        for f in files:
            size = os.path.getsize(os.path.join(self.current_path, f))
            size_str = self._format_size(size)
            self.file_list.insert(tk.END, f"\U0001F4C4 {f}  ({size_str})")

        self.status.config(text=f"  {len(dirs)} folders, {len(files)} files")

    def _format_size(self, size):
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024:
                return f"{size:.0f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    def _on_double_click(self, event):
        self._open_selected()

    def _open_selected(self):
        sel = self.file_list.curselection()
        if not sel:
            return
        text = self.file_list.get(sel[0])
        # Remove icon prefix
        name = text.split(" ", 1)[1].split("  (")[0] if " " in text else text
        full = os.path.join(self.current_path, name)

        if os.path.isdir(full):
            self._navigate(full)
        else:
            self._open_file(full)

    def _open_file(self, path):
        system = platform.system()
        try:
            if system == "Linux":
                subprocess.Popen(["xdg-open", path],
                                 stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL)
            elif system == "Darwin":
                subprocess.Popen(["open", path])
            elif system == "Windows":
                os.startfile(path)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _navigate(self, path):
        if os.path.isdir(path):
            self.current_path = os.path.abspath(path)
            self._refresh()

    def _go_up(self):
        parent = os.path.dirname(self.current_path)
        if parent != self.current_path:
            self._navigate(parent)

    def _go_home(self):
        self._navigate(os.path.expanduser("~"))

    def _context_menu(self, event):
        self.ctx_menu.post(event.x_root, event.y_root)

    def _delete_selected(self):
        sel = self.file_list.curselection()
        if not sel:
            return
        text = self.file_list.get(sel[0])
        name = text.split(" ", 1)[1].split("  (")[0]
        full = os.path.join(self.current_path, name)

        if messagebox.askyesno("Delete", f"Delete '{name}'?"):
            try:
                if os.path.isdir(full):
                    shutil.rmtree(full)
                else:
                    os.remove(full)
                self._refresh()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def _new_folder(self):
        self._input_dialog("New Folder", "Folder name:", self._create_folder)

    def _new_file(self):
        self._input_dialog("New File", "File name:", self._create_file)

    def _create_folder(self, name):
        try:
            os.makedirs(os.path.join(self.current_path, name), exist_ok=True)
            self._refresh()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _create_file(self, name):
        try:
            path = os.path.join(self.current_path, name)
            with open(path, "w") as f:
                pass
            self._refresh()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _input_dialog(self, title, prompt, callback):
        dialog = tk.Toplevel(self.parent)
        dialog.title(title)
        dialog.geometry("300x100")
        dialog.configure(bg="#1a1a2e")

        tk.Label(dialog, text=prompt, bg="#1a1a2e", fg="#e0e0e0",
                 font=("Segoe UI", 10)).pack(pady=5)
        entry = tk.Entry(dialog, bg="#0d1117", fg="#e0e0e0",
                         insertbackground="#e0e0e0", font=("Segoe UI", 10))
        entry.pack(padx=10, fill=tk.X)
        entry.focus_set()

        def submit():
            val = entry.get().strip()
            if val:
                callback(val)
            dialog.destroy()

        entry.bind("<Return>", lambda e: submit())
        tk.Button(dialog, text="Create", bg="#533483", fg="#e0e0e0",
                  relief=tk.FLAT, command=submit).pack(pady=5)
