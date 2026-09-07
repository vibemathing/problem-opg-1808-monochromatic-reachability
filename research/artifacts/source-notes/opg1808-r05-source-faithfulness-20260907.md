# R05 source and semantic audit

Verdict: candidate_only. Issue #3. Read main:
`0a1ea30e8c6711abaddb133b6230d0eb5299cf2d`, Harness 1.2.4.

Primary mathematical source: Agelos Georgakopoulos and Philipp Spruessel,
*On 3-coloured tournaments*, arXiv:0904.1967v2. Lemma 2.1 on printed pp. 2-3
restates Shen's missing-predecessor Hamilton-cycle reduction. Retrieved
2026-09-07 via https://arxiv.org/pdf/0904.1967 (parsed title identifies v2).
The PDF date line and arXiv revision metadata are not treated as a novelty
claim. Screenshot requests failed at the fetch layer; the statement/proof
comparison used parsed text, not a claimed visual check.

The source uses minimality under induced-subtournament containment. Selecting
a minimum-order nonempty counterexample yields that hypothesis. Its
monochromatic domination is directed and the colour may vary with the target.
R05 supplies its own explicit finite proof and does not require an external
black-box verification of this lemma. The paper's Theorem 1.1 additionally
restricts each vertex to at most two incident colours; that theorem is NOT
substituted for the root statement or used to prune this replay.

Frozen code audited at the above revision:
- `research/artifacts/candidates/root-native-smt-r04.py`, SHA-256
  a2381c88441f864be5d554ebce3161c74a4c546717918cbbce204db02f4aeb06.
- `research/artifacts/candidates/root-native-batch-r04.py`, SHA-256
  b741c964fac0a7cc8d2886b404693691e50ceea50fffe49fc9b52402555353a4.
- `research/artifacts/candidates/root-interval-driver-r03.py`: reference
  word definition; complete newly generated lists compared, not just counts.
- `research/artifacts/candidates/opg1808-root-r03-report-20260906.json`:
  prior report only, not used as a verification receipt or replay output.

Runtime interface source: official Z3 C API documentation,
https://z3prover.github.io/api/html/group__capi.html , retrieved 2026-09-07.
The lifted Boolean result mapping is false=-1, undefined=0, true=1.
Actual native version and binary digest are separately recorded by the run;
documentation freshness is not used to infer the installed version.

R04's positive R bits are superrelations. Replacing them with exact physical
reachability makes a stronger formula on arbitrary graphs, not an equivalent
model space. Completeness on MINIMUM counterexamples is the required bridge.
The recorded n=4 off-hypothesis proxy example illustrates this distinction;
it has a rainbow directed triangle and is not a root counterexample.

The new replay is a new generator-side observation, with an independently
implemented orbit algorithm and exact circuit rather than the old encoder.
This does not confer independent-verifier status: the native Z3 binary and
trust domain are shared. The proposed finite case is 1<=n<=11, not the empty
case or all n. Original unavailable M01/R04 source dependencies remain
unavailable; no old output was reconstructed. The latest user message is the
scope for this bounded candidate task; no central authorization receipt or
Evidence/admission object is generated or attested here.
