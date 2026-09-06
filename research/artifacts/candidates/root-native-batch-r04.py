"""Serial incremental SMT word coverage. Only explicit unsat counts as complete."""
import argparse, ctypes as C, ctypes.util, importlib.util, json, hashlib, time
from pathlib import Path
HERE=Path(__file__).resolve().parent

def module(name,file):
    spec=importlib.util.spec_from_file_location(name,file);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

class Solver:
    def __init__(self,n,seconds,stars,palette=3,rainbow=True,positive=True):
        self.palette=palette
        self.n=n;self.lib=C.CDLL(ctypes.util.find_library('z3'));self.P=C.c_void_p;self.I=C.c_uint;self.S=C.c_char_p
        self.version=[self.I() for _ in range(4)];self.fn('Z3_get_version',None,[C.POINTER(self.I)]*4)(*[C.byref(v) for v in self.version])
        cfg=self.fn('Z3_mk_config',self.P,[])();self.ctx=self.fn('Z3_mk_context',self.P,[self.P])(cfg);self.fn('Z3_del_config',None,[self.P])(cfg)
        self.solver=self.fn('Z3_mk_solver',self.P,[self.P])(self.ctx);self.fn('Z3_solver_inc_ref',None,[self.P,self.P])(self.ctx,self.solver)
        params=self.fn('Z3_mk_params',self.P,[self.P])(self.ctx);self.fn('Z3_params_inc_ref',None,[self.P,self.P])(self.ctx,params)
        sym=self.fn('Z3_mk_string_symbol',self.P,[self.P,self.S]);setp=self.fn('Z3_params_set_uint',None,[self.P,self.P,self.P,self.I])
        for key,val in [('timeout',int(seconds*1000)),('random_seed',0),('threads',1)]:setp(self.ctx,params,sym(self.ctx,key.encode()),val)
        self.fn('Z3_solver_set_params',None,[self.P,self.P,self.P])(self.ctx,self.solver,params)
        self.text=module('encoding',HERE/'root-native-smt-r04.py').smt_text(n,seconds,stars,False,palette,rainbow,positive)
        self.fn('Z3_solver_from_string',None,[self.P,self.P,self.S])(self.ctx,self.solver,self.text.encode())
        sort=self.fn('Z3_mk_bool_sort',self.P,[self.P])(self.ctx);const=self.fn('Z3_mk_const',self.P,[self.P,self.P,self.P])
        self.arcs={(u,v,c):const(self.ctx,sym(self.ctx,f'a_{u}_{v}_{c}'.encode()),sort) for u in range(n) for v in range(n) if u!=v for c in range(palette)}
    def fn(self,name,ret,args):
        f=getattr(self.lib,name);f.restype=ret;f.argtypes=args;return f
    def solve(self,word):
        P=self.P;I=self.I;ctx=self.ctx;solver=self.solver
        self.fn('Z3_solver_push',None,[P,P])(ctx,solver)
        assert len(word)==self.n and set(word)<=set(str(c) for c in range(self.palette))
        for u,c in enumerate(word):self.fn('Z3_solver_assert',None,[P,P,P])(ctx,solver,self.arcs[u,(u+1)%self.n,int(c)])
        t=time.monotonic();status=self.fn('Z3_solver_check',C.c_int,[P,P])(ctx,solver)
        result={'n':self.n,'word':word,'status':{1:'sat',-1:'unsat',0:'unknown'}[status],'seconds':time.monotonic()-t}
        if status==0:result['reason']=self.fn('Z3_solver_get_reason_unknown',self.S,[P,P])(ctx,solver).decode()
        if status==1:
            model=self.fn('Z3_solver_get_model',P,[P,P])(ctx,solver);ev=self.fn('Z3_model_eval',C.c_bool,[P,P,P,C.c_bool,C.POINTER(P)]);val=P();bv=self.fn('Z3_get_bool_value',C.c_int,[P,P])
            result['arcs']=[]
            for q,expr in self.arcs.items():
                assert ev(ctx,model,expr,True,C.byref(val))
                if bv(ctx,val)==1:result['arcs'].append(list(q))
            result['physical_audit']=audit(self.n,result['arcs'],self.palette)
        self.fn('Z3_solver_pop',None,[P,P,I])(ctx,solver,1)
        return result
    def close(self):self.fn('Z3_del_context',None,[self.P])(self.ctx)

def audit(n,arcs,palette=3):
    edges={};rows=[[[False]*n for _ in range(n)] for c in range(palette)]
    for u,v,c in arcs:
        assert u!=v and 0<=u<n and 0<=v<n and 0<=c<palette and (u,v) not in edges and (v,u) not in edges
        edges[u,v]=c;rows[c][u][v]=True
    assert len(arcs)==n*(n-1)//2
    rainbow=[]
    for u in range(n):
        for v in range(u+1,n):
            for w in range(v+1,n):
                for cyc in [(u,v,w),(u,w,v)]:
                    keys=[(cyc[j],cyc[(j+1)%3]) for j in range(3)]
                    if all(e in edges for e in keys) and len({edges[e] for e in keys})==3:rainbow.append(list(cyc))
    missing=[]
    for u in range(n):
        total={u}
        for c in range(palette):
            seen={u};todo=[u]
            while todo:
                x=todo.pop()
                for y in range(n):
                    if rows[c][x][y] and y not in seen:seen.add(y);todo.append(y)
            total|=seen
        missing.append(sorted(set(range(n))-total))
    return {'rainbow_triangles':rainbow,'unreachable_targets':missing,'is_coloured_counterexample':not rainbow and all(missing),'is_root_counterexample':palette<=3 and not rainbow and all(missing)}

def main():
    p=argparse.ArgumentParser();p.add_argument('n',type=int);p.add_argument('log',type=Path);p.add_argument('--driver',type=Path,required=True);p.add_argument('--seconds',type=float,default=1);p.add_argument('--batch',type=float,default=20);p.add_argument('--no-stars',action='store_true');a=p.parse_args()
    assert 3<=a.n<=16 and a.seconds>0 and a.batch>0
    words=module('words',a.driver).words(a.n)
    old=[json.loads(l) for l in a.log.read_text().splitlines()] if a.log.exists() else []
    assert all(r['n']==a.n and r['stars']==(not a.no_stars) for r in old)
    done={r['word']:r for r in old if r['status']=='unsat'};assert set(done)<=set(words)
    attempted_before={r['word'] for r in old};remaining=[w for w in words if w not in done];remaining.sort(key=lambda w:(w in attempted_before,w))
    solver=Solver(a.n,a.seconds,not a.no_stars)
    digest=hashlib.sha256(solver.text.encode()).hexdigest()
    assert all(r['base_smt_sha256']==digest for r in old), 'cannot mix distinct encodings in one log'
    assert all(r['native_z3']=='.'.join(str(v.value) for v in solver.version) for r in old), 'cannot mix solver versions'
    t=time.monotonic();count=0
    try:
        with a.log.open('a') as f:
            for w in remaining:
                if time.monotonic()-t>a.batch:break
                r=solver.solve(w);r.update({'timeout_seconds':a.seconds,'stars':not a.no_stars,'native_z3':'.'.join(str(v.value) for v in solver.version),'base_smt_sha256':hashlib.sha256(solver.text.encode()).hexdigest(),'verdict':'candidate_only'})
                f.write(json.dumps(r,separators=(',',':'))+'\n');f.flush();count+=1
                if r['status']=='unsat':done[w]=r
                if r['status']=='sat':print(json.dumps(r));break
        print(json.dumps({'n':a.n,'words':len(words),'complete':len(done),'attempted':count,'remaining':len(words)-len(done),'sum_complete_seconds':sum(r['seconds'] for r in done.values()),'batch_seconds':time.monotonic()-t,'word_sha256':hashlib.sha256(('\n'.join(words)+'\n').encode()).hexdigest()}))
    finally:solver.close()
if __name__=='__main__':main()
