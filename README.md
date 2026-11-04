# GI Lab

GI Lab is a small Python workbench for exploring graph isomorphism tests. It
includes colour refinement (1-WL), 2-WL, hand-built example graphs, and an
exact backtracking checker for small examples.

> A different WL signature proves that two graphs are not isomorphic. A
> matching signature is inconclusive: the graphs may still be different. The
> exact checker is intended for small examples, not large inputs.

## Get started

Requires Python 3.11 or newer. From this directory, install the project in
editable mode:

```bash
python -m pip install -e .
python -m gi_lab list
```

Compare the classic rook and Shrikhande graphs:

```bash
python -m gi_lab compare rook4 shrikhande --algorithms 1wl 2wl exact
```

Run the example corpus or search for a 1-WL collision:

```bash
python -m gi_lab corpus --algorithms 1wl 2wl --include-permutations
python -m gi_lab find-collision --algorithm 1wl --model regular \
  --vertices 10 --degree 2 --seed 7
```

## Explore the notebook

Install the optional notebook environment and launch Jupyter from this
directory:

```bash
conda env create -f environment.yml
conda activate gi-lab
jupyter lab
```

Open [the GI Lab workbench](notebooks/gi_lab_workbench.ipynb) to build graphs,
compare refinement results, and explore reproducible examples.

## Project layout

- `gi_lab/graph.py`: a compact undirected graph representation.
- `gi_lab/algorithms.py`: 1-WL and 2-WL invariants.
- `gi_lab/families.py`: named graphs and adversarial examples.
- `gi_lab/exact.py`: a small-graph isomorphism checker.
- `gi_lab/search.py`: seeded random graph generation and collision search.
- `tests/`: executable examples of expected behavior.

To add an invariant, implement the `Invariant` protocol in
`gi_lab/algorithms.py` and register it in `BUILTINS`. To add a named example,
add its constructor in `gi_lab/families.py` and include it in
`default_corpus()`.
