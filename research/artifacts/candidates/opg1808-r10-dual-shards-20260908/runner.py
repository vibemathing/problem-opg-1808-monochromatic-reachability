"""Parent receipts, no abnormal or footer-less output is credited."""
from pathlib import Path
import json,hashlib,subprocess,time,sys,collections,os,signal
H=lambda b:hashlib.sha256(b).hexdigest()
J=lambda x:json.dumps(x,sort_keys=True,separators=(',',':'))+'\n'
HERE=Path(__file__).resolve().parent

def run(req,tag,out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    rp=out/(tag+'.request.json');lp=out/(tag+'.log.jsonl');ep=out/(tag+'.exit.json')
    if rp.exists() or lp.exists() or ep.exists():raise FileExistsError(tag)
    raw=J(req).encode();rp.write_bytes(raw);t=time.monotonic();code=None;timeout=False
    cmd=[sys.executable,str(HERE/'dual_worker.py'),str(rp),str(lp)]
    env=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
    try:
        r=subprocess.run(cmd,capture_output=True,timeout=40,env=env);code=r.returncode;stdout=r.stdout;stderr=r.stderr
    except subprocess.TimeoutExpired as e:timeout=True;stdout=e.stdout or b'';stderr=e.stderr or b''
    log=lp.read_bytes() if lp.exists() else b'';entries=[]
    try:entries=[json.loads(l) for l in log.splitlines()]
    except (ValueError,UnicodeError):pass
    rows=[r for r in entries if r.get('type')=='instance'];ids=[x.get('ordinal') for x in req['instances']]
    valid=bool(code==0 and len(entries)>=2 and entries[0].get('type')=='header' and entries[-1].get('type')=='footer'
       and entries[-1]['request_sha256']==H(raw) and entries[-1]['rows']==len(rows)
       and [r['ordinal'] for r in rows]==ids[:len(rows)])
    receipt={'verdict':'candidate_only','command':['python','dual_worker.py',rp.name,lp.name],'exit_code':code,'external_timeout':timeout,
      'hard_wall_seconds':40,'elapsed_seconds':time.monotonic()-t,'request_sha256':H(raw),'raw_log_sha256':H(log),
      'stdout_sha256':H(stdout),'stderr_sha256':H(stderr),'stderr_empty':not stderr,'valid_footer_and_exit':valid,
      'processed':len(rows),'requested_ordinals':ids,'statuses':dict(collections.Counter(r['status'] for r in rows)),
      'unprocessed_ordinals':ids[len(rows):],'eligible_unsat_ordinals':[r['ordinal'] for r in rows if valid and r['status']=='unsat']}
    ep.write_text(J(receipt));print(J({'tag':tag,**{k:receipt[k] for k in ('exit_code','valid_footer_and_exit','statuses','elapsed_seconds')}}),flush=True)
    return receipt,rows
if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--mode',choices=['controls','priority'],required=True);a=p.parse_args();t=time.monotonic();events=[]
    r06=HERE.parent/'opg1808-r06-cert-shards-20260907';r07=HERE.parent/'opg1808-r07-adaptive-20260907'
    if a.mode=='controls':
        for core in ['cuts','supported']:
            for n,k,ban,w,expected in [(3,3,False,'012','sat'),(3,3,True,'012','unsat'),(6,4,True,None,'sat')]:
                req={'n':n,'palette':k,'rainbow':ban,'core':core,'query_ms':5000,'seed':167,'instances':[{'ordinal':None,'word':w}]}
                ev,rows=run(req,f'{core}-{n}-{int(ban)}',HERE/'controls');events.append(ev)
                assert ev['valid_footer_and_exit'] and rows[0]['status']==expected,(core,n,rows)
    else:
        words=(r06/'words-12.txt').read_text().splitlines();shard=json.loads((r07/'next-shard-manifest.json').read_text())['shards'][0]
        assert words[314]=='000001010221';assert H((''.join(words[i]+'\n' for i in shard['immutable_word_ordinals'])).encode())==shard['word_sequence_sha256']
        for core in ['cuts','supported']:
            req={'n':12,'core':core,'query_ms':1000,'seed':167,'parent_shard':'r07-next-0000','instances':[{'ordinal':i,'word':words[i]} for i in shard['immutable_word_ordinals']]}
            ev,rows=run(req,core,HERE/'priority');events.append(ev)
    (HERE/(a.mode+'-parent.json')).write_text(J({'verdict':'candidate_only','parent_footer':True,'events':events,'elapsed_seconds':time.monotonic()-t}))
