"""
ChampCom Network Replication - State synchronization
"""


class Snapshot:
    def __init__(self, entity_id, position):
        self.id = entity_id
        self.pos = list(position)

    def __repr__(self):
        return f"Snap({self.id}, {self.pos})"


class Replication:
    """Captures and applies ECS state snapshots for network sync."""

    def __init__(self):
        self.last = {}

    def capture(self, ecs):
        """Take a snapshot of all transform components."""
        snaps = []
        for eid, pos in ecs.get("transform").items():
            snaps.append(Snapshot(eid, pos))
            self.last[eid] = list(pos)
        return snaps

    def apply(self, ecs, snapshots):
        """Apply received snapshots to local ECS."""
        for snap in snapshots:
            ecs.components["transform"][snap.id] = list(snap.pos)

    def get_delta(self, ecs):
        """Get only entities that changed since last capture."""
        delta = []
        for eid, pos in ecs.get("transform").items():
            old = self.last.get(eid)
            if old is None or old != pos:
                delta.append(Snapshot(eid, pos))
                self.last[eid] = list(pos)
        return delta
