# Release and submission checklist

Status: **reviewed source release; publication verification is tracked in ASSIGNMENT_CHECKLIST.md**. Preserve the current local fallback. Do not publish from the full working tree: it contains machine/session metadata, caches and historical private paths. Use only the audited clean source candidate and inspect it before publication.

## Authoritative requirements and timing

Read directly from the supplied three-page CS4680 Prompt Engineering AI Assistant Project PDF (SHA-256 `9f98a70ee21c6fcfb7df6f808c1096d9e4e81e1ea236bc8718a5084417aa5add`). The PDF says **“See the date in Canvas”**, so it contains no explicit calendar deadline. The user separately stated midnight Pacific tonight; the working deadline is **midnight ending 23 October 2026 Pacific / 24 October 07:00 UTC**. Confirm Canvas's exact cutoff; midnight itself is 00:00 on 24 October Pacific. Latest user submission target: **23 October 10:30 pm Pacific /24 October 05:30 UTC**, worst case **11 pm Pacific /06:00 UTC**. Earlier publication/freeze targets are superseded. Reserve the final30minutes for link/form verification. These are user/planning context, not a date claimed from the PDF.

| Required item | Current evidence / remaining action |
| --- | --- |
| Practical problem and working AI MVP | Requirement-linked Python test review; real local Qwen inference and UI are implemented |
| At least two course prompt patterns, explained | Persona, few-shot and iterative refinement; `prompts.py`, UI inspection and `docs/PROMPT_PATTERNS.md` |
| Required usable UI and AI outputs | Browser review, clarification, stale-state and export workflows verified |
| Complete code/documentation GitHub URL | Published and verified anonymously: https://github.com/Prabscodes/test-evidence . Final checklist: ASSIGNMENT_CHECKLIST.md. |
| Published short demo video link | Script ready in `docs/DEMO.md`; record, edit, check strictly <120 seconds and publish after authorization |
| Live presentation/demo | Rehearse the real model wait, fixture distinction, prompt patterns, limitations and disclosed recording fallback |
| Submit project through Google Form | https://forms.gle/nMHp5owwYidszwt58 — GitHub link and short video; not submitted |
| Publicly hosted app | Optional in the rubric, now explicitly desired by the user; host/inference destination remains unconfirmed |

Design is required as part of the process but has no separate document submission in the PDF. Grading: problem relevance 10%, implementation 30%, prompt engineering 20%, UI/UX 10%, presentation/live demo 30%. Video is requested in the final semester week; confirm course scheduling in Canvas.

## Before the hard freeze

- [x] Preserve the working app/provider and all model failures; avoid speculative features.
- [x] Provide concise README, reproducible demo/model settings, architecture, prompt mapping and licensing notes.
- [ ] Finalize any bounded improvements using development examples, then run affected checks.
- [ ] Rebuild the candidate after the last change; a preparation ZIP is not the final freeze.
- [ ] Confirm application source license and video destination; repository owner/name/public visibility are approved.
- [ ] Confirm Canvas cutoff and required tonight fields against the actual course page.

## At freeze and before publication

- [ ] Stop feature/model exploration at the planned freeze. Keep the proven local fallback available.
- [ ] Run all 90 automated tests and DOM regressions; run bounded demo browser smoke. Record exact times/results.
- [ ] Verify an actual model review remains available; preserve previous genuine evidence if no new model call is needed.
- [ ] Rebuild with `python scripts/package.py` using the explicit allowlist; verify ZIP CRCs, manifest and absence of weights/caches/private metadata.
- [ ] Scan the clean candidate for secrets with redacted output. Review any findings; do not publish the whole development directory.
- [ ] Confirm clean extraction reproduces tests using isolated existing dependencies. No automatic dependency/model downloads.
- [ ] Review exact source candidate and license notes, then obtain publication authorization for that repository/destination.
- [ ] Create/push GitHub repository only after authorization; check a fresh clone's README/run commands and links.
- [ ] Record/edit the 90–110-second script; distinguish actual model calls, shortened waiting and deterministic demo fixtures. Verify duration <120 seconds, audio, legibility and no private data.
- [ ] Publish video only after authorization; check link access signed out or in an appropriate viewer session.
- [ ] Put the final GitHub/video URLs in the Google Form; review all fields, then submit only with authorization. Save receipt.

No deadline, GitHub publication, video or course submission is silently marked complete. Current technical results are in `docs/SUBMISSION_VALIDATION.md`; final actions remain for the owner/authorized publishing step.


Latest bounded usability update: [request UX validation](docs/REQUEST_UX_VALIDATION.md). 90 tests and desktop/mobile synthetic-transport parser checks pass, alongside preserved earlier actual-inference UI evidence; the older verified ZIP is preserved. New candidates remain preparation snapshots until the planned hard freeze.

Current timeboxed publication plan: [PUBLISH_PLAN.md](docs/PUBLISH_PLAN.md). User will narrate the under-two-minute video; prepare genuine screen footage, storyboard and captions without generated replacement narration.

Current evidence:90 tests, public-browser/container checks and12-case author-created frozen readout complete. Silent105second video and timed narration are ready; user narration and video publication remain pending. Repository publication status is tracked separately. See docs/QWEN27_VALIDATION.md and docs/PUBLIC_DEPLOYMENT.md.
