# Review workflow implementation plan

Goal: make the existing evidence-review workflow understandable and keyboard/mobile usable without changing semantic judgments or execution boundaries.
Architecture: retain FastAPI endpoints, vanilla JS request lifecycle, server-owned citations, demo/live distinction and immutable fixtures. Add guided loading, input help, evidence navigation and accessible result/error focus to the current page. No prompt/model/schema changes.

The user authorized implementation and rubric/UI audit. This is scoped inline execution; a new wizard or a framework migration would add navigation/state risk without solving the observed gaps.

- [x] Inspect rendered desktop/mobile baseline and source; preserve before screenshots internally.
- [x] Verify host readiness: app responds; configured local27B endpoint is unavailable. No service/model startup or resource changes.
- [x] Add browser behavior regressions and observe failure on the current UI: quick start, labels/help, focus, next actions and stale exports.
- [x] static/index.html: add skip/navigation links, guided-example loading, field help/counts, labelled regions, result summary/next action and explicit three evidence types. Keep existing IDs/endpoints.
- [x] static/app.js: share example loading; announce populated inputs; label configured provider as readiness unverified; focus current results/errors; offer status-based human next actions; block onboarding during active requests. Never auto-submit or retry.
- [x] static/style.css: improve text contrast/size, visible focus, file-input focus, 44px controls, narrow layouts and reduced motion. Preserve light visual identity.
- [x] Run existing 90 application tests and three Node regressions; run real browser actual demo/refinement/fixture/export and synthetic delayed/interrupted/error/late-response paths. No new semantic evaluation.
- [x] Capture after desktop/mobile screenshots and check keyboard, 320/390/768/1440 widths, 200% zoom and computed key text contrast.
- [x] Document exact rubric gaps, changes and evidence; correct submission status to include existing PPTX and pending native Slides/video/form.
- [x] Review diff, refresh source manifest and prepare a local commit after manifest verification. Public push requires confirmed scope: earlier authorization covered the audited release and docs; this new UI release will be reported before an uncertain public write.

Acceptance: loading an example never calls a model; no demo is labelled inference; fields and uploads have unique accessible labels/help; successful current results receive focus; edits and mode changes keep exports stale; busy/interrupted requests cannot duplicate work; mobile has no page overflow; errors guide recovery without leaked source/secrets. Static/LLM/fixture evidence remains distinct. Model readiness and semantic accuracy are explicitly limited.
