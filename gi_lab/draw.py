"""Optional Matplotlib renderers for inspecting counterexample graph pairs."""

from __future__ import annotations

import math
from collections import deque
from typing import TYPE_CHECKING

from .graph import Graph, Vertex

if TYPE_CHECKING:
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure


def _component_layout(graph: Graph) -> dict[Vertex, tuple[float, float]]:
    """Deterministic circular component layout; useful for hand-checking graphs."""
    unseen = set(graph.vertices)
    components: list[list[Vertex]] = []
    while unseen:
        start = min(unseen, key=repr)
        queue, component = deque([start]), []
        unseen.remove(start)
        while queue:
            vertex = queue.popleft()
            component.append(vertex)
            for neighbor in sorted(graph.adjacency[vertex], key=repr):
                if neighbor in unseen:
                    unseen.remove(neighbor)
                    queue.append(neighbor)
        components.append(sorted(component, key=repr))
    positions: dict[Vertex, tuple[float, float]] = {}
    gap = 3.2
    for component_index, component in enumerate(components):
        radius = max(0.7, len(component) / 7)
        for index, vertex in enumerate(component):
            angle = 2 * math.pi * index / len(component)
            positions[vertex] = (component_index * gap + radius * math.cos(angle),
                                 radius * math.sin(angle))
    return positions


def draw_graph(graph: Graph, ax: "Axes", title: str = "Graph") -> None:
    """Draw a small graph on a supplied Matplotlib axis without extra packages."""
    positions = _component_layout(graph)
    for left, right in graph.edge_list():
        x1, y1 = positions[left]
        x2, y2 = positions[right]
        ax.plot((x1, x2), (y1, y2), color="#94a3b8", linewidth=1.5, zorder=1)
    for vertex in graph.vertices:
        x, y = positions[vertex]
        ax.scatter(x, y, s=440, color="#2563eb", edgecolor="white", linewidth=1.4, zorder=2)
        ax.text(x, y, str(vertex), ha="center", va="center", color="white", fontsize=8, zorder=3)
    ax.set_title(f"{title}\n|V|={graph.order}, |E|={graph.size}")
    ax.set_aspect("equal")
    ax.margins(0.2)
    ax.axis("off")


def draw_pair(left: Graph, right: Graph, titles: tuple[str, str] = ("Left", "Right")) -> "Figure":
    """Render a non-isomorphic candidate pair side by side."""
    try:
        import matplotlib.pyplot as plt
    except ImportError as error:  # pragma: no cover - depends on optional notebook extra
        raise ImportError("Drawing requires matplotlib; install the Conda environment.") from error
    figure, axes = plt.subplots(1, 2, figsize=(12, 5))
    draw_graph(left, axes[0], titles[0])
    draw_graph(right, axes[1], titles[1])
    figure.tight_layout()
    return figure
