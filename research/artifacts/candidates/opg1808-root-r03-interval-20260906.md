# R03: interval path obligations and complete search through order ten

Verdict: `candidate_only`. Candidate: `candidate:opg1808-root-r03-interval-20260906`.
Problem: `problem:opg-1808-monochromatic-reachability`.
Attempt: `attempt:web-20260906-opg1808-a01`.
Historical route: `route:directed-gallai-decomposition-v1`.
Graph: `graph:opg1808-initial-v1`. Target: `obligation:opg1808-root`.
Base: `489ae8ca7ef47db13716b9fe752828f9e67b7476`. Issue: #3.

## Scope and progress beyond R02

Candidate conclusion: every NONEMPTY tournament of order at most ten, coloured
from {0,1,2} without a rainbow directed triangle, has a vertex reaching every
other vertex by a monochromatic directed path. Colours may differ by target.
This conclusion is conditional on the reduction, algorithm and recorded finite
runs being correct; no trusted replay, EvidenceLink or Result exists.

R02 used mandatory global reachabilities and completed order nine. R03 uses
paths inside proper cyclic intervals and forces actual first/last arcs when
potential path choices leave only one possibility. It completes all 1002
canonical cycle-colour words at order ten, and rechecks orders three to nine.
The obsolete partition-existence assertion is never used. The historical root
DAG dependency on that assertion still needs coordinator revision before
admission; no protected record has been edited. Empty-graph conventions are
not used to produce a purported root counterexample.

## Minimality, the exceptional cycle, and an interval lemma

Take a minimum-order nonempty root counterexample T, if one exists. Define F
by u->v iff v cannot monochromatically reach u. Every such arc belongs to T,
and every vertex of F has positive indegree. An F-cycle induces a counterexample:
its vertices cannot reach their predecessors even inside that induced graph.
Absence of rainbow directed triangles is inherited by induced subtournaments.
Minimality therefore makes every F-cycle spanning. Label one 0->1->...->n-1->0.
Any extra F-arc closes a shorter cycle, so every i reaches exactly all vertices
except pred(i)=i-1 modulo n. Orders one and two have an immediate monosource.

For u != v and v != pred(u), let I(u,v) be the vertices encountered from u to v
following this cycle, including both ends. It is a PROPER subset. By minimality
T[I(u,v)] has a monosource. Each vertex z other than u has pred(z) in this
interval and cannot reach it even in T. Thus z cannot be that monosource.
Consequently u is the monosource of T[I(u,v)], and there is a monochromatic
u-to-v path wholly inside this interval. This stronger local demand, not just
global reachability, is what R03 adds.

Attribution: the exceptional-cycle reduction is Shen's lemma, restated as
Lemma 2.1 in Georgakopoulos--Spruessel, *On 3-coloured tournaments*,
arXiv:0904.1967v2. The proper-interval lemma is Lemma 2.5 in that paper.
Locator: https://arxiv.org/html/0904.1967v2 . No novelty is claimed for either.
Their short arguments are included to specify exactly the finite search domain.

## Lower requirements and upper physical graphs

For each colour c keep a reflexive transitive lower relation L_c of necessary
reachabilities. It contains assigned c-arcs but may include unmaterialised
path requirements. Inserting u L_c v adds L_c(*,u) x L_c(v,*); reject if this
makes any i reach pred(i). These are monotone necessary facts, NOT new physical
arcs. The closure formula follows by shortening a new walk to use the inserted
relation at most once, and works even when a cycle is formed.

For every unassigned unordered pair enumerate both orientations and all three
colours. Exclude only choices that form an ACTUAL rainbow directed triangle
or force a forbidden predecessor reachability. A valid completion loses none
of its actual choices. A singleton domain forces its actual arc; an empty
domain rejects the state. The cycle arcs have already been physically assigned.

Let P_c contain actual c-arcs plus every surviving physical c-arc choice.
Compute global upper closure U_c. Any completion's c-path lies in P_c, so
L_c not contained in U_c is impossible. In particular virtual lower shortcuts
are NOT inserted into P_c. Such insertion would defeat path materialisation.

For each required pair u,v, candidate colours are those for which P_c[I(u,v)]
contains a path u->v and adding u L_c v would not force a forbidden pair.
An empty colour set rejects; a singleton makes that colour reachability
mandatory in L_c. Potential graphs may become stale after a new lower fact,
but remain overestimates of valid completions. A changed round is rebuilt.

## First-arc and last-arc cut rule

Suppose an interval requirement u->v has unique possible colour c. Every
actual monochromatic path can be chosen simple. Its first successor w lies
in the following explicitly computable set:

F = N^+_{P_c}(u) intersect I(u,v) intersect
    {w : w can reach v in P_c[I(u,v) minus {u}]}.

Its last predecessor w lies in:

B = N^-_{P_c}(v) intersect I(u,v) intersect
    {w : u can reach w in P_c[I(u,v) minus {v}]}.

The removed endpoints prevent a walk that returns to its initial vertex, or
leaves and returns to its final vertex, from falsely supporting a first/last
choice. Every simple completion path contributes an element of each set.
Thus F or B empty means no completion; F={w} forces the PHYSICAL arc u->w in c;
B={w} forces w->v in c. After forcing an arc, domains are rebuilt immediately.
This is a cut-of-path necessity, not an assumption that all potential edges
coexist. If the potential graph has extra mutually inconsistent edges, that
only enlarges F or B and weakens the test; it cannot invalidate this necessity.

Every successful round adds a new physical arc or lower-relation bit. Both
sets are finite. At a fixed point the program branches on a smallest remaining
physical domain and explores every member. At a leaf it separately recomputes
reachability by graph search from physical arcs, checking all exceptional
pairs, all interval paths and all actual directed triangles. A failed leaf
audit is an error, not a counterexample. No vertex-degree or module restriction
is assumed. The only symmetry quotient is global colour renaming and cycle
rotation, exhaustively handled by the word driver.

## Actual completed generator-side runs

The canonical word is the least cyclic rotation after first-occurrence colour
normalisation. Every one of the following finite word lists was completed.

| n | Canonical words | Completed words | Search-tree nodes |
|---|---:|---:|---:|
| 3 | 3 | 3 | 0 |
| 4 | 6 | 6 | 4 |
| 5 | 9 | 9 | 7 |
| 6 | 26 | 26 | 45 |
| 7 | 53 | 53 | 315 |
| 8 | 146 | 146 | 3817 |
| 9 | 369 | 369 | 77004 |
| 10 | 1002 | 1002 | 3211149 |

Every completed status is exhausted_no_witness. Counts measure recursive
search nodes, NOT tournaments, colourings or isomorphism classes. At n=10
four initial short-budget runs were incomplete; all four were subsequently
rerun to completion. An incomplete status never contributes an exclusion.
The report stores every completed node count in sorted canonical-word order,
word-list SHA-256, append-only-log SHA-256, and incomplete-run counts.

The n=9 word 000000122 used 888 nodes here, versus 97266 in R02's report.
This is a comparison of different sound search constraints, not identical
search-tree enumerations. The hardest R03 n=10 word was 0000001011 at 45365 nodes.

## Controls and actual runtime

Disabling the rainbow test recovers the cyclic RGB triangle. With FOUR colours,
the six-vertex word 021021 recovers the 15-arc witness already used in R01/R02.
These are calibration objects, not counterexamples to the three-colour root.

The fragment control tests every subset of its nine noncycle arcs (512),
every cycle rotation (6) and all colour permutations (24): 73728 feasible
partial states. None is rejected; every forced arc agrees with the physical
fixture and every lower requirement lies in a fresh Floyd--Warshall closure.
This does not prove global soundness, but directly attacks over-pruning and
confusing lower requirements with real arcs. Both programs are in the SAME
generator trust domain. Burnside orbit counts agree with generated word counts
at n=3,...,11; the formula used is recorded in the report.

Executed locally: Python 3.13.5; g++ (Debian 14.2.0-19) 14.2.0; C++17 -O3,
-Wall -Wextra -pedantic; no compiler warnings. Serial subprocesses, 512 MiB
address-space bound, one MiB output budget, explicit per-word wall/node caps
and an outer timeout. No repository Harness command, solver, proof assistant,
trusted verifier or admission command was executed. Sources, not binaries,
are transported in this packet.

Compile root-interval-search-r03.cpp and run root-interval-driver-r03.py with
N and a fresh append-only log, --mode 2, bounded --seconds and --batch. Repeat
bounded batches until its remaining_count is zero. MODE=0 retains only global
requirements; MODE=1 adds intervals; MODE=2 also adds boundary cuts. Compile
the adjacent root-interval-controls-r03.cpp for the fragment calibration.
All source hashes and machine observations are in the accompanying report.

## Open work and checkpoint

All statements are candidate. A trusted verifier must replay the finite
coverage, review the minimality/interval/cut proofs, audit the implementation,
and connect statement-faithful evidence before any admission. The finite bound
does not close the universal root. No complete root proof or root counterexample
has been obtained.

best_verified_result: none. best_verified_candidate: none.
best_candidate: direct-root exclusion through order ten, subject to the above.
state: nonterminal. open_obligations: root and historical partition obligation.
next_action: strengthen interval requirements to unions of cycle intervals,
check their minimality justification, and continue bounded order-eleven search
with all 2685 canonical words and all incomplete branches explicitly tracked.
