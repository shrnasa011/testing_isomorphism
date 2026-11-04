"""Small canonical simple-undirected graph model used by all experiments."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Hashable, Iterable

Vertex = Hashable


@dataclass(frozen=True)
class Graph:
    """A loop-free undirected graph with arbitrary hashable vertex labels."""

    vertices: tuple[Vertex, ...]
    adjacency: dict[Vertex, frozenset[Vertex]]

    @classmethod
    def from_edges(
        cls, edges: Iterable[tuple[Vertex, Vertex]], vertices: Iterable[Vertex] = ()
    ) -> "Graph":
        labels = set(vertices)
        edge_list = list(edges)
        labels.update(x for edge in edge_list for x in edge)
        adjacency: dict[Vertex, set[Vertex]] = {v: set() for v in labels}
        for left, right in edge_list:
            if left == right:
                raise ValueError("simple graphs cannot contain self-loops")
            adjacency[left].add(right)
            adjacency[right].add(left)
        # repr ordering supports mixed hashable labels too.
        ordered = tuple(sorted(labels, key=repr))
        return cls(ordered, {v: frozenset(adjacency[v]) for v in ordered})

    @property
    def order(self) -> int:
        return len(self.vertices)

    @property
    def size(self) -> int:
        return sum(len(self.adjacency[v]) for v in self.vertices) // 2

    def degree(self, vertex: Vertex) -> int:
        return len(self.adjacency[vertex])

    def has_edge(self, left: Vertex, right: Vertex) -> bool:
        return right in self.adjacency[left]

    def relabel(self, mapping: dict[Vertex, Vertex]) -> "Graph":
        if set(mapping) != set(self.vertices) or len(set(mapping.values())) != self.order:
            raise ValueError("mapping must be a bijection on the vertex set")
        return Graph.from_edges(
            ((mapping[u], mapping[v]) for u in self.vertices for v in self.adjacency[u]
             if repr(u) < repr(v)),
            vertices=mapping.values(),
        )

    def describe(self) -> dict[str, int]:
        return {"vertices": self.order, "edges": self.size,
                "min_degree": min(map(self.degree, self.vertices), default=0),
                "max_degree": max(map(self.degree, self.vertices), default=0)}

    def edge_list(self) -> list[tuple[Vertex, Vertex]]:
        """One copy of every edge, suitable for `Graph.from_edges` reproduction."""
        return [(u, v) for u in self.vertices for v in self.adjacency[u] if repr(u) < repr(v)]
