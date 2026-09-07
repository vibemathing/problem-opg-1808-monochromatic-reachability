# R10: run-transversal SCC bound and equal-connector endpoint obstruction

Verdict: `candidate_only`. Target: `obligation:opg1808-root`.
Problem: `problem:opg-1808-monochromatic-reachability`.
Attempt: `attempt:web-20260906-opg1808-a01`.
Historical Route: `route:directed-gallai-decomposition-v1`, identity only.
Graph: `graph:opg1808-initial-v1`. Research Issue: #3.
Read base: `eefa4b7bb6d55db45a754bc4bcda8b18f05f0d47`.

## 1. Domain and negative-pair property

A tournament here is finite, simple and NONEMPTY. Its arcs have colours in a
specified finite palette. The root restricts this palette to {0,1,2}; different
targets may use different colours. A path has distinct vertices; a same-colour
walk with distinct endpoints can be shortened by erasing repeated segments.
Let C=(v_0,...,v_(n-1),v_0), n>=3, be an actual directed spanning cycle. Property
N means that no v_i has a monochromatic path, of ANY colour, to v_(i-1).
Neither an arbitrary Hamilton cycle nor an arbitrary tournament is assumed to
satisfy N. All assertions below state exactly where N is used.

The reduction from a minimum nonempty root counterexample to N was rechecked:
(1) orders one and two have monosources; (2) u->F v iff v cannot mono-reach u,
so every F arc is physical; (3) every vertex has positive F INdegree;
(4) a finite incoming-predecessor walk yields a simple F-cycle;
(5) its induced tournament still misses the cycle predecessors and inherits
no rainbow directed triangle, so minimality makes it spanning;
(6) an extra F arc u->v closes the cycle segment v...u with 2<=distance<=n-2,
producing a shorter counterexample (n=3 has no such chord);
(7) hence F is precisely C. Only that particular cycle-induced subtournament
inherits failure. The no-rainbow property itself is hereditary. No finite
search is a premise of this argument. The prior R05 proof attributes the
reduction to Shen, as restated in Georgakopoulos--Spruessel, Lemma 2.1.

## 2. General run-transversal theorem

Assume N. Fix a colour c and let k be the number of C arcs NOT coloured c.
Then every c-monochromatic strongly connected component S satisfies

    |S| <= min(k, floor(n/2)).

If k=0, C itself supplies a c-path to a predecessor, so N is impossible.
For k>0, remove the k non-c arcs of C. The vertices split into k disjoint
c-directed paths, with singleton paths allowed. Suppose S meets one of these
paths in two vertices x before y. The path x...y is c-monochromatic, and S
supplies a c-path y...x. Each internal vertex of x...y is therefore mutually
c-reachable with x, so the whole segment lies in S. In particular S contains
a consecutive pair v_j,v_(j+1) of C. Its internal strong connectivity gives
a c-path v_(j+1)...v_j, contrary to N. Thus S meets each of the k paths at most
once, proving |S|<=k. Independently, S and succ_C(S) are disjoint, again by N.
Successor is a bijection, so 2|S|<=n, giving the second bound.

This proof uses neither the palette-three restriction nor no rainbow triangles.
It strengthens the previously recorded SCC bound by using the number of
non-c cycle arcs. It does not assert that large SCCs exist.

Precise conditional word-family elimination: if a candidate comes with a
certified c-SCC of size s, every canonical word w with #_c(w)>n-s is incompatible
with N. Rotation and colour permutation preserve the statement. The SCC is a
necessary input to this test; this is NOT an unconditional exclusion of those
words for all tournaments. A monochromatic path witness to a predecessor can
be extracted when two certified SCC vertices occur in one c-run. No additional
n=12 solver word is credited on the basis of this conditional theorem.

## 3. A proposed three-exception repair and its exact relaxation

R08 proves the unconditional obstruction for at most two non-c cycle arcs.
The three-exception family is not being declared excluded. We tested a
stronger premise than the mixed-colour endpoint shortcut in the R09 checkpoint:
ALL three exceptional connector arcs have the same colour 1.

For k disjoint, nontrivial colour-0 runs retain only start/end symbols a_i,b_i,
i modulo k. Number them a_i=2i, b_i=2i+1. Let E be a complete 3-coloured
endpoint tournament and let R_c be off-diagonal transitive superrelations.
The tested endpoint system has exactly these axioms:

A. E has one oriented colour on every unordered pair, and no rainbow directed
triangle. Each E_c is contained in R_c; R_c is transitive on distinct triples.
B. R_0(a_i,b_i) holds and R_0(b_i,a_i) does not hold. These forward run relations
are virtual path assertions, not assertions that the direct endpoint arc is red.
C. Every connector E_1(b_i,a_(i+1)) is present.
D. R_c(a_i,b_(i-1)) is false for every c.
E. Every other ordered endpoint pair has at least one positive R colour.
F. For x outside {a_i,b_i}, if E(x,a_i) and E(b_i,x), then
   R_0(x,b_i) or R_0(a_i,x).

E is a necessary minimum-counterexample condition for runs of length at least
two edges, so that an end's predecessor is not another retained endpoint.
F is a valid endpoint-turn consequence. If both displayed red relations fail,
no physical red arc can go from x into that run or from that run into x:
otherwise the red run prefix or suffix supplies the forbidden relation.
Along the run, an out-to-in orientation change at x must occur. At the first
change, the two cross arcs are non-red. Equal colours give a monochromatic
reverse path across the internal consecutive pair; distinct colours give a
rainbow directed triangle. Both contradict the full problem assumptions.
Consequently a minimum-counterexample realization of the runs satisfies A-F.
The converse, especially expansion of an endpoint model to actual runs, is NOT
asserted. R is not required to be exact endpoint-graph reachability.

## 4. Minimum endpoint countermodel, even with equal connectors

The attached `endpoint-model.json` has k=3. It contains all 15 actual arcs and
all 28 positive R triples; a standalone checker tests every axiom A-F, using
ordinary graph traversal for the actual arcs. Its connectors 1->2, 3->4, 5->0
are all colour 1. It has no rainbow directed triangle and has an actual
monosource, so it is NOT a root counterexample. In particular its positive R
pairs must not be reported as physical endpoint paths.

The parameter k=3 is minimum for this endpoint system. For k=1, B requires
R_0(a_0,b_0), whereas D forbids it. For k=2, red cross-relations between the two
runs are impossible: extending any such relation by the virtual red run prefix
and suffix yields one of D's forbidden red pairs. Whichever way the edge
a_0a_1 points, combine it with the appropriate connector b_i->a_(1-i).
The premise of F then holds, while both red alternatives are impossible.
Thus k=2 is contradictory, with no solver result needed for this minimum-k
argument. Six is the minimum number of DISTINCT endpoint symbols here, not
a lower bound on the order of a root counterexample.

This exactly defeats endpoint-only inconsistency even after requiring equal
connector colours. It does not disprove a three-exception theorem about full
tournaments, and does not retry the false directed Gallai partition.
The full runs and their interior constraints are still a genuine open bridge.

## 5. Computation and reproducibility boundaries

`endpoint_guard.py` generates A-F and queried k=1,2,3 with 5000ms query budgets,
seed17, native Z3 4.13.3.0. The final run returned UNSAT, UNSAT, SAT. The final
SAT model is evaluated once from one solver model, preserving matching E/R
assignments. A first exploratory implementation and its outputs are retained
separately and are not used as the definitive model. Resource limits and
measured parent exit are in `endpoint-exit.json`. `check_endpoint_model.py`
rechecks the fixed mathematical object without loading any solver.

The two n=12 engines are distinct: forward-closed separating vertex sets and
R07's supported transitive superrelations. The former witnesses nonreachability
by closure of a set containing the source and excluding its predecessor; the
latter uses physical reachability contained in R. Both are complete for minimum
counterexamples, but not claimed model-equivalent. Every returned SAT model is
physically checked by the frozen BFS plus Kosaraju checker. There is no graph
to reconstruct from UNSAT. A result bit, footer, CI, review or merge is not a
native UNSAT proof certificate or trusted mathematical admission.

Old R09 missing raw logs were NOT reconstructed. Its published unresolved
bitset was decoded and matched both published hashes. Separate new executions
recheck its carried-negative ordinals where possible. Counts from freshly
read executable logs and counts carried from a coordination checkpoint are
reported separately until new receipts bridge that provenance gap.

No stored record, verifier registry, Harness, workflow, EvidenceLink, Result,
Solution or historical source-gap note is changed. The general root is open.
