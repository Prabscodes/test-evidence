# Structural workflow redesign —26 October2026

The preceding03abeeb commit was visual polish. The user rejected it as insufficiently structural. It remains a rollback point, along with2a63673; no commit is rewritten.

Observed weaknesses: a landing page and editor shared one long document; requirement/source/tests formed a large undifferentiated form; report and input lengths competed for attention; every finding/evidence quote expanded at once; clarification sat after long evidence; citation navigation required scrolling through the form; navigation did not describe a distinct task state.

Chosen architecture: three routes in the same local tab, Start → Inputs → Review, without a mandatory wizard. Start chooses a bundled example or an own-change draft. Inputs keeps requirement authority visible beside Source/Tests tabs with before/after comparisons. Review selects one finding, with server-owned citations disclosed progressively and clarification beside it. Status/limits remain visible; provider/prompts/raw/static/execution/export tools remain inspectable without dominating findings.

Navigation is presentation state only. Browser back/forward and view switching preserve DOM inputs, selected artifact and selected finding; no localStorage or remote persistence. Refresh does not preserve draft. Opening a route does notPOST or infer. Citation navigation selects the correct editor and exact lines. A late result must not steal focus/navigation when the user has returned to inspect inputs. Replacing a nonempty differing draft with an example asks before clearing it.

Selected finding context is a navigation aid; clarification still applies to the complete review. No hidden finding-derived authority is inserted into prompts. Status is not a numeric confidence score. No backend/API/prompt/schema, arbitrary-code-execution or provider-consent boundary changes. Model remains offline. No services or GPU work and no public push.

Acceptance test is tests/scripts/workflow-browser.py. It was written first and failed on the previous UI with Missing focused start view. Verify structural state, native back/forward, draft-replace cancellation, artifact-tab keyboard navigation, finding selection, citation/editor focus, current/stale exports, refinement payload, duplicate/interrupted requests and responsive layouts. Preserve original raw model evidence and clearly label simulated transport separately from actual deterministic demo/fixture execution.

## Actual structural differences

| Before03abeeb | Current workflow |
| --- | --- |
| Landing content and all inputs/results in one long document | Dedicated Start, Inputs and Review views with explicit navigation |
| Four code/test fields in one extended form | Requirement authority beside Source/Tests tabs; before/after pair in each tab |
| All finding cards and full quotations expanded together | Finding navigator, one active reader, native citation disclosures and exact editor jump |
| Clarification follows the report | Adjacent refinement panel tied to selected finding context; global clarification scope remains explicit |
| Tools compete with the main report | Export, provider/raw/prompts, static observations and immutable execution disclosed separately |
| Scrolling used as navigation | Browser back/forward and route buttons retain draft, selected tab and finding; mobile section jumps |

The primary input action is Review change. In Review, Refine review is the primary follow-up action; the redundant input action bar is removed. New inputs never auto-submit. Selecting a finding does not create authority or a model request. No numerical confidence score is invented.

## Verification and observed fixes

-90 existing application tests passed in7.857s. Python backend, API contracts, prompts, provider configuration, strict citation/JSON guards and fixture runner are unchanged.
-Existing clarification and DOM regressions pass; request-lifecycle coverage now has seven passing cases, including locking the sample selector while a request outcome is uncertain.
-Real Chromium149.0.7827.53: actual hand-authored labelled-demo review/refinement and JSON export; actual allowlisted fixture and separate export. Source and test data retain original request keys. No successful current live inference is claimed.
-Structural regression passes three-view navigation, back/forward, draft/tab preservation, replace-confirm cancellation, keyboard tab switching, selected-finding retention, citation selection in the correct editor, whole-review refinement context, stale exports across views and a late result not stealing the current view.
-Controlled transport tests cover multiple findings, interrupted/duplicate requests and late completion; these are explicit synthetic responses, not accuracy evidence. Public synthetic-provider checks pass consent/reset across navigation, safe errors/exports/logs, forwarded-header-resistant limits, absence fail-closed and mobile layout.
-All views have no page overflow at320,390,768,1024,1440pixels. Keyboard skip, associated labels/help,3px focus,32 visible44px controls,200% CSS zoom, reduced motion and unique IDs pass.47 sampled text/background combinations pass, minimum5.66:1. No external asset requests. These are bounded checks, not comprehensive accessibility certification.
-The first structural regression caught a body-level navigation listener stealing focus; selectors now bind only navigation buttons. A separate red test reproduced delayed file reads overwriting newer typing; version/value checks now discard that read with a visible explanation. A failing lifecycle test caught sample replacement during uncertain transport; the selector is now locked until explicit status recovery. Original private red logs remain; portable excerpts are included.
-A screenshot-path bug in the new harness was corrected; application behavior was not changed to accommodate it. Native screenshot capture waits for short control transitions to settle. No model waits were accelerated.

Evidence: tests/results/workflow_v3. Before/after screenshots are actual rendered local UI using the bundled hand-authored demo, delivered separately. Model endpoint remains offline. Loading/failure/multi-finding simulations are not presented as live inference. Draft data is kept only in the current tab; refresh does not persist it. Public push, native Slides link, voiced-video publication and form submission remain unverified/pending.

Reproduce frontend acceptance with Playwright/Chromium available: start a separate loopback `TE_PROVIDER=none python -m uvicorn app:app --host 127.0.0.1 --port 18770`, then `python tests/scripts/workflow-browser.py --url http://127.0.0.1:18770 --out /tmp/test-evidence-workflow`. The previous uiux-browser.py entrypoint delegates to this current test; the original is preserved in03abeeb and its recorded evidence. Other scripts: workflow-accessibility.py and workflow-public-browser.py expose explicit CLI arguments; no dependency or model downloads are automatic.

The same local preview http://127.0.0.1:8765 serves the new static frontend after reload. Rollback commits03abeeb and2a63673 are preserved, and local original static files are backed up privately. No app/model/ComfyUI/Polaris service was restarted or reconfigured. No public push occurred.
