"""Small exact oracle; intentionally not presented as a scalable GI algorithm."""

from __future__ import annotations

from .graph import Graph, Vertex


def is_isomorphic(left: Graph, right: Graph) -> bool:
    """Degree-pruned backtracking, suitable for validating small corpus cases."""
    if left.order != right.order or left.size != right.size:
        return False
    if sorted(left.degree(v) for v in left.vertices) != sorted(right.degree(v) for v in right.vertices):
        return False
    candidates = {u: [v for v in right.vertices if right.degree(v) == left.degree(u)]
                  for u in left.vertices}
    ordered = sorted(left.vertices, key=lambda u: (len(candidates[u]), -left.degree(u), repr(u)))
    mapping: dict[Vertex, Vertex] = {}
    used: set[Vertex] = set()

    def search(index: int) -> bool:
        if index == len(ordered):
            return True
        u = ordered[index]
        for v in candidates[u]:
            if v in used:
                continue
            if all(left.has_edge(u, prior) == right.has_edge(v, mapping[prior]) for prior in mapping):
                mapping[u] = v
                used.add(v)
                if search(index + 1):
                    return True
                used.remove(v)
                del mapping[u]
        return False

    return search(0)
