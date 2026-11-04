# GI Lab — graph-isomorphism algorithm workbench

`gi-lab` is a compact, dependency-free Python project for studying practical
polynomial-time graph-isomorphism *tests*, especially colour refinement and
the Weisfeiler–Leman (WL) hierarchy.  It is deliberately built around small,
inspectable examples: every graph family has a direct construction and the
runner records enough information to explain a result.

> Important: a WL mismatch proves non-isomorphism; equal WL signatures do
> **not** prove isomorphism.  General graph isomorphism has a
> quasi-polynomial algorithm, while fixed-dimensional WL is a polynomial-time
> incomplete invariant.  The included exact solver is only a small-graph
> oracle for checking experiments.

## What is included

- Immutable-ish simple undirected `Graph` representation with a readable
  `Graph.from_edges(...)` construction API.
- Pluggable `Invariant` protocol; add a new test without changing the runner.
- 1-WL / colour refinement and 2-WL implementations, with round-by-round
  certificates, plus a random-walk stationary-distribution invariant.
- A small exact backtracking oracle, intended to label generated counterexamples.
- Manual and named adversarial graph families, including a classic 1-WL
  collision: the 4×4 rook graph versus the Shrikhande graph.
- A reproducible corpus runner that reports true separations and false
  positives (collisions).

The `stationary` algorithm uses the random walk on an undirected graph, whose
degree-weighted stationary probability is `degree(v) / (2m)`. That remains a
valid stationary distribution on disconnected graphs, though it is not unique
across components; the algorithm picks this canonical degree-weighted choice
(isolated vertices have zero mass). For an edgeless graph it uses the uniform
distribution over vertices, and the empty graph has an empty distribution.
The label-independent signature is the sorted list of `(degree, probability)`
pairs, keeping each vertex's two values together. Since the probability is
determined by degree and graph size, this still captures only the degree
multiset. Different signatures rule out isomorphism, but matching signatures
do not establish it (the rook and Shrikhande graphs both have the same pairs).

## Quick start

```bash
python -m gi_lab list
python -m gi_lab compare rook4 shrikhande --algorithms 1wl 2wl exact
python -m gi_lab compare rook4 shrikhande --algorithms stationary exact
python -m gi_lab corpus --algorithms 1wl 2wl --include-permutations
python -m gi_lab find-collision --algorithm 1wl --model regular --vertices 10 --degree 2 --seed 7
python -m gi_lab find-collision --algorithm stationary --model regular --vertices 16 --degree 6 --connected-only
python -m gi_lab find-collision --algorithm stationary --model erdos --vertices 20 --average-degree 4 --connected-only
python -m unittest discover -s tests -v
```

## Jupyter / Conda

The runnable notebook is [notebooks/gi_lab_workbench.ipynb](notebooks/gi_lab_workbench.ipynb).
Create its environment and launch Jupyter from the repository root:

```bash
conda env create -f environment.yml
conda activate gi-lab
jupyter lab
```

The `rook4` / `shrikhande` pair is non-isomorphic, but both are strongly
regular with the same parameters.  It is expected to collide under 1-WL; use
it as a first regression case whenever modifying refinement.

## Finding counterexamples randomly

`find-collision` samples a deterministic stream of graphs, buckets them by a
chosen invariant signature, and then checks only same-bucket pairs with the exact
small-graph oracle.  On success it prints the seed and the two edge lists, so
the result can be pasted directly into `Graph.from_edges(...)` and added to a
manual regression case. Add `--connected-only` to skip disconnected samples
when searching for collisions within individual connected components. The
sample budget counts all generated graphs, including skipped disconnected
ones. With `--model erdos`, choose either `--edge-probability p` or
`--average-degree d`; the latter sets `p = d / (vertices - 1)`, so `d` is the
expected average degree, not a guaranteed degree. The default random-regular
model is intentionally useful for finding 1-WL failures, because every
sampled graph has the same initial degree colour. It is not evidence that a
method is sound if a finite search does not find a collision.

In the Jupyter notebook, `draw_pair(left, right)` renders any candidate pair
side by side.  The random search and rook/Shrikhande examples already call it.

## Architecture

```text
constructors ──> Graph ──> Invariant.refine() ──> Signature / Trace
      │                       │
      └── CounterexampleCase  └──> ExperimentRunner ──> JSON-friendly results
                                      │
                              ExactBacktrackingOracle (small inputs only)
```

### Adding an algorithm

Implement `Invariant` in `gi_lab/algorithms.py`, return a canonical,
JSON-friendly `RefinementResult`, then register it in `BUILTINS`.  Algorithms
should expose their resource growth in the docstring (for example, 2-WL has
quadratic tuple space).  This keeps experiments honest about what is
polynomial for a fixed WL dimension.

### Adding hard instances

Add a constructor in `gi_lab/families.py`, then a `CounterexampleCase` in
`default_corpus()`.  Prefer named parameterized constructors over serialized
edge lists so a reader can reconstruct each example by hand.  The test suite
is the right home for a short mathematical explanation of an expected
collision/separation.

## Suggested extensions

1. Add `k`-WL for configurable, fixed `k`, using tuple neighbourhood caching.
2. Add CFI graphs over configurable base graphs, which give systematic WL
   lower-bound instances.
3. Add individualization-refinement (IR) search / nauty-style partition
   refinement and compare its search tree to WL certificates.
4. Add an optional adapter for NetworkX or SageMath for cross-validation—not
   as a dependency of the core.
5. Persist generated graphs and experiment metadata as graph6 + JSON, and add
   property-based fuzzing with deterministic seeds.
