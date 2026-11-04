"""Hand-checkable graph families and named regression/counterexample cases."""

from __future__ import annotations

from dataclasses import dataclass

from .graph import Graph


def cycle(n: int) -> Graph:
    if n < 3:
        raise ValueError("a cycle needs at least 3 vertices")
    return Graph.from_edges((i, (i + 1) % n) for i in range(n))


def complete(n: int) -> Graph:
    return Graph.from_edges(((i, j) for i in range(n) for j in range(i + 1, n)), range(n))


def disjoint_cycles(*lengths: int) -> Graph:
    """Disjoint union of cycles, retaining component boundaries by construction."""
    if any(length < 3 for length in lengths):
        raise ValueError("each component must be a cycle of length at least 3")
    edges: list[tuple[tuple[int, int], tuple[int, int]]] = []
    vertices: list[tuple[int, int]] = []
    for component, length in enumerate(lengths):
        component_vertices = [(component, index) for index in range(length)]
        vertices.extend(component_vertices)
        edges.extend((component_vertices[index], component_vertices[(index + 1) % length])
                     for index in range(length))
    return Graph.from_edges(edges, vertices)


def rook_graph(n: int = 4) -> Graph:
    """Vertices are squares; edges join squares sharing a row or column."""
    squares = [(row, col) for row in range(n) for col in range(n)]
    return Graph.from_edges(((a, b) for a in squares for b in squares
                             if repr(a) < repr(b) and (a[0] == b[0] or a[1] == b[1])), squares)


def shrikhande_graph() -> Graph:
    """Cayley graph on Z4² with steps ±(1,0), ±(0,1), ±(1,1)."""
    vertices = [(x, y) for x in range(4) for y in range(4)]
    steps = {(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1)}
    return Graph.from_edges(
        ((x, y), ((x + dx) % 4, (y + dy) % 4))
        for x, y in vertices for dx, dy in steps
        if repr((x, y)) < repr(((x + dx) % 4, (y + dy) % 4))
    )


def permuted(graph: Graph) -> Graph:
    """A deterministic nontrivial relabelling for positive-control cases."""
    return graph.relabel({v: f"p{index}" for index, v in enumerate(reversed(graph.vertices))})


@dataclass(frozen=True)
class CounterexampleCase:
    name: str
    left: Graph
    right: Graph
    isomorphic: bool
    note: str


def named_graphs() -> dict[str, Graph]:
    return {"cycle6": cycle(6), "complete6": complete(6), "rook4": rook_graph(),
            "shrikhande": shrikhande_graph()}


def default_corpus(include_permutations: bool = False) -> tuple[CounterexampleCase, ...]:
    cases = [
        CounterexampleCase("degree-separation", cycle(6), complete(6), False,
                           "Basic sanity check: degree sequence differs."),
        CounterexampleCase("rook-vs-shrikhande", rook_graph(), shrikhande_graph(), False,
                           "Strongly regular (16,6,2,2): canonical 1-WL collision."),
        CounterexampleCase("connectedness-blindness", cycle(12), disjoint_cycles(6, 6), False,
                           "Every vertex has degree two, so 1-WL misses the component split."),
    ]
    if include_permutations:
        graph = rook_graph()
        cases.append(CounterexampleCase("relabelled-rook", graph, permuted(graph), True,
                                        "Positive control: signatures must agree on relabelling."))
    return tuple(cases)
