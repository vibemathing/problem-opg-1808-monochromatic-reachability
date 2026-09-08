"""Fresh implementation of forward-closed source sets; no transitivity/Floyd.
This is new candidate code, not a recovered version of unavailable R09 code.
"""
from itertools import combinations, permutations

def build(n, palette=3, rainbow=True):
    if not 3 <= n <= 16 or not 2 <= palette <= 4: raise ValueError('domain')
    lines=['(set-logic QF_FD)']
    def e(c,u,v): return f'e{c}_{u}_{v}'
    def m(c,s,u):
        if u==s:return 'true'
        if u==(s-1)%n:return 'false'
        return f'm{c}_{s}_{u}'
    def emit(s):lines.append('(assert '+s+')')
    for u in range(n):
        for v in range(n):
            if u!=v:
                for c in range(palette):lines.append(f'(declare-const {e(c,u,v)} Bool)')
    for u,v in combinations(range(n),2):
        es=[e(c,x,y) for x,y in [(u,v),(v,u)] for c in range(palette)]
        emit('(or '+' '.join(es)+')')
        for a,b in combinations(es,2):emit(f'(not (and {a} {b}))')
    for u in range(n):emit('(or '+' '.join(e(c,u,(u+1)%n) for c in range(palette))+')')
    emit(e(0,0,1))
    if rainbow:
        for a,b,c in combinations(range(n),3):
            for x,y,z in [(a,b,c),(a,c,b)]:
                for d,f,g in permutations(range(palette),3):emit(f'(not (and {e(d,x,y)} {e(f,y,z)} {e(g,z,x)}))')
    for c in range(palette):
        for s in range(n):
            for u in range(n):
                if u not in (s,(s-1)%n):lines.append(f'(declare-const {m(c,s,u)} Bool)')
            for u in range(n):
                for v in range(n):
                    if u!=v:emit(f'(=> (and {m(c,s,u)} {e(c,u,v)}) {m(c,s,v)})')
    return '\n'.join(lines)+'\n'
