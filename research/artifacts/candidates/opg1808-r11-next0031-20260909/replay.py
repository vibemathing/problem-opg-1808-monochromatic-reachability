"""Restore public recorded bytes and regenerate only SHA-bound input text.
--audit checks records/SAT arcs without solving; --prepare-run creates clean
source/runtime inputs for a later explicit `python launch.py` execution.
No network, Git, trusted verifier identity, or output reconstruction.
"""
from pathlib import Path,PurePosixPath
import argparse,base64,hashlib,importlib.util,json,lzma,resource,subprocess,sys,time
H=lambda b:hashlib.sha256(b).hexdigest()
REL='research/artifacts/candidates/opg1808-r11-next0031-20260909'
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);ap.add_argument('--audit',action='store_true');ap.add_argument('--prepare-run',action='store_true');a=ap.parse_args()
 if a.audit and a.prepare_run:raise ValueError('choose audit or fresh preparation')
 resource.setrlimit(resource.RLIMIT_AS,(805306368,)*2);resource.setrlimit(resource.RLIMIT_CPU,(50,51));resource.setrlimit(resource.RLIMIT_FSIZE,(1048576,)*2)
 here=Path(__file__).resolve().parent;out=a.output.resolve()
 if out==here:raise ValueError('separate output workspace required')
 index=json.loads((here/'capsule-index.json').read_bytes());parts=[]
 for p in index['parts']:
  q=PurePosixPath(p['path'])
  if len(q.parts)!=1:raise ValueError('part path')
  b=(here/q).read_bytes()
  if len(b)!=p['bytes'] or H(b)!=p['sha256']:raise ValueError('part digest')
  parts.append(b.strip())
 comp=base64.b64decode(b''.join(parts),validate=True)
 dec=lzma.LZMADecompressor(memlimit=134217728);raw=dec.decompress(comp,max_length=2097153)
 if not dec.eof or dec.unused_data or len(raw)!=index['decoded_bytes'] or H(raw)!=index['decoded_sha256']:raise ValueError('catalog digest')
 objects=json.loads(raw)['files'];seen=set();written=0
 if len(objects)!=index['file_count']:raise ValueError('file count')
 def save(rel,b):
  nonlocal written
  q=PurePosixPath(rel)
  if q.is_absolute() or '..' in q.parts or not rel.startswith('research/artifacts/candidates/'):raise ValueError('unsafe path')
  p=out.joinpath(*q.parts)
  if any(x.is_symlink() for x in [p,*p.parents]):raise ValueError('symlink target')
  if len(b)>1048576:raise ValueError('file bound')
  if p.exists():
   if p.read_bytes()!=b:raise ValueError('existing different bytes')
  else:p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
  written+=1
 for item in objects:
  rel=item['path'];b=item['text_utf8'].encode()
  if rel in seen or H(b)!=item['sha256'] or len(b)!=item['bytes']:raise ValueError('object identity')
  seen.add(rel)
  keep=not a.prepare_run or item.get('reused_main_runtime') or rel in [REL+'/'+x for x in ('run.py','launch.py','audit.py','policy.json','incoming.json')]
  if keep:save(rel,b)
 p=out/REL;pol=json.loads((p/'policy.json').read_bytes());rt=(p/pol['runtime_relative']).resolve()
 for f,h in pol['pins'].items():
  if H((rt/f).read_bytes())!=h:raise ValueError('runtime source pin')
 generated=0
 if not a.prepare_run:
  def load(name,f):
   s=importlib.util.spec_from_file_location(name,f);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
  cuts=load('replay_cuts',rt/'opg1808-r10-dual-replay-20260908/closed_sets.py')
  sys.path.insert(0,str(rt/'opg1808-r07-adaptive-20260907'));import supported_superrelation
  done=set()
  for req in sorted((p/'runs').glob('*.request.json')):
   q=json.loads(req.read_bytes());log=p/'runs'/req.name.replace('.request.json','.jsonl');hd=json.loads(log.read_text().splitlines()[0])
   key=(q['engine'],q['n'],q['palette'],q['rainbow'])
   if key in done:continue
   text=cuts.build(*key[1:]) if key[0]=='cuts' else supported_superrelation.build(*key[1:],True)
   if H(text.encode())!=hd['base_sha256']:raise ValueError('regenerated input mismatch')
   target=rt/'opg1808-r10-dual-replay-20260908'/hd['base_path'];save(target.relative_to(out).as_posix(),text.encode());done.add(key);generated+=1
 receipt={'verdict':'candidate_only','restored_objects':written,'catalog_file_count':len(objects),'catalog_sha256':H(raw),'regenerated_input_bases':generated,'solver_outputs_regenerated':False,'solver_queries_executed':False,'prepare_new_run_only':a.prepare_run}
 if a.audit:
  def limits():
   resource.setrlimit(resource.RLIMIT_AS,(805306368,)*2);resource.setrlimit(resource.RLIMIT_CPU,(35,36));resource.setrlimit(resource.RLIMIT_FSIZE,(1048576,)*2)
  t=time.monotonic();r=subprocess.run(['python','audit.py'],cwd=p,capture_output=True,timeout=40,preexec_fn=limits)
  receipt.update(audit_exit_code=r.returncode,audit_elapsed_seconds=time.monotonic()-t,audit_stdout_sha256=H(r.stdout),audit_stderr_sha256=H(r.stderr))
  print(r.stdout.decode(),end='')
  if r.returncode:raise RuntimeError('record audit did not pass')
 print(json.dumps(receipt,sort_keys=True,separators=(',',':')))
if __name__=='__main__':main()
