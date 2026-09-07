# R08: two-exception cycle obstruction

Verdict: `candidate_only`. Primary owner: `math-proof`.
Problem: `problem:opg-1808-monochromatic-reachability`.
Attempt: `attempt:web-20260906-opg1808-a01`.
Historical route: `route:directed-gallai-decomposition-v1` (identity only).
Graph: `graph:opg1808-initial-v1`; target: `obligation:opg1808-root`.
Read base: `aa702573cf51c587cccc6d31c28a54bcc64eb5d9`; Issue #3.

## Exact statement

Let T be a finite simple tournament of order n >= 3, with arcs coloured from
ANY palette, and let C be the directed spanning cycle v_i -> v_(i+1), indexed
modulo n. Fix a colour r. If at most two arcs of C are not colour r, then T
contains either (a) a rainbow DIRECTED triangle, or (b) a monochromatic directed
path from some v_i to v_(i-1). The colour of the latter path is not prescribed.
The path has distinct vertices. This is a constructive disjunction, not a
claim about underlying undirected rainbow triangles.

Consequently, in a rainbow-directed-triangle-free tournament where every
predecessor pair of C is monochromatically unreachable, each colour occurs
on C at most n-3 times. In particular, for a minimum nonempty root
counterexample the canonical colour word has max colour multiplicity <= n-3.
This eliminates the all-orders family with at least n-2 occurrences of any
one colour, including arbitrarily separated exceptions, not just long runs.
It does not eliminate all canonical words or close the general root.

## Proof of the constructive statement

If at most one cycle arc is not r, start immediately after that arc (or anywhere
if all arcs are r). The next n-1 cycle arcs form an r-path from the chosen vertex
to its predecessor. Hence assume there are exactly two non-r cycle arcs.

Cut C at those two arcs. The vertex set is partitioned into two nonempty,
vertex-disjoint red directed paths A=(a_0,...,a_p), B=(b_0,...,b_q), where
red denotes r, p,q >= 0, p+q=n-2. The connecting cycle arcs are a_p -> b_0 and
b_q -> a_0. Zero-length paths, consisting of a single vertex, are allowed.
In particular pred(a_0)=b_q and pred(b_0)=a_p.

If a cross arc a_i -> b_j is red, concatenate the prefix a_0,...,a_i, that
arc, and the suffix b_j,...,b_q. It is a simple red path from a_0 to pred(a_0).
If a cross arc b_j -> a_i is red, the analogous path b_0,...,b_j,a_i,...,a_p
runs from b_0 to pred(b_0). Disjointness of A and B prevents repeated vertices.
Thus unless alternative (b) already holds, NO cross arc between A and B is red.

Exactly one of a_0 -> b_0 and b_0 -> a_0 exists, by the tournament property.
If a_0 -> b_0, consider x=a_0 and the red path P=B. The first vertex of P is
beaten by x, while its last vertex beats x because b_q -> a_0 lies on C.
If b_0 -> a_0, use x=b_0 and P=A; the same endpoint conditions follow from
a_p -> b_0. The selected P has at least one edge: otherwise the two endpoint
conditions would be opposite arcs on a single unordered pair.

Choose the first vertex P_j which beats x. Then j>=1, x -> P_(j-1), and
P_(j-1) -> P_j is red. Both cross arcs x -> P_(j-1) and P_j -> x are non-red.
If their colours differ, x -> P_(j-1) -> P_j -> x is a rainbow directed triangle.
If their colours agree, P_j -> x -> P_(j-1) is a monochromatic path from P_j
to its predecessor on C. These exhaust the possibilities and prove the claim.

No minimality, reachability proxies, solver result, or bound on palette size
was used in this proof. The algorithm examines at most |A||B| cross arcs and
then one path; it terminates after finitely many pair checks. The witness is
always either three triangle arcs or at most n-1 path arcs.

## Separate audit of the F-cycle bridge

For a hypothetical minimum-order NONEMPTY root counterexample, define
u ->_F v iff v cannot reach u by a directed monochromatic path of any colour.
(1) Orders one and two have an immediate monosource, so n>=3.
(2) Every F arc is physical: otherwise v -> u is itself a forbidden one-edge path.
(3) Every vertex v has an unreachable target u, hence positive F-INdegree.
(4) Following incoming arcs in a finite graph gives a directed F-cycle; it has
length at least three because F has neither loops nor opposite arc pairs.
(5) The induced tournament on that cycle still misses each predecessor and
inherits the absence of rainbow directed triangles. Minimality makes it spanning.
Failure of the root is asserted hereditary only for this particular cycle set.
(6) An extra arc u ->_F v is not a cycle successor arc. The cycle path from v to u
has distance d with 2<=d<=n-2; d=1 is impossible because it reverses a physical
cycle arc. The new F-cycle has length d+1<=n-1, contradicting (5). For n=3 no
such chord exists. (7) F is exactly C, so every vertex misses exactly its
predecessor and reaches every other target, with a target-dependent colour.

This reproduces and audits the explicit reduction in R05 README Section 2;
it is not a new attribution claim for that reduction. The old false partition
existence statement is not a premise. A trusted coordinator, not this candidate,
would have to revise the historical dependency in the admitted graph.

## Separate audit of the monochromatic SCC bound

No monochromatic strongly connected component S can contain both v_i and
v_(i+1), since it would give a monochromatic path from v_(i+1) to v_i.
Thus S and succ_C(S) are disjoint. The successor map is a bijection, so
2|S| <= n. This proves |S| <= floor(n/2) from the negative predecessor property
alone. It does not require the no-rainbow hypothesis; the two-exception lemma
uses that hypothesis in a different, explicit triangle step. Neither bound
has silently been introduced as an unproved solver pruning rule.

## Pressure tests and limitations

The accompanying deterministic certificate extractor implements the proof,
not a reachability oracle. A separate witness check verifies actual path arcs,
common colour, distinct vertices and predecessor endpoints, or actual directed
triangle arcs and three distinct colours. Exhaustive tests fixed every coloured
spanning cycle with at most two nonzero arcs and every remaining chord choice,
using three colours: 19 tables at n=3, 1188 at n=4, and 396576 at n=5. All returned
valid witnesses. This bounded test is not the proof for arbitrary n or palettes.
The execution report includes its code digest and limits. It is a generator
observation, not a trusted verification receipt or UNSAT proof trace.

The tournament assumption matters: the sparse directed 4-cycle with word 0011
and no chords has neither a rainbow triangle nor any monochromatic path to a
predecessor. It is not a tournament and is not a counterexample to this lemma.
The known complete four-vertex off-hypothesis R07 mutation also has word 0011,
but has a rainbow directed triangle. It is therefore consistent with this
lemma and must not be used as a root counterexample.

The palette-three consequence gives direct exclusions for n=3,4, since
3(n-3)<n there. For n=12 the family is only a small subset of the frozen words;
no claim is made that these are new solver discharges or that the remaining
words are excluded. Finite n<=11 results, n=12 partial runs, and this structural
lemma remain distinct candidates. No EvidenceLink, Result or Solution is created.
