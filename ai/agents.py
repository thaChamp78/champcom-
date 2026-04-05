"""
ChampCom AI Agents - Specialized autonomous agents
"""
from ai.brain import AINode


class FileAgent(AINode):
    """Agent that handles file operations."""

    def __init__(self):
        super().__init__("FileAgent", "executor", "Handle file operations")

    def _execute(self, context):
        return f"[FILE] Processing file operation: {context}"


class NetworkAgent(AINode):
    """Agent that monitors network activity."""

    def __init__(self):
        super().__init__("NetworkAgent", "analyzer", "Monitor network")

    def _analyze(self, context):
        return f"[NET] Network status: stable | {context}"


class SystemAgent(AINode):
    """Agent that monitors system health."""

    def __init__(self):
        super().__init__("SystemAgent", "analyzer", "Monitor system health")

    def _analyze(self, context):
        return f"[SYS] System health: OK | {context}"


def create_default_agents():
    """Create the standard set of AI agents."""
    from ai.brain import AINode
    return [
        AINode("Planner", "planner"),
        AINode("Executor", "executor"),
        AINode("Analyzer", "analyzer"),
        AINode("Responder", "responder"),
    ]
