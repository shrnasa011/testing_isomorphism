"""Seeded random instance generation and collision search for invariants."""

from __future__ import annotations

import random
from dataclasses import dataclass

from .algorithms import Invariant
from .exact import is_isomorphic
from .graph import Graph


def erdos_renyi(vertices: int, probability: float, rng: random.Random) -> Graph:
    """Generate G(n,p), with all randomness supplied by the caller's RNG."""
    if vertices < 0 or not 0 <= probability <= 1:
        raise ValueError("vertices must be nonnegative and probability must be in [0, 1]")
    return Graph.from_edges(((u, v) for u in range(vertices) for v in range(u + 1, vertices)
                             if rng.random() < probability), range(vertices))


def random_regular(vertices: int, degree: int, rng: random.Random, attempts: int = 1_000) -> Graph:
    """Generate a simple d-regular graph by rejecting bad configuration pairings."""
    if not 0 <= degree < vertices or vertices * degree % 2:
        raise ValueError("need 0 <= degree < vertices and an even vertices*degree")
    stubs = [vertex for vertex in range(vertices) for _ in range(degree)]
    for _ in range(attempts):
        rng.shuffle(stubs)
        edges = [(stubs[index], stubs[index + 1]) for index in range(0, len(stubs), 2)]
        if all(left != right for left, right in edges) and len({tuple(sorted(edge)) for edge in edges}) == len(edges):
            return Graph.from_edges(edges, range(vertices))
    raise RuntimeError("could not sample a simple regular graph; reduce degree or raise attempts")


def _is_connected(graph: Graph) -> bool:
    """Return whether a graph has exactly one connected component."""
    if not graph.vertices:
        return False
    reached = {graph.vertices[0]}
    frontier = [graph.vertices[0]]
    while frontier:
        vertex = frontier.pop()
        for neighbor in graph.adjacency[vertex] - reached:
            reached.add(neighbor)
            frontier.append(neighbor)
    return len(reached) == graph.order


@dataclass(frozen=True)
class Collision:
    algorithm: str
    seed: int
    samples_examined: int
    left: Graph
    right: Graph

    def reproduce(self) -> dict:
        return {"algorithm": self.algorithm, "seed": self.seed,
                "samples_examined": self.samples_examined,
                "left_edges": self.left.edge_list(), "right_edges": self.right.edge_list()}


def find_collision(
    algorithm: Invariant, *, vertices: int, samples: int, seed: int,
    model: str = "regular", degree: int = 2, probability: float | None = None,
    connected_only: bool = False,
) -> Collision | None:
    """Find a non-isomorphic signature collision, or return None within the budget.

    Graphs are bucketed before invoking the exponential exact oracle, so normal
    misses stay cheap.  A collision is a genuine counterexample to using the
    selected invariant as a complete isomorphism test.
    """
    if model not in {"regular", "erdos"}:
        raise ValueError("model must be 'regular' or 'erdos'")
    edge_probability = (0.5 if probability is None else probability) if model == "erdos" else None
    rng = random.Random(seed)
    buckets: dict[tuple, list[Graph]] = {}
    for index in range(1, samples + 1):
        graph = (random_regular(vertices, degree, rng) if model == "regular"
                 else erdos_renyi(vertices, edge_probability, rng))
        if connected_only and not _is_connected(graph):
            continue
        signature = algorithm.refine(graph).signature
        for prior in buckets.setdefault(signature, []):
            if not is_isomorphic(prior, graph):
                return Collision(algorithm.name, seed, index, prior, graph)
        buckets[signature].append(graph)
    return None
