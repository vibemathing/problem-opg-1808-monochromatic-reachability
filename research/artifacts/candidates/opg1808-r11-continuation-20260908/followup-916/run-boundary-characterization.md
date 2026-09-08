# R11 follow-up: exact run-boundary characterization

Verdict: `candidate_only`. Primary owner: `math-proof`.
Problem: `problem:opg-1808-monochromatic-reachability`.
Attempt: `attempt:web-20260906-opg1808-a01`.
Historical Route: `route:directed-gallai-decomposition-v1` (identity only).
Graph: `graph:opg1808-initial-v1`; target: `obligation:opg1808-root`.
Issue: #3. Read base: `eefa4b7bb6d55db45a754bc4bcda8b18f05f0d47`.

## Frozen definitions

Let T be a finite simple tournament with an actual directed spanning cycle
C=(v_0,...,v_(n-1),v_0), n>=3. Arc colours belong to a specified palette.
Fix one colour c. N_c means that no v_i has a c-monochromatic directed path
to v_(i-1). N means N_c for every colour; it does not require one common colour
for all targets of a monosource. All reachability and SCCs in this note refer
to actual physical arcs, not Boolean R proxies.

Let k be the number of cycle arcs not coloured c. When k>=1, deleting those
arcs partitions V(T) into k nonempty directed c-paths P_0,...,P_(k-1), in
cyclic order. Singleton paths are allowed. The last vertex of P_(j-1) is the
predecessor on C of the first vertex of P_j. Indices j are modulo k.

## Exact theorem

For k>=1, N_c is equivalent to BOTH conditions:

A. Each actual c-SCC meets each P_j in at most one vertex.
B. There is no actual c-path from any vertex of P_j to any vertex of P_(j-1).

In B, a zero-edge path at the same vertex is allowed as a reachability test.
This matters only when k=1: B then fails, as it must, since P_0 is already
a c-path from its first vertex to its cycle predecessor. When k=0 the whole
cycle is c-monochromatic and its first n-1 arcs directly disprove N_c.

### Necessity of A

Suppose an SCC contains x before y on one c-run. The run segment x...y and
an actual c-path y...x make each vertex of the segment mutually c-reachable
with x. In particular, some consecutive pair of C belongs to the same SCC.
The reverse c-path between that pair violates N_c.

### Necessity of B, with an explicit witness

Suppose an actual c-path Q goes from u in P_j to v in P_(j-1). Concatenate
the run prefix from s=start(P_j) to u, Q, and the run suffix from v to
end(P_(j-1))=pred_C(s). All arcs have colour c. The concatenation may repeat
vertices, but its endpoints are distinct. Erase each repeated-vertex segment
to obtain a simple c-path from s to its predecessor. Each erasure strictly
reduces the number of edges, so it terminates and preserves the endpoints
and arc colours. This contradicts N_c.

### Sufficiency

Assume A and B. Suppose a c-path goes from v_i to v_(i-1). If the cycle arc
v_(i-1)->v_i is c-coloured, that arc and the reverse path put these two vertices
in one c-SCC and in one c-run, contradicting A. Otherwise v_i starts a run and
v_(i-1) ends the preceding run, contradicting B. These are all possible cycle
arc colours. Therefore N_c holds.

No no-rainbow hypothesis, palette-size bound, minimality or solver outcome
is a premise of this theorem. For application to the root, use the separately
proved minimum-counterexample F-cycle reduction in R05 README Section 2:
u->_F v iff v cannot mono-reach u; F is physical and has positive indegree;
a directed F-cycle inherits its predecessor failures and no-rainbow property;
minimality makes it spanning, and an extra F chord creates a shorter F-cycle.
The false directed-Gallai partition is not used.

## Relation to the R11 SCC gap bound

Under N_c, A implies at most one SCC vertex per c-run. B implies that an SCC
cannot occupy two cyclically adjacent c-runs, since it supplies reachability
in both directions between any two of its vertices. The occupied run-index
set and its successor set are disjoint and have the same size. Hence
2|S|<=k, recovering |S|<=floor(k/2). The numerical bound alone does not imply
A or B and is not a substitute for physical reachability checks.

## A witness-bearing canonical-word family

Fix an actual c-path Q from u to v and a proposed cycle start s. Every cycle
word having only colour c on the cycle interval s...u and on the cycle interval
v...pred_C(s) is incompatible with N whenever those intervals and Q are actual
arcs of the tournament. Concatenation and loop erasure give the certificate.
All other cycle colours may vary. Rotation and a global colour permutation
preserve this rule. If a certified SCC supplies Q, its internal path must be
materialized and checked; an R bit or a claimed SCC size is insufficient.

This is a conditional family of physical instances, not unconditional deletion
of colour strings by frequency. In the new n=12 diagnostic below, it includes
all words with initial three arcs colour 0 together with the actual bridge
3->11 of colour 0: 0->1->2->3->11 is then a predecessor-path certificate.
For arbitrary n>=5, replace 11 by n-1. This is an all-orders conditional rule.
No extra n=12 UNSAT ordinal is credited through this rule in this turn.

## Smallest physical counterexample to sufficiency of the size bounds

Use the four-vertex cycle word 0011 and the complete arc table:

    0->1:0, 1->2:0, 2->3:1, 3->0:1, 0->2:0, 3->1:0.

There is no rainbow directed triangle (only two colours are used). Every
monochromatic SCC is a singleton. For colours 0 and 1, k=2 and the bound is 1;
for unused colour 2, k=4 and the bound is 2. Thus all SCC size bounds hold.
Nevertheless 3->1->2 is a colour-0 path to pred_C(3)=2. Vertex 3 is a
monosource: it reaches 1 and 2 in colour 0 and 0 in colour 1. This is NOT a
root counterexample. It specifically defeats treating the size bounds as
sufficient for the negative-predecessor property.

Order four is minimum in the stated domain n>=3. On three vertices the whole
tournament is the specified directed triangle. If it is not rainbow, some
colour occurs at least twice, so k<=1. Its nonempty SCCs have size at least 1,
which cannot satisfy |S|<=floor(k/2). Orders one and two have no directed
spanning cycle and are outside this statement.

## Diagnostic extracted from a newly closed n=12 word

The original ordinal 4928, word 000122110012, has new UNSAT observations in
both frozen encodings. To obtain an actual table for the structural test,
a SEPARATE diagnostic formula removes ONLY source 0's predecessor exclusions
and forces the actual colour-0 path 0->1->2->3->11. The remaining sources retain
their closed-set exclusions. That relaxed formula returned SAT. Its complete
66-arc table is saved separately. Physical FIFO BFS and Kosaraju checks find
no rainbow directed triangle, all monochromatic SCCs singleton, and the unique
monosource 0. Thus it satisfies the numerical bounds but violates B. Its SAT
status is never counted in the original n=12 SAT/UNSAT ledger.

## Finite tests and assurance limits

The separate solver-free run-boundary checker tests the equivalence and each
extracted physical path on 27 fixed-cycle three-vertex tables and 2916
fixed-cycle four-vertex tables, for all three colours. It checks 81 and 8748
colour cases respectively; 21 and 3276 cases produce verified predecessor
paths. It also checks the complete four-vertex and twelve-vertex diagnostics.
The general theorem above is a deductive proof candidate, not an inference
from these finite tests. The diagnostic SAT run and tests have explicit
version, input, CPU/wall/memory/output and normal-exit records.

The native solver, shared generator domain, transport CI, commit and review
supply no trusted verifier authority. There is no native UNSAT proof trace,
EvidenceLink, Result, Solution or root closure. The original R06/R07/R10/R11
archives remain immutable; this note does not claim their pending files have
all been transported. New material stays in the existing R11 transaction.
