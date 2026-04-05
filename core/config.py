"""
ChampCom Config System - YAML-like config parser (no external deps)
"""
import os


class Config:
    def __init__(self):
        self.data = {}

    def load(self, path):
        if not os.path.exists(path):
            return
        with open(path, "r") as f:
            self._parse(f.readlines())

    def _parse(self, lines):
        stack = [self.data]
        indent_stack = [-1]

        for line in lines:
            stripped = line.rstrip()
            if not stripped or stripped.lstrip().startswith("#"):
                continue

            indent = len(line) - len(line.lstrip())
            content = stripped.strip()

            # Pop stack for dedents
            while indent <= indent_stack[-1]:
                stack.pop()
                indent_stack.pop()

            if content.endswith(":") and ":" == content[-1]:
                # Section header
                key = content[:-1].strip()
                new_section = {}
                stack[-1][key] = new_section
                stack.append(new_section)
                indent_stack.append(indent)
            elif ":" in content:
                key, value = content.split(":", 1)
                key = key.strip()
                value = value.strip()
                # Type coercion
                if value.lower() in ("true", "yes"):
                    value = True
                elif value.lower() in ("false", "no"):
                    value = False
                else:
                    try:
                        value = int(value)
                    except ValueError:
                        try:
                            value = float(value)
                        except ValueError:
                            pass
                stack[-1][key] = value

    def get(self, key, default=None):
        """Get nested key like 'app.name'"""
        parts = key.split(".")
        current = self.data
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return default
        return current

    def set(self, key, value):
        parts = key.split(".")
        current = self.data
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        current[parts[-1]] = value

    def save(self, path):
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w") as f:
            self._write_dict(f, self.data, 0)

    def _write_dict(self, f, d, indent):
        prefix = "  " * indent
        for key, value in d.items():
            if isinstance(value, dict):
                f.write(f"{prefix}{key}:\n")
                self._write_dict(f, value, indent + 1)
            else:
                if isinstance(value, bool):
                    value = str(value).lower()
                f.write(f"{prefix}{key}: {value}\n")
