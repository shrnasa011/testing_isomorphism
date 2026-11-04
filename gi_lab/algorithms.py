"""Extensible graph-invariant API and Weisfeiler--Leman implementations."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Protocol

from .graph import Graph, Vertex


@dataclass(frozen=True)
class RefinementResult:
    """A canonical invariant plus a compact trace usable in reports."""

    name: str
    signature: tuple
    rounds: int
    colour_classes: tuple[int, ...]


class Invariant(Protocol):
    """Any deterministic necessary condition for graph isomorphism."""

    name: str

    def refine(self, graph: Graph) -> RefinementResult: ...


def _renumber(keys: dict[object, tuple]) -> dict[object, int]:
    """Assign stable colours by sorting structural keys rather than labels."""
    palette = {key: index for index, key in enumerate(sorted(set(keys.values()), key=repr))}
    return {item: palette[key] for item, key in keys.items()}


class ColorRefinement:
    """1-WL. Runs in polynomial time and refines vertex colours to stability."""

    name = "1wl"

    def refine(self, graph: Graph) -> RefinementResult:
        # Keep structural labels as well as compact local colours.  The latter
        # detects stabilization; the former makes signatures comparable across
        # *different* graphs (a bare local colour number would not).
        labels: dict[Vertex, tuple] = {v: ("degree", graph.degree(v)) for v in graph.vertices}
        colours = _renumber(labels)
        rounds = 0
        while True:
            keys = {v: (labels[v], tuple(sorted((labels[n] for n in graph.adjacency[v]), key=repr)))
                    for v in graph.vertices}
            new = _renumber(keys)
            rounds += 1
            if all(new[v] == colours[v] for v in graph.vertices):
                break
            colours = new
            labels = keys
        histogram = tuple(sorted(Counter(colours.values()).values()))
        return RefinementResult(self.name, (graph.order, tuple(sorted(keys.values(), key=repr))), rounds, histogram)


class TwoWL:
    """2-WL on ordered vertex pairs; O(n^3) work per refinement round."""

    name = "2wl"

    def refine(self, graph: Graph) -> RefinementResult:
        pairs = [(u, v) for u in graph.vertices for v in graph.vertices]
        labels = {pair: ("=",) if pair[0] == pair[1] else
                   ("E",) if graph.has_edge(*pair) else ("N",) for pair in pairs}
        colours = _renumber(labels)
        rounds = 0
        while True:
            keys = {
                (u, v): (labels[(u, v)], tuple(sorted(
                    ((labels[(w, v)], labels[(u, w)]) for w in graph.vertices), key=repr)))
                for u, v in pairs
            }
            new = _renumber(keys)
            rounds += 1
            if all(new[pair] == colours[pair] for pair in pairs):
                break
            colours = new
            labels = keys
        histogram = tuple(sorted(Counter(colours.values()).values()))
        return RefinementResult(self.name, (graph.order, tuple(sorted(keys.values(), key=repr))), rounds, histogram)


class StationaryDistribution:
    """A canonical stationary distribution for an undirected graph.

    When there is at least one edge, pi(v) = degree(v) / (2m) is stationary,
    even if the graph is disconnected. For disconnected graphs, stationary
    distributions are not unique; this chooses the canonical degree-weighted
    one (isolated vertices receive zero mass). For an edgeless graph, choose
    the uniform distribution. The signature sorts (degree, probability) pairs
    to be independent of vertex labels. Equal signatures still do not capture
    the graph's full structure.
    """

    name = "stationary"

    def refine(self, graph: Graph) -> RefinementResult:
        if graph.size == 0:
            # The empty vector is the unique distribution on no vertices;
            # otherwise use uniform mass for the edgeless graph's isolates.
            vertex_data = (() if graph.order == 0 else
                           tuple(sorted((0, 1 / graph.order) for _ in graph.vertices)))
        else:
            vertex_data = tuple(sorted((graph.degree(v), graph.degree(v) / (2 * graph.size))
                                        for v in graph.vertices))
        return RefinementResult(self.name, (graph.order, vertex_data), 1,
                                tuple(sorted(Counter(vertex_data).values())))


BUILTINS: dict[str, Invariant] = {
    "1wl": ColorRefinement(), "2wl": TwoWL(),
    "stationary": StationaryDistribution(),
}
