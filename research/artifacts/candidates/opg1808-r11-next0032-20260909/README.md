# R11 next-0032: twenty-word solver-receipt increment

Verdict: `candidate_only`. State: `NONTERMINAL_CHECKPOINT`.
Problem ID: `problem:opg-1808-monochromatic-reachability`.
Target: `obligation:opg1808-root`; primary owner: `math-proof`.

Only the twenty original ordinals in `summary.json` were newly queried.
Per word, the order was cuts1000ms/seed251; UNKNOWN-only cuts4000ms/257;
then supported-R1000ms/251 and UNKNOWN-only4000ms/257. Original numbering
and the 7434-word SHA-256 are unchanged. No previously credited solver word
was rerun. Six physical controls are outside the original-domain ledger.

Actual results: cuts1s gave12 UNSAT and8 UNKNOWN; the8 cuts4s retries all
returned UNSAT. Supported-R1s gave20 UNSAT, so its4s stage was not executed.
Initial UNKNOWN ordinals7011,7013,7016,7017,7019,7020,7026,7030 remain in
immutable logs. All20 words have both-core UNSAT receipts. No original-domain
SAT occurred. Seven successful historical record audits reconstructed7158
UNSAT/276 UNKNOWN; exactly20 new ordinals give7178/256. Crosschecks are empty.
One preliminary record-audit wrapper failed before its audit because its CPU
hard cap was too low; a compatible bounded retry succeeded. The failure is
not a mathematical observation. Its traceback contains a local path and is
not published; its digest and error classification are retained.

All54 solver workers and11 parent groups exited0 with valid input-bound
footers. There were48 root queries (40 UNSAT observations,8 UNKNOWN), not40
new ordinals. Four SAT controls exported physical arc tables and passed the
frozen FIFO BFS and iterative Kosaraju/condensation checker; two negative
controls were UNSAT. The two encodings have different reachability cores but
share the native solver/interface and candidate-generation trust domain.

Recorded environment: Python3.13.5, native Z3 4.13.3.0, one solver thread,
library SHA-256
`7accc397d4ac387468b09489bdaff9d82bfac4ca6a7e339b8fbb2167edf9c1c0`.
Workers:768MiB AS, CPU38/39s, wall40s/external43s,1MiB per file. Parent groups:
CPU150/151s and wall150s, enclosed by160/161s CPU and160s wall limits.
Unified slice budget600s including inter-group pauses with50s reserve before
new work. Groups contain two ordinals. The sum of outer measured group
elapsed times was122.776895319s; that sum is not the whole conversation time.
Total measured child CPU was126.242625s. Output budget5MiB.

## Exact restoration and record audit (no solver query)

From this directory, use a new destination:

    python replay.py restored

The base64/XZ capsule restores378 exact public UTF-8 input/request/log/exit,
source and derived bookkeeping objects with per-object SHA-256 checks.
Only8 deterministic SMT INPUT bases are regenerated from pinned source;
their hashes and every full-query hash are rechecked. Solver OUTPUT is never
regenerated. The replay rechecks footers, per-word escalation order, physical
SAT controls, and all ten two-word batch snapshots. The clean replay actually
exited0 and reproduced full accounting SHA-256
`3752bf0b40e70541c3085c7a4faeb4f4895988eb95b483ea5ecfb00aba0442d4`.

This does not check an UNSAT proof. For a new solver replay, restore to an
empty location, retain originals elsewhere, and invoke the frozen driver in
an otherwise empty execution directory using its recorded runtime/config.
Existing request names are immutable and refuse overwrite. New UNKNOWN,
timeout, abnormal exit or missing footer remains unresolved.

## Mathematical and provenance limits

The separately frozen general minimum-counterexample F-cycle reduction and
one-way encoding soundness/completeness bridges remain required. No false
Gallai partition or arbitrary-model R/physical equality is assumed.
No structural pruning or canonical-word rule was introduced. There is no
new actual SCC/path witness. These are solver receipts, not native UNSAT
proof traces, trusted verifier receipts, EvidenceLink, Result or Solution.
Neither this slice nor a complete finite n=12 classification closes the root.
`best_verified_result=none`; trusted closure remains absent.

Historical complete capsules remain separate provenance dependencies. This
release records the audits actually performed; it does not claim to include
all older raw logs. The supplied and landed atomic25/next0031 executions are
not merged into one query history. Their outgoing frontier hashes agree.
M01/R04 missing original outputs were not reconstructed.

## Transport and exact next input

Actual fresh base: `9640427b7ae807d85021828f23a73158781213ef` (PR19 merged).
Branch: `web/attempt-opg1808-r11-next0032-20260909`.
Exactly one new packet; old packets and files are unchanged. The final Issue3
comment records actual PR/check/merge receipts; CI is transport only.

All256 remaining IDs are in `unresolved-ordinals.json`, with matching words
and complete13-shard continuation in `next-shards.json`. The next shard is
r11-next-0033, first ordinal7034/001200212012. It has NOT been executed here.
