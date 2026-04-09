# ChampCom INF - Wiring graph builder
# Author: Jordan Marzette (C) All Rights Reserved
# LOCK_IN = True   SOVEREIGN = Jordan Marzette
#
# This turns the flat registry (cc.systems) into a living graph (cc.edges)
# by routing every module through its category hub, chaining hubs through
# the Runtime triad (ExecutionEngine / EventBus / StateEngine), and laying
# down the cross-category backbone connections.
from champcom.core.eco import _eco

LOCK_IN = True
SOVEREIGN = "Jordan Marzette"

# ------------------------------------------------------------------
# Category -> hub name. Every tag used by the batch generator lands
# on exactly one hub so propagation has a deterministic path.
# ------------------------------------------------------------------
CATEGORY_HUBS = {
    # AI family
    "ai":               "AI.AgentOrchestrator",
    "ai_agent":         "AI.AgentOrchestrator",
    "ai_registry":      "AI.AgentOrchestrator",
    "ai_research":      "AI.AgentOrchestrator",
    "avatar":           "AI.AgentOrchestrator",

    # Cognitivity + mental models
    "cognitivity":      "Cognitivity.MemoryCore",

    # Neural / scan stack
    "neural":           "Neural.SignalRouter",
    "neural_ui":        "Neural.SignalRouter",
    "neural_int":       "Neural.SignalRouter",
    "neural_final":     "Neural.SignalRouter",
    "neuroscan":        "Neural.SignalRouter",
    "scan":             "Neural.SignalRouter",

    # Learning / therapy
    "learning":         "Learning.Engine",
    "therapy":          "Therapy.Engine",

    # Voice
    "voice":            "Voice.SynthEngine",

    # GPT
    "gpt":              "GPT.InferenceGateway",

    # Streaming / media
    "sports":           "ChampTV.StreamRouter",
    "stremio":          "ChampTV.StreamRouter",

    # Browser / maps / navigation
    "browser":          "Browser.NavigationCore",
    "maps":             "Browser.NavigationCore",
    "navigation":       "Browser.NavigationCore",

    # Network plane
    "network":          "Network.PacketRouter",

    # Security / identity / observability
    "security":         "Security.PolicyEngine",
    "identity":         "Identity.AccessManager",
    "observability":    "Observability.Logging",

    # Data plane
    "storage":          "Storage.PersistenceLayer",

    # Compute / infra plane
    "cloud":            "Runtime.ExecutionEngine",
    "edge":             "Runtime.ExecutionEngine",
    "compute":          "Runtime.ExecutionEngine",
    "runtime":          "Runtime.ExecutionEngine",
    "build":            "Runtime.ExecutionEngine",
    "devtools":         "Runtime.ExecutionEngine",
    "control":          "Runtime.ExecutionEngine",
    "hardware":         "Runtime.ExecutionEngine",
    "software":         "Runtime.ExecutionEngine",
    "app":              "Runtime.ExecutionEngine",
    "apps":             "Runtime.ExecutionEngine",
    "system":           "Runtime.ExecutionEngine",
    "final":            "Runtime.ExecutionEngine",
    "core":             "Runtime.ExecutionEngine",

    # OS plane
    "os":               "OS.KernelBus",

    # UI / UX
    "ui":               "UI.RenderEngine",
    "ux":               "UI.RenderEngine",

    # Expansion / platform
    "expansion":        "Expansion.PluginManager",
    "platform":         "Platform.ModuleRegistry",
}

# ------------------------------------------------------------------
# Runtime triad - every hub routes into these.
# ------------------------------------------------------------------
RUNTIME_TRIAD = (
    "Runtime.ExecutionEngine",
    "Runtime.EventBus",
    "Runtime.StateEngine",
)

# ------------------------------------------------------------------
# Cross-category backbone edges.
# ------------------------------------------------------------------
CROSS_EDGES = [
    ("AI.AgentOrchestrator",    "Cognitivity.MemoryCore"),
    ("AI.AgentOrchestrator",    "Security.PolicyEngine"),
    ("Security.PolicyEngine",   "Identity.AccessManager"),
    ("Security.PolicyEngine",   "Observability.Logging"),
    ("Cognitivity.MemoryCore",  "Storage.PersistenceLayer"),
    ("Cognitivity.MemoryCore",  "Learning.Engine"),
    ("Neural.SignalRouter",     "Cognitivity.MemoryCore"),
    ("Therapy.Engine",          "Cognitivity.MemoryCore"),
    ("Learning.Engine",         "Cognitivity.MemoryCore"),
    ("Voice.SynthEngine",       "AI.AgentOrchestrator"),
    ("Browser.NavigationCore",  "Network.PacketRouter"),
    ("ChampTV.StreamRouter",    "Network.PacketRouter"),
    ("GPT.InferenceGateway",    "AI.AgentOrchestrator"),
    ("UI.RenderEngine",         "Control.CommandRouter"),
    ("OS.KernelBus",            "Runtime.ExecutionEngine"),
    ("Expansion.PluginManager", "Platform.ModuleRegistry"),
]

# Control.CommandRouter is referenced by UI.RenderEngine so it needs to exist.
EXTRA_HUBS = ("Control.CommandRouter",) + RUNTIME_TRIAD


def _ensure_hub(cc, name, cat="hub"):
    """Register a hub as a real eco system if it isn't already."""
    if name not in cc.systems:
        cc.systems[name] = _eco(name, cat)


def _add_edge(edges, src, dst):
    if src == dst:
        return
    bucket = edges.setdefault(src, [])
    if dst not in bucket:
        bucket.append(dst)


def build_edges(cc):
    """Turn cc.systems into a wired graph stored at cc.edges."""
    edges = {}

    # 1. Make sure every hub (category + runtime triad + extras) is live.
    for hub in set(CATEGORY_HUBS.values()):
        _ensure_hub(cc, hub)
    for hub in EXTRA_HUBS:
        _ensure_hub(cc, hub)

    # 2. Wire every module to its category hub.
    for mod_name, eco in cc.systems.items():
        if mod_name in set(CATEGORY_HUBS.values()) or mod_name in EXTRA_HUBS:
            continue  # hubs don't wire back to themselves
        cat = eco.get("cat", "core")
        hub = CATEGORY_HUBS.get(cat, "Runtime.ExecutionEngine")
        _add_edge(edges, mod_name, hub)

    # 3. Every hub pipes into the Runtime triad.
    for hub in set(CATEGORY_HUBS.values()):
        for runtime_node in RUNTIME_TRIAD:
            _add_edge(edges, hub, runtime_node)

    # 4. Cross-category backbone.
    for src, dst in CROSS_EDGES:
        _ensure_hub(cc, src)
        _ensure_hub(cc, dst)
        _add_edge(edges, src, dst)

    cc.edges = edges
    return cc


def edge_count(cc):
    return sum(len(v) for v in getattr(cc, "edges", {}).values())


def propagate(cc, signal, source):
    """BFS-propagate `signal` outward from `source` up to depth 5.

    Each reached module has its hybrid variant `.adapt(signal)` called.
    Returns the number of distinct modules reached (source included).
    """
    edges = getattr(cc, "edges", None) or {}
    if source not in cc.systems:
        return 0

    visited = {source}
    # depth-tagged queue
    frontier = [(source, 0)]
    while frontier:
        node, depth = frontier.pop(0)
        eco = cc.systems.get(node)
        if eco and "hybrid" in eco:
            eco["hybrid"].adapt(signal)
        if depth >= 5:
            continue
        for nxt in edges.get(node, ()):
            if nxt not in visited:
                visited.add(nxt)
                frontier.append((nxt, depth + 1))
    return len(visited)
