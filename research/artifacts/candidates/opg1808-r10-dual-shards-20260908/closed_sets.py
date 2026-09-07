"""Forward-closed separating sets; no transitive R or Floyd recurrence.
SAT implies physical predecessor nonreachability. No positive reach assertion.
Candidate-generation code; no trusted-verifier status is claimed.
"""
from itertools import combinations, permutations

def formula(n:int,palette:int=3,rainbow:bool=True)->str:
    if not 3<=n<=16 or not 2<=palette<=4: raise ValueError('scope')
    out=['(set-logic QF_FD)']
    emit=lambda t:out.append('(assert '+t+')')
    e=lambda c,u,v:f'e{c}_{u}_{v}'
    x=lambda c,s,v:f'x{c}_{s}_{v}'
    for c in range(palette):
        for u in range(n):
            for v in range(n):
                if u!=v:out.append(f'(declare-const {e(c,u,v)} Bool)')
        for s in range(n):
            for v in range(n):out.append(f'(declare-const {x(c,s,v)} Bool)')
            emit(x(c,s,s));emit('(not '+x(c,s,(s-1)%n)+')')
            for u in range(n):
                for v in range(n):
                    if u!=v:emit(f'(or (not {x(c,s,u)}) (not {e(c,u,v)}) {x(c,s,v)})')
    for u in range(n):
        for v in range(u+1,n):
            opts=[e(c,a,b) for a,b in [(u,v),(v,u)] for c in range(palette)]
            emit('(or '+' '.join(opts)+')')
            for i in range(len(opts)):
                for j in range(i):emit(f'(or (not {opts[i]}) (not {opts[j]}))')
        emit('(or '+' '.join(e(c,u,(u+1)%n) for c in range(palette))+')')
    emit(e(0,0,1))
    if rainbow:
        for a,b,c in combinations(range(n),3):
            for u,v,w in [(a,b,c),(a,c,b)]:
                for i,j,k in permutations(range(palette),3):
                    emit(f'(or (not {e(i,u,v)}) (not {e(j,v,w)}) (not {e(k,w,u)}))')
    return '\n'.join(out)+'\n'

def word_assertions(w:str)->str:
    n=len(w)
    return ''.join(f'(assert e{c}_{u}_{(u+1)%n})\n' for u,c in enumerate(w))
