# R11 atomic25: five crosschecks and one twenty-word shard

Verdict: `candidate_only`. State: `NONTERMINAL_CHECKPOINT`.
Problem: `problem:opg-1808-monochromatic-reachability`.
Attempt: `attempt:web-20260906-opg1808-a01`; target: `obligation:opg1808-root`.
Historical Route: `route:directed-gallai-decomposition-v1` (identity only).
Graph: `graph:opg1808-initial-v1`; coordinating Issue: #3.

## Exact scope and outcome

This increment contains the actual new replay of supported-R at 4000ms/seed257
for original ordinals 6931,6934,6935,6936,6937, and both frozen encoding cores
for the twenty ordinals in r11-next-0030 starting 6954 / 001120201102.
The five crosschecks are complete and do not add to the credited count. The
twenty new words returned UNSAT in both cores. Cuts at 1000ms/seed251 yielded
15 UNSAT and 5 UNKNOWN; its five UNKNOWNs returned UNSAT at 4000ms/seed257.
Supported-R at 1000ms/seed251 yielded 20 UNSAT. All 17 workers (11 query,
6 control) exited zero with complete requests and footers. No original-domain
SAT, external timeout, missing footer or partial request occurred in this slice.

The reaudited incoming candidate ledger was 7118 UNSAT and 316 UNKNOWN; adding
only these twenty gives 7138 UNSAT and 296 UNKNOWN. The other four current
ordinal classes are zero. Historical UNKNOWN attempts remain in the logs.
Crosscheck pending is empty. Next source shard is r11-next-0031, starting
ordinal 6981 / 001120211022. The full increasing list is referenced by execution.json and stored in
unresolved-ordinals.json; its SHA-256 is
51cb8dbb0a05234eee3837ea1e8cf24b10cfecd001884aaaf931d53ac5f0e0f5.
No complete n=12 exclusion or unbounded root conclusion is asserted.

## Replay and physical checks

From this directory, with ordinary non-optimized Python:

```sh
python replay.py
python replay.py --restore restored
python replay.py --replay a000-supported-4000 --output fresh-crosschecks
```

The default checks exact source pins, every formula-plus-word input hash,
request, output/footer, exit receipt, and physical control. It loads no solver.
The normalized event rows and frozen decoder reproduce all 85 original public
request/log/stdout/stderr/receipt objects byte for byte; this was compared with
the original files in the current run. Normalization is storage, not a new run.
The --replay option performs a NEW bounded query group and refuses an existing
output directory. UNKNOWN or a missing/failed footer remains unresolved.

The recorded environment is Python 3.13.5 and native Z3 4.13.3.0, with the exact
library SHA-256 in execution.json. A repeat environment needs that library
available to the frozen NativeSolver loader; no environment installation or
trusted execution is implied. Every worker limits address space to 768MiB,
CPU to 38/39 seconds, internal wall to 40 seconds, outer wall to 43 seconds,
and each output file to 1MiB. One Z3 thread is used. The atomic groups were
launched separately, not as one 900-second parent process. The first five-word
wrapper had no extra parent CPU limit; its worker limits still applied.

The cuts core uses forward-closed sets containing a source and excluding its
predecessor. Path induction makes this a certificate of physical nonreachability;
actual reachable sets prove the required completeness. The supported core uses
transitive R supersets and physical first/last support. Physical reachability is
contained in R, so its negative predecessor pairs are physically reliable. No
arbitrary model equivalence with exact closure is claimed. Both cores share the
native solver and generator trust domain. The general minimum-counterexample
F-cycle bridge remains the separately frozen R05 proof obligation.

Each positive control has a complete actual arc table. The frozen FIFO BFS and
Kosaraju checker recomputes per-colour reachability, directed rainbow triangles,
monosources and predecessor failures. Controls are outside the original-domain
ledger: RGB omits the rainbow ban; the six-vertex control allows four colours.
Restoring the RGB ban is the negative control. There is no graph to reconstruct
from UNSAT: negative results are solver receipts, NOT native proof traces.
No new word-family deletion is credited without a physical path/SCC witness.

## Baseline and transport provenance

The five baseline audit exits are in baseline-audit-chain.json. They audited
accessible original R10/R11 input/exit/footer capsules without rerunning closed
queries. Those historical capsules are not replaced by this compact audit chain.
This directory provides a self-contained replay of the NEW atomic25 increment,
not a trusted verifier. Older R06/R07/R10/R11 complete attachment transports are
separate unfinished dependencies and are NOT claimed delivered by this increment.
Existing R11 branch notes and their separate run summaries are retained unchanged.
Only the existing R11 inbox path is used; no second packet is added.

No old missing M01/R04 output was reconstructed. No records, verifier registry,
Harness, schema, workflow, EvidenceLink, Result or Solution was changed. Admission
requires an appropriate registered verifier, statement-faithfulness review and
closure gate; none has supplied a successful receipt for this candidate.
