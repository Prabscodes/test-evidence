# Submission Readiness Implementation Plan

**Goal:** Make the existing small Python change reviewer easier to understand and demonstrate against CS4680 requirements.

**Architecture:** Preserve inference, input limits, consent, defaults and review state. Improve static copy and expose the existing actual-template loader before a review. Keep runtime detail available through disclosure.

**Tech Stack:** FastAPI, vanilla HTML/CSS/JavaScript, unittest, Node.

- [x] Update `static/index.html`: identify students and developers reviewing one small function; explain that snippets, not repositories, are inputs; show Persona, Few-shot and Iterative refinement purposes with the existing `/api/prompts` loader in a globally accessible disclosure.
- [x] Keep provider/raw-result panels in Review; move only the existing prompt button/output to the global disclosure, preserving unique IDs and its existing listener.
- [x] Put verbose request-status explanation in a native details element while leaving progress, errors and status check visible. Add narrowly scoped CSS.
- [x] Add `docs/SUBMISSION_READY_RUNBOOK.md` with a timed genuine-inference walkthrough, actual pattern evidence, and explicit remaining publication/video checks.
- [x] Run the complete unittest suite and the three existing Node regression scripts. Check unique HTML IDs and prompt inspector placement.
- [x] Review diff and commit source/docs only. Public deployment, video verification and course submission remain separate checks, not inferred success.

Validation: 93 unittest tests passed in 7.476s with TE_PROVIDER=none outside the sandbox. All three Node scripts passed. Unique HTML IDs and pre-review inspector placement verified. Real browser/model checks are performed separately by the coordinating agent.
