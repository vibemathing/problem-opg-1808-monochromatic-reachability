# M01: path materialisation and complete order-ten coverage

Verdict: `candidate_only`.
Candidate: `candidate:opg1808-root-m01-materialization-20260906`.
Problem: `problem:opg-1808-monochromatic-reachability`.
Attempt: `attempt:web-20260906-opg1808-a01`.
Historical route: `route:directed-gallai-decomposition-v1` (provenance only).
Graph: `graph:opg1808-initial-v1`. Target: `obligation:opg1808-root`.
Base: `489ae8ca7ef47db13716b9fe752828f9e67b7476`. Research Issue: #3.

## Exact finite claim

Every NONEMPTY finite tournament on at most ten vertices, with arc colours
from a three-element palette and no rainbow DIRECTED triangle, has a vertex
reaching every other vertex by a monochromatic directed path. The path colour
may depend on its target. This is a computational proof CANDIDATE; no larger
order, empty-graph convention, trusted replay or novelty claim is asserted.

R02 at this base supplies completed lower orders, the minimum-counterexample
coverage proof, and mandatory lower/physical upper reachability propagation.
M01 adds path materialisation, and recomputes the complete nine- and ten-vertex
cycle-word domains. R02's mathematical candidate arguments, not its CI status,
are the dependencies. No Gallai partition existence assertion is used. The
root's historical partition dependency remains a coordinator issue before
admission; no protected record is edited.

## Minimum-counterexample coverage

In a smallest nonempty counterexample, put x->y in F precisely when y cannot
monochromatically reach x. Such an arc is physical, since the reverse physical
arc would give a path. Every vertex of F has positive indegree. Any F-cycle
induces a counterexample: each vertex still cannot reach its predecessor and
the no-rainbow-directed-triangle condition is hereditary. Minimality forces
that cycle to span T. An additional F-arc would close a shorter F-cycle.
Thus label the spanning cycle 0->1->...->n-1->0: each i reaches every vertex
other than i-1. Orders one and two have direct monosources. Excluding this
minimum-counterexample domain at each order through ten excludes all nonempty
root counterexamples through ten. This is not a restriction on every tournament.

## Path-filtering lemma

For colour c, L_c is a reflexive transitive LOWER relation containing physical
c-arcs and additional necessary c-reachabilities. Every surviving completion
must realise all its pairs by physical monochromatic paths. P_c is the potential
PHYSICAL graph of assigned c-arcs and all surviving c-arc domain choices.
Every completion's c-graph is a subgraph of P_c.

For a required pair u L_c v, u!=v, define M_c(u,v) as the vertices x for which
adjoining BOTH u L_c x and x L_c v, with transitive closure after each insertion,
does not produce a forbidden pair (i,i-1). Every vertex of a completion's
physical c-path u->...->v lies in M_c(u,v): the prefix and suffix of that path
realise the two added relations in that very completion. Hence every realising
path lies in P_c[M_c(u,v)]. If that induced graph has no u->v path, reject.

If removing an interior vertex x disconnects u from v in this induced potential
graph, every realising c-path must pass through x. Therefore u L_c x and x L_c v
are necessary and may be inserted into the lower relation. This vertex-dominator
inference creates PATH requirements, not fictitious physical tournament arcs.
All rainbow-triangle tests continue to use the physical arc table alone.

A graph or admissible-interior mask computed earlier in a propagation round
can become stale when new lower facts are added, but remains an overestimate.
Using it cannot discard a valid completion. All domains are rebuilt after a
successful round. Every new fact adds a previously absent bit to finite lower
relations, so the fixed-point loop terminates. Branch on a smallest physical
arc domain and retain every value. At full leaves recompute exact physical
Floyd closure and actual directed triangles from scratch.

The lower-closure insertion formula is
L' = L union (L(*,u) times L(v,*)).
It is valid for reflexive transitive L even if the insertion creates a cycle:
a simple path through the inserted relation need use it at most once.

## Complete executed domain

MODE=3 of root-path-materialization-m01-20260906.cpp implements these rules.
Its source header retains the local development label R03; this M01 artifact
is deliberately distinct from the different existing R03 interval-search branch.

| Order | Canonical cycle-colour words | Completed | Recursive nodes |
|---|---:|---:|---:|
| 9 | 369 | 369 | 76362 |
| 10 | 1002 | 1002 | 2547015 |

All final statuses are `exhausted_no_witness`. Three initial ten-vertex runs
hit one-second limits and were subsequently rerun with three-second limits;
all completed. The report's arrays contain one completed count per sorted
canonical word, excluding all partial counts. The hardest final ten-vertex
word was 0000012022, with 30872 nodes. These are search-tree node counts, not
tournament counts, colouring counts, or isomorphism-class counts.

The whole nine-vertex domain shrank from R02's 979759 nodes to 76362. At word
000000122, the R02 tree had 97266 nodes and M01 used 732. Both positive controls
were recovered: the rainbow directed T3 with the triangle prohibition removed,
and the four-colour six-vertex no-rainbow witness with the palette enlarged.
Their missing targets were recomputed from physical arcs by Python. The
four-colour object is NOT a root witness. R02 and M01 also agree on all 18
canonical words at orders 3,4,5 with the no-rainbow filter disabled. These are
generator-side comparisons, not a new trusted verification domain.

## Word coverage and digest conventions

The driver enumerates first-occurrence colour words and chooses the minimum
under cyclic rotation and global colour relabelling. It does not quotient by
reflection. Once the cycle is fixed, all colour labels and every non-cycle arc
direction are retained. Constant words fail already on their monochromatic
cycle. No unproved module or degree preprocessing is used in MODE=3.

There is also a Burnside cross-check. For rotation r put d=gcd(n,r), L=n/d.
The number of orbits is
(1/(6n)) sum_r [3^d + 3*(3^d if 2 divides L else 1)
                     + 2*(3^d if 3 divides L else 0)].
The three terms correspond to the identity, the three transpositions, and the
two 3-cycles of the colour permutation group. A starting colour on each of d
rotation cycles must be fixed by the L-th power of that permutation. The
formula matches the generated counts at orders nine and ten and all lower
checked orders. It does not depend on the recursive canonical-word generator.

M01's word-list digests hash ordinary json.dumps(sorted_words) followed by one
newline. R02 used compact JSON without a trailing newline. The nine-vertex
word sets agree exactly although their serialisation digests differ. Raw
append-log hashes cover all rows, including initial incomplete runs. Full
logs are retained in the local downloadable checkpoint bundle.

## Reproduction and limitations

Compile root-path-materialization-m01-20260906.cpp with g++ -O3 -std=c++17.
Place the resulting executable named search-r03 beside root-word-driver-m01-20260906.py;
that executable name is retained for exact reproduction of the recorded driver.
The driver takes N, per-word seconds, per-call seconds (at most 40). The
executable takes N PALETTE NO_RAINBOW MODE SECONDS NODE_CAP WORD. Use MODE=3.
The driver only accepts explicit successful statuses with matching exit codes.
Incomplete and invalid runs cannot discharge a word.

Actual tools: Python 3.13.5 and g++ (Debian 14.2.0-19) 14.2.0; C++17 -O3,
one process, 512 MiB address-space limit, external wall timeout, one-MiB
per-process output limit. No external SAT solver or proof assistant was used.
This is auxiliary local candidate generation, not repository Harness execution.
No trusted mathematical receipt, EvidenceLink, Result or Solution exists.

The separate M01 colour/interval note contains additional structural lemmas.
They were NOT silently used as pruning assumptions for the table above.
The existing web/attempt-opg1808-root-r03-n10-20260906 branch was found with a
different interval-search implementation and left untouched. Its code or any
reported counts are not attributed to M01. Distinct filenames prevent overlap.

best_verified_result: none. best_verified_candidate: none.
best_candidate: direct-root finite exclusion through ten, subject to replay/audit.
next_action: interval-contained support and deleted-set boundary restrictions,
with all unresolved order-eleven words retained. State: nonterminal.
