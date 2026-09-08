"""Candidate Boolean encoding; no Floyd/path-pivot recurrence.
A implies a colour-transitive R superrelation. Negative predecessor R entries
certify physical nonreachability; positives need only hold for minimum examples.
All symmetry used here is fixed cycle plus renaming its first arc to colour 0.
"""
from itertools import combinations, permutations

def build(n: int, palette: int = 3, rainbow: bool = True, positive: bool = True) -> str:
    if not 3 <= n <= 16 or not 2 <= palette <= 4:
        raise ValueError('bounded nonempty domain')
    e=lambda u,v,c:f'e{c}_{u}_{v}'
    r=lambda u,v,c:f'r{c}_{u}_{v}'
    lines=['(set-logic QF_FD)']
    def emit(s): lines.append('(assert '+s+')')
    for c in range(palette):
        for u in range(n):
            for v in range(n):
                if u != v:
                    lines += [f'(declare-const {e(u,v,c)} Bool)',f'(declare-const {r(u,v,c)} Bool)']
    for u,v in combinations(range(n),2):
        choices=[e(a,b,c) for c in range(palette) for a,b in ((u,v),(v,u))]
        emit('(or '+' '.join(choices)+')')
        for a,b in combinations(choices,2): emit(f'(or (not {a}) (not {b}))')
    for c in range(palette):
        for u in range(n):
            for v in range(n):
                if u==v: continue
                emit(f'(=> {e(u,v,c)} {r(u,v,c)})')
                for w in range(n):
                    if len({u,v,w})==3:
                        emit(f'(=> (and {r(u,v,c)} {r(v,w,c)}) {r(u,w,c)})')
    for u in range(n):
        emit('(or '+' '.join(e(u,(u+1)%n,c) for c in range(palette))+')')
        for c in range(palette): emit('(not '+r(u,(u-1)%n,c)+')')
        if positive:
            for v in range(n):
                if v not in (u,(u-1)%n): emit('(or '+' '.join(r(u,v,c) for c in range(palette))+')')
    if rainbow:
        for u,v,w in combinations(range(n),3):
            for a,b,c in ((u,v,w),(u,w,v)):
                for x,y,z in permutations(range(palette),3):
                    emit(f'(not (and {e(a,b,x)} {e(b,c,y)} {e(c,a,z)}))')
    emit(e(0,1,0))
    return '\n'.join(lines)+'\n'

def word_assertions(word: str) -> str:
    n=len(word)
    if not 3<=n<=16 or any(c not in '0123' for c in word): raise ValueError('word')
    return ''.join(f'(assert e{c}_{u}_{(u+1)%n})\n' for u,c in enumerate(word))
