#!/usr/bin/env python3
"""Generator-supplied finite recheck script; not a trusted verifier receipt.

Checks the two explicit witnesses and the blow-up family at orders 4..7.
It enumerates set partitions of each fixed witness, NOT all colored tournaments.
No mathematical execution of this script is claimed by the accompanying bundle.
Python 3.10+; standard library only; one process, no network.
"""
from __future__ import annotations
import argparse
from itertools import combinations
import json
from pathlib import Path
import platform
import sys
import time
from typing import Iterator

MAX_N = 7
MAX_INPUT_BYTES = 1_048_576
MAX_OUTPUT_BYTES = 65_536

class Budget:
    def __init__(self, seconds: float) -> None:
        self.deadline = time.monotonic() + seconds
    def check(self) -> None:
        if time.monotonic() > self.deadline:
            raise TimeoutError("bounded check exceeded its wall-time budget")

class Tournament:
    def __init__(self, vertices: list[str], arcs: list[list[object]]) -> None:
        if not 2 <= len(vertices) <= MAX_N or len(set(vertices)) != len(vertices):
            raise ValueError("vertices must be distinct, with order in [2,7]")
        self.vertices = tuple(vertices)
        vertex_set = set(vertices)
        self.arcs: dict[tuple[str, str], int] = {}
        self.colors: dict[frozenset[str], int] = {}
        for record in arcs:
            if len(record) != 3:
                raise ValueError("each arc must have tail, head, color")
            u, v, color = record
            if not isinstance(u, str) or not isinstance(v, str):
                raise ValueError("vertex labels must be strings")
            if u == v or u not in vertex_set or v not in vertex_set:
                raise ValueError("invalid endpoint")
            if type(color) is not int or color not in (1, 2, 3):
                raise ValueError("this witness checker uses the frozen three-color palette")
            pair = frozenset((u, v))
            if pair in self.colors:
                raise ValueError("duplicate unordered pair")
            self.arcs[u, v] = color
            self.colors[pair] = color
        if len(self.arcs) != len(vertices) * (len(vertices) - 1) // 2:
            raise ValueError("arc list is not a complete tournament")

    def signature(self, u: str, v: str) -> tuple[bool, int]:
        return (u, v) in self.arcs, self.colors[frozenset((u, v))]

    def reachable(self, source: str, color: int | None) -> set[str]:
        seen = {source}
        todo = [source]
        while todo:
            u = todo.pop()
            for v in self.vertices:
                if v not in seen and (u, v) in self.arcs:
                    if color is None or self.arcs[u, v] == color:
                        seen.add(v)
                        todo.append(v)
        return seen

    def strong(self) -> bool:
        return all(len(self.reachable(v, None)) == len(self.vertices)
                   for v in self.vertices)

    def mono_roots(self) -> list[str]:
        roots = []
        for u in self.vertices:
            reach = set().union(*(self.reachable(u, c) for c in (1, 2, 3)))
            if len(reach) == len(self.vertices):
                roots.append(u)
        return roots

    def rainbow_counts(self) -> tuple[int, int]:
        undirected = directed = 0
        for triple in combinations(self.vertices, 3):
            colors = {self.colors[frozenset(e)] for e in combinations(triple, 2)}
            if len(colors) == 3:
                undirected += 1
                is_cycle = all(
                    sum((u, v) in self.arcs for v in triple if v != u) == 1
                    for u in triple)
                if is_cycle:
                    directed += 1
        return undirected, directed

def partitions(vertices: tuple[str, ...], budget: Budget) -> Iterator[tuple[tuple[str, ...], ...]]:
    """Each set partition appears once, using restricted-growth labels."""
    n = len(vertices)
    labels = [0] * n
    def visit(i: int, top: int) -> Iterator[tuple[tuple[str, ...], ...]]:
        budget.check()
        if i == n:
            yield tuple(tuple(vertices[j] for j in range(n) if labels[j] == k)
                        for k in range(top + 1))
            return
        for label in range(top + 2):
            labels[i] = label
            yield from visit(i + 1, max(top, label))
    yield from visit(1, 0)

def acceptable(T: Tournament, blocks: tuple[tuple[str, ...], ...]) -> bool:
    if len(blocks) < 2:
        return False
    used: set[int] = set()
    for B, C in combinations(blocks, 2):
        signatures = {T.signature(u, v) for u in B for v in C}
        if len(signatures) != 1:
            return False
        used.add(next(iter(signatures))[1])
    return len(used) <= 2

def family(m: int) -> Tournament:
    if not 1 <= m <= 4:
        raise ValueError("the finite family check is restricted to m=1..4")
    D = [f"d{i}" for i in range(1, m + 1)]
    arcs: list[list[object]] = [["a","b",1], ["b","c",1], ["c","a",3]]
    for d in D:
        arcs += [["a",d,2], [d,"b",1], [d,"c",2]]
    for i in range(m):
        for j in range(i + 1, m):
            arcs.append([D[i], D[j], 1])
    return Tournament(["a", "b", "c"] + D, arcs)

def inspect(name: str, T: Tournament, require_strong_gallai: bool,
            budget: Budget) -> dict[str, object]:
    budget.check()
    undirected, directed = T.rainbow_counts()
    total = acceptable_count = 0
    for P in partitions(T.vertices, budget):
        total += 1
        acceptable_count += acceptable(T, P)
    roots = T.mono_roots()
    strong = T.strong()
    if directed != 0 or acceptable_count != 0 or "a" not in roots:
        raise AssertionError(f"{name}: a frozen witness claim failed")
    if require_strong_gallai and (not strong or undirected != 0):
        raise AssertionError(f"{name}: strengthened witness premise failed")
    return {
        "name": name, "order": len(T.vertices), "set_partitions_examined": total,
        "acceptable_nontrivial_partitions": acceptable_count,
        "rainbow_directed_triangles": directed,
        "rainbow_undirected_triangles": undirected,
        "strong": strong, "monochromatic_roots": roots
    }

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--witnesses", required=True, type=Path)
    parser.add_argument("--timeout-seconds", type=float, default=10.0)
    args = parser.parse_args()
    if not 0 < args.timeout_seconds <= 30:
        parser.error("timeout must be in (0,30]")
    budget = Budget(args.timeout_seconds)
    with args.witnesses.open("rb") as handle:
        raw = handle.read(MAX_INPUT_BYTES + 1)
    if len(raw) > MAX_INPUT_BYTES:
        raise ValueError("witness input exceeds the size budget")
    data = json.loads(raw)
    cases = data.get("instances", [])
    if len(cases) != 2 or {x.get("name") for x in cases} != {"transitive3","strong4"}:
        raise ValueError("expected the two frozen named instances")
    results = []
    for item in cases:
        T = Tournament(item["vertices"], item["arcs"])
        results.append(inspect(item["name"], T, item["name"] == "strong4", budget))
    for m in range(1, 5):
        results.append(inspect(f"strong-family-m{m}", family(m), True, budget))
    output = json.dumps({
        "verdict": "candidate_only",
        "scope": "fixed witness checks only; no Result or EvidenceLink",
        "python_version": platform.python_version(),
        "results": results
    }, ensure_ascii=False, indent=2)
    if len(output.encode("utf-8")) > MAX_OUTPUT_BYTES:
        raise ValueError("output exceeds the size budget")
    print(output)
    return 0

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, KeyError, TypeError, AssertionError, TimeoutError, OSError) as exc:
        print(f"candidate check failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise SystemExit(1)
