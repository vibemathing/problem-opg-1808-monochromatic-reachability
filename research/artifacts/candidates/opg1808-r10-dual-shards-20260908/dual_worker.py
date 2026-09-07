"""One bounded batch. Only parent-exit-zero plus a validated footer is eligible.
Physical SAT tables use frozen BFS/SCC checker, not either SMT core.
"""
from __future__ import annotations
import sys,json,hashlib,time,resource,importlib.util,ctypes as C,argparse
from pathlib import Path
from datetime import datetime,timezone
H=lambda b:hashlib.sha256(b).hexdigest()
J=lambda d:json.dumps(d,sort_keys=True,separators=(',',':'))+'\n'
MEM=805306368;CAP=1048576

def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def main():
    ap=argparse.ArgumentParser();ap.add_argument('request',type=Path);ap.add_argument('output',type=Path);a=ap.parse_args()
    reqraw=a.request.read_bytes();req=json.loads(reqraw);here=Path(__file__).resolve().parent;coll=here.parent
    resource.setrlimit(resource.RLIMIT_AS,(MEM,)*2);resource.setrlimit(resource.RLIMIT_CPU,(36,37));resource.setrlimit(resource.RLIMIT_FSIZE,(CAP,)*2)
    r05=coll/'opg1808-r05-replay-20260907';r06=coll/'opg1808-r06-cert-shards-20260907';r07=coll/'opg1808-r07-adaptive-20260907'
    native=load('native_r10',r05/'exact_replay.py');checker=load('physical_r10',r06/'physical_checker.py')
    sys.path.insert(0,str(r07));import assumption_api
    import closed_sets
    n=req['n'];k=req.get('palette',3);rainbow=req.get('rainbow',True);core=req['core'];ms=req['query_ms'];seed=req['seed']
    if not 1<=ms<=5000 or len(req['instances'])>20:raise ValueError('query budget')
    if core=='cuts':text=closed_sets.formula(n,k,rainbow);corefiles=[here/'closed_sets.py']
    elif core=='supported':
        import supported_superrelation
        text=supported_superrelation.build(n,k,rainbow,True);corefiles=[r07/'supported_superrelation.py',r07/'superrelation.py']
    else:raise ValueError('core')
    s=native.NativeSolver(text,ms);assumption_api.setup(s,n,k,ms,seed)
    extra=req.get('fixed_arcs',[])
    if extra:s.load(''.join(f'(assert e{c}_{u}_{v})\n' for u,v,c in extra))
    base=text+''.join(f'(assert e{c}_{u}_{v})\n' for u,v,c in extra)
    started=time.monotonic();rows=[];used=0
    with a.output.open('x') as f:
        def emit(d):
            nonlocal used
            line=J(d);used+=len(line.encode())
            if used>CAP-8192:raise RuntimeError('output limit')
            f.write(line);f.flush()
        emit({'type':'header','verdict':'candidate_only','created_at':datetime.now(timezone.utc).isoformat(),'request_sha256':H(reqraw),'core':core,
          'base_input_sha256':H(base.encode()),'code_pins':{p.name:H(p.read_bytes()) for p in corefiles+[here/'dual_worker.py',r05/'exact_replay.py',r07/'assumption_api.py',r06/'physical_checker.py']},
          'solver':s.version,'solver_sha256':s.library_sha256,'python':sys.version.split()[0],'query_ms':ms,'seed':seed,'threads':1,'memory_bytes':MEM,
          'cpu_soft_seconds':36,'cpu_hard_seconds':37,'worker_wall_seconds':34,'output_cap_bytes':CAP,'native_unsat_proof':False})
        try:
            for it in req['instances']:
                if time.monotonic()-started+ms/1000>34:break
                word=it.get('word');result=assumption_api.query(s,n,k,word)
                if result['status']=='sat':
                    physical=checker.check(n,k,result['arcs']);result['physical_audit']=physical
                    good=physical['predecessor_pairs_unreachable'] and physical['spanning_cycle_present'] and (not rainbow or physical['no_rainbow_directed_triangle'])
                    result['physical_conditions_pass']=good
                    if not good: result['status']='invalid_sat_model'
                row={'type':'instance','ordinal':it.get('ordinal'),'word':word,'core':core,'query_ms':ms,'seed':seed,
                     'input_sha256':H((base+(closed_sets.word_assertions(word) if word else '')).encode()),**result}
                emit(row);rows.append(row)
            from collections import Counter
            emit({'type':'footer','completed_ordinals':[r['ordinal'] for r in rows],'rows':len(rows),'requested':len(req['instances']),
              'complete_request':len(rows)==len(req['instances']),'statuses':dict(Counter(r['status'] for r in rows)),
              'elapsed_seconds':time.monotonic()-started,'process_cpu_seconds':time.process_time(),'request_sha256':H(reqraw)})
        finally:s.close()
    print(J({'footer_written':True,'rows':len(rows),'log_sha256':H(a.output.read_bytes())}),end='')
if __name__=='__main__':main()
