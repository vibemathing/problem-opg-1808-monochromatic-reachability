"""Restore exact public records and audit them; never solve on the default path."""
from pathlib import Path,PurePosixPath
import base64,hashlib,importlib.util,json,lzma,resource,subprocess,sys,time
P=Path(__file__).resolve().parent
H=lambda b:hashlib.sha256(b).hexdigest()
J=lambda o:json.dumps(o,sort_keys=True,separators=(',',':'))+'\n'
def load(name,path):
 sp=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def safe(root,rel,body):
 q=PurePosixPath(rel)
 if q.is_absolute() or '..' in q.parts or len(body)>1048576:raise ValueError('unsafe path/size')
 f=root.joinpath(*q.parts)
 if f.exists():
  if f.is_symlink() or f.read_bytes()!=body:raise ValueError('refusing different bytes: '+rel)
 else:f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(body)
def restore(root):
 idx=json.loads((P/'capsule-index.json').read_bytes());parts=[]
 for ch in idx['chunks']:
  b=(P/ch['path']).read_bytes()
  if H(b)!=ch['sha256'] or len(b)!=ch['bytes']:raise ValueError('part digest')
  parts.append(b.strip())
 comp=base64.b64decode(b''.join(parts),validate=True)
 if H(comp)!=idx['compressed_sha256'] or len(comp)!=idx['compressed_bytes']:raise ValueError('compressed digest')
 dec=lzma.LZMADecompressor(memlimit=134217728);raw=dec.decompress(comp,max_length=8388609)
 if not dec.eof or dec.unused_data or len(raw)>8388608 or H(raw)!=idx['payload_sha256']:raise ValueError('payload digest/limit')
 objects=json.loads(raw)['objects'];seen=set();total=0
 for ob in objects:
  if ob['path'] in seen:raise ValueError('duplicate object')
  b=ob['text_utf8'].encode();seen.add(ob['path']);total+=len(b)
  if H(b)!=ob['sha256'] or len(b)!=ob['bytes']:raise ValueError('object digest')
  safe(root,ob['path'],b)
 if len(seen)!=idx['objects'] or total!=idx['original_utf8_bytes']:raise ValueError('object totals')
 pins=json.loads((root/'runtime-pins.json').read_bytes())
 for name,h in pins.items():
  if H((root/'runtime'/name).read_bytes())!=h:raise ValueError('runtime pin')
 sys.path.insert(0,str(root/'runtime/opg1808-r07-adaptive-20260907'))
 cuts=load('r32_cuts',root/'runtime/opg1808-r10-dual-replay-20260908/closed_sets.py')
 sup=load('r32_sup',root/'runtime/opg1808-r07-adaptive-20260907/supported_superrelation.py')
 bases={}
 for f in (root/'runs').glob('*.request.json'):
  r=json.loads(f.read_bytes());key=(r['engine'],r['n'],r['palette'],r['rainbow'])
  if key not in bases:
   b=(cuts.build(*key[1:]) if key[0]=='cuts' else sup.build(*key[1:],True)).encode();bases[key]=b
 for ob in idx['regenerate_input_bases']:
  match=[b for b in bases.values() if H(b)==ob['sha256'] and len(b)==ob['bytes']]
  if len(match)!=1:raise ValueError('input base mismatch')
  safe(root,ob['path'],match[0])
 return idx
if __name__=='__main__':
 resource.setrlimit(resource.RLIMIT_AS,(805306368,)*2);resource.setrlimit(resource.RLIMIT_CPU,(60,61));resource.setrlimit(resource.RLIMIT_FSIZE,(1048576,)*2)
 target=Path(sys.argv[1] if len(sys.argv)>1 else 'restored')
 if target.exists():raise SystemExit('use an empty destination')
 t=time.monotonic();target.mkdir(parents=True);idx=restore(target)
 r=subprocess.run(['python','verify_release.py','replaycheck'],cwd=target,capture_output=True,timeout=30)
 if r.returncode:raise SystemExit('record audit failed: '+r.stderr.decode()[-1000:])
 a=(target/'replaycheck-accounting.json').read_bytes()
 if H(a)!=idx['accounting_sha256']:raise SystemExit('accounting mismatch')
 print(J({'verdict':'candidate_only','restored_exact_objects':idx['objects'],'restored_utf8_bytes':idx['original_utf8_bytes'],'regenerated_input_bases':len(idx['regenerate_input_bases']),'accounting_sha256':H(a),'record_audit_exit':r.returncode,'solver_queries':0,'native_unsat_proof_checked':False,'elapsed_seconds':time.monotonic()-t,'classes':json.loads(a)['classes']}),end='')
