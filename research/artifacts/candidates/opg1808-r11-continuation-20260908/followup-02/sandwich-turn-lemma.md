# R11 followup-02: a physical sandwich-turn exclusion

Verdict: `candidate_only`. Target: `obligation:opg1808-root`.
Repository: `vibemathing/problem-opg-1808-monochromatic-reachability`.
Attempt: `attempt:web-20260906-opg1808-a01`.
Historical route: `route:directed-gallai-decomposition-v1` (identity only).
Graph: `graph:opg1808-initial-v1`; coordination Issue #3.

## Exact constructive statement

Let T be a finite simple tournament with a directed spanning cycle C, n>=3,
and any finite palette. Fix colour c. Deleting the k>=3 non-c cycle arcs
partitions C into cyclically ordered nonempty c-paths P_0,...,P_(k-1).
Singleton runs are allowed. Let P=P_j have at least two vertices.
Assume the following PHYSICAL witnesses are supplied:

* A vertex h outside P, in an actual c-SCC S.
* A c-path Q_in from u in P_(j+1) to h, and a c-path Q_out from h to v in
  P_(j-1). Zero-edge paths are allowed when an endpoint equals h.
* Actual arcs h->start(P) and end(P)->h, with their colours recorded.

Then T contains either a rainbow DIRECTED triangle or an actual monochromatic
path from a cycle vertex to its cycle predecessor. The output path colour
need not equal c. No proxy R bit, SCC-size estimate, or solver answer can
substitute for the supplied arcs and paths.

## Proof and certificate algorithm

Along P, choose the first vertex b which beats h. Its predecessor a on P is
beaten by h; b exists and is not the first vertex by the two endpoint arcs.
Thus h->a->b->h is a physical directed triangle, with a->b coloured c.

If h->a is c, concatenate the prefix of P_(j+1) ending at u, Q_in, h->a,
and the suffix of P beginning at a. This is a c-walk from start(P_(j+1))
to end(P)=pred_C(start(P_(j+1))).

If b->h is c, concatenate the prefix of P ending at b, b->h, Q_out, and
 the suffix of P_(j-1) beginning at v. This is a c-walk from start(P) to
end(P_(j-1))=pred_C(start(P)).

These walks have distinct endpoints. Erasing a repeated-vertex segment
strictly reduces their length, preserves endpoints and colours, and therefore
terminates with a simple monochromatic predecessor path.

Otherwise the two cross arcs are both non-c. If they have one common colour d,
b->h->a is a d-path to pred_C(b)=a. If their colours differ, h,a,b is a rainbow
directed triangle. This exhausts all cases, for any finite palette.

## Conditional canonical-word family, not frequency pruning

Let N forbid every monochromatic predecessor path along C. In a rainbow-
directed-triangle-free realization satisfying N, actual entry/exit paths as
above force NOT(h->start(P) AND end(P)->h). Equivalently, start(P)->h or
h->end(P) must hold. This condition uses path locations and orientations,
not just colour multiplicities. A fixed witness tuple specifies a family of
words whose displayed run intervals are c-coloured; all other colours may vary
provided those run boundaries and the physical witness arcs remain valid.

In the earlier two-sided SCC notation, the entry and exit give j+1 in I(S)
and j-1 in O(S). The first-turn argument supplies the missing bridge or an
other-colour predecessor path; in the c-bridge cases it creates exactly the
forbidden I(S) intersection with succ(O(S)). No word is discarded unless its
actual witness tuple is checked. No extra n=12 solver credit is taken here.

For a minimum NONEMPTY root counterexample, the separately frozen F-cycle
reduction supplies N. Here u->F v means that v cannot mono-reach u; F is a
physical subdigraph, has positive indegree, and any F-cycle induces a smaller
counterexample unless spanning. An extra F chord closes a shorter cycle, so
F equals that spanning cycle. No false Gallai partition is a premise.

## Actual objects and checks

The solver-free extractor and direct path/triangle validator check the exact
statement. Exhaustive tests cover 27 fixed-cycle tables at n=3 and 2916 at n=4,
with all three choices of c. These finite tests are not the general proof.

A separate twelve-vertex diagnostic uses newly queried ordinal 6446,
word 001021100221, but OMITS all negative-predecessor requirements. It has
three-coloured physical arcs, no rainbow directed triangle, and acyclic
single-colour subgraphs. For c=0, P=[3,4], Q_in=[5,7], Q_out=[7,2], h=7,
S={7}; 7->3 and 4->7 both have colour 2. The resulting path 4->7->3 has colour
2 and ends at pred_C(4). All numerical SCC bounds hold. Its complete arc table,
BFS/Kosaraju check and solver runtime are saved. It is NOT a root counterexample,
and its diagnostic SAT is excluded from the original-domain solver ledger.

The claim is a general constructive lemma candidate. Transport, test exit 0,
shared-solver replay and a model's self-review do not create trusted evidence.
No native UNSAT trace, EvidenceLink, Result, Solution or root closure is claimed.
