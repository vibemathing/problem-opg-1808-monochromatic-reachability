"""Bounded candidate SMT experiment using an existing native Z3, no installation."""
import argparse, ctypes as C, ctypes.util, hashlib, itertools, json, time
from pathlib import Path

def smt_text(n, seconds, stars=True, incident=False, palette=3, rainbow=True, positive=True):
    assert 2<=palette<=4 and (not stars or palette==3)
    arc=lambda u,v,c:f'a_{u}_{v}_{c}'
    rel=lambda u,v,c:f'r_{u}_{v}_{c}'
    lines=['(set-logic QF_UF)']
    emit=lambda s:lines.append('(assert '+s+')')
    for u in range(n):
        for v in range(n):
            if u==v:continue
            for c in range(palette):
                lines.extend([f'(declare-const {arc(u,v,c)} Bool)',f'(declare-const {rel(u,v,c)} Bool)'])
    for u in range(n):
        for v in range(u+1,n):
            opts=[arc(x,y,c) for x,y in [(u,v),(v,u)] for c in range(palette)]
            emit('(or '+' '.join(opts)+')')
            for a,b in itertools.combinations(opts,2):emit(f'(or (not {a}) (not {b}))')
    for c in range(palette):
        for u in range(n):
            for v in range(n):
                if u==v:continue
                emit(f'(=> {arc(u,v,c)} {rel(u,v,c)})')
                for w in range(n):
                    if w!=u and w!=v:emit(f'(=> (and {rel(u,v,c)} {rel(v,w,c)}) {rel(u,w,c)})')
    for u in range(n):
        emit('(or '+' '.join(arc(u,(u+1)%n,c) for c in range(palette))+')')
        for c in range(palette):emit('(not '+rel(u,(u-1)%n,c)+')')
        for v in range(n):
            if positive and v!=u and v!=(u-1)%n:emit('(or '+' '.join(rel(u,v,c) for c in range(palette))+')')
    for a,b,c in (itertools.combinations(range(n),3) if rainbow else []):
        for cyc in [(a,b,c),(a,c,b)]:
            for colors in itertools.permutations(range(palette),3):
                emit('(not (and '+' '.join(arc(cyc[j],cyc[(j+1)%3],colors[j]) for j in range(3))+'))')
    emit(arc(0,1,0))
    if stars:
        for u in range(n):
            for c in range(palette):
                for direction in [0,1]:
                    opts=[arc(v,u,d) if direction else arc(u,v,d) for v in range(n) if v!=u for d in range(palette) if d!=c]
                    emit('(or '+' '.join(opts)+')')
    if incident:
        for u in range(n):
            for c in range(palette):emit('(or '+' '.join(arc(x,y,c) for v in range(n) if u!=v for x,y in [(u,v),(v,u)])+')')
    return '\n'.join(lines)+'\n'

def main():
    p=argparse.ArgumentParser();p.add_argument('n',type=int);p.add_argument('seconds',type=float);p.add_argument('output_prefix',type=Path);p.add_argument('--word');p.add_argument('--no-stars',action='store_true');p.add_argument('--incident',action='store_true');a=p.parse_args()
    assert 3<=a.n<=16 and 0<a.seconds<=40
    text=smt_text(a.n,a.seconds,not a.no_stars,a.incident)
    if a.word:
        assert len(a.word)==a.n and set(a.word)<=set('012')
        text+=''.join(f'(assert a_{u}_{(u+1)%a.n}_{c})\n' for u,c in enumerate(a.word))
    a.output_prefix.with_suffix('.smt2').write_text(text)
    lib=C.CDLL(ctypes.util.find_library('z3'))
    def fn(name,ret,args):
        f=getattr(lib,name);f.restype=ret;f.argtypes=args;return f
    P=C.c_void_p;I=C.c_uint;S=C.c_char_p
    version=[I() for _ in range(4)];fn('Z3_get_version',None,[C.POINTER(I)]*4)(*[C.byref(v) for v in version])
    cfg=fn('Z3_mk_config',P,[])();fn('Z3_set_param_value',None,[P,S,S])(cfg,b'model',b'true')
    ctx=fn('Z3_mk_context',P,[P])(cfg);fn('Z3_del_config',None,[P])(cfg)
    try:
        solver=fn('Z3_mk_solver',P,[P])(ctx);fn('Z3_solver_inc_ref',None,[P,P])(ctx,solver)
        params=fn('Z3_mk_params',P,[P])(ctx);fn('Z3_params_inc_ref',None,[P,P])(ctx,params)
        symbol=fn('Z3_mk_string_symbol',P,[P,S]);setp=fn('Z3_params_set_uint',None,[P,P,P,I])
        for key,val in [('timeout',int(a.seconds*1000)),('random_seed',0),('threads',1)]:setp(ctx,params,symbol(ctx,key.encode()),val)
        fn('Z3_solver_set_params',None,[P,P,P])(ctx,solver,params)
        fn('Z3_solver_from_string',None,[P,P,S])(ctx,solver,text.encode());t=time.monotonic()
        result=fn('Z3_solver_check',C.c_int,[P,P])(ctx,solver)
        report={'verdict':'candidate_only','n':a.n,'word':a.word,'stars':not a.no_stars,'all_three_incident':a.incident,'native_z3':'.'.join(str(v.value) for v in version),'timeout_seconds':a.seconds,'status':{1:'sat',-1:'unsat',0:'unknown'}[result],'elapsed_seconds':time.monotonic()-t,'input_sha256':hashlib.sha256(text.encode()).hexdigest(),'arcs':[]}
        if not result:report['reason']=fn('Z3_solver_get_reason_unknown',S,[P,P])(ctx,solver).decode()
        if result==1:
            model=fn('Z3_solver_get_model',P,[P,P])(ctx,solver);sort=fn('Z3_mk_bool_sort',P,[P])(ctx)
            const=fn('Z3_mk_const',P,[P,P,P]);evaluate=fn('Z3_model_eval',C.c_bool,[P,P,P,C.c_bool,C.POINTER(P)]);truth=fn('Z3_get_bool_value',C.c_int,[P,P])
            for u in range(a.n):
                for v in range(a.n):
                    if u==v:continue
                    for c in range(3):
                        expr=const(ctx,symbol(ctx,f'a_{u}_{v}_{c}'.encode()),sort);val=P()
                        assert evaluate(ctx,model,expr,True,C.byref(val))
                        if truth(ctx,val)==1:report['arcs'].append([u,v,c])
        a.output_prefix.with_suffix('.json').write_text(json.dumps(report,separators=(',',':'))+'\n');print(json.dumps(report))
    finally:fn('Z3_del_context',None,[P])(ctx)
if __name__=='__main__':main()
