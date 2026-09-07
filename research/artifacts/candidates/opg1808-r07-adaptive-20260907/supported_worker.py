"""Bounded R07 worker: immutable header/rows/footer, physical BFS/SCC on SAT.
The transport binding is reused, but the formula is not R05/R06 Floyd encoding.
"""
from __future__ import annotations
import argparse,ctypes as C,hashlib,importlib.util,json,resource,signal,sys,time
from pathlib import Path
from superrelation import word_assertions
from supported_superrelation import build
from assumption_api import setup,query
H=lambda b:hashlib.sha256(b).hexdigest()
D=lambda x:json.dumps(x,sort_keys=True,separators=(',',':'))+'\n'
R05_SHA='cd4ce25fc30127268397db6d1720bf235b8f6cec85c205f6284b4ebf3593931a'
CHECK_SHA='80750940f9644eb40ab8b358df91df8256ecdb80af79d244cd817f91cda8f41a'
LIB_SHA='7accc397d4ac387468b09489bdaff9d82bfac4ca6a7e339b8fbb2167edf9c1c0'
def module(path,name,digest):
    if H(path.read_bytes())!=digest:raise ValueError('source pin')
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def run(args):
    resource.setrlimit(resource.RLIMIT_AS,(805306368,)*2)
    resource.setrlimit(resource.RLIMIT_CPU,(43,44))
    resource.setrlimit(resource.RLIMIT_FSIZE,(1048576,)*2)
    def alarm(s,f):raise TimeoutError('worker wall cap')
    signal.signal(signal.SIGALRM,alarm);signal.setitimer(signal.ITIMER_REAL,45)
    req=json.loads(args.request.read_bytes())
    if not 0<req['query_ms']<=10000 or len(req['instances'])>256:raise ValueError('worker budget')
    n=req['n'];palette=req.get('palette',3)
    core=module(args.binding,'r05binding',R05_SHA);core.SEED=req['seed']
    check=module(args.checker,'r06physical',CHECK_SHA).check
    text=build(n,palette,req.get('rainbow',True),req.get('positive',True))
    solver=core.NativeSolver(text,req['query_ms'])
    setup(solver,n,palette,req['query_ms'],req['seed'])
    if solver.version!='4.13.3.0' or solver.library_sha256!=LIB_SHA or sys.version.split()[0]!='3.13.5':raise ValueError('runtime pin')
    header={'type':'header','request_sha256':H(args.request.read_bytes()),'base_input_sha256':H(text.encode()),'n':n,'palette':palette,
        'rainbow':req.get('rainbow',True),'positive':req.get('positive',True),'seed':req['seed'],'query_ms':req['query_ms'],
        'binding_sha256':R05_SHA,'checker_sha256':CHECK_SHA,'formula_code_sha256':H((Path(__file__).parent/'superrelation.py').read_bytes()),'support_code_sha256':H((Path(__file__).parent/'supported_superrelation.py').read_bytes()),
        'worker_sha256':H(Path(__file__).read_bytes()),'python':'3.13.5','solver':solver.version,'solver_sha256':solver.library_sha256,
        'memory_bytes':805306368,'cpu_soft_seconds':43,'cpu_hard_seconds':44,'wall_seconds':45,'max_file_bytes':1048576,'threads':1,'verdict':'candidate_only','query_interface':'check_assumptions','assumption_api_sha256':H((Path(__file__).parent/'assumption_api.py').read_bytes())}
    count=0;statuses={};begin=time.monotonic()
    with args.log.open('x') as out:
        out.write(D(header));out.flush()
        try:
            for item in req['instances']:
                word=item.get('word');extra=item.get('extra','')
                if time.monotonic()-begin+req['query_ms']/1000>req.get('batch_seconds',38):break
                if extra: raise ValueError('assumption worker rejects unnamed extra constraints')
                ans=query(solver,n,palette,word)
                ans.pop('physical_audit',None)
                ans.update(type='instance',ordinal=item.get('ordinal'),word=word,query_ms=req['query_ms'],seed=req['seed'],
                    instance_sha256=H((text+(word_assertions(word) if word else '')+extra).encode()))
                if ans['status']=='sat':
                    ans['physical']=check(n,palette,ans['arcs'])
                    p=ans['physical']
                    if not p['predecessor_pairs_unreachable'] or not p['spanning_cycle_present'] or (req.get('rainbow',True) and not p['no_rainbow_directed_triangle']):
                        ans['status']='invalid_sat_model'
                out.write(D(ans));out.flush();count+=1;statuses[ans['status']]=statuses.get(ans['status'],0)+1
                if ans['status']=='invalid_sat_model' or (ans['status']=='sat' and n==12 and palette==3 and req.get('rainbow',True)):break
            out.write(D({'type':'footer','rows':count,'statuses':statuses,'complete_request':count==len(req['instances'])}));out.flush()
        finally:solver.close()
    signal.setitimer(signal.ITIMER_REAL,0)
    print(D({'rows':count,'statuses':statuses}),end='')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--request',type=Path,required=True);p.add_argument('--log',type=Path,required=True)
    p.add_argument('--binding',type=Path,required=True);p.add_argument('--checker',type=Path,required=True);run(p.parse_args())
