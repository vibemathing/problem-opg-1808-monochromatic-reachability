"""Physical tournament checker. No solver or Floyd-circuit implementation imports.
BFS and a separate Kosaraju-SCC condensation traversal must agree exactly.
This is a candidate-side checker, not an admitted verifier principal.
"""
from __future__ import annotations
from collections import deque
from itertools import combinations
import argparse, hashlib, json
from pathlib import Path


def _bfs(graph: list[list[int]], start: int):
    parent = [-1] * len(graph)
    parent[start] = start
    q = deque([start])
    while q:
        u = q.popleft()
        for v in graph[u]:
            if parent[v] == -1:
                parent[v] = u
                q.append(v)
    return {i for i, p in enumerate(parent) if p != -1}, parent


def _scc_closures(graph: list[list[int]]):
    n = len(graph)
    reverse = [[] for _ in range(n)]
    for u, row in enumerate(graph):
        for v in row:
            reverse[v].append(u)
    # Iterative DFS finishing order; independent of the BFS implementation.
    seen = set()
    finish = []
    for root in range(n):
        if root in seen:
            continue
        seen.add(root)
        stack = [(root, iter(graph[root]))]
        while stack:
            u, it = stack[-1]
            v = next(it, None)
            if v is None:
                finish.append(u)
                stack.pop()
            elif v not in seen:
                seen.add(v)
                stack.append((v, iter(graph[v])))
    component = [-1] * n
    groups = []
    for root in reversed(finish):
        if component[root] != -1:
            continue
        label = len(groups)
        members = []
        stack = [root]
        component[root] = label
        while stack:
            u = stack.pop()
            members.append(u)
            for v in reverse[u]:
                if component[v] == -1:
                    component[v] = label
                    stack.append(v)
        groups.append(sorted(members))
    dag = [set() for _ in groups]
    for u, row in enumerate(graph):
        for v in row:
            if component[u] != component[v]:
                dag[component[u]].add(component[v])
    reachable_groups = []
    for label in range(len(groups)):
        visited = {label}
        stack = [label]
        while stack:
            for other in dag[stack.pop()]:
                if other not in visited:
                    visited.add(other)
                    stack.append(other)
        reachable_groups.append(set().union(*(set(groups[j]) for j in visited)))
    return [reachable_groups[component[u]] for u in range(n)], groups, [sorted(s) for s in dag]


def check(n: int, palette: int, arcs: list[list[int]]) -> dict:
    if type(n) is not int or not 1 <= n <= 32:
        raise ValueError('nonempty order must be in [1,32]')
    if type(palette) is not int or not 1 <= palette <= 4:
        raise ValueError('palette must be in [1,4]')
    if type(arcs) is not list:
        raise ValueError('arc table must be a list')
    graphs = [[[] for _ in range(n)] for _ in range(palette)]
    table = {}
    for arc in arcs:
        if not isinstance(arc, (list, tuple)) or len(arc) != 3 or any(type(x) is not int for x in arc):
            raise ValueError('invalid arc record')
        u, v, c = arc
        if not (0 <= u < n and 0 <= v < n and u != v and 0 <= c < palette):
            raise ValueError('arc outside frozen domain')
        if (u, v) in table or (v, u) in table:
            raise ValueError('repeated unordered pair')
        table[u, v] = c
        graphs[c][u].append(v)
    if len(table) != n * (n - 1) // 2:
        raise ValueError('incomplete tournament')
    closures = [[None] * n for _ in range(palette)]
    sccs = []
    for c, graph in enumerate(graphs):
        component_reach, groups, dag = _scc_closures(graph)
        sccs.append({'components': groups, 'dag': dag})
        for s in range(n):
            reached, _ = _bfs(graph, s)
            if reached != component_reach[s]:
                raise AssertionError('BFS versus SCC mismatch')
            closures[c][s] = sorted(reached)
    missing = []
    for u in range(n):
        reached = set().union(*(set(closures[c][u]) for c in range(palette)))
        missing.append(sorted(set(range(n)) - reached))
    rainbow = []
    for u, v, w in combinations(range(n), 3):
        for x, y, z in [(u, v, w), (u, w, v)]:
            if (x, y) in table and (y, z) in table and (z, x) in table:
                colors = [table[x, y], table[y, z], table[z, x]]
                if len(set(colors)) == 3:
                    rainbow.append({'cycle': [x, y, z], 'colors': colors})
    cycle_present = n >= 3 and all((u, (u+1) % n) in table for u in range(n))
    pred_missing = n >= 2 and all((u-1) % n in missing[u] for u in range(n))
    exactly_pred = n >= 2 and all(missing[u] == [(u-1) % n] for u in range(n))
    sources = [u for u in range(n) if not missing[u]]
    return {'n': n, 'palette': palette, 'tournament': True, 'nonempty': True,
            'bfs_scc_equal': True, 'reach_by_colour_then_source': closures,
            'scc_condensations': sccs, 'rainbow_directed_triangles': rainbow,
            'no_rainbow_directed_triangle': not rainbow, 'monosources': sources,
            'no_monosource': not sources, 'unreachable_targets': missing,
            'spanning_cycle_present': cycle_present,
            'predecessor_pairs_unreachable': pred_missing,
            'exactly_predecessor_pairs_unreachable': exactly_pred,
            'root_counterexample': palette <= 3 and not rainbow and not sources}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('input', type=Path)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    if args.input.stat().st_size > 1048576:
        raise ValueError('input bound')
    payload = args.input.read_bytes()
    obj = json.loads(payload)
    result = check(obj['n'], obj['palette'], obj['arcs'])
    result.update(verdict='candidate_only', input_sha256=hashlib.sha256(payload).hexdigest())
    args.output.write_text(json.dumps(result, sort_keys=True, separators=(',', ':'))+'\n')

if __name__ == '__main__':
    main()
