"""Physical guarded-run interval obstruction. Candidate only; no SAT pruning.
All paths are checked on arcs; the SCC and reachability come from BFS/Kosaraju.
"""
from collections import deque,Counter
from itertools import combinations,product
import importlib.util,json,hashlib,resource,signal,time,sys
from pathlib import Path
P=Path(__file__).parent;S=P.parent.parent
H=lambda b:hashlib.sha256(b).hexdigest()
J=lambda x:json.dumps(x,sort_keys=True,separators=(',',':'))+'\n'
def load_physical():
 path=S/'opg1808-r06-cert-shards-20260907/physical_checker.py'
 sp=importlib.util.spec_from_file_location('physical_subinterval',path);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m

def path(E,n,c,u,v):
 parent={u:None};q=deque([u])
 while q:
  x=q.popleft()
  if x==v:
   ans=[]
   while x is not None:ans.append(x);x=parent[x]
   return ans[::-1]
  for y in range(n):
   if E.get((x,y))==c and y not in parent:parent[y]=x;q.append(y)
 return None

def runs(n,E,c):
 cuts=[i for i in range(n) if E[i,(i+1)%n]!=c]
 if not cuts:return []
 starts=[(i+1)%n for i in cuts];out=[]
 for s in starts:
  row=[s]
  while E[row[-1],(row[-1]+1)%n]==c:row.append((row[-1]+1)%n)
  out.append(row)
 return out

def erase(walk):
 out=[];pos={}
 for x in walk:
  if x in pos:
   k=pos[x]
   for y in out[k+1:]:del pos[y]
   out=out[:k+1]
  else:pos[x]=len(out);out.append(x)
 return out

def verify_path(E,seq,c):
 return bool(seq) and len(set(seq))==len(seq) and all(E.get((u,v))==c for u,v in zip(seq,seq[1:]))

def extract(n,arcs,c,j,h,entry,exitpath):
 E={(u,v):d for u,v,d in arcs};R=runs(n,E,c);k=len(R)
 if k<3:raise ValueError('at least three runs required')
 A=R[j];B=R[(j+1)%k];D=R[(j-1)%k]
 if h in A or len(A)<2 or entry[0] not in B or entry[-1]!=h or exitpath[0]!=h or exitpath[-1] not in D:raise ValueError('guard endpoints')
 if not verify_path(E,entry,c) or not verify_path(E,exitpath,c):raise ValueError('nonphysical guards')
 turns=[i for i in range(1,len(A)) if (h,A[i-1]) in E and (A[i],h) in E]
 if not turns:return None
 i=turns[0];a,b=A[i-1:i+1]
 if E[h,a]==c:
  walk=B[:B.index(entry[0])+1]+entry[1:]+A[i-1:];cert={'kind':'predecessor_path','colour':c,'path':erase(walk),'case':'c-entry'}
 elif E[b,h]==c:
  walk=A[:i+1]+exitpath+D[D.index(exitpath[-1])+1:];cert={'kind':'predecessor_path','colour':c,'path':erase(walk),'case':'c-exit'}
 elif E[h,a]==E[b,h]:cert={'kind':'predecessor_path','colour':E[h,a],'path':[b,h,a],'case':'equal-cross-colours'}
 else:cert={'kind':'rainbow_directed_triangle','vertices':[h,a,b],'case':'distinct-cross-colours'}
 cert.update(run_index=j,run=A,hub=h,entry=entry,exit=exitpath,turn_index=i)
 return cert

def validate(n,E,cert):
 if cert['kind']=='predecessor_path':
  p=cert['path'];return len(p)>1 and p[-1]==(p[0]-1)%n and verify_path(E,p,cert['colour'])
 v=cert['vertices'];return len(v)==len(set(v))==3 and all((v[i],v[(i+1)%3]) in E for i in range(3)) and len({E[v[i],v[(i+1)%3]] for i in range(3)})==3

def example(n,word):
 E={(u,v):0 for u,v in combinations(range(n),2)}
 E.pop((0,n-1));E[n-1,0]=int(word[-1])
 for i in range(n-1):E[i,i+1]=int(word[i])
 if n==12:
  E.pop((1,5));E[5,1]=2;E[0,5]=1;E[2,5]=2;E[0,10]=1;entry=[3,5];exitpath=[5,11];h=5
 else:
  E.pop((1,3));E[3,1]=0;E[0,3]=2;entry=[3];exitpath=[3,1,4];h=3
 arcs=[[u,v,d] for (u,v),d in sorted(E.items())];R=runs(n,E,0);j=R.index([0,1,2]);cert=extract(n,arcs,0,j,h,entry,exitpath);assert validate(n,E,cert)
 physical=load_physical().check(n,3,arcs);assert physical['bfs_scc_equal'] and physical['no_rainbow_directed_triangle'] and not physical['root_counterexample']
 assert all(len(x)==1 for ob in physical['scc_condensations'] for x in ob['components'])
 return {'n':n,'word':word,'arcs':arcs,'guard_scc':[h],'certificate':cert,'physical':physical,'whole_run_endpoint_turn':(h,0) in E and (2,h) in E,'constructed_not_solver_model':True}

def tests():
 total=0;witnesses=Counter();triggers=0;n=5;w='00112';cycle={(i,(i+1)%n) for i in range(n)};chords=[(u,v) for u,v in combinations(range(n),2) if (u,v) not in cycle and (v,u) not in cycle]
 for opts in product(range(6),repeat=len(chords)):
  arcs=[(i,(i+1)%n,int(w[i])) for i in range(n)]+[(u,v,x//2) if x%2==0 else (v,u,x//2) for (u,v),x in zip(chords,opts)];E={(u,v):d for u,v,d in arcs};R=runs(n,E,0);j=R.index([0,1,2]);B=R[(j+1)%len(R)];D=R[(j-1)%len(R)]
  for h in (3,4):
   q=next((p for u in B if (p:=path(E,n,0,u,h))),None);r=next((p for v in D if (p:=path(E,n,0,h,v))),None)
   if q and r:
    cert=extract(n,arcs,0,j,h,q,r)
    if cert:assert validate(n,E,cert);triggers+=1;witnesses[cert['case']]+=1
  total+=1
 return dict(tables=total,triggered=triggers,cases=dict(witnesses),all_actual_witnesses_valid=True)

if __name__=='__main__':
 resource.setrlimit(resource.RLIMIT_AS,(805306368,)*2);resource.setrlimit(resource.RLIMIT_CPU,(35,36));resource.setrlimit(resource.RLIMIT_FSIZE,(1048576,)*2);signal.alarm(38);t=time.monotonic()
 output={'verdict':'candidate_only','examples':[example(12,'001021100221'),example(5,'00112')],'tests':tests(),'python':sys.version.split()[0],'code_sha256':H(Path(__file__).read_bytes()),'cpu_limit':[35,36],'wall_limit':38,'memory_bytes':805306368,'output_cap':1048576,'footer':True,'elapsed_seconds':time.monotonic()-t}
 (P/'subinterval-witnesses.json').write_text(J(output));print(J({'footer':True,'tests':output['tests'],'elapsed_seconds':output['elapsed_seconds']}),end='')
