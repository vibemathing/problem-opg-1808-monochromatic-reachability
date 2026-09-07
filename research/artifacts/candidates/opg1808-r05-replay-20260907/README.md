# R05 — exact-closure replay of the finite root case through eleven

Verdict: `candidate_only`. Candidate status: `RESULT_CANDIDATE_READY` applies
only when the adjacent observed run has all its required checks complete.
Problem: `problem:opg-1808-monochromatic-reachability`.
Attempt: `attempt:web-20260906-opg1808-a01`.
Historical route: `route:directed-gallai-decomposition-v1` (identity, not a premise).
Graph: `graph:opg1808-initial-v1`. Target: `obligation:opg1808-root`. Issue: #3.
Read baseline: `0a1ea30e8c6711abaddb133b6230d0eb5299cf2d`, Harness 1.2.4.

## 1. Frozen finite claim and dependencies

For each NONEMPTY finite simple tournament T with 1 <= |V(T)| <= 11 and an
arc-colouring into {0,1,2}, absence of a rainbow DIRECTED triangle implies a
vertex s such that, for every t != s, some directed s-to-t path is monochromatic.
Its colour may depend on t; unused colours are permitted. Equivalently, any
nonempty minimum-order counterexample to the unrestricted root has order >= 12.
The finite result is a computational proof candidate, not a general root proof.
The literal empty-tournament convention is excluded explicitly, not changed in
the ProblemContract. No direction-uniform partition existence premise is used.

Dependency chain: minimum-counterexample reduction (Section 2), physical
encoding fidelity (Sections 3-4), complete symmetry coverage (Section 5), and
actual finite UNSAT observations (observations.json) imply the finite claim.
The old reports/logs were not recovered. This is a newly executed replay with
new inputs and observations, not a reconstruction of old execution output.

## 2. Minimum counterexample to the spanning missing-pair cycle

1. Suppose a nonempty counterexample of order at most N exists. Choose one T
   of minimum order among such objects. Orders one and two have immediate
   monosources; hence its order n is at least three. Every smaller nonempty
   induced subtournament has no rainbow directed triangle and has a monosource.
   The first property is hereditary; the second follows from minimality.
2. Define a digraph F on distinct vertices by u ->_F v exactly when v has NO
   monochromatic directed path to u in T, of any of the three colours.
3. Every F arc is a physical arc u -> v of T. Otherwise v -> u would itself
   be a one-edge monochromatic path, contradicting its definition.
4. Each vertex v has an unreachable target u because it is not a monosource.
   Therefore indegree_F(v) >= 1. Repeatedly choose an incoming predecessor.
   Finiteness yields a repetition, from which a simple directed F-cycle can
   be extracted. It has at least three vertices, because F is a tournament
   subdigraph, without loops or opposite arc pairs.
5. Let S be the vertex set of this cycle. Each v in S still cannot reach its
   cycle predecessor in T[S]: every path there would be a path in T. Thus
   T[S] has no monosource; it also has no rainbow directed triangle, by
   heredity. Minimality forces S = V(T). Importantly, arbitrary induced
   subtournaments are NOT being claimed to inherit failure of the root.
6. Label this physical spanning cycle i -> i+1 modulo n. If F contained an
   extra arc u -> v, then v is neither u nor succ(u). The arc plus the cycle
   segment v,...,u would be a directed F-cycle of length at most n-1 (the
   opposite-consecutive case is already impossible in a tournament). Step 5
   would yield a smaller counterexample. Hence there are no extra F arcs.
7. F is exactly this cycle. Consequently each i fails to reach exactly pred(i),
   and reaches every other distinct vertex in at least one colour. This does
   not assert a common colour for all those paths.

This is the reduction attributed to Shen and restated as Lemma 2.1 in
Georgakopoulos--Spruessel, *On 3-coloured tournaments*, arXiv:0904.1967v2,
pp. 2-3. The above proof spells out the finite cycle extraction, direction of
F, and hereditary step. Their separate local-colour Theorem 1.1 is NOT used.

## 3. Audit of the frozen R04 superrelation formula

The old constructor is `root-native-smt-r04.py` in the parent candidate
collection. The audit disables stars and all-three-incident restrictions.
It has physical arc bits A(u,v,c), exactly one oriented colour per unordered
pair, and off-diagonal bits R(u,v,c). Physical arcs imply R; R is transitively
closed on triples of pairwise distinct vertices. It forbids R(i,pred(i),c),
requires some positive R for all other distinct pairs, fixes the spanning
cycle and its first colour, and forbids physical rainbow directed triangles.

Soundness: induction on the length of a SIMPLE physical c-path shows its
endpoints belong to R_c. For a path of length at least two the initial vertex,
penultimate vertex and endpoint are distinct, so the encoded transitivity
clause applies. Arbitrary directed walks can be shortened by deleting repeated
segments. Omitting diagonal R bits cannot defeat this argument for distinct
endpoints. Therefore actual monochromatic reachability is a SUBSET of R.
Negative predecessor R clauses imply genuine physical non-reachability.
Together with the exactly-one and physical-triangle clauses, any SAT model
in the original three-colour/no-rainbow domain supplies a root counterexample.
Positive R bits need not be actual paths, and are never used as path witnesses.

Completeness FOR MINIMUM COUNTEREXAMPLES: assign their actual physical arcs
and actual off-diagonal colour reachabilities to A and R. Section 2 gives all
negative and positive clauses. Actual reachability satisfies transitivity.
Cycle labelling and global colour renaming give the fixed first arc. Thus a
minimum counterexample has a model of an appropriate canonical-word instance.
This suffices for finite exclusion. It does NOT say every proxy model has
exactly one physically unreachable target per vertex.

### Explicit expected relaxation difference, not a root bug

With the rainbow prohibition REMOVED, the canonical four-vertex word 0011 has
old-formula status SAT but exact-positive-formula status UNSAT. A returned
physical table is:

```
0 -> 1 : 0     0 -> 2 : 0     1 -> 2 : 0
1 -> 3 : 2     2 -> 3 : 1     3 -> 0 : 1
```

Its BFS missing targets are [3], [0], [1], [1,2], respectively. The triple
{0,1,3} is a rainbow directed cycle, so this is OUTSIDE the root hypothesis.
The extra non-predecessor missing pair 3 -> 1 can be filled virtually in
R_2; adding that pair to the physical closures creates only the {1,3} colour-2
cycle and violates no negative predecessor clause. Dropping exact positive
requirements allows this same fixed physical table in the new formula.

This defeats an overstrong claim of unconditional old/new model equivalence,
not the R04 finite exclusion. Exhaustive n=3 comparisons have no such difference;
n=4 is the smallest observed distinction in the tested n>=3 domain. The audit
reports ten expected relaxation differences off the rainbow-free hypothesis,
zero unexpected differences, and no root counterexample. No R04 failed-route
entry is proposed on the basis of this expected semantic difference.

## 4. Different replay: biconditional physical Floyd circuits

`exact_replay.py` does not use R04's R-superrelation constructor. For each
colour, start with W[-1](u,v) = (u=v) OR A(u,v,c). For k=0,...,n-1 encode

    W[k](u,v) <-> W[k-1](u,v) OR
                         (W[k-1](u,k) AND W[k-1](k,v)).

The invariant is that W[k] means a physical directed walk with all internal
vertices drawn from {0,...,k}. Base and step follow by splitting at pivot k;
walks reduce to paths for distinct endpoints. When u=k or v=k the recurrence
is an identity because diagonal entries are true; for u=v it stays true.
Skipping precisely these updates preserves the invariant. Every other gate
uses Boolean EQUALITY, not merely an implication. Thus final W is exact.
The new formula imposes the cycle, negative predecessors and all other positive
reachabilities using W, and the original physical triangle and palette clauses.
Section 2 proves completeness for minimum counterexamples. A SAT physical
model is audited separately by BFS and actual triangle enumeration.

All 216 complete colour/orientation assignments on three vertices were fixed
one by one, while asserting that some final W bit differs from direct BFS.
Every such query was UNSAT. This is a finite mutation test, not a replacement
for the general invariant argument. Incremental reset tests alternated 000,
012,000,012 in the same no-rainbow-ban solver and returned UNSAT,SAT,UNSAT,SAT.

## 5. Full word coverage, not just counts

For each n=3,...,11, the new generator begins with ALL 3^n words. In lexical
order it takes the first remaining word and deletes its orbit under all six
colour permutations and n cyclic rotations. Every selected word is therefore
the least of an entire orbit; termination leaves no unassigned word. Fixed
points cause no problem: set deletion, not a presumed orbit size, is used.
This algorithm is distinct from the R03 restricted-growth/normalization
algorithm; the two complete sorted word lists were compared for equality.
Reflections are NOT quotiented. Cyclic relabelling preserves the predecessor
pattern and global colour permutations preserve the root predicates. Every
minimum counterexample is represented, with arbitrary chord orientations.

The word counts for n=3,...,11 are 3,6,9,26,53,146,369,1002,2685. All 4299
instances were executed with exact physical closure. Each returned UNSAT;
no UNKNOWN, timeout, SAT, skipped word or duplicate discharge is counted.
The per-order word-set hashes, input-family hashes, log hashes, explicit empty
unresolved sets and compact per-word outcomes are in observations.json.
The compact outcome format indexes the FULL independently generated ordered
word set; it is a lossless status/timeout representation, not a proof trace.

## 6. Direct small-order enumeration and positive controls

`direct_enumeration.cpp` uses neither F nor SMT. It examines physical coloured
tournaments through n=5. For n>=2 fix 0->1 with colour 0. Each of the six
possible first-arc choices maps bijectively to this fixed sector by swapping
vertices 0/1 when needed and swapping its colour with 0. Hence weight six,
without any free-orbit assumption. A partial rainbow triangle rejects all
6^(remaining pairs) suffixes. The code checks accepted+rejected coverage.
For every accepted leaf, BFS for every source/colour agrees with a separately
computed Floyd closure. No accepted leaf has zero monosources. In particular,
34,294,176 of the 60,466,176 labelled five-vertex assignments are rainbow-free,
all with a monosource. This is labelled coverage, not an isomorphism count.

Two freshly solved SAT controls exercise the physical-variable mapping:
removing the rainbow ban recovers cyclic RGB; allowing four colours recovers
a rainbow-free six-vertex tournament with no monosource. Full physical tables,
BFS closures and missing targets are in observations.json. They respectively
fail the rainbow and palette hypotheses. Fixing the same tables in the frozen
old encoder also returns SAT. Reinstating the rainbow ban for RGB returns UNSAT.

## 7. Reproduction, limits and evidence ceiling

Use Python 3.13.5 and an existing libz3 reporting 4.13.3.0, with library SHA-256
7accc397d4ac387468b09489bdaff9d82bfac4ca6a7e339b8fbb2167edf9c1c0.
The standalone direct enumerator uses g++ (Debian 14.2.0-19) 14.2.0, C++17 -O3.
No solver, library or proof assistant is installed by the scripts. From this
candidate directory, use a NEW output directory:

    python reproduce.py --out replay-output --legacy ../root-native-smt-r04.py --total-seconds 600

The coordinator pins source hashes, Python/compiler/solver identities, uses
one process at a time, seed 17 and one solver thread. Exact queries have 0.5s
solver limits, batches at most 20s and child wall caps 35s; controls have 5s
per query and 25s wall cap; adversarial checks have 2s per query and 40s wall
cap. Children have CPU 38/39s and 768 MiB address-space limits. Files are capped
at 1 MiB and total produced data at 5 MiB. A hard 600s whole-coordinator alarm
and per-child remaining-time caps enforce the total deadline. All incomplete
states retain their exact unresolved word set. No timeout is interpreted as
UNSAT. The executed coordinator record is included in observations.json.

Initial exploratory batches and the final coordinated rerun are separately
identified. An initial auxiliary C++ build had a name collision, corrected
before compilation/run; that compile error supplied no mathematical result.

The solver binary and generator trust domain are not independent of the old
observations. There is a different encoder/strategy and a solver-free small
case check, but no trusted verifier receipt, kernel run, native resolution
certificate, EvidenceLink or admission. Mathematical replay is not transport
CI. The root remains open, as does the historical ledger obligation. Its old
partition dependency is not used and requires coordinator action before any
admission. Existing unavailable-source classifications remain unchanged.

Reasoning-discipline audit: scope/quantifiers frozen; dependencies explicit;
finite existence reduction constructive; physical controls and boundary n=1,2
checked; exact-closure invariant and finite word-deletion termination proved;
minimum-order choice and symmetries justified; probability/asymptotics not
used. Computational and statement-faithfulness obligations remain at candidate
level. No induction from eleven to arbitrary order is claimed.
