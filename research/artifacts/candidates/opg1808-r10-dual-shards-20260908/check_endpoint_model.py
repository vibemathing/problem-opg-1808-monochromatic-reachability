"""Stdlib-only check of all endpoint axioms; no solver or Floyd imported."""
from itertools import combinations,permutations
import json,sys,hashlib,resource
from pathlib import Path

def audit(d):
 k=d['k'];n=2*k;assert 1<=k<=16 and d['palette']==3
 E={};R=set()
 for u,v,c in d['arcs']:
  assert type(u)==type(v)==type(c)==int and 0<=u<n and 0<=v<n and u!=v and 0<=c<3
  assert (u,v) not in E and (v,u) not in E;E[u,v]=c
 assert len(E)==n*(n-1)//2
 for u,v,c in d['relations']:
  assert 0<=u<n and 0<=v<n and u!=v and 0<=c<3 and (u,v,c) not in R;R.add((u,v,c))
 for (u,v),c in E.items():assert (u,v,c) in R
 for u,v,w in permutations(range(n),3):
  for c in range(3):assert not ((u,v,c) in R and (v,w,c) in R) or (u,w,c) in R
 for a,b,c in combinations(range(n),3):
  for x,y,z in ((a,b,c),(a,c,b)):
   if (x,y) in E and (y,z) in E and (z,x) in E:assert len({E[x,y],E[y,z],E[z,x]})<3
 for i in range(k):
  a,b,prev=2*i,2*i+1,2*((i-1)%k)+1
  assert (a,b,0) in R and (b,a,0) not in R
  assert E[b,2*((i+1)%k)]==1
  assert all((a,prev,c) not in R for c in range(3))
  for x in range(n):
   if x not in (a,b) and (x,a) in E and (b,x) in E:assert (x,b,0) in R or (a,x,0) in R
 for u,v in permutations(range(n),2):
  if not (u%2==0 and v==2*((u//2-1)%k)+1):assert any((u,v,c) in R for c in range(3))
 missing=[]
 for u in range(n):
  total={u}
  for c in range(3):
   seen={u};todo=[u]
   while todo:
    x=todo.pop()
    for y in range(n):
     if E.get((x,y))==c and y not in seen:seen.add(y);todo.append(y)
   total|=seen
  missing.append(sorted(set(range(n))-total))
 return {'verdict':'candidate_only','all_axioms_A_to_F':True,'no_rainbow_directed_triangle':True,'missing_targets':missing,
         'physical_monosources':[u for u in range(n) if not missing[u]],'k':k,'root_counterexample':all(bool(x) for x in missing)}
if __name__=='__main__':
 resource.setrlimit(resource.RLIMIT_AS,(805306368,)*2);resource.setrlimit(resource.RLIMIT_CPU,(8,9));resource.setrlimit(resource.RLIMIT_FSIZE,(1048576,)*2)
 p=Path(sys.argv[1] if len(sys.argv)>1 else 'endpoint-model.json');raw=p.read_bytes();r=audit(json.loads(raw));r['input_sha256']=hashlib.sha256(raw).hexdigest();print(json.dumps(r,sort_keys=True,separators=(',',':')))
