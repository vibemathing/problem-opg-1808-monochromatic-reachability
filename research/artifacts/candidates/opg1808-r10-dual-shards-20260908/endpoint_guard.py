"""Three equal-colour exceptional connectors: explicit endpoint-relaxation test.
No claim that a macro model expands into a root counterexample.
"""
import itertools,json,time,ctypes as C,resource,sys
from pathlib import Path
from runner import J,H,HERE
sys.path.insert(0,str(HERE.parent/'opg1808-r05-replay-20260907'))
from exact_replay import NativeSolver
sys.path.insert(0,str(HERE.parent/'opg1808-r06-cert-shards-20260907'))
from physical_checker import check

def build(k):
 n=2*k;lines=['(set-logic QF_FD)'];e=lambda u,v,c:f'e{c}_{u}_{v}';r=lambda u,v,c:f'r{c}_{u}_{v}'
 def emit(x):lines.append('(assert '+x+')')
 for u in range(n):
  for v in range(n):
   if u!=v:
    for c in range(3):lines.extend([f'(declare-const {e(u,v,c)} Bool)',f'(declare-const {r(u,v,c)} Bool)'])
 for u,v in itertools.combinations(range(n),2):
  opts=[e(a,b,c) for a,b in [(u,v),(v,u)] for c in range(3)];emit('(or '+' '.join(opts)+')')
  for a,b in itertools.combinations(opts,2):emit(f'(or (not {a}) (not {b}))')
 for c in range(3):
  for u,v in itertools.permutations(range(n),2):
   emit(f'(=> {e(u,v,c)} {r(u,v,c)})')
   for w in range(n):
    if w not in (u,v):emit(f'(=> (and {r(u,v,c)} {r(v,w,c)}) {r(u,w,c)})')
 for a,b,c in itertools.combinations(range(n),3):
  for x,y,z in [(a,b,c),(a,c,b)]:
   for i,j,l in itertools.permutations(range(3),3):emit(f'(not (and {e(x,y,i)} {e(y,z,j)} {e(z,x,l)}))')
 for i in range(k):
  a,b=2*i,2*i+1;prev=2*((i-1)%k)+1;emit(r(a,b,0));emit('(not '+r(b,a,0)+')');emit(e(b,2*((i+1)%k),1))
  for c in range(3):emit('(not '+r(a,prev,c)+')')
  for x in range(n):
   if x in (a,b):continue
   out='(or '+' '.join(e(x,a,c) for c in range(3))+')';inc='(or '+' '.join(e(b,x,c) for c in range(3))+')'
   emit(f'(=> (and {out} {inc}) (or {r(x,b,0)} {r(a,x,0)}))')
 for u,v in itertools.permutations(range(n),2):
  if u%2==0 and v==2*((u//2-1)%k)+1:continue
  emit('(or '+' '.join(r(u,v,c) for c in range(3))+')')
 return '\n'.join(lines)+'\n'

def plain(k,arcs,rels):
 n=2*k;phy=check(n,3,arcs);R={tuple(q) for q in rels};E={(u,v):c for u,v,c in arcs};tests=0
 assert phy['no_rainbow_directed_triangle']
 for u,v,c in arcs:assert (u,v,c) in R;tests+=1
 for c in range(3):
  for u,v,w in itertools.permutations(range(n),3):assert not ((u,v,c) in R and (v,w,c) in R) or (u,w,c) in R;tests+=1
 for i in range(k):
  a,b,prev=2*i,2*i+1,2*((i-1)%k)+1
  assert (a,b,0) in R and (b,a,0) not in R;assert E[b,2*((i+1)%k)]==1
  for c in range(3):assert (a,prev,c) not in R
  for x in range(n):
   if x not in (a,b) and (x,a) in E and (b,x) in E:assert (x,b,0) in R or (a,x,0) in R
 for u,v in itertools.permutations(range(n),2):
  if not (u%2==0 and v==2*((u//2-1)%k)+1):assert any((u,v,c) in R for c in range(3))
 return {'all_endpoint_axioms_pass':True,'transitive_implications_checked':3*n*(n-1)*(n-2),'physical':phy}

def main():
 resource.setrlimit(resource.RLIMIT_AS,(805306368,)*2);resource.setrlimit(resource.RLIMIT_CPU,(28,29));resource.setrlimit(resource.RLIMIT_FSIZE,(1048576,)*2)
 rows=[];start=time.monotonic()
 for k in (1,2,3):
  text=build(k);s=NativeSolver(text,5000);tick=time.monotonic();status=s.fn('Z3_solver_check',C.c_int,[s.P,s.P])(s.ctx,s.solver);ans={'status':{1:'sat',-1:'unsat',0:'unknown'}[status],'seconds':time.monotonic()-tick};row={'k':k,'input_sha256':H(text.encode()),'solver':s.version,'solver_sha256':s.library_sha256,'query_ms':5000,'seed':17,**ans}
  if ans['status']=='sat':
   P=s.P;ctx=s.ctx;assert status==1
   model=s.fn('Z3_solver_get_model',P,[P,P])(ctx,s.solver);s.fn('Z3_model_inc_ref',None,[P,P])(ctx,model)
   sort=s.fn('Z3_mk_bool_sort',P,[P])(ctx);mk=s.fn('Z3_mk_const',P,[P,P,P]);ev=s.fn('Z3_model_eval',C.c_bool,[P,P,P,C.c_bool,C.POINTER(P)]);truth=s.fn('Z3_get_bool_value',C.c_int,[P,P]);R=[];arcs=[]
   for u,v in itertools.permutations(range(2*k),2):
    for c in range(3):
     for prefix,target in [('r',R),('e',arcs)]:
      ast=mk(ctx,s.symbol(ctx,f'{prefix}{c}_{u}_{v}'.encode()),sort);val=P();assert ev(ctx,model,ast,True,C.byref(val))
      if truth(ctx,val)==1:target.append([u,v,c])
   s.fn('Z3_model_dec_ref',None,[P,P])(ctx,model);row['arcs']=arcs;row['relations']=R;row['plain_audit']=plain(k,arcs,R)
  rows.append(row);s.close()
 out={'verdict':'candidate_only','rows':rows,'footer':True,'elapsed_seconds':time.monotonic()-start,'new_root_counterexample':False,'code_sha256':H(Path(__file__).read_bytes()),'python':sys.version.split()[0],'memory_bytes':805306368,'cpu_soft_seconds':28,'cpu_hard_seconds':29,'output_cap_bytes':1048576}
 (HERE/'endpoint-guard-result.json').write_text(J(out));print(J(out))
if __name__=='__main__':main()
