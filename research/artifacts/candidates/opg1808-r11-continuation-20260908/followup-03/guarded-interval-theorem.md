# R11 followup-03: guarded run subinterval witness rule

Verdict: `candidate_only`. Problem: `problem:opg-1808-monochromatic-reachability`.
Attempt: `attempt:web-20260906-opg1808-a01`; graph: `graph:opg1808-initial-v1`.
Historical route: `route:directed-gallai-decomposition-v1` (identity only).
Target: `obligation:opg1808-root`. Coordination Issue: #3.
Read main: `eefa4b7bb6d55db45a754bc4bcda8b18f05f0d47`.

## Frozen domain and supplied physical data

Let T be a finite simple tournament with an actual directed spanning cycle C,
of order n>=3 and with colours in a finite palette. Fix colour c. Cutting C at
its k>=3 non-c arcs gives cyclically ordered, nonempty c-paths P_0,...,P_(k-1).
Singleton paths are allowed. Fix P=P_j, a vertex h outside P, an actual c-SCC
containing h, and actual c-paths Q_in from u in P_(j+1) to h and Q_out from h
to v in P_(j-1). The paths may have zero edges; their actual arcs and colours
must be supplied. Boolean reachability proxies or SCC sizes do not suffice.

Claim: if ANY subinterval of P has a first vertex beaten by h and a later
vertex beating h, T contains either a rainbow directed triangle or an actual
monochromatic path from a cycle vertex to its predecessor. The latter path's
colour need not be c. No rainbow prohibition or negative-predecessor assumption
is needed for this constructive disjunction itself.

Consequently, under the root's no-rainbow condition and the negative-predecessor
property N, directions between h and P form a single threshold: an initial
segment beats h, and h beats the remaining terminal segment. Every cross arc
between h and P is non-c. This uses positions, actual paths and directions,
not just cycle-colour multiplicities.

## Proof, with terminating witness extraction

First, a c arc h->a into P immediately yields the c-walk obtained from the
P_(j+1) prefix to u, Q_in, h->a, and the P suffix to end(P). Its endpoints are
start(P_(j+1)) and its predecessor end(P). Similarly, a c arc b->h from P gives
a c-walk from start(P), along P to b, then b->h, Q_out and the suffix of
P_(j-1), ending at pred(start(P)). Therefore N forbids all these c cross arcs.
This observation is not used as an unproved assumption in the extractor below.

Given an out-before-in pair on P, scan the intervening interval and choose the
first adjacent out-to-in transition a,b. Thus h->a, a->b and b->h are physical
arcs, a->b has colour c, and pred_C(b)=a.

If h->a has colour c, use the first walk above. If b->h has colour c, use the
second walk. If neither has colour c and their colours agree, b->h->a is an
actual monochromatic predecessor path. If their colours differ, h,a,b is a
rainbow directed triangle. These cases exhaust every palette.

The concatenated walks have distinct endpoints. Erasing a segment between
repeated occurrences of a vertex preserves endpoints and arc colours and
strictly reduces the number of edges; finite termination gives a simple path.
Scanning P and this loop erasure are bounded finite algorithms. With N and no
rainbow directed triangle, an out-to-in transition is impossible. A finite
binary direction sequence with no such transition has exactly the stated
initial-in/terminal-out threshold form, allowing either segment to be empty.

The recorded followup-02 sandwich lemma tests the full run's endpoints. This
note saturates that argument over ALL subintervals, and does not claim a new
attribution for its elementary first-turn step. The full endpoint test alone
can miss an interior turn when the run starts with an in-neighbour of h.

## Relation to actual SCC basins and conditional word families

For the actual c-SCC S of h, Q_in witnesses j+1 in I(S), while Q_out witnesses
j-1 in O(S). A c cross arc into P adds j to O(S); a c cross arc from P adds j
to I(S). Either creates the previously proved forbidden intersection
I(S) intersect succ(O(S)). If neither c bridge occurs, the physical turn gives
the other-colour path or rainbow triangle directly.

A checked witness tuple, including actual run intervals, Q_in, Q_out and the
two cross directions, therefore excludes every realization of the associated
canonical-word cylinder under N and no rainbow. Other cycle colours may vary
only while those specified intervals and boundary identities stay valid.
Rotation and global colour permutation preserve the rule. No bare colour word
is discarded by frequency or by an unmaterialized R relation. No additional
solver ordinal is credited by this lemma in the current execution ledger.

For the root, N comes from the separately audited minimum NONEMPTY
counterexample F-cycle reduction: u->_F v means that v cannot mono-reach u;
F is physical and has positive indegree; a cycle-induced subgraph preserves
its predecessor failures and inherits no rainbow; minimality makes the cycle
spanning; any extra F chord makes a shorter such cycle. The false directed
Gallai partition is never a premise.

## Actual diagnostic at the current priority word

For n=12 and ordinal 6446, cycle word 001021100221, start from all increasing
arcs coloured 0. Replace 0->11 by 11->0 and colour the twelve cycle arcs by
the word. Replace 1->5 by 5->1:2, and set 0->5:1, 2->5:2, 0->10:1. All other
non-cycle increasing arcs retain colour 0. This specifies all 66 arcs.

For c=0 choose P=[0,1,2], h=5, actual SCC S={5}, Q_in=[3,5] and Q_out=[5,11].
The direction sequence on P is in,out,in: 0->5, 5->1, 2->5. The whole-run
endpoint sandwich test does not trigger, since h does not beat start(P).
The interior turn gives the actual colour-2 path 2->5->1 to pred_C(2).
The physical BFS/Kosaraju check finds no rainbow directed triangle, only
singleton monochromatic SCCs, and a monosource. It is NOT a root counterexample,
and is a direct construction, not an original-domain SAT model.

## Smallest interior-turn boundary example

A five-vertex example has cycle word 00112 and arcs
0->1:0, 0->2:0, 0->3:2, 4->0:2, 1->2:0, 3->1:0,
1->4:0, 2->3:1, 2->4:0, 3->4:1.
Take P=[0,1,2], h=3, S={3}, Q_in=[3], Q_out=[3,1,4]. The full endpoint test
again fails to see the interior turn; the extractor returns 3->1->2, colour 0.
The object is rainbow-free and all single-colour SCCs are singletons, but it
has a monosource and violates N. Minimum order five here refers ONLY to this
interior-turn-versus-whole-endpoints boundary: k>=3 and a run of at least three
vertices require at least 3+1+1=5 vertices. It is not a root lower bound.

## Executed checks and limits

The accompanying extractor and separate direct certificate validator were
executed on all 7776 chord assignments for the fixed five-vertex cycle word
00112. There were 1452 triggered physical certificates: 660 c-entry, 528
c-exit, 132 equal-cross-colour paths, and 132 rainbow triangles. All passed.
Both explicit objects were checked by the frozen R06 BFS/Kosaraju implementation.
Runtime Python 3.13.5; CPU35/36s, internal wall38s/external40s, 768MiB, 1MiB output.
Normal exit 0; source SHA-256 f81a57e9659c29efdeca7866b1addff84620fbf485e9b3bd6004060604047d35.
These are generator-side tests, not the general proof, native UNSAT traces,
trusted verifier receipts, EvidenceLinks, Results or root closure.
