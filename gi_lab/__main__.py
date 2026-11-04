"""Command line for hand-checkable GI experiments."""

from __future__ import annotations

import argparse
import json

from .algorithms import BUILTINS
from .exact import is_isomorphic
from .experiments import as_jsonable, run
from .families import default_corpus, named_graphs
from .search import find_collision


def _algorithms(names: list[str]):
    unknown = set(names) - set(BUILTINS) - {"exact"}
    if unknown:
        raise SystemExit(f"unknown algorithms: {', '.join(sorted(unknown))}")
    return [BUILTINS[name] for name in names if name != "exact"]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list", help="list built-in manual graph constructions")
    compare = sub.add_parser("compare", help="compare two named graphs")
    compare.add_argument("left", choices=sorted(named_graphs()))
    compare.add_argument("right", choices=sorted(named_graphs()))
    compare.add_argument("--algorithms", nargs="+", default=["1wl", "2wl"])
    corpus = sub.add_parser("corpus", help="run the adversarial regression corpus")
    corpus.add_argument("--algorithms", nargs="+", default=["1wl", "2wl"])
    corpus.add_argument("--include-permutations", action="store_true")
    search = sub.add_parser("find-collision", help="search seeded random graphs for an invariant collision")
    search.add_argument("--algorithm", choices=sorted(BUILTINS), default="1wl")
    search.add_argument("--model", choices=["regular", "erdos"], default="regular")
    search.add_argument("--vertices", type=int, default=10)
    search.add_argument("--degree", type=int, default=2,
                        help="regular degree (used by --model regular)")
    search.add_argument("--edge-probability", type=float,
                        help="edge probability (used by --model erdos)")
    search.add_argument("--average-degree", type=float,
                        help="target expected average degree (used by --model erdos; mutually exclusive with --edge-probability)")
    search.add_argument("--samples", type=int, default=40)
    search.add_argument("--seed", type=int, default=0)
    search.add_argument("--connected-only", action="store_true",
                         help="ignore sampled graphs that are disconnected")
    args = parser.parse_args()
    if args.command == "list":
        print(json.dumps({name: graph.describe() for name, graph in named_graphs().items()}, indent=2))
        return
    if args.command == "compare":
        graphs = named_graphs()
        requested = _algorithms(args.algorithms)
        exact = is_isomorphic(graphs[args.left], graphs[args.right])
        results = [{"algorithm": a.name, "same_signature":
                                       a.refine(graphs[args.left]).signature == a.refine(graphs[args.right]).signature}
                   for a in requested]
        if "exact" in args.algorithms:
            results.append({"algorithm": "exact", "same_signature": exact})
        print(json.dumps({"exact_isomorphic": exact, "results": results}, indent=2))
        return
    if args.command == "find-collision":
        collision = find_collision(BUILTINS[args.algorithm], vertices=args.vertices,
                                   samples=args.samples, seed=args.seed, model=args.model,
                                   degree=args.degree, probability=args.edge_probability,
                                   connected_only=args.connected_only)
        print(json.dumps(None if collision is None else collision.reproduce(), indent=2))
        return
    print(json.dumps(as_jsonable(run(default_corpus(args.include_permutations),
                                      _algorithms(args.algorithms))), indent=2))


if __name__ == "__main__":
    main()
