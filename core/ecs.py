"""
ChampCom ECS - Entity Component System
"""
from collections import defaultdict


class Entity:
    _next_id = 0

    def __init__(self):
        Entity._next_id += 1
        self.id = Entity._next_id

    def __hash__(self):
        return self.id

    def __eq__(self, other):
        return isinstance(other, Entity) and self.id == other.id

    def __repr__(self):
        return f"Entity({self.id})"


class ECS:
    """Full Entity Component System with queries and iteration."""

    def __init__(self):
        self.components = defaultdict(dict)
        self.entities = {}  # id -> Entity
        self.tags = defaultdict(set)  # tag -> set of entity ids

    def create(self, name=None):
        e = Entity()
        self.entities[e.id] = e
        if name:
            self.tags[name].add(e.id)
        return e

    def destroy(self, entity):
        eid = entity.id if isinstance(entity, Entity) else entity
        if eid in self.entities:
            del self.entities[eid]
            for comp_type in list(self.components.keys()):
                self.components[comp_type].pop(eid, None)
            for tag in list(self.tags.keys()):
                self.tags[tag].discard(eid)

    def add(self, entity, comp_type, data):
        eid = entity.id if isinstance(entity, Entity) else entity
        self.components[comp_type][eid] = data

    def get(self, comp_type):
        return dict(self.components[comp_type])

    def get_component(self, entity, comp_type):
        eid = entity.id if isinstance(entity, Entity) else entity
        return self.components[comp_type].get(eid)

    def has(self, entity, comp_type):
        eid = entity.id if isinstance(entity, Entity) else entity
        return eid in self.components[comp_type]

    def query(self, *comp_types):
        """Return entity IDs that have ALL specified component types."""
        if not comp_types:
            return set()
        sets = [set(self.components[t].keys()) for t in comp_types]
        return set.intersection(*sets)

    def tag(self, entity, tag_name):
        eid = entity.id if isinstance(entity, Entity) else entity
        self.tags[tag_name].add(eid)

    def get_tagged(self, tag_name):
        return set(self.tags.get(tag_name, set()))

    def count(self):
        return len(self.entities)

    def update_transforms(self, dt):
        """Move entities with transform + velocity components."""
        movers = self.query("transform", "velocity")
        for eid in movers:
            t = self.components["transform"][eid]
            v = self.components["velocity"][eid]
            t[0] += v[0] * dt
            t[1] += v[1] * dt
            t[2] += v[2] * dt
