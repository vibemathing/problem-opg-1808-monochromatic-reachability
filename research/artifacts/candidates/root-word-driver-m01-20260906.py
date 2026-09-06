"""Bounded serial reproduction; incomplete/error outputs never discharge a word."""
import datetime, json, pathlib, resource, subprocess, sys, time
ROOT=pathlib.Path(__file__).parent
n=int(sys.argv[1]); seconds=float(sys.argv[2]); budget=float(sys.argv[3])
if not (3<=n<=12 and 0<seconds<=60 and 0<budget<=40):raise ValueError('bounds')
def normal(w):
 d={}; return tuple(d.setdefault(x,len(d)) for x in w)
def canonical(w):return min(normal(w[i:]+w[:i]) for i in range(len(w)))
words=set()
def gen(w):
 if len(w)==n:words.add(canonical(w));return
 for c in range(min(3,max(w,default=-1)+2)):gen(w+(c,))
gen(())
words=sorted(''.join(map(str,w)) for w in words)
(ROOT/f'words-{n}.json').write_text(json.dumps(words)+'\n')
log=ROOT/f'runs-{n}.jsonl';done={};seen={}
if log.exists():
 for line in log.read_text().splitlines():
  r=json.loads(line);seen[r['cycle_word']]=r
  if r['status'] in ('exhausted_no_witness','witness') and r.get('exit_code')==0:done[r['cycle_word']]=r
start=time.monotonic();count=0
for word in sorted(words,key=lambda w:(w in seen,w)):
 if word in done:continue
 if time.monotonic()-start+seconds+1>budget:break
 def limits():resource.setrlimit(resource.RLIMIT_AS,(536870912,536870912))
 try:
  x=subprocess.run([str(ROOT/'search-r03'),str(n),'3','1','3',str(seconds),'20000000',word],capture_output=True,text=True,timeout=seconds+1,preexec_fn=limits)
  if len(x.stdout.encode())>1048576:raise ValueError('output bound')
  r=json.loads(x.stdout)
  if r['cycle_word']!=word or r['n']!=n:raise ValueError('binding mismatch')
  if r['status'] not in ('exhausted_no_witness','witness','incomplete'):raise ValueError('unknown status')
  if x.returncode != (2 if r['status']=='incomplete' else 0):raise ValueError('exit/status mismatch')
  r['exit_code']=x.returncode
 except subprocess.TimeoutExpired:r={'cycle_word':word,'n':n,'status':'incomplete','reason':'hard_timeout'}
 r['wall_limit_seconds']=seconds
 with log.open('a') as f:f.write(json.dumps(r,separators=(',',':'))+'\n')
 count+=1
 if r['status'] in ('exhausted_no_witness','witness') and r.get('exit_code')==0:done[word]=r
 if r['status']=='witness':print(json.dumps(r));break
print(json.dumps({'n':n,'representatives':len(words),'complete':len(done),'unresolved':len(words)-len(done),'nodes_sum':sum(r['nodes'] for r in done.values()),'processed':count,'elapsed':time.monotonic()-start,'witnesses':sum(r['status']=='witness' for r in done.values())}))
