"""
ChampCom Render Graph - Pass-based rendering pipeline
"""


class RenderPass:
    def __init__(self, name, execute_fn):
        self.name = name
        self.execute = execute_fn
        self.enabled = True

    def __repr__(self):
        return f"RenderPass({self.name})"


class RenderGraph:
    """Manages ordered render passes."""

    def __init__(self):
        self.passes = []

    def add_pass(self, name, fn):
        self.passes.append(RenderPass(name, fn))

    def remove_pass(self, name):
        self.passes = [p for p in self.passes if p.name != name]

    def execute(self):
        for p in self.passes:
            if p.enabled:
                p.execute()

    def toggle_pass(self, name):
        for p in self.passes:
            if p.name == name:
                p.enabled = not p.enabled

    def list_passes(self):
        return [(p.name, p.enabled) for p in self.passes]
