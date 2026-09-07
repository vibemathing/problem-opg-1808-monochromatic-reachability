"""Fresh bounded replay coordinator. No old logs are reused or reconstructed."""
import argparse,json,os,resource,signal,subprocess,sys,time
from pathlib import Path
import exact_replay as r
HERE=Path(__file__).resolve().parent
PINS={'exact_replay.py':'cd4ce25fc30127268397db6d1720bf235b8f6cec85c205f6284b4ebf3593931a','direct_enumeration.cpp':'a68eda12d2a6435bf61dd18de757a9478e27e133c1227e92a06f91e794170cf8','adversarial_audit.py':'c98d2e436dab814220a60f63c4ea298dce9b9774a840f414d5edf4fd2f53e42b'}
def main():
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--legacy',type=Path,required=True);p.add_argument('--total-seconds',type=int,default=600);a=p.parse_args()
 if not 30<=a.total_seconds<=900 or a.out.exists():raise ValueError('fresh output and bounded time required')
 if sys.version_info[:3]!=(3,13,5):raise RuntimeError('Python pin')
 for name,h in PINS.items():
  if r.digest((HERE/name).read_bytes())!=h:raise RuntimeError('source pin: '+name)
 if r.digest(a.legacy.read_bytes())!='a2381c88441f864be5d554ebce3161c74a4c546717918cbbce204db02f4aeb06':raise RuntimeError('legacy pin')
 resource.setrlimit(resource.RLIMIT_AS,(r.MEMORY_BYTES,)*2);resource.setrlimit(resource.RLIMIT_FSIZE,(1048576,)*2)
 start=time.monotonic();deadline=start+a.total_seconds;a.out.mkdir(parents=True);events=[]
 result={'verdict':'candidate_only','status':'NONTERMINAL_CHECKPOINT','total_timeout_seconds':a.total_seconds,'memory_bytes':r.MEMORY_BYTES,'max_file_bytes':1048576,'max_total_output_bytes':5242880,'python':sys.version.split()[0],'seed':r.SEED,'threads':1,'events':events}
 def save():
  result['elapsed_seconds']=time.monotonic()-start;result['unresolved_words']={}
  for n in range(3,12):
   wp=a.out/f'words-{n}.txt';lp=a.out/f'exact-log-{n}.jsonl';names=wp.read_text().splitlines() if wp.exists() else r.restricted_growth_words(n)
   rows=[json.loads(s) for s in lp.read_text().splitlines()] if lp.exists() else [];done={x['word'] for x in rows if x.get('status')=='unsat'}
   result['unresolved_words'][str(n)]=sorted(set(names)-done)
  (a.out/'run.json').write_text(r.dump(result)+'\n')
 def limits():
  resource.setrlimit(resource.RLIMIT_CPU,(38,39));resource.setrlimit(resource.RLIMIT_AS,(r.MEMORY_BYTES,)*2);resource.setrlimit(resource.RLIMIT_FSIZE,(1048576,)*2)
 def execute(label,args,cap):
  left=deadline-time.monotonic()
  if left<1:raise TimeoutError('global budget')
  ev={'operation':label,'wall_limit_seconds':min(cap,left)};events.append(ev);beg=time.monotonic()
  try:x=subprocess.run(args,cwd=HERE,capture_output=True,text=True,timeout=min(cap,left),preexec_fn=limits,env={**os.environ,'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1','PYTHONDONTWRITEBYTECODE':'1'})
  except subprocess.TimeoutExpired:ev['status']='timeout';raise
  ev.update({'exit_code':x.returncode,'seconds':time.monotonic()-beg,'stdout_sha256':r.digest(x.stdout.encode())})
  if x.returncode or len(x.stdout.encode())+len(x.stderr.encode())>1048576:raise RuntimeError('child failure: '+label)
  if sum(f.stat().st_size for f in a.out.rglob('*') if f.is_file())>5242880:raise RuntimeError('total output cap')
  return x.stdout
 def alarm(signum,frame):raise TimeoutError('hard global deadline')
 signal.signal(signal.SIGALRM,alarm);signal.setitimer(signal.ITIMER_REAL,a.total_seconds)
 try:
  print(execute('word_sets',[sys.executable,str(HERE/'exact_replay.py'),'words','--out',str(a.out)],40),flush=True)
  execute('controls',[sys.executable,str(HERE/'exact_replay.py'),'controls','--out',str(a.out)],25)
  controls=json.loads((a.out/'controls.json').read_text())
  if any(x['solver_version']!='4.13.3.0' or x['solver_library_sha256']!='7accc397d4ac387468b09489bdaff9d82bfac4ca6a7e339b8fbb2167edf9c1c0' for x in controls):raise RuntimeError('solver pin')
  for n in range(3,12):
   previous=-1
   while True:
    text=execute('exact_batch_'+str(n),[sys.executable,str(HERE/'exact_replay.py'),'batch','--n',str(n),'--seconds','0.5','--total-seconds','20','--out',str(a.out)],35);s=json.loads(text);print(r.dump(s),flush=True)
    if not s['unresolved_count']:break
    if s['completed_unsat']<=previous:raise RuntimeError('no progress')
    previous=s['completed_unsat']
  compiler=execute('compiler_version',['g++','--version'],5).splitlines()[0]
  if compiler!='g++ (Debian 14.2.0-19) 14.2.0':raise RuntimeError('compiler pin')
  binary=a.out/'direct_enumeration';execute('compile',['g++','-std=c++17','-O3',str(HERE/'direct_enumeration.cpp'),'-o',str(binary)],30);direct=[]
  for n in range(1,6):
   x=json.loads(execute('direct_n'+str(n),[str(binary),str(n),'25'],28))
   if x['status']!='exhausted_no_counterexample':raise RuntimeError('direct mismatch')
   x['process_exit']=0;direct.append(x)
  (a.out/'direct-enumeration.json').write_text(r.dump({'verdict':'candidate_only','compiler':compiler,'flags':['-std=c++17','-O3'],'code_sha256':PINS['direct_enumeration.cpp'],'records':direct})+'\n')
  execute('adversarial',[sys.executable,str(HERE/'adversarial_audit.py'),str(a.legacy),str(a.out/'adversarial-audit.json')],40);result['status']='RESULT_CANDIDATE_READY'
 except (RuntimeError,TimeoutError,subprocess.TimeoutExpired) as e:result['failure_class']=type(e).__name__
 finally:signal.setitimer(signal.ITIMER_REAL,0);save()
 print(r.dump({'status':result['status'],'elapsed_seconds':result['elapsed_seconds'],'unresolved_count':sum(len(x) for x in result['unresolved_words'].values())}),flush=True)
 return 0 if result['status']=='RESULT_CANDIDATE_READY' else 2
if __name__=='__main__':raise SystemExit(main())
