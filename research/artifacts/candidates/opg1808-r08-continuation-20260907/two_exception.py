"""Construct a local obstruction, not a solver or a trusted verifier.
Any coloured tournament with a directed spanning cycle having at most two
non-red cycle arcs contains a rainbow directed triangle or a monochromatic
path from some cycle vertex to its predecessor. Palette size is arbitrary.
"""
from itertools import combinations,product

def extract(n, arcs, red=0):
    E={(u,v):c for u,v,c in arcs}
    if n<3 or len(arcs)!=n*(n-1)//2 or len(E)!=len(arcs):raise ValueError('not a tournament')
    for u,v in combinations(range(n),2):
        if ((u,v) in E)+((v,u) in E)!=1:raise ValueError('pair missing/duplicated')
    if any(not 0<=u<n or not 0<=v<n or u==v for u,v in E):raise ValueError('bad endpoint')
    if any((u,(u+1)%n) not in E for u in range(n)):raise ValueError('cycle absent')
    bad=[i for i in range(n) if E[i,(i+1)%n]!=red]
    if len(bad)>2:raise ValueError('not in two-exception family')
    def path(nodes):return {'kind':'predecessor_monochromatic_path','vertices':nodes}
    if len(bad)<=1:
        s=(bad[0]+1)%n if bad else 0
        return path([(s+j)%n for j in range(n)])
    p,q=bad
    A=list(range(p+1,q+1));B=list(range(q+1,n))+list(range(0,p+1))
    # A and B are disjoint red paths. Each starts after the end of the other.
    for i,a in enumerate(A):
        for j,b in enumerate(B):
            if E.get((a,b))==red:return path(A[:i+1]+B[j:])
            if E.get((b,a))==red:return path(B[:j+1]+A[i:])
    # No cross arc is red. Pick the red path on which orientation must change.
    if (A[0],B[0]) in E:x=A[0];P=B
    else:x=B[0];P=A
    if (x,P[0]) not in E or (P[-1],x) not in E:raise AssertionError('endpoint orientation')
    j=next(j for j in range(1,len(P)) if (P[j],x) in E)
    a,b=P[j-1],P[j]
    if E[x,a]==E[b,x]:return path([b,x,a])
    return {'kind':'rainbow_directed_triangle','vertices':[x,a,b]}

def validate(n,arcs,certificate):
    E={(u,v):c for u,v,c in arcs};v=certificate['vertices']
    if len(set(v))!=len(v):return False
    pairs=list(zip(v,v[1:]))
    if certificate['kind']=='rainbow_directed_triangle':
        pairs.append((v[-1],v[0]));return len(v)==3 and all(p in E for p in pairs) and len({E[p] for p in pairs})==3
    if certificate['kind']=='predecessor_monochromatic_path':
        return len(v)>=2 and v[-1]==(v[0]-1)%n and all(p in E for p in pairs) and len({E[p] for p in pairs})==1
    return False

def finite_tests():
    counts=[]
    for n in range(3,6):
        cycle={(i,(i+1)%n) for i in range(n)}
        chords=[(u,v) for u,v in combinations(range(n),2) if (u,v) not in cycle and (v,u) not in cycle]
        types={};total=0
        for w in product(range(3),repeat=n):
            if sum(c!=0 for c in w)>2:continue
            fixed=[(i,(i+1)%n,w[i]) for i in range(n)]
            for opts in product(range(6),repeat=len(chords)):
                arcs=fixed+[(u,v,o//2) if o%2==0 else (v,u,o//2) for (u,v),o in zip(chords,opts)]
                cert=extract(n,arcs)
                if not validate(n,arcs,cert):raise AssertionError((n,arcs,cert))
                total+=1;types[cert['kind']]=types.get(cert['kind'],0)+1
        counts.append({'n':n,'tables':total,'certificate_types':types})
    return counts
if __name__=='__main__':
    import hashlib,json,resource,signal,time
    from pathlib import Path
    resource.setrlimit(resource.RLIMIT_AS,(268435456,)*2);resource.setrlimit(resource.RLIMIT_CPU,(35,36));resource.setrlimit(resource.RLIMIT_FSIZE,(1048576,)*2)
    signal.signal(signal.SIGALRM,lambda s,f:(_ for _ in ()).throw(TimeoutError('wall')));signal.alarm(38)
    t=time.monotonic();print(json.dumps({'verdict':'candidate_only','code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'counts':finite_tests(),'elapsed_seconds':time.monotonic()-t,'cpu_limit':[35,36],'wall_limit':38,'memory_bytes':268435456,'output_limit':1048576},sort_keys=True))
