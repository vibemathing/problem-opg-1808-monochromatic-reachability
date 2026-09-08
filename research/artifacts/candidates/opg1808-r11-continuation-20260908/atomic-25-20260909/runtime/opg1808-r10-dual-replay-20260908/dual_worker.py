"""Bounded candidate-side dual replay; no admission or verifier authority."""
from __future__ import annotations
import hashlib,importlib.util,json,resource,signal,sys,time
from collections import Counter
from pathlib import Path
HERE=Path(__file__).resolve().parent
H=lambda b:hashlib.sha256(b).hexdigest()
D=lambda x:json.dumps(x,sort_keys=True,separators=(',',':'))+'\n'

def module(name,p):
    spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def main(rp,lp):
    begin=time.monotonic();raw=rp.read_bytes();req=json.loads(raw)
    resource.setrlimit(resource.RLIMIT_AS,(805306368,)*2);resource.setrlimit(resource.RLIMIT_CPU,(38,39));resource.setrlimit(resource.RLIMIT_FSIZE,(1048576,)*2)
    signal.signal(signal.SIGALRM,lambda a,b:(_ for _ in ()).throw(TimeoutError('worker wall limit')));signal.alarm(40)
    sibling=HERE.parent;r05=sibling/'opg1808-r05-replay-20260907';r06=sibling/'opg1808-r06-cert-shards-20260907';r07=sibling/'opg1808-r07-adaptive-20260907'
    sys.path.insert(0,str(r07));native=module('native_candidate',r05/'exact_replay.py');native.SEED=req['seed'];physical=module('physical_candidate',r06/'physical_checker.py')
    native.physical_audit=lambda n,arcs,palette:physical.check(n,palette,arcs)
    if req['engine']=='cuts':
        import closed_sets
        text=closed_sets.build(req['n'],req['palette'],req['rainbow']);encfiles=[HERE/'closed_sets.py']
    elif req['engine']=='supported':
        import supported_superrelation
        text=supported_superrelation.build(req['n'],req['palette'],req['rainbow'],True);encfiles=[r07/'supported_superrelation.py',r07/'superrelation.py']
    else:raise ValueError('engine')
    if 'fixed_arcs' in req:text+=''.join(f'(assert e{c}_{u}_{v})\n' for u,v,c in req['fixed_arcs'])
    solver=native.NativeSolver(text,req['query_ms'])
    base=HERE/'formulas'/f"{req['engine']}-{req['n']}-{req['palette']}-{int(req['rainbow'])}-{H(text.encode())[:16]}.smt2"
    if base.exists():assert base.read_bytes()==text.encode()
    else:base.parent.mkdir(exist_ok=True);base.write_text(text)
    pins={str(p.relative_to(sibling)):H(p.read_bytes()) for p in encfiles+[r05/'exact_replay.py',r06/'physical_checker.py',HERE/'dual_worker.py']}
    hd={'type':'header','verdict':'candidate_only','request_sha256':H(raw),'base_sha256':H(text.encode()),'base_path':str(base.relative_to(HERE)),
      'engine':req['engine'],'pins':pins,'python':sys.version.split()[0],'solver':solver.version,'solver_sha256':solver.library_sha256,
      'seed':req['seed'],'query_ms':req['query_ms'],'memory_bytes':805306368,'cpu_seconds':[38,39],'wall_seconds':40,'file_bytes':1048576,'threads':1}
    rows=[]
    with lp.open('x') as out:
        out.write(D(hd));out.flush()
        try:
            for task in req['instances']:
                if time.monotonic()-begin+req['query_ms']/1000+2>=38:break
                w=task.get('word');extra='' if w is None else ''.join(f'(assert e{c}_{u}_{(u+1)%req["n"]})\n' for u,c in enumerate(w))
                ans=solver.solve(req['n'],req['palette'],w)
                ans.update(type='instance',ordinal=task.get('ordinal'),word=w,input_sha256=H((text+extra).encode()),query_ms=req['query_ms'],seed=req['seed'])
                if ans['status']=='sat':
                    check=physical.check(req['n'],req['palette'],ans['arcs']);ans['physical_audit']=check
                    ok=check['spanning_cycle_present'] and check['predecessor_pairs_unreachable'] and (not req['rainbow'] or check['no_rainbow_directed_triangle'])
                    if not ok:ans['status']='invalid_sat_model'
                out.write(D(ans));out.flush();rows.append(ans)
                if ans['status'] in ['sat','invalid_sat_model'] and not req.get('control'):break
            ft={'type':'footer','request_sha256':H(raw),'processed':len(rows),'processed_ordinals':[x['ordinal'] for x in rows],
              'complete_request':len(rows)==len(req['instances']),'statuses':dict(Counter(x['status'] for x in rows)),
              'wall_seconds':time.monotonic()-begin,'cpu_seconds':time.process_time(),'verdict':'candidate_only'}
            out.write(D(ft));out.flush()
        finally:solver.close()
    print(D(ft),end='')
if __name__=='__main__':main(Path(sys.argv[1]),Path(sys.argv[2]))
