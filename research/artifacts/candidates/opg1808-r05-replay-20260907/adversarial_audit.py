"""Bounded cross-encoding and exact-closure mutation tests; candidate-only."""
import argparse, hashlib, importlib.util, itertools, json
from pathlib import Path
import exact_replay as r

def load(path):
    spec=importlib.util.spec_from_file_location('legacy',path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def old_formula(old,n,k,rainbow):
    text=old.smt_text(n,2,False,False,k,rainbow,True)
    # Aliases preserve the old formula; they adapt only physical model extraction.
    for u in range(n):
        for v in range(n):
            if u==v:continue
            for c in range(k):
                text+=f'(declare-const e{c}_{u}_{v} Bool)\n(assert (= e{c}_{u}_{v} a_{u}_{v}_{c}))\n'
    return text

def physical_constraints(arcs):
    return ''.join(f'(assert e{c}_{u}_{v})\n' for u,v,c in arcs)

def main():
    p=argparse.ArgumentParser();p.add_argument('legacy',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
    r.bound_process(38)
    h=r.digest(a.legacy.read_bytes())
    if h!='a2381c88441f864be5d554ebce3161c74a4c546717918cbbce204db02f4aeb06':raise ValueError('legacy source mismatch')
    old=load(a.legacy);out={'verdict':'candidate_only','legacy_source_sha256':h,'seed':r.SEED,'per_query_timeout_seconds':2,'closure_tests':[],'encoding_comparisons':[]}
    text,reach=r.build_formula(3,3,False,False,False)
    solver=r.NativeSolver(text,2000)
    pairs=list(itertools.combinations(range(3),2))
    for assignment in itertools.product(range(6),repeat=3):
        arcs=[([v,u,x%3] if x>=3 else [u,v,x%3]) for (u,v),x in zip(pairs,assignment)]
        bfs=r.physical_audit(3,arcs,3)['monochromatic_bfs']
        differences=[]
        for s in range(3):
            for c in range(3):
                for v in range(3):
                    if s==v:continue
                    x=reach[c][s][v]
                    differences.append(f'(not {x})' if v in bfs[s][c] else x)
        extra=physical_constraints(arcs)+'(assert (or '+' '.join(differences)+'))\n'
        ans=solver.solve(3,3,None,extra)
        if ans['status']!='unsat':raise RuntimeError(r.dump({'closure_mismatch':assignment,'result':ans}))
        out['closure_tests'].append({'assignment':list(assignment),'status':'unsat'})
    solver.close()
    for n in [3,4,5]:
        for forbidden in [False,True]:
            new,_=r.build_formula(n,3,forbidden)
            legacy=old_formula(old,n,3,forbidden)
            sn=r.NativeSolver(new,2000);so=r.NativeSolver(legacy,2000)
            for word in r.word_orbits(n):
                rn=sn.solve(n,3,word);ro=so.solve(n,3,word)
                if 'unknown' in (rn['status'],ro['status']):raise RuntimeError('unresolved comparison')
                if forbidden and rn['status']!=ro['status']:raise RuntimeError('root-domain mismatch')
                if rn['status']=='sat' and ro['status']!='sat':raise RuntimeError('completeness-direction mismatch')
                row={'n':n,'forbid_rainbow':forbidden,'word':word,'exact_status':rn['status'],'legacy_status':ro['status'],'expected_relaxation_difference':rn['status']!=ro['status']}
                if ro['status']=='sat':
                    row['old_physical_audit']=ro['physical_audit'];row['old_arcs']=ro['arcs']
                    if not all(ro['physical_audit']['unreachable_targets']):raise RuntimeError('spurious SAT negative path')
                out['encoding_comparisons'].append(row)
            sn.close();so.close()
    text,_=r.build_formula(3,3,False)
    sn=r.NativeSolver(text,2000)
    out['incremental_reset_sequence']=[{'word':w,'status':sn.solve(3,3,w)['status']} for w in ['000','012','000','012']]
    sn.close()
    if [x['status'] for x in out['incremental_reset_sequence']]!=['unsat','sat','unsat','sat']:raise RuntimeError('incremental residual')
    controls=json.loads((a.output.parent/'controls.json').read_text())
    old_controls=[]
    for control in controls[:2]:
        n=control['n'];k=control['palette'];text=old_formula(old,n,k,control['forbid_rainbow'])
        so=r.NativeSolver(text,2000);ans=so.solve(n,k,None,physical_constraints(control['arcs']));so.close()
        if ans['status']!='sat' or ans['arcs']!=control['arcs']:raise RuntimeError('legacy physical control mismatch')
        old_controls.append({'n':n,'palette':k,'status':'sat','fixed_arcs':control['arcs'],'physical_audit':ans['physical_audit']})
    out['legacy_positive_controls']=old_controls
    differences=[x for x in out['encoding_comparisons'] if x['expected_relaxation_difference']]
    if not differences:raise RuntimeError('expected proxy distinction was not observed')
    first=differences[0]
    # Witness is outside the forbidden-rainbow hypothesis; it is not a root bug.
    n=first['n'];arcs=first['old_arcs']
    weak,_=r.build_formula(n,3,False,False)
    sw=r.NativeSolver(weak,2000);ans=sw.solve(n,3,None,physical_constraints(arcs));sw.close()
    if ans['status']!='sat':raise RuntimeError('negative-predecessor witness failed')
    first['exact_without_positive_status']=ans['status']
    out['smallest_observed_proxy_relaxation']=first
    out['unexpected_mismatches']=0
    out['expected_relaxation_differences']=len(differences)
    out['scope']='216 complete order-three colour/orientation assignments test all exact closure bits; 36 old/new word queries and two fixed positive controls; not a proof of all encoding properties.'
    out['audit_code_sha256']=r.digest(Path(__file__).read_bytes())
    a.output.write_text(r.dump(out)+'\n')
    print(r.dump({'closure_tests':len(out['closure_tests']),'encoding_comparisons':len(out['encoding_comparisons']),'legacy_positive_controls':len(old_controls),'unexpected_mismatches':0,'expected_relaxation_differences':len(differences),'output_sha256':r.digest(a.output.read_bytes())}))
if __name__=='__main__':main()
