"""Direct check_assumptions interface; does not depend on :named parsing.
Core lists are diagnostic until rechecked. Only the full word query result is
credited by the worker. No bare core, including [], proves a global claim.
"""
import ctypes as C,time

def setup(s,n,palette,ms,seed):
 P,U,ctx=s.P,s.U,s.ctx
 sort=s.fn('Z3_mk_bool_sort',P,[P])(ctx);mk=s.fn('Z3_mk_const',P,[P,P,P])
 s.arc_ast={(u,v,c):mk(ctx,s.symbol(ctx,f'e{c}_{u}_{v}'.encode()),sort) for u in range(n) for v in range(n) if u!=v for c in range(palette)}
 params=s.fn('Z3_mk_params',P,[P])(ctx);s.fn('Z3_params_inc_ref',None,[P,P])(ctx,params)
 for k,v in [('timeout',ms),('random_seed',seed),('threads',1)]:s.fn('Z3_params_set_uint',None,[P,P,P,U])(ctx,params,s.symbol(ctx,k.encode()),v)
 s.fn('Z3_params_set_bool',None,[P,P,P,C.c_bool])(ctx,params,s.symbol(ctx,b'unsat_core'),True)
 s.fn('Z3_solver_set_params',None,[P,P,P])(ctx,s.solver,params)
 s.fn('Z3_params_dec_ref',None,[P,P])(ctx,params)

def query(s,n,palette,word=None,positions=None):
 P,U,ctx=s.P,s.U,s.ctx
 ids=list(range(n)) if positions is None else positions
 if word is None:ids=[]
 if word is not None and (len(word)!=n or any(not 0<=int(c)<palette for c in word)):raise ValueError('word')
 arr=(P*len(ids))(*[s.arc_ast[i,(i+1)%n,int(word[i])] for i in ids]);t=time.monotonic()
 result=s.fn('Z3_solver_check_assumptions',C.c_int,[P,P,U,C.POINTER(P)])(ctx,s.solver,len(ids),arr)
 ans={'status':{1:'sat',-1:'unsat',0:'unknown'}[result],'seconds':time.monotonic()-t}
 if result==0:ans['reason']=s.fn('Z3_solver_get_reason_unknown',s.S,[P,P])(ctx,s.solver).decode()
 if result==-1:
  vec=s.fn('Z3_solver_get_unsat_core',P,[P,P])(ctx,s.solver);length=s.fn('Z3_ast_vector_size',U,[P,P])(ctx,vec)
  names={f'e{word[i]}_{i}_{(i+1)%n}':i for i in ids} if word else {}
  out=[]
  for k in range(length):
   ast=s.fn('Z3_ast_vector_get',P,[P,P,U])(ctx,vec,k);name=s.fn('Z3_ast_to_string',s.S,[P,P])(ctx,ast).decode()
   if name not in names:raise ValueError('foreign unsat core literal')
   out.append(names[name])
  ans['diagnostic_core_positions']=sorted(out)
 if result==1:
  model=s.fn('Z3_solver_get_model',P,[P,P])(ctx,s.solver);s.fn('Z3_model_inc_ref',None,[P,P])(ctx,model)
  evaluate=s.fn('Z3_model_eval',C.c_bool,[P,P,P,C.c_bool,C.POINTER(P)]);truth=s.fn('Z3_get_bool_value',C.c_int,[P,P]);arcs=[]
  for triple,expr in s.arc_ast.items():
   value=P()
   if not evaluate(ctx,model,expr,True,C.byref(value)):raise ValueError('failed model evaluation')
   if truth(ctx,value)==1:arcs.append(list(triple))
  s.fn('Z3_model_dec_ref',None,[P,P])(ctx,model);ans['arcs']=arcs
 return ans
