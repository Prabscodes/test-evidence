# CS4680 rubric audit and guided workflow —26 October2026

This is an engineering/UI review, not a grade prediction, accessibility certification or model accuracy evaluation. The existing app was inspected in Chromium before changes. A scoped local branch retains the FastAPI/vanillaJS architecture and the original review contract.

| Rubric | Existing evidence | Observed gap and bounded change | Remaining limitation |
| --- | --- | --- | --- |
| Problem relevance10% | Explicit requirement compared with before/after Python source/tests; evidence-linked judgments | Explain the boundary example at the entry point; load five editable sections with one click without sending a request | User relevance/adoption study not performed |
| Design/implementation30% | Server-owned line citations, AST-only upload inspection, strict JSON guards, separate immutable fixture execution, stale/request locking and public privacy controls | Preserve these boundaries; add predictable result/error focus and navigation without a new API, prompt or framework | Current configured local27B endpoint is offline; configuration is not readiness |
| Prompt patterns20% | Persona, few-shot and iterative refinement already implemented and inspectable | Keep template inspection and clarify previous-review context versus authoritative clarification | Prompt patterns do not establish semantic correctness; no tuning or new benchmark here |
| UI/UX10% | Before/after inputs, loading timer, reports, clarification and separate exports existed; baseline had no horizontal mobile overflow | Added guided start, described field limits/content, unique upload labels, filled-section summary, skip/workflow links, 3px visible focus, 44px controls, clearer status legends, next actions, reduced motion and responsive typography | Browser keyboard/layout/contrast checks cover specific flows; no screen-reader user study or full WCAG audit |
| Presentation/live demo30% | Genuine earlier recorded27B workflow,105second silent edit and timed narration exist; eight-slide PPTX prepared separately | Guided example supports a predictable explainable workflow; demo is hand-authored and never silently promoted to inference | Native Google Slides URL, user narration, published video and form submission remain unverified; no new live model demo while endpoint offline |

## Changes and acceptance

- The quick-start action loads the bundled boundary example, clears prior review context and focuses the requirement. It never calls an LLM or auto-submits. Custom inputs remain editable.
- Inputs have associated descriptive help and explicit limits; missing authority is allowed and should remain unresolved. Upload controls have distinct accessible names and visible focus on their labels.
- Successful current reports focus the judgment heading. Citation controls focus and select original lines. Uncertain transport errors focus the error, preserve inputs, block review retries and require an explicit status check. Old reports and exports stay stale after changes or failure.
- Suggested next actions derive only from displayed statuses and ask the human to inspect/clarify. They do not validate claims or change judgments. Static observations, labelled demo/model judgments and executed fixture evidence remain separately named and exported.
- Provider status says configured/readiness not verified. No automatic readiness generation, GPU allocation, service restart, model download, paid call, public endpoint or assignment submission was introduced.
- Elapsed timers remain non-live screen-reader regions; request status is announced without invented percentages or a per-second duplicate announcement.

## Verification

- New browser acceptance first failed on the unchanged UI with `AssertionError: Missing guided example action`. This evidence predates implementation.
- Full existing application regression run: **90 tests passed in7.819s**. No model calls. Existing Node clarification, DOM and six request-lifecycle checks pass.
- Real Chromium149.0.7827.53 browser flows: actual labelled-demo review, clarification/refinement, citation selection, JSON/Markdown exports, actual immutable fixture execution and separate execution export; guided loading sends zeroPOST requests.
- Actual keyboard/focus assertions: skip link, workspace, requirement after guided load, current judgment, citations, clarification and errors. Unique upload labels and all six textarea help associations checked.
- Layout: no page horizontal overflow at320,390,768,1440pixels and200% browser CSS zoom. Representative before/after desktop/mobile screenshots retained privately for review.
- Sampled32 visible key text/background combinations meet the applicable4.5:1 or large-text3:1 thresholds; minimum observed5.06:1. This is sampled contrast evidence, not comprehensive accessibility conformance.
- Explicitly simulated transport: slow request, duplicate clicks, interrupted fetch, unavailable provider and late response after edited inputs. No automatic retry, stale result export or browser exception observed. These paths are not live inference evidence.
- Public-mode browser regression uses a synthetic provider only: consent beforePOST, consent reset on configuration change, forwarded-header spoof resistance, source/key-safe failures, provider absence fails closed, stale exports and mobile layout all pass. No external API/GPU calls.
- Initial browser test used string predicates that violated the existing strict CSP. The harness was corrected to function predicates; the app's CSP was not weakened.

Reproduce from this checkout with existing installed dependencies: run `python -m unittest discover -s tests -v`; `node tests/scripts/clarification-regression.js`; `node tests/scripts/dom-smoke.js`; `node tests/scripts/request-lifecycle.js`. For UI QA, start a separate `TE_PROVIDER=none python -m uvicorn app:app --host 127.0.0.1 --port 18766`, then `python tests/scripts/uiux-browser.py --url http://127.0.0.1:18766 --out /tmp/test-evidence-uiux-browser`. Playwright/Chromium are separate development tools, not new application dependencies. Use an unused loopback port without stopping its owner.

## Assignment status and publishing scope

The form requires Name, GitHub Repo URL, Demo Video URL and Google Slides URL. Email is optional; Published URL is optional/highly recommended. An existing validated eight-slide PPTX is handled separately; native Google Slides sharing remains pending connection. Do not duplicate the deck or imply it has a submitted URL.

Earlier public authorization covered the reviewed release and bounded documentation corrections. This new UI release is prepared as a reviewed local commit and reported before an uncertain public push. Existing published evidence remains unchanged until approval covers the new release. No public deployment or course submission occurred. The local app at http://127.0.0.1:8765 serves the updated static files after a reload; no process restart was needed. One actual request to its configured loopback model returned503 in the served-flow check, with visible error focus, no accepted report/export, no automatic retry and manual status recovery. See tests/results/uiux_v1/served_model_offline.json. The model service was not started or reconfigured.

Portable verification summaries and logs are in `tests/results/uiux_v1/`. Before/after screenshots and original private operational traces remain on the PC and are excluded from the source manifest.

Packaging audit caught local dependency paths in the passing-test log. Only the portable log copy replaces those paths with `<LOCAL_PATH>`; the original private log and test outcomes are unchanged.
