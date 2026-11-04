"""Experiment harness that distinguishes an invariant from an exact decision."""

from __future__ import annotations

from dataclasses import asdict, dataclass

from .algorithms import Invariant
from .exact import is_isomorphic
from .families import CounterexampleCase


@dataclass(frozen=True)
class Trial:
    case: str
    algorithm: str
    agrees: bool
    exact_isomorphic: bool
    verdict: str
    left_rounds: int
    right_rounds: int


def run(cases: tuple[CounterexampleCase, ...], algorithms: list[Invariant], verify: bool = True) -> list[Trial]:
    results: list[Trial] = []
    for case in cases:
        truth = is_isomorphic(case.left, case.right) if verify else case.isomorphic
        if truth != case.isomorphic:
            raise AssertionError(f"corpus label disagrees with oracle for {case.name}")
        for algorithm in algorithms:
            left, right = algorithm.refine(case.left), algorithm.refine(case.right)
            agrees = left.signature == right.signature
            verdict = "collision" if agrees and not truth else "separated" if not agrees else "consistent"
            results.append(Trial(case.name, algorithm.name, agrees, truth, verdict,
                                 left.rounds, right.rounds))
    return results


def as_jsonable(trials: list[Trial]) -> list[dict]:
    return [asdict(trial) for trial in trials]
