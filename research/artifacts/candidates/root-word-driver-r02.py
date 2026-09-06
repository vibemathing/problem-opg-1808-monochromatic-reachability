"""Serial, bounded candidate search driver. All outcomes retained in append-only JSONL."""
import itertools,json,subprocess,resource,time,sys,pathlib,datetime
ROOT=pathlib.Path(__file__).parent
N=int(sys.argv[1]);per=float(sys.argv[2]);budget=float(sys.argv[3]);mode=int(sys.argv[4]) if len(sys.argv)>4 else 2
assert 3<=N<=12 and 0<per<=60 and 0<budget<=40 and mode in [0,1,2]
def normal(w):
 d={}
 return tuple(d.setdefault(x,len(d)) for x in w)
def canonical(w):return min(normal(w[i:]+w[:i]) for i in range(len(w)))
# First-occurrence strings avoid generating all colour permutations.
words=set()
def gen(w):
 if len(w)==N: words.add(canonical(w));return
 for x in range(min(3,max(w,default=-1)+2)):gen(w+(x,))
gen(())
words=sorted(''.join(map(str,w)) for w in words)
wf=ROOT/f'words-{N}.json';wf.write_text(json.dumps(words)+'\n')
log=ROOT/f'runs-{N}-mode{mode}.jsonl'
done={}
seen={}
if log.exists():
 for line in log.read_text().splitlines():
  row=json.loads(line)
  seen[row['cycle_word']]=row
  if row.get('status')!='incomplete':done[row['cycle_word']]=row
start=time.monotonic(); processed=0
for word in sorted(words,key=lambda w:(w in seen,w)):
 if word in done:continue
 if time.monotonic()-start+per+1>budget:break
 args=[str(ROOT/'search-r02'),str(N),'3','1',str(mode),str(per),'100000000',word]
 def limits():resource.setrlimit(resource.RLIMIT_AS,(536870912,536870912))
 try:
  p=subprocess.run(args,capture_output=True,text=True,timeout=per+1,preexec_fn=limits)
  assert len(p.stdout.encode())<1048576
  row=json.loads(p.stdout);row['exit_code']=p.returncode
 except subprocess.TimeoutExpired:row={'cycle_word':word,'n':N,'mode':mode,'status':'incomplete','reason':'hard_timeout'}
 row['wall_limit_seconds']=per
 with log.open('a') as f:f.write(json.dumps(row,separators=(',',':'))+'\n')
 processed+=1
 if row['status']!='incomplete':done[word]=row
 if row['status']=='witness':print(json.dumps(row));break
print(json.dumps({'n':N,'mode':mode,'canonical_words':len(words),'completed':len(done),'unresolved':len(words)-len(done),'processed_this_call':processed,'total_complete_nodes':sum(r.get('nodes',0) for r in done.values()),'seconds_this_call':time.monotonic()-start,'witnesses':sum(r['status']=='witness' for r in done.values())}))
