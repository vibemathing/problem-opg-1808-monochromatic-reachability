# R02: mandatory colour reachability and complete order-nine coverage

Verdict: `candidate_only`. Candidate: `candidate:opg1808-root-r02-propagation-20260906`.
Problem: `problem:opg-1808-monochromatic-reachability`.
Attempt: `attempt:web-20260906-opg1808-a01`.
Historical route ID: `route:directed-gallai-decomposition-v1`.
Graph: `graph:opg1808-initial-v1`. Target: `obligation:opg1808-root`.
Base: `af56f062b0837bc6da8f16cc93264324dd34c69d`. Issue: #3.

## Frozen scope and change since R01

We study NONEMPTY finite tournaments, colours from {0,1,2}, directed paths
whose colour may depend on their target, and absence of rainbow DIRECTED
triangles. No claim about empty-tournament conventions is made. The root and
its historical partition dependency remain open; the latter is not assumed.
This candidate proposes that every such tournament on at most nine vertices
has a monosource, conditional on the reductions and executed programs being
correct. There is no trusted mathematical receipt or novelty claim.

R01 searched a spanning cycle of forbidden predecessor pairs through order
eight. R02 also uses the positive reachabilities forced by minimality. These
are path requirements, not fictitious physical tournament arcs. R02 supplies
an explicit sound propagation rule, a new program, a deterministic driver,
complete canonical-word node counts, and fresh positive controls.

## Coverage and exact exceptional pairs

In a smallest nonempty counterexample T, write u ~> v when some monochromatic
path goes from u to v in T. Put x->y in F iff y cannot reach x. Then F is a
subgraph of T, since the opposite physical arc would give a path, and every
vertex of F has positive indegree. Any directed F-cycle induces a smaller
counterexample unless it spans T: each of its vertices still cannot reach its
predecessor and the absence of rainbow directed triangles is hereditary.
Consequently such a cycle is spanning; label it i->i+1 modulo n.

An additional arc x->y of F, other than a cycle arc, would close a strictly
shorter F-cycle by following the spanning cycle from y to x. Thus F has
exactly the cycle arcs. Every i reaches every vertex except i-1; self-reach
is represented reflexively. This positive statement is about a MINIMUM
counterexample, not every tournament failing the root. Orders one/two have
a direct monosource; inductive exclusion of this domain at orders 3,...,9
therefore excludes all nonempty root counterexamples of order at most nine.

This is the Shen-cycle reduction already restated in the supplied C06 and
R01 (R01 cites Georgakopoulos--Spruessel, arXiv:0904.1967v2, Lemma 2.1).
The proof here is included so the computation does not rely on a source
being available or a transport check being mathematical evidence.

## A useful local consequence

Let a_i be the colour of i->i+1. At a change a_(i-1) != a_i, every
monochromatic path from i+1 to i-1 must have the THIRD colour. A path in colour
a_i could be prepended with i->i+1, violating i's forbidden predecessor.
A path in colour a_(i-1) could be appended with i-1->i, violating the forbidden
predecessor of i+1. The required path exists for n>=3 by the preceding lemma.
It avoids i. This consequence needs exactly three available colours, but not
an extra no-rainbow assumption beyond that used for minimal-domain coverage.

## Propagation invariant and proof

For each colour c maintain a reflexive transitive LOWER relation L_c.
It includes every assigned c-arc, and may additionally include pairs that
EVERY valid completion is required to connect in c. Initially it is the
closure of the fixed cycle arcs. Inserting a requirement u L_c v adds
L_c(*,u) x L_c(v,*). This formula is valid even if a directed cycle forms:
a simple path through the inserted relation uses it at most once.
A requirement that makes any i reach i-1 rejects the state.

For an unassigned unordered pair, test all directions and all colour labels.
Reject a physical arc only if it completes an actual rainbow directed
triangle, conflicts with the cycle direction, or its insertion into L_c
forces a forbidden predecessor reachability. Any physical arc occurring
in a valid completion survives these tests. Empty domains are impossible.

Construct a potential PHYSICAL graph P_c from the assigned c-arcs and all
surviving c-arc domain choices, and compute its reflexive transitive closure
U_c. Do not add mandatory shortcut pairs directly to P_c: doing so would hide
whether their paths can actually be materialised. Every completion's actual
c-path is contained in P_c, so its reachability is contained in U_c.
If L_c is not contained in U_c, no completion exists.

For every required pair (u,v), v != u-1, let A(u,v) contain those colours c
for which u U_c v and inserting the pair into L_c creates no forbidden pair.
Every actual completion must use one member of A(u,v). If it is empty,
reject. If it is a singleton, add that one necessary reachability to L_c.
Repeat. Even when domains become stale during a round, they remain an
OVERESTIMATE of possible arcs; after any new fact the whole round is repeated.
Every successful additional fact enlarges a finite lower relation, so this
fixed-point loop terminates. Every inference preserves all valid completions.

After reaching a fixed point, branch on a smallest physical-arc domain and
explore all choices. Virtual path requirements are never tested as physical
triangle edges. At a full leaf, ordinary Boolean Floyd--Warshall is recomputed
from actual tournament arcs, checking the exact predecessor gaps and actual
triangles. A leaf failing that audit is a program error, not a witness.

## Exhaustive word coverage, not a random sample

The fixed Hamilton cycle is coloured first. Take the least word among all
cyclic rotations, after relabelling colour names in first-occurrence order.
The driver enumerates ALL first-occurrence strings on at most three colours,
then takes these canonical representatives. Vertex rotation and global colour
renaming preserve the exact search domain. There is no reflection quotient,
unproved module preprocessing, degree restriction or tournament-isomorphism
census in R02. With a fixed nonconstant cycle word there is no need to prune
unused colours during DFS; all k labels are tested. Constant words are rejected
when their physical monochromatic cycle already reaches a forbidden predecessor.

The new MODE=2 program completed every representative at each order 3,...,9:

| Order | Canonical cycle words | Completed words | Total search nodes |
|---|---:|---:|---:|
| 3 | 3 | 3 | 0 |
| 4 | 6 | 6 | 4 |
| 5 | 9 | 9 | 19 |
| 6 | 26 | 26 | 152 |
| 7 | 53 | 53 | 1295 |
| 8 | 146 | 146 | 25932 |
| 9 | 369 | 369 | 979759 |

Every completed status was `exhausted_no_witness`. These are search-tree nodes,
NOT counts of tournaments, colourings, or isomorphism classes. Some prefixes
fail before entering DFS. The first nine-vertex pass left two timeouts, which
were subsequently rerun to completion; the report counts only completed runs.
The hardest order-nine word was 000000122, requiring 97266 nodes. The report
encodes each word's count in sorted canonical-word order, with a word-list hash.

At the eight-vertex word 00000121, R01 reported 4684988 nodes; the new propagator
needed 722. The domains differ by proved minimum-counterexample requirements;
this is not an assertion that the two programs enumerate equal search trees.

## Controls, execution identity and boundaries

Deleting the no-rainbow test at n=3 recovers the physical rainbow directed
triangle with cycle word 012. Allowing FOUR colours at n=6, word 021021,
recovers the same 15-arc no-rainbow witness recorded by R01. In both controls,
actual paths and missing targets are recomputed from physical arcs. The latter
is outside the root palette and is not a root counterexample.

Execution was auxiliary local candidate generation expressly requested by the
user: Python 3.13.5, g++ (Debian 14.2.0-19) 14.2.0, C++17 -O3, one process at a
time, 512 MiB address-space limit, bounded per-word wall/node budgets, one MiB
output cap. No theorem prover, external SAT solver, repository Harness command,
trusted verifier, EvidenceLink or Result admission was run or fabricated.
Compiler warnings about indentation were corrected before the frozen source.

Reproduce using `root-reach-propagation-r02.cpp` and `root-word-driver-r02.py`.
The executable arguments are N PALETTE NO_RAINBOW MODE SECONDS NODE_CAP WORD.
MODE=0 omits positive reach requirements; MODE=1 checks them against upper
closures; MODE=2 also propagates unique-colour requirements. R02's complete
counts use MODE=2. The driver supports serial continuation through append-only
logs, processes previously untried words first, and never calls an incomplete
run a negative result. Different word-list generation may change ordering;
the report's canonical-list digest and length must match before comparing counts.

## Remaining obligation

A trusted replay must audit coverage, the requirement/physical-arc distinction,
the upper-graph construction, the fixed point, and actual outputs. R01's second
implementation only covered through six; R02 is not a second trust domain.
The root's obsolete partition dependency needs a coordinator revision before
admission. No protected record is edited. The next live search bound is ten,
with every timeout retained as unresolved; no order-ten conclusion is part of R02.

best_verified_result: none. best_verified_candidate: none.
best_candidate: direct-root finite exclusion through nine, subject to these caveats.
State: nonterminal. Root and historical target remain open.
