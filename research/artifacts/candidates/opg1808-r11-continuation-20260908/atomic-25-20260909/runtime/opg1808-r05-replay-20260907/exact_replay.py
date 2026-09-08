"""Candidate-only replay: fresh word orbits, exact Floyd circuits, physical BFS.
Python stdlib + existing libz3. No dependence on R04's R-superrelation encoder.
All computations are bounded; an incomplete record never discharges a word.
"""
from __future__ import annotations
import argparse
import ctypes as C
import ctypes.util
import hashlib
import itertools
import json
import resource
import sys
import time
from pathlib import Path

SEED = 17
MEMORY_BYTES = 805306368
MAX_FILE_BYTES = 1048576
HERE = Path(__file__).resolve().parent

def digest(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def dump(x) -> str:
    return json.dumps(x, sort_keys=True, separators=(',', ':'))

def bound_process(cpu=40):
    resource.setrlimit(resource.RLIMIT_AS, (MEMORY_BYTES, MEMORY_BYTES))
    resource.setrlimit(resource.RLIMIT_FSIZE, (MAX_FILE_BYTES, MAX_FILE_BYTES))
    resource.setrlimit(resource.RLIMIT_CPU, (cpu, cpu + 1))

def word_orbits(n: int, palette: int = 3) -> list[str]:
    """Partition ALL palette**n words via explicit rotations x permutations.
    Iterate in lex order: the first unused word is the orbit minimum. Does not
    use restricted-growth recursion or first-occurrence normalization.
    """
    if not 3 <= n <= 11 or not 2 <= palette <= 4:
        raise ValueError('word bounds')
    permutations = list(itertools.permutations(range(palette)))
    remaining = set(itertools.product(range(palette), repeat=n))
    result = []
    for w in itertools.product(range(palette), repeat=n):
        if w not in remaining:
            continue
        result.append(''.join(map(str, w)))
        for p in permutations:
            renamed = tuple(p[c] for c in w)
            for j in range(n):
                remaining.discard(renamed[j:] + renamed[:j])
    if remaining:
        raise RuntimeError('uncovered orbit')
    return result

def restricted_growth_words(n: int, palette: int = 3) -> list[str]:
    """Second word algorithm, implementing the frozen R03 definition."""
    def norm(w):
        m = {}
        return ''.join(str(m.setdefault(c, len(m))) for c in w)
    def gen(s, largest):
        if len(s) == n:
            if s == min(norm(s[j:] + s[:j]) for j in range(n)):
                yield s
        else:
            for c in range(min(palette - 1, largest + 1) + 1):
                yield from gen(s + str(c), max(c, largest))
    return sorted(gen('0', 0))

def build_formula(n: int, palette: int = 3, forbid_rainbow: bool = True,
                  require_positive: bool = True, fixed_cycle: bool = True):
    """Exact reachability: gate = (old OR (left AND right)), never one-way.
    Endpoint-equal pivots are identities under reflexive reachability; diagonal
    entries are True and never become solver variables.
    """
    if not 3 <= n <= 11 or not 2 <= palette <= 4:
        raise ValueError('formula bounds')
    lines = ['(set-logic QF_FD)']
    def declare(x): lines.append(f'(declare-const {x} Bool)')
    def assertion(x): lines.append(f'(assert {x})')
    def arc(u, v, c): return f'e{c}_{u}_{v}'
    for c in range(palette):
        for u in range(n):
            for v in range(n):
                if u != v: declare(arc(u, v, c))
    for u, v in itertools.combinations(range(n), 2):
        options = [arc(a, b, c) for c in range(palette) for a, b in [(u, v), (v, u)]]
        assertion('(or ' + ' '.join(options) + ')')
        for a, b in itertools.combinations(options, 2):
            assertion(f'(or (not {a}) (not {b}))')
    if fixed_cycle:
        for u in range(n):
            assertion('(or ' + ' '.join(arc(u, (u + 1) % n, c) for c in range(palette)) + ')')
        assertion(arc(0, 1, 0))
    if forbid_rainbow:
        for verts in itertools.combinations(range(n), 3):
            x, y, z = verts
            for cycle in [(x, y, z), (x, z, y)]:
                for cs in itertools.permutations(range(palette), 3):
                    es = [arc(cycle[j], cycle[(j + 1) % 3], cs[j]) for j in range(3)]
                    assertion('(not (and ' + ' '.join(es) + '))')
    reach = []
    for c in range(palette):
        prev = [[('true' if u == v else arc(u, v, c)) for v in range(n)] for u in range(n)]
        for k in range(n):
            curr = [r[:] for r in prev]
            for u in range(n):
                for v in range(n):
                    if u == v or u == k or v == k: continue
                    x = f'f{c}_{k}_{u}_{v}'
                    declare(x)
                    assertion(f'(= {x} (or {prev[u][v]} (and {prev[u][k]} {prev[k][v]})))')
                    curr[u][v] = x
            prev = curr
        reach.append(prev)
    if fixed_cycle:
        for u in range(n):
            v = (u - 1) % n
            for c in range(palette): assertion(f'(not {reach[c][u][v]})')
            if require_positive:
                for v in range(n):
                    if v != u and v != (u - 1) % n:
                        assertion('(or ' + ' '.join(reach[c][u][v] for c in range(palette)) + ')')
    return '\n'.join(lines) + '\n', reach

def physical_audit(n: int, arcs: list, palette: int) -> dict:
    """BFS from actual arcs, not from any SMT reach variable."""
    adjacency = [[[] for _ in range(n)] for _ in range(palette)]
    table = {}
    for u, v, c in arcs:
        if not (0 <= u < n and 0 <= v < n and u != v and 0 <= c < palette):
            raise ValueError('invalid physical arc')
        key = tuple(sorted((u, v)))
        if key in table: raise ValueError('duplicate physical pair')
        table[key] = (u, v, c)
        adjacency[c][u].append(v)
    if len(table) != n * (n - 1) // 2: raise ValueError('incomplete tournament')
    mono_reach = []
    missing = []
    for s in range(n):
        by_colour = []
        for c in range(palette):
            visited = {s}; queue = [s]
            for u in queue:
                for v in adjacency[c][u]:
                    if v not in visited: visited.add(v); queue.append(v)
            by_colour.append(sorted(visited))
        mono_reach.append(by_colour)
        missing.append(sorted(set(range(n)) - set().union(*(set(a) for a in by_colour))))
    triangles = []
    for vs in itertools.combinations(range(n), 3):
        es = [table[p] for p in itertools.combinations(vs, 2)]
        if len({c for _, _, c in es}) == 3 and all(sum(u == x for u, _, _ in es) == 1 for x in vs):
            triangles.append(list(vs))
    return {'monochromatic_bfs': mono_reach, 'unreachable_targets': missing,
            'rainbow_directed_triples': triangles,
            'monosources': [u for u in range(n) if not missing[u]],
            'root_counterexample': palette <= 3 and not triangles and all(missing)}

class NativeSolver:
    def __init__(self, text: str, milliseconds: int):
        name = ctypes.util.find_library('z3')
        if not name: raise RuntimeError('native Z3 absent')
        self.lib = C.CDLL(name); self.ctx = None
        self.P, self.U, self.S = C.c_void_p, C.c_uint, C.c_char_p
        P, U, S = self.P, self.U, self.S
        vv = [U() for _ in range(4)]
        self.fn('Z3_get_version', None, [C.POINTER(U)] * 4)(*[C.byref(v) for v in vv])
        self.version = '.'.join(str(v.value) for v in vv)
        # Pin the actual library contents as well as its reported version.
        matches = {l.split()[-1] for l in Path('/proc/self/maps').read_text().splitlines() if 'libz3.so' in l}
        self.library_sha256 = digest(Path(sorted(matches)[0]).read_bytes()) if matches else None
        cfg = self.fn('Z3_mk_config', P, [])()
        self.ctx = self.fn('Z3_mk_context', P, [P])(cfg)
        self.fn('Z3_del_config', None, [P])(cfg)
        self.symbol = self.fn('Z3_mk_string_symbol', P, [P, S])
        logic = self.symbol(self.ctx, b'QF_FD')
        self.solver = self.fn('Z3_mk_solver_for_logic', P, [P, P])(self.ctx, logic)
        self.fn('Z3_solver_inc_ref', None, [P, P])(self.ctx, self.solver)
        param = self.fn('Z3_mk_params', P, [P])(self.ctx)
        self.fn('Z3_params_inc_ref', None, [P, P])(self.ctx, param)
        setter = self.fn('Z3_params_set_uint', None, [P, P, P, U])
        for k, v in [('timeout', milliseconds), ('random_seed', SEED), ('threads', 1)]:
            setter(self.ctx, param, self.symbol(self.ctx, k.encode()), v)
        self.fn('Z3_solver_set_params', None, [P, P, P])(self.ctx, self.solver, param)
        self.fn('Z3_params_dec_ref', None, [P, P])(self.ctx, param)
        self.load(text)
    def fn(self, name, ret, args):
        f = getattr(self.lib, name); f.restype = ret; f.argtypes = args; return f
    def load(self, text):
        self.fn('Z3_solver_from_string', None, [self.P, self.P, self.S])(self.ctx, self.solver, text.encode())
    def solve(self, n, palette, word=None, extra=''):
        P = self.P
        self.fn('Z3_solver_push', None, [P, P])(self.ctx, self.solver)
        try:
            if word is not None:
                if len(word) != n or any(int(c) >= palette for c in word): raise ValueError('word mismatch')
                self.load(''.join(f'(assert e{c}_{u}_{(u + 1) % n})\n' for u, c in enumerate(word)))
            if extra: self.load(extra)
            started = time.monotonic()
            r = self.fn('Z3_solver_check', C.c_int, [P, P])(self.ctx, self.solver)
            ans = {'status': {1: 'sat', -1: 'unsat', 0: 'unknown'}[r], 'seconds': time.monotonic() - started}
            if r == 0:
                ans['reason'] = self.fn('Z3_solver_get_reason_unknown', self.S, [P, P])(self.ctx, self.solver).decode()
            if r == 1:
                model = self.fn('Z3_solver_get_model', P, [P, P])(self.ctx, self.solver)
                self.fn('Z3_model_inc_ref', None, [P, P])(self.ctx, model)
                sort = self.fn('Z3_mk_bool_sort', P, [P])(self.ctx)
                const = self.fn('Z3_mk_const', P, [P, P, P])
                evaluate = self.fn('Z3_model_eval', C.c_bool, [P, P, P, C.c_bool, C.POINTER(P)])
                truth = self.fn('Z3_get_bool_value', C.c_int, [P, P])
                arcs = []
                for u in range(n):
                    for v in range(n):
                        if u == v: continue
                        for c in range(palette):
                            expr = const(self.ctx, self.symbol(self.ctx, f'e{c}_{u}_{v}'.encode()), sort)
                            val = P()
                            if not evaluate(self.ctx, model, expr, True, C.byref(val)): raise RuntimeError('model evaluation')
                            if truth(self.ctx, val) == 1: arcs.append([u, v, c])
                self.fn('Z3_model_dec_ref', None, [P, P])(self.ctx, model)
                ans['arcs'] = arcs; ans['physical_audit'] = physical_audit(n, arcs, palette)
            return ans
        finally:
            self.fn('Z3_solver_pop', None, [P, P, self.U])(self.ctx, self.solver, 1)
    def close(self):
        if self.ctx:
            self.fn('Z3_solver_dec_ref', None, [self.P, self.P])(self.ctx, self.solver)
            self.fn('Z3_del_context', None, [self.P])(self.ctx); self.ctx = None

def main():
    p = argparse.ArgumentParser()
    p.add_argument('mode', choices=['words', 'batch', 'controls'])
    p.add_argument('--n', type=int, default=3)
    p.add_argument('--seconds', type=float, default=.25)
    p.add_argument('--total-seconds', type=float, default=25)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    if not 0 < a.seconds <= 10 or not 0 < a.total_seconds <= 30: raise ValueError('time budget')
    bound_process(38)
    a.out.mkdir(parents=True, exist_ok=True)
    if a.mode == 'words':
        summary = []
        for n in range(3, 12):
            w = word_orbits(n); ref = restricted_growth_words(n)
            if w != ref: raise RuntimeError('word-set mismatch')
            payload = ('\n'.join(w) + '\n').encode()
            (a.out / f'words-{n}.txt').write_bytes(payload)
            summary.append({'n': n, 'count': len(w), 'sha256': digest(payload), 'exact_set_equal': True})
        (a.out / 'word-audit.json').write_text(dump(summary) + '\n')
        print(dump(summary)); return
    if a.mode == 'controls':
        results = []
        for n, k, rainbow, word in [(3, 3, False, '012'), (6, 4, True, None), (3, 3, True, '012')]:
            text, _ = build_formula(n, k, rainbow, True)
            solver = NativeSolver(text, 5000)
            ans = solver.solve(n, k, word)
            ans.update({'n': n, 'palette': k, 'forbid_rainbow': rainbow, 'word': word,
                        'base_input_sha256': digest(text.encode()), 'solver_version': solver.version,
                        'solver_library_sha256': solver.library_sha256, 'seed': SEED, 'timeout_seconds': 5})
            results.append(ans); solver.close()
        if [r['status'] for r in results] != ['sat', 'sat', 'unsat']: raise RuntimeError('control mismatch')
        if not results[0]['physical_audit']['rainbow_directed_triples']: raise RuntimeError('control RGB lost')
        if results[1]['physical_audit']['rainbow_directed_triples'] or results[1]['physical_audit']['monosources']: raise RuntimeError('4-colour control invalid')
        (a.out / 'controls.json').write_text(dump(results) + '\n')
        print(dump(results)); return
    n = a.n
    words_file = a.out / f'words-{n}.txt'
    names = words_file.read_text().splitlines()
    text, _ = build_formula(n)
    base_digest = digest(text.encode())
    code_digest = digest(Path(__file__).read_bytes())
    base_path = a.out / f'exact-{n}.smt2'
    if base_path.exists() and base_path.read_text() != text: raise RuntimeError('input mutation')
    base_path.write_text(text)
    log = a.out / f'exact-log-{n}.jsonl'
    records = [json.loads(s) for s in log.read_text().splitlines()] if log.exists() else []
    solver = NativeSolver(text, int(a.seconds * 1000))
    header = {'type':'header','n':n,'base_input_sha256':base_digest, 'solver_version':solver.version,
              'solver_library_sha256':solver.library_sha256,'code_sha256':code_digest,'seed':SEED,
              'python_version':sys.version.split()[0],'memory_bytes':MEMORY_BYTES,'threads':1}
    if records and records[0] != header: raise RuntimeError('stale log header')
    if not records: log.write_text(dump(header) + '\n')
    prior = records[1:]
    for r in prior:
        if r['word'] not in names or r['n'] != n: raise RuntimeError('out of domain record')
        if r['status'] == 'sat': raise RuntimeError('prior SAT requires inspection')
    done = {r['word'] for r in prior if r['status'] == 'unsat'}
    attempted = {r['word'] for r in prior}
    pending = sorted(set(names) - done, key=lambda w: (w in attempted, w))
    begin = time.monotonic(); count = 0
    try:
        with log.open('a') as f:
            for word in pending:
                if time.monotonic() - begin + a.seconds + 1 > a.total_seconds: break
                if log.stat().st_size > MAX_FILE_BYTES - 4096: break
                extra = ''.join(f'(assert e{c}_{u}_{(u + 1) % n})\n' for u, c in enumerate(word))
                r = solver.solve(n, 3, word)
                r.update({'n': n, 'word': word, 'instance_sha256': digest((text + extra).encode()),
                    'timeout_seconds': a.seconds})
                f.write(dump(r) + '\n'); f.flush(); count += 1
                if r['status'] == 'unsat': done.add(word)
                if r['status'] == 'sat': break
    finally: solver.close()
    unresolved = sorted(set(names) - done)
    (a.out / f'unresolved-{n}.json').write_text(dump(unresolved) + '\n')
    print(dump({'n': n, 'words': len(names), 'completed_unsat': len(done), 'attempted_this_batch': count,
        'unresolved_count': len(unresolved), 'batch_seconds': time.monotonic() - begin,
        'log_sha256': digest(log.read_bytes()), 'unresolved_sha256': digest((dump(unresolved)+'\n').encode())}))
if __name__ == '__main__': main()
