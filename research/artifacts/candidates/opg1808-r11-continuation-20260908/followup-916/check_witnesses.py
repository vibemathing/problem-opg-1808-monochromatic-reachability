"""Solver-free physical checks for the two explicit diagnostic tournaments.
This is a candidate checker, not a registered or independent verifier.
"""
from collections import deque
from itertools import combinations
from pathlib import Path
import hashlib,json,resource,signal,time,sys

def inspect(obj):
 n=obj['n'];a=obj['arcs'];E={}
 for u,v,c in a:
  assert 0<=u<n and 0<=v<n and u!=v and 0<=c<3
  assert (u,v) not in E and (v,u) not in E
  E[u,v]=c
 assert len(E)==n*(n-1)//2 and all((i,(i+1)%n) in E for i in range(n))
 reach=[];sizes=[]
 for c in range(3):
  R=[]
  for s in range(n):
   seen={s};q=deque([s])
   while q:
    u=q.popleft()
    for v in range(n):
     if E.get((u,v))==c and v not in seen:seen.add(v);q.append(v)
   R.append(seen)
  todo=set(range(n));cs=[]
  while todo:
   s=min(todo);S={v for v in todo if v in R[s] and s in R[v]};todo-=S;cs.append(len(S))
  k=sum(E[i,(i+1)%n]!=c for i in range(n));assert all(x<=k//2 for x in cs)
  reach.append(R);sizes.append(cs)
 rainbow=[]
 for a,b,c in combinations(range(n),3):
  for x,y,z in [(a,b,c),(a,c,b)]:
   ee=[(x,y),(y,z),(z,x)]
   if all(e in E for e in ee) and len({E[e] for e in ee})==3:rainbow.append([x,y,z])
 assert not rainbow
 missing=[sorted(set(range(n))-set.union(*(reach[c][s] for c in range(3)))) for s in range(n)]
 source=[s for s in range(n) if not missing[s]]
 p=obj.get('forced_path',obj.get('predecessor_path',{}).get('vertices'))
 col=obj.get('forced_colour',obj.get('predecessor_path',{}).get('colour'))
 assert p and len(set(p))==len(p) and p[-1]==(p[0]-1)%n
 assert all(E[u,v]==col for u,v in zip(p,p[1:]))
 assert source==([3] if n==4 else [0])
 return {'n':n,'tournament':True,'no_rainbow_directed_triangle':True,'monosources':source,'SCC_sizes':sizes,'predecessor_path':p,'colour':col,'size_bounds_hold':True,'not_root_counterexample':True}

def main():
 resource.setrlimit(resource.RLIMIT_AS,(805306368,)*2);resource.setrlimit(resource.RLIMIT_CPU,(10,11));resource.setrlimit(resource.RLIMIT_FSIZE,(1048576,)*2);signal.alarm(12);t=time.monotonic();P=Path(__file__).parent;rows=[]
 for f in ['four-vertex-size-bound-counterexample.json','twelve-vertex-path-diagnostic.json']:
  b=(P/f).read_bytes();rows.append({'path':f,'sha256':hashlib.sha256(b).hexdigest(),'check':inspect(json.loads(b))})
 out={'verdict':'candidate_only','rows':rows,'footer':True,'python':sys.version.split()[0],'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'elapsed_seconds':time.monotonic()-t,'memory_bytes':805306368,'cpu_seconds':[10,11],'wall_seconds':12,'output_bytes':1048576}
 (P/'witness-check.json').write_text(json.dumps(out,sort_keys=True,separators=(',',':'))+'\n');print(json.dumps(out,sort_keys=True,separators=(',',':')))
if __name__=='__main__':main()
