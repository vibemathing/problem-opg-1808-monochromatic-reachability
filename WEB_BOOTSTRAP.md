# Web Research Bootstrap

- Repository: `vibemathing/problem-opg-1808-monochromatic-reachability`
- Repository binding: `verified`
- Repository database ID: `1358762635`
- Repository node ID: `R_kgDOUP0Siw`
- Default branch: `main`
- Visibility: `public`
- Canonical Problem: `problem:opg-1808-monochromatic-reachability`
- ProblemContract SHA-256: `7ad1410069206a73b3cfd2149fc75d1509efc664f180b0ac96ae1f0f36473e8f`
- Problem lifecycle: `active`
- Problem admission: `canonical_admitted`
- Harness suite: `harness-source:web-research-full` `1.1.1`
- Suite manifest SHA-256: `c615d53afae447ea46d8ec53b442c9514e87948676c8c448ecafb68b8f41175b`
- Harness snapshot SHA-256: `5df12d6ab6c26192caeac27700d64e44a4de778887011af84a90a847cd0398da`
- Channel: `chatgpt-web-github-issue-pr-writer`

## Required read order

1. `AGENTS.md`
2. `WEB_CHANNEL_PROFILE.json`
3. `HARNESS_SNAPSHOT.json`
4. `WEB_CONTEXT_BUNDLE.md`
5. `WEB_ACTIVE_SKILLS.json`
6. `problem-library/records/canonical-problems.jsonl`
7. `research/records/failed-routes.jsonl`
8. the current route and obligation packet named by the Issue
9. exactly the owner Skill files selected by `WEB_ACTIVE_SKILLS.json`
10. `WEB_OUTPUT_CONTRACT.json`

Return a `web-bootstrap-ack.schema.json` object before mathematical work. Hashes shown here are manifest-declared values; do not claim to have recomputed them in chat.

## AI-native writable route

After repository admission, perform the routine candidate transport end to end without project-added human handoffs:

1. Open or use one Issue labeled `web-research-question` for the bounded question.
2. Create branch `web/attempt-<attempt-suffix>`.
3. Add, revise, or delete files only under `research/artifacts/web-inbox/**`, `research/artifacts/candidates/**`, or `research/artifacts/source-notes/**`.
4. Commit real changes and open a PR using the web candidate template.
5. Monitor required checks and, when needed, rerun the existing candidate workflow.
6. Review and revise the candidate PR; this AI review is not independent mathematical review.
7. After transport checks pass, merge the candidate PR and write the next checkpoint.

Do not create repositories, direct-push the default branch, modify workflow/truth paths, force-push, cancel/dispatch Actions, or sign Evidence/Result. Follow only platform-mandatory confirmation UI; no extra human approval is required for routine candidate operations. Issue, PR, review, merge, Actions status, command exit 0, or model self-review never closes a mathematical obligation.
