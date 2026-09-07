"""Reduce real replay logs to complete indexed outcomes; never run a solver."""
import argparse,json,collections
from pathlib import Path
import exact_replay as r

def collect(path):
 audit=json.loads((path/'word-audit.json').read_text());orders=[]
 for n in range(3,12):
  names=(path/f'words-{n}.txt').read_text().splitlines()
  if names!=r.word_orbits(n) or names!=r.restricted_growth_words(n):raise ValueError('full word-set mismatch')
  base,_=r.build_formula(n);input_bytes=(path/f'exact-{n}.smt2').read_bytes()
  if input_bytes!=base.encode():raise ValueError('input bytes mismatch')
  log=path/f'exact-log-{n}.jsonl';rows=[json.loads(x) for x in log.read_text().splitlines()];h=rows[0];rows=rows[1:]
  if h['code_sha256']!=r.digest((Path(__file__).parent/'exact_replay.py').read_bytes()) or h['base_input_sha256']!=r.digest(input_bytes):raise ValueError('header binding')
  if [x['word'] for x in rows]!=names:raise ValueError('duplicate, skipped, or unordered row')
  instance_digests=[];runs=[]
  for i,x in enumerate(rows):
   extra=''.join(f'(assert e{c}_{u}_{(u+1)%n})\n' for u,c in enumerate(x['word']))
   if x['n']!=n or x['instance_sha256']!=r.digest((base+extra).encode()) or x['status']!='unsat':raise ValueError('unresolved or binding failure')
   instance_digests.append(x['instance_sha256']);key=[x['status'],x['timeout_seconds']]
   if runs and runs[-1][2:]==key:runs[-1][1]=i+1
   else:runs.append([i,i+1]+key)
  word_hash=r.digest(('\n'.join(names)+'\n').encode())
  if not any(x['n']==n and x['sha256']==word_hash and x['exact_set_equal'] for x in audit):raise ValueError('word audit binding')
  if json.loads((path/f'unresolved-{n}.json').read_text())!=[]:raise ValueError('unresolved set nonempty')
  orders.append({'n':n,'word_count':len(names),'word_set_sha256':word_hash,'base_input_sha256':r.digest(input_bytes),
   'ordered_instance_sha256_list_digest':r.digest(('\n'.join(instance_digests)+'\n').encode()),'raw_log_sha256':r.digest(log.read_bytes()),
   'outcome_runs':runs,'unresolved_words':[],'status_counts':dict(collections.Counter(x['status'] for x in rows)),
   'solver_seconds_sum':sum(x['seconds'] for x in rows),'solver_seconds_max':max(x['seconds'] for x in rows)})
 return {'header_common':{k:v for k,v in h.items() if k not in ['n','base_input_sha256']},'orders':orders,'total_words':sum(x['word_count'] for x in orders)}
def main():
 p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True);p.add_argument('--exploratory',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 r.bound_process(38)
 run=json.loads((a.data/'run.json').read_text())
 if run['status']!='RESULT_CANDIDATE_READY' or any(run['unresolved_words'].values()):raise ValueError('coordinator incomplete')
 actual=json.loads((a.data/'adversarial-audit.json').read_text())
 out={'verdict':'candidate_only','status':'RESULT_CANDIDATE_READY','scope':'nonempty three-coloured tournaments, orders 1 through 11',
  'outcome_format':'outcome_runs=[start,end_exclusive,status,timeout_seconds], indexed by the full sorted word_orbits(n) list; all inputs regenerate from build_formula plus cycle assertions. Lossless for word/status/timeout; timing is aggregated. Not a solver proof certificate.',
  'primary_replay':collect(a.data),'coordinator_run':run,
  'controls':json.loads((a.data/'controls.json').read_text()),'direct_enumeration':json.loads((a.data/'direct-enumeration.json').read_text()),
  'adversarial':{'closure_test_domain':'all 216 base-six assignments on labelled order-three pairs; every final exact closure bit compared to physical BFS','closure_test_count':len(actual['closure_tests']),
   'closure_status_counts':dict(collections.Counter(x['status'] for x in actual['closure_tests'])),
   'comparisons':[{k:v for k,v in x.items() if k not in ['old_arcs','old_physical_audit']} for x in actual['encoding_comparisons']],
   'smallest_observed_proxy_relaxation':actual['smallest_observed_proxy_relaxation'],'legacy_positive_controls':actual['legacy_positive_controls'],
   'incremental_reset_sequence':actual['incremental_reset_sequence'],'expected_relaxation_differences':actual['expected_relaxation_differences'],
   'unexpected_mismatches':actual['unexpected_mismatches'],'raw_audit_sha256':r.digest((a.data/'adversarial-audit.json').read_bytes())},
  'limitations':['No trusted verifier receipt or admission; same native solver binary/trust domain as earlier generator work.',
   'Old M01/R04 missing logs remain unavailable; this is newly executed work.',
   'Finite bound only; no empty-case or general-root closure.',
   'No native UNSAT proof trace; replay requires executing the pinned input family.']}
 if a.exploratory:out['exploratory_replay']=collect(a.exploratory)
 a.out.write_text(r.dump(out)+'\n');print(r.dump({'sha256':r.digest(a.out.read_bytes()),'bytes':a.out.stat().st_size,'words':out['primary_replay']['total_words']}))
if __name__=='__main__':main()
