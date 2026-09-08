"""Restore and audit exact atomic-run receipts; optionally replay one worker.
No native proof verification, external services, repository writes or admission.
"""
import argparse,collections,hashlib,importlib.util,json,resource,subprocess,sys,time
from pathlib import Path
P=Path(__file__).resolve().parent
H=lambda b:hashlib.sha256(b).hexdigest()
J=lambda x:json.dumps(x,sort_keys=True,separators=(',',':'))+'\n'
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def decode(data):
 R=P/'runtime';sys.path.insert(0,str(R/'opg1808-r07-adaptive-20260907'))
 import supported_superrelation
 cuts=load('atomic_cuts',R/'opg1808-r10-dual-replay-20260908/closed_sets.py')
 physical=load('atomic_physical',R/'opg1808-r06-cert-shards-20260907/physical_checker.py')
 for rel,digest in data['pins'].items():
  if H((R/rel).read_bytes())!=digest:raise ValueError('source mismatch: '+rel)
 common=data['worker_constants'];querycounts=collections.Counter();credit=collections.defaultdict(set);objects={}
 for ev in data['events']:
  key=ev['key'];engine=ev['engine'];n=ev['n'];pal=ev['palette'];ms=ev['query_ms'];seed=ev['seed']
  q={k:ev[k] for k in ['engine','n','palette','rainbow','control','source_shard','query_ms','seed']}
  q.update(word_manifest_sha256=data['frozen_words_sha256'],instances=[{'ordinal':r[0],'word':r[1]} for r in ev['rows']])
  rb=J(q).encode();assert H(rb)==ev['request_sha256']
  text=cuts.build(n,pal,ev['rainbow']) if engine=='cuts' else supported_superrelation.build(n,pal,ev['rainbow'],True)
  bsha=H(text.encode());enc=['opg1808-r10-dual-replay-20260908/closed_sets.py'] if engine=='cuts' else ['opg1808-r07-adaptive-20260907/supported_superrelation.py','opg1808-r07-adaptive-20260907/superrelation.py']
  names=enc+['opg1808-r05-replay-20260907/exact_replay.py','opg1808-r06-cert-shards-20260907/physical_checker.py','opg1808-r10-dual-replay-20260908/dual_worker.py']
  hd={k:common[k] for k in ['python','solver','solver_sha256','threads','memory_bytes','cpu_seconds','wall_seconds','file_bytes']}
  hd.update(type='header',verdict='candidate_only',request_sha256=H(rb),base_sha256=bsha,base_path=f'formulas/{engine}-{n}-{pal}-{int(ev["rainbow"])}-{bsha[:16]}.smt2',engine=engine,pins={k:data['pins'][k] for k in names},seed=seed,query_ms=ms)
  rows=[]
  for i,w,status,secs,isha,reason,arcs in ev['rows']:
   extra='' if w is None else ''.join(f'(assert e{c}_{u}_{(u+1)%n})\n' for u,c in enumerate(w))
   assert H((text+extra).encode())==isha
   row={'type':'instance','ordinal':i,'word':w,'status':status,'seconds':secs,'input_sha256':isha,'query_ms':ms,'seed':seed}
   if reason is not None:row['reason']=reason
   if arcs is not None:
    row['arcs']=arcs;row['physical_audit']=physical.check(n,pal,arcs)
    assert row['physical_audit']['bfs_scc_equal'] and row['physical_audit']['predecessor_pairs_unreachable']
    if ev['rainbow']:assert row['physical_audit']['no_rainbow_directed_triangle']
   if ev['control']:assert status==('sat' if not ev['rainbow'] or pal==4 else 'unsat')
   else:
    assert n==12 and pal==3 and ev['rainbow'];querycounts[status]+=1
    if status=='unsat':credit[i].add(engine)
   rows.append(row)
  statuses=dict(collections.Counter(r['status'] for r in rows))
  ft={'type':'footer','request_sha256':H(rb),'processed':len(rows),'processed_ordinals':[r['ordinal'] for r in rows],'complete_request':True,'statuses':statuses,'wall_seconds':ev['footer_wall_seconds'],'cpu_seconds':ev['footer_cpu_seconds'],'verdict':'candidate_only'}
  lb=''.join(J(x) for x in [hd,*rows,ft]).encode();so=J(ft).encode();assert H(lb)==ev['log_sha256']
  rec={'key':key,'command':['python','../../opg1808-r10-dual-replay-20260908/dual_worker.py',f'runs/{key}.request.json',f'runs/{key}.jsonl'],'engine':engine,'query_ms':ms,'seed':seed,'request_sha256':H(rb),'log_sha256':H(lb),'stdout_sha256':H(so),'stderr_sha256':H(b''),'exit_code':0,'external_timeout':False,'elapsed_seconds':ev['elapsed_seconds'],'cpu_user_seconds':ev['cpu_user_seconds'],'cpu_system_seconds':ev['cpu_system_seconds'],'external_wall_seconds':43,'cpu_seconds':[38,39],'memory_bytes':805306368,'per_file_bytes':1048576,'valid_footer':True,'complete_request':True,'processed':len(rows),'statuses':statuses,'verdict':'candidate_only'}
  assert H(J(rec).encode())==ev['receipt_sha256']
  for suf,raw in [('request.json',rb),('jsonl',lb),('stdout.txt',so),('stderr.txt',b''),('receipt.json',J(rec).encode())]:objects[f'{key}.{suf}']=raw
 assert querycounts=={'unsat':45,'unknown':5}
 assert set(credit)==set(data['new_credited_ordinals'])|set(data['crosschecks_completed'])
 assert all(credit[i]=={'cuts','supported'} for i in data['new_credited_ordinals'])
 assert all('supported' in credit[i] for i in data['crosschecks_completed'])
 assert len(data['unresolved_ordinals'])==296 and len(set(data['unresolved_ordinals']))==296
 assert H(J(data['unresolved_ordinals']).encode())==data['unresolved_ordinals_sha256']
 assert data['classes']['normal_unsat']==data['baseline_classes']['normal_unsat']+20
 return objects

def main():
 a=argparse.ArgumentParser();a.add_argument('--restore',type=Path);a.add_argument('--replay');a.add_argument('--output',type=Path);args=a.parse_args()
 resource.setrlimit(resource.RLIMIT_AS,(805306368,)*2);resource.setrlimit(resource.RLIMIT_CPU,(60,61));resource.setrlimit(resource.RLIMIT_FSIZE,(1048576,)*2)
 data=json.loads((P/'execution.json').read_bytes());data['events']=[]
 data['unresolved_ordinals']=json.loads((P/data['unresolved_ordinals_path']).read_bytes())
 for item in data['event_parts']:
  b=(P/item['path']).read_bytes();assert H(b)==item['sha256'] and len(b)==item['bytes']
  ev=json.loads(b);assert len(ev)==item['events'];data['events'].extend(ev)
 objects=decode(data)
 if args.restore:
  args.restore.mkdir(parents=True,exist_ok=True)
  for name,b in objects.items():
   t=args.restore/name
   if t.exists() and t.read_bytes()!=b:raise ValueError('refusing changed destination')
   if not t.exists():t.write_bytes(b)
 if args.replay:
  keys={e['key'] for e in data['events']}
  if args.replay not in keys or args.output is None:raise ValueError('known key and --output required')
  args.output.mkdir(parents=True,exist_ok=False);rq=args.output/'request.json';rq.write_bytes(objects[args.replay+'.request.json'])
  cmd=[sys.executable,str(P/'runtime/opg1808-r10-dual-replay-20260908/dual_worker.py'),str(rq.resolve()),str((args.output/'run.jsonl').resolve())]
  start=time.monotonic()
  with (args.output/'stdout.txt').open('xb') as so,(args.output/'stderr.txt').open('xb') as se:
   try:r=subprocess.run(cmd,stdout=so,stderr=se,timeout=43);rc=r.returncode;expired=False
   except subprocess.TimeoutExpired:rc=None;expired=True
  (args.output/'launch.json').write_text(J({'verdict':'candidate_only','exit_code':rc,'external_timeout':expired,'elapsed_seconds':time.monotonic()-start,'external_wall_seconds':43}))
  print('Fresh solver replay recorded; inspect its footer and physical SAT checks, not historical status assumptions.')
 else:print(J({'verdict':'candidate_only','audit':'byte-input-footer-and-physical-control-checks','classes':data['classes'],'restorable_objects':len(objects),'solver_executed':False}),end='')
if __name__=='__main__':main()
