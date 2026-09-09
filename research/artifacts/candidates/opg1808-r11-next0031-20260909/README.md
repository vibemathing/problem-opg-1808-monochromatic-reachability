# R11 next-0031: twenty-word bounded continuation

Verdict: `candidate_only`. State: `NONTERMINAL_CHECKPOINT`.
Repository: `vibemathing/problem-opg-1808-monochromatic-reachability`.
Problem: `problem:opg-1808-monochromatic-reachability`.
Attempt: `attempt:web-20260906-opg1808-a01`; historical route identity:
`route:directed-gallai-decomposition-v1`; graph: `graph:opg1808-initial-v1`.
Target: `obligation:opg1808-root`. Coordination Issue #3.
Read main: `fc5a27164ed100679c0e37409b569aacf78f4114`.

## Frozen scope and actual observations

This increment queries ONLY the twenty original ordinals in r11-next-0031:
6981,6983,6984,6986,6988,6989,6994,6995,6997,6998,6999,7000,7001,7002,
7003,7004,7006,7007,7008,7009. No previously credited root query was rerun.
Each word uses cuts1000ms/seed251, cuts4000ms/seed257 only after UNKNOWN,
then supported1000ms/seed251, supported4000ms/seed257 only after UNKNOWN.

All twenty returned UNSAT under BOTH frozen cores. Cuts1000 gave 15 UNSAT
and 5 UNKNOWN (6983,6984,6988,7001,7008); precisely those five returned UNSAT
at4000ms. Supported1000 gave20 UNSAT; supported4000 was not executed.
Thus45 root queries contain40 UNSAT and5 historical UNKNOWN observations,
not40 new ordinals. Six additional controls are outside the root ledger:
two RGB rainbow-allowed SAT, two six-vertex four-colour SAT, and two
rainbow-forbidden three-vertex UNSAT. All four SAT arc tables were checked
by frozen FIFO BFS plus Kosaraju SCC reachability. No original-domain SAT.
All51 workers and the parent exited0 with complete, input-bound footers.

The physical domain is nonempty finite simple tournaments with palette
{0,1,2}, not necessarily using every colour. Different targets may use
different monochromatic path colours. The general minimum-counterexample
F-cycle reduction is a separate prerequisite, not a conclusion of this slice.
The false directed-Gallai partition is never a premise. Forward-closed-set
separators and supported transitive R use distinct reachability cores but
share the native solver, interface and candidate-generation trust domain.
No arbitrary model equivalence is asserted.

## Recomputed ledger and provenance

Six actually rerun record audits, without rerunning old solver queries,
reconstructed the supplied capsule chain through7138 UNSAT/296 UNKNOWN.
Adding exactly20 new ordinals gives7158 UNSAT/276 UNKNOWN; SAT, timeout,
missing-footer and never-queried current ordinal classes are0. Crosscheck
pending is empty. Historical failed or UNKNOWN observations are retained.
Per-word snapshots and the full new event ledger are in the transparent
capsule. The supplied local atomic25 capsule and main's landed PR18 payload
are DISTINCT executions with identical outgoing ordinal/word hashes;
their individual observation counts are not silently merged.
The historical full capsules remain provenance dependencies. This new
increment does not re-upload them or pretend its baseline summary replaces
all historical raw logs. Missing M01/R04 outputs were not reconstructed.

Frozen full-word SHA256:
`705031dc21d6a7ffa37bf8ad04ec93615531fad0415f9bd7366c71d3d4ede850`.
The complete new276-ordinal list and its word list are separate readable files.
The next source shard is r11-next-0032, first7010 / 001200120202; it is not run.

## Executed limits

Python3.13.5, native Z3 4.13.3.0, library SHA256
`7accc397d4ac387468b09489bdaff9d82bfac4ca6a7e339b8fbb2167edf9c1c0`.
One solver thread. Workers:768MiB AS, CPU38/39s, internal wall40s,
external43s (outer CPU42/43s), per-file1MiB. Parent: internal360s with45s
safety reserve, external380s, internalCPU350/351s, outerCPU375/376s,
768MiB and cumulative childCPU budget300s. Total output5MiB, high-water4.5MiB.
Parent measured67.59340581599997s and exited0. Limits, exact commands,
versions, source/input/log hashes and footer bindings accompany each event.
An initial container streaming launch was unavailable BEFORE any query
started; the explicit bounded supervisor then executed the recorded run.
That launch error is not a mathematical outcome.

## Portable record restoration and later solver replay

capsule-index.json and six capsule-part-*.txt files encode322 original
public UTF-8 objects using xz+base64. Each object's length/SHA256 and the
whole catalog hash are checked. Included are exact runtime cores, query
requests and all actual outputs/exit/footer records, not hidden reasoning.
Only deterministic SMT INPUT bases are regenerated from pinned builders;
all8 generated base hashes and every full-query hash are compared to the
original headers. Solver OUTPUT is never regenerated during record audit.

From this directory, in a separate disposable workspace:

    python replay.py --output ../record-check --audit

This restores recorded bytes and checks inputs, footers and physical SAT
controls WITHOUT solving. The clean check actually exited0, restored322
record objects plus8 generated input bases, and reproduced the full new
accounting exactly. This is a record audit, not an UNSAT-proof checker.
For a deliberately new solver execution, use a DIFFERENT empty workspace:

    python replay.py --output ../new-run --prepare-run
    cd ../new-run/research/artifacts/candidates/opg1808-r11-next0031-20260909
    python launch.py

The latter commands were not executed again during packaging. They retain
the same bounded20-word scope. A later replay can differ in timing/UNKNOWN
outcomes; never overwrite old receipts or count UNKNOWN as UNSAT.

## Open assurance and transport boundary

No new canonical-word pruning or witness-free structural rule is generated.
No native UNSAT proof trace, trusted attestation, statement-faithfulness
success, EvidenceLink, Result, Solution or general root closure is supplied.
best_verified_result=none. The exact-encoding and F-cycle semantic bridges,
trusted replay/proof checking and admission remain separate obligations.

PR18 has already merged the prior R11 packet. This increment therefore uses
fresh main and ONE new immutable packet; it does not revise PR18's packet,
combine historical packets, rewrite refs, or edit protected truth paths.
Transport checks and merge do not add mathematical assurance.
