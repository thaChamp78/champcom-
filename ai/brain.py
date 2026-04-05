"""
ChampCom AI Brain - Central intelligence hub with memory and reasoning
"""
import time
import threading
from collections import deque


class AINode:
    """A specialized AI processing node."""

    def __init__(self, name, role, instructions=""):
        self.name = name
        self.role = role
        self.instructions = instructions
        self.history = deque(maxlen=100)

    def process(self, context):
        result = self._think(context)
        self.history.append({"input": context, "output": result, "time": time.time()})
        return result

    def _think(self, context):
        """Process input based on role."""
        if self.role == "planner":
            return self._plan(context)
        elif self.role == "executor":
            return self._execute(context)
        elif self.role == "analyzer":
            return self._analyze(context)
        elif self.role == "responder":
            return self._respond(context)
        return f"[{self.name}] Processed: {context}"

    def _plan(self, context):
        keywords = context.lower().split()
        if any(w in keywords for w in ["build", "create", "make"]):
            return f"[PLAN] Strategy for '{context}': 1) Analyze requirements 2) Allocate resources 3) Execute"
        return f"[PLAN] Evaluating: {context}"

    def _execute(self, context):
        return f"[EXEC] Executing task: {context}"

    def _analyze(self, context):
        return f"[ANALYSIS] Context '{context}' - Status: nominal, Confidence: high"

    def _respond(self, context):
        # Simple keyword-based responses
        ctx = context.lower()
        if any(w in ctx for w in ["hello", "hi", "hey"]):
            return "Hello! I'm ChampCom AI. How can I help you?"
        if any(w in ctx for w in ["help", "what can you do"]):
            return ("I can help with: planning tasks, analyzing data, "
                    "managing files, running commands, and more. Just ask!")
        if any(w in ctx for w in ["status", "how are you"]):
            return "All systems operational. Ready for commands."
        if any(w in ctx for w in ["time", "date"]):
            return f"Current time: {time.strftime('%Y-%m-%d %H:%M:%S')}"
        return f"I understand: '{context}'. How would you like me to proceed?"


class Brain:
    """Central AI hub managing all nodes and memory."""

    def __init__(self):
        self.nodes = {}
        self.memory = deque(maxlen=500)
        self.running = True

    def add_node(self, node):
        self.nodes[node.name] = node

    def remove_node(self, name):
        self.nodes.pop(name, None)

    def process(self, context, node_name=None):
        """Process through a specific node or all nodes."""
        results = []
        if node_name and node_name in self.nodes:
            result = self.nodes[node_name].process(context)
            results.append(result)
        else:
            for node in self.nodes.values():
                results.append(node.process(context))

        self.memory.append({
            "context": context,
            "results": results,
            "time": time.time()
        })
        return results

    def chat(self, message):
        """Send a chat message to the responder node."""
        if "Responder" in self.nodes:
            results = self.process(message, "Responder")
            return results[0] if results else "No response available."
        # Fallback
        return self.process(message)[0] if self.nodes else "AI not initialized."

    def get_memory(self, count=10):
        return list(self.memory)[-count:]

    def clear_memory(self):
        self.memory.clear()


class Autonomy:
    """Autonomous background processing loop."""

    def __init__(self, brain):
        self.brain = brain
        self.running = False
        self.thread = None
        self.tick_rate = 2.0
        self.listeners = []

    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False

    def on_tick(self, callback):
        self.listeners.append(callback)

    def _loop(self):
        while self.running:
            results = self.brain.process("autonomous_tick")
            for listener in self.listeners:
                try:
                    listener(results)
                except Exception:
                    pass
            time.sleep(self.tick_rate)
