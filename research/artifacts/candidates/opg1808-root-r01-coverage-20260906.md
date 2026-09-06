# R01: direct-root finite search through eight vertices

Verdict: `candidate_only`. Candidate: `candidate:opg1808-root-r01-20260906`.
Problem: `problem:opg-1808-monochromatic-reachability`.
Attempt: `attempt:web-20260906-opg1808-a01`.
Route identity retained for provenance: `route:directed-gallai-decomposition-v1`.
Graph: `graph:opg1808-initial-v1`. Target: `obligation:opg1808-root`.
Base: `b8e462251af9679a3a628ff4bbb9ed4536109088`. Issue: #3.

## Claim and scope

Candidate conclusion: every NONEMPTY tournament of order at most eight, with
arcs coloured from {0,1,2} and no rainbow directed triangle, has a monosource.
Equivalently, any minimum-order nonempty root counterexample has order at least
nine, conditional on the coverage argument and finite programs below being correct.
A monosource may use a different colour for each target. Empty tournaments are
not exploited; the frozen contract is unchanged. The failed uniform-partition
assertion is never assumed. No novelty claim is made.

The user now requests direct root work. This packet binds the already-existing
root obligation, not a newly invented ID. The graph still lists the failed
partition obligation as a root dependency. That obsolete dependency is NOT a
valid argument and must be revised by the trusted coordinator before admission.
The candidate author has not edited the graph, records, Harness or verifiers.

## Coverage reduction (restated from the supplied C06 draft)

Suppose a smallest nonempty counterexample T exists. Write x~>y for existence
of some monochromatic directed path in T. Form F with arc u->v exactly when
v cannot reach u. Each such arc is an arc of T (the reverse arc would itself
be a monochromatic path). Every v has an unreachable target, so F has positive
indegree at every vertex. A finite graph with this property contains a directed
cycle, obtained by repeatedly choosing an incoming predecessor.

On any F-cycle each vertex cannot reach its predecessor, even in the induced
subtournament. That subtournament is still rainbow-directed-triangle-free and
has no monosource. Minimality therefore forces the cycle to span all vertices.
Label it 0->1->...->n-1->0. Thus every minimal counterexample appears in the
search domain whose vertices cannot monochromatically reach i-1 modulo n.
If another forbidden pair existed, its F-arc would close a strictly shorter
cycle using the appropriate segment of the spanning cycle; hence these are
exactly the forbidden pairs. Only the first (weaker) assertion is used by R01.
Orders one and two have a direct monosource. Searching n=3,...,8 therefore
suffices for the stated finite conclusion. This does not presume any degree,
module, SCC, or directed-Gallai preprocessing theorem.

Historical attribution: the cycle reduction is Shen's lemma, restated as
Lemma 2.1 in Georgakopoulos--Spruessel, arXiv:0904.1967v2. It is not new here.
The supplied C06 proof contains the same reduction. The 2026 Rocq preprint
arXiv:2604.21376 concerns the TWO-colour SSW theorem, not this three-colour root;
it supplies no verification receipt for these candidates.
Sources: https://arxiv.org/html/0904.1967v2 ; https://arxiv.org/abs/2604.21376 .

## Primary search: exact invariant and exhaustive branching

`root-cycle-search-20260906.cpp` keeps one unassigned/coloured arc per unordered
pair. Hamilton-cycle orientations are fixed; every other direction is available.
An assigned arc uses an integer colour. For each colour c, R_c is the exact
reflexive transitive closure of currently assigned c-arcs.

Inserting u->v adds precisely R_c(*,u) x R_c(v,*): a simple new path uses the
new edge at most once, and all its earlier/later edges were already present.
This also handles insertions that create cycles. Reject an insertion only when
it completes a rainbow directed triangle or makes some i reach i-1 in a colour.
Both failures persist under any completion, so pruning cannot remove a witness.

Every still unassigned pair is tested for all locally admissible directions
and colours. An empty domain rejects the state; otherwise branch on a smallest
domain (ties use pair order). Recursively extend all its members. The only
symmetry pruning introduces unused colours in order 0,1,2. Unused colour names
are interchangeable; swapping them fixes every assigned arc and preserves the
chosen pair and feasibility. Therefore each full colouring has a represented
colour-renaming orbit. No vertex-automorphism census is claimed.

The empty initial state fixes no cycle colours. At a leaf all pairs are assigned,
the object is a tournament with no rainbow directed triangle, and every vertex
has an actual unreachable predecessor. Such a leaf would be a ROOT witness,
not merely a partition obstruction. None occurred at the completed bounds.

## Order eight: complete colour-word splitting

`root-cycle-word-search-20260906.cpp` is the same search with an optional full
cycle-colour word. It first inserts these actual cycle arcs, then runs the same
branching. Normalise a word by renaming colours in first-occurrence order;
then take the lexicographically least normalised cyclic rotation. The set of
such representatives from all 3^8 words has 146 elements. The report lists ALL
146 representative strings and their completed search-node counts. All have
status exhausted_no_witness, including the monochromatic word rejected during
prefix insertion. Every labelled cycle word lies in one represented orbit.
No reflection or unproved orientation/module restriction is used.

The first unpartitioned n=8 run stopped at its explicit 25-second cap; it was
incomplete, not a negative result. Complete per-word runs supersede that bound.
Three words needed a later run beyond the initial per-word three-second cap;
all three subsequently completed. Their complete node counts are 2223488,
4684988,1506231 for 00000112,00000121,00000122. Prior partial logs are retained
locally, and their complete append-only log digest is in the report.

## Actual generator-side observations

Primary unprefixed search: n=3,4,5,6,7 had respectively 3,18,261,7383,439082
recursive nodes and no witness. Order eight used 146 complete colour-word
searches with 14871526 total recursive nodes and no witness. Counts are TREE
NODES, not numbers of tournaments, isomorphism classes or colourings.

`root-cycle-reference-20260906.cpp` uses fixed lexicographic pair order, retains
all colour labels except fixing the first arc to colour 0, and recomputes each
colour's closure by ordinary Boolean Floyd--Warshall. It completed n=3,4,5,6
with 4,87,7262,1811209 nodes and no witness. It was not run to completion at
orders seven/eight. It belongs to the SAME generator trust domain, not a
trusted mathematical verifier.

Controls: deleting the forbidden-triangle test recovers a cyclic rainbow T3.
Allowing four colours recovers a six-vertex no-rainbow object with no monosource.
The latter is NOT a root counterexample. The report includes its 15 arcs and
BFS/closure-checked unreachable targets, plus the T3 control. The insertion
formula was also compared against fresh closure for all 4096 loopless digraphs
on four vertices and all 24576 missing-arc insertions, with no discrepancy.

Environment actually observed: Python 3.13.5; g++ (Debian 14.2.0-19) 14.2.0;
C++17, O2 (primary/reference), O3 (word variant). Each search was single-threaded,
512 MiB address-space bound; output budget one MiB. No solver or proof assistant
was installed/used. This is auxiliary local candidate generation under the
explicit bounded-search request, not an execution of the repository Harness.

## Reproduction and limits

Compile each of the three adjacent C++ sources with the flags above. The five
required arguments are N, palette size, forbid-rainbow (0 or 1), wall seconds,
and node cap for the two primary variants. The word variant accepts a sixth
argument containing the cycle word. For example use `8 3 1 30 20000000 00000121`.
The reference executable takes N, palette, forbid-rainbow, wall seconds.
Set a surrounding hard timeout and memory bound as in the recorded runs.

Generate all normalised cyclic words, run each, and require exact coverage and
no incomplete status. Recompute the positive controls' physical per-colour
closures from their arc tables. Re-run the reference checker or a separately
implemented exhaustive/SAT certificate verifier at higher orders. The current
program outputs are not proof-assistant certificates and have not been replayed
by a trusted verifier. CI checks transport only. No EvidenceLink or Result exists.

## Checkpoint and atomic claims

All claims are candidate: cycle-domain coverage; monotone soundness of both
prunes; colour/rotation orbit coverage; completed exclusions through eight;
positive-control validity. None depends on partition existence or C01-C03 CI.
best_verified_result: none. best_verified_candidate: none.
best_candidate: direct-root finite exclusion through eight, with stated caveats.
open_obligations: root and historical partition target remain open in the ledger.
next_action: exploit colour-transition required reachabilities for n=9, retain
all unresolved cycle words, and develop SCC/colour-neighbourhood lemmas. Do not
restart the failed partition-existence argument.
