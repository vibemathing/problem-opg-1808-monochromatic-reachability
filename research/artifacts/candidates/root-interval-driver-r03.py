"""Serial bounded candidate-generation driver; negative results require full coverage."""
import argparse, hashlib, json, resource, subprocess, time
from pathlib import Path

def normalize(word):
    names = {}
    return ''.join(str(names.setdefault(c, len(names))) for c in word)

def words(n, k=3):
    def generate(s, largest):
        if len(s) == n:
            if s == min(normalize(s[j:] + s[:j]) for j in range(n)):
                yield s
        else:
            for c in range(min(k-1, largest+1)+1):
                yield from generate(s+str(c), max(c, largest))
    return sorted(generate('0', 0))

def limits():
    resource.setrlimit(resource.RLIMIT_AS, (512*1024*1024,)*2)
    resource.setrlimit(resource.RLIMIT_FSIZE, (1048576,)*2)

def main():
    p=argparse.ArgumentParser()
    p.add_argument('executable');p.add_argument('n',type=int);p.add_argument('log',type=Path)
    p.add_argument('--seconds',type=float,default=0.5)
    p.add_argument('--batch',type=float,default=20)
    p.add_argument('--mode',type=int,choices=[0,1,2],default=2)
    a=p.parse_args(); assert 3<=a.n<=16 and a.seconds>0 and a.batch>0
    names=words(a.n); old=[]
    if a.log.exists(): old=[json.loads(s) for s in a.log.read_text().splitlines() if s.strip()]
    done={r['word']:r for r in old if r['status']=='exhausted_no_witness' and r['mode']==a.mode}
    assert set(done)<=set(names)
    previously={r['word'] for r in old}
    pending=[w for w in names if w not in done]
    pending.sort(key=lambda w:(w in previously,w))
    start=time.monotonic(); attempted=0
    with a.log.open('a') as out:
        for word in pending:
            if time.monotonic()-start>=a.batch: break
            cmd=[a.executable,str(a.n),'3','1',str(a.mode),str(a.seconds),'100000000',word]
            try:
                run=subprocess.run(cmd, capture_output=True, text=True,
                    timeout=a.seconds+3,preexec_fn=limits)
                if len(run.stdout)>1048576 or len(run.stderr)>1048576:
                    raise RuntimeError('output budget exceeded')
                if run.returncode not in (0,2): raise RuntimeError(run.stderr)
                r=json.loads(run.stdout)
                assert r['word']==word and r['n']==a.n and r['mode']==a.mode
                assert (run.returncode==2)==(r['status']=='incomplete')
                r['process_exit']=run.returncode
            except subprocess.TimeoutExpired:
                r={'n':a.n,'word':word,'mode':a.mode,'status':'external_timeout'}
            r['budget_seconds']=a.seconds
            out.write(json.dumps(r,separators=(',',':'))+'\n');out.flush();attempted+=1
            if r['status']=='exhausted_no_witness':done[word]=r
            if r['status']=='witness': print(json.dumps(r));break
    print(json.dumps({'n':a.n,'mode':a.mode,'words':len(names),'complete':len(done),
        'attempted':attempted,'remaining_count':sum(w not in done for w in names),
        'remaining_sample':[w for w in names if w not in done][:8],
        'completed_nodes':sum(r['nodes'] for r in done.values()),
        'word_list_sha256':hashlib.sha256(('\n'.join(names)+'\n').encode()).hexdigest(),
        'batch_seconds':time.monotonic()-start}))
if __name__=='__main__':main()
