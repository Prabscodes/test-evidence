> Historical record below. Current finishing evidence: [27 October validation](FINISHING_VALIDATION.md), 93 application tests, structural workflow, partial scope notices and genuine current 4B review/refinement. Current publication state is in the assignment checklist and release receipt. Earlier 27B results are not current endpoint performance.

> Historical preparation snapshot. For the current90-test release and latest quality/publication evidence, see [assignment checklist](../ASSIGNMENT_CHECKLIST.md), [27B validation](QWEN27_VALIDATION.md) and [public deployment](PUBLIC_DEPLOYMENT.md). Older measured results below are preserved.

# Submission preparation validation — 23 October 2026

This is a **preparation snapshot**, not the final freeze, submission, or a broad accuracy claim. Changes for this preparation are documentation, explicit-allowlist packaging and a bounded browser check. At that snapshot the application Python/static source hashes matched both earlier sealed GPU profiles. A later, separately documented request-UX update changes UI/error wrappers; it leaves prompts, assessment guards and fixture semantics unchanged. See [current request UX validation](REQUEST_UX_VALIDATION.md). All original failures remain in the local development tree; selected unaltered synthetic raw failures are included in the source candidate. Private paths/startup protocols and executable environments are excluded.

## Current application checks

- `python -m unittest discover -s tests -v`: **50 tests passed in 2.778 seconds** (2.984 seconds external process wall time). Log: `tests/results/submission_preparation_v1/unittest.txt`.
- Clarification request regression: exit 0; 0.021 seconds wall time. DOM smoke: exit 0; 1.040 seconds wall time. Logs alongside the test log. Mocked DOM/provider checks are application tests, not model judgments.
- Real Chrome **149.0.7827.53** with existing Playwright: bounded separate demo server, **3.171 seconds** wall time, no model calls. Four demo samples, both clarification buttons, prior context only on Refine, exact citation selection, stale export blocking, AST-only upload workflow, immutable fixture execution despite uploaded edits, separate execution export, review JSON/Markdown downloads, actual prompt inspection and 390-pixel layout all passed. No page errors. `browser/summary.json` and screenshots record coverage.
- The browser check stopped only its own demo server on port 8766. Existing app/model on 8765/18081 and unrelated services were kept running. A new model experiment was not required for this release check.

The source candidate's extraction, tests, secret scan and manifest receive their own sidecar verification. Do not treat this page as proof of unexecuted future publication or final-freeze checks. Public copies of application logs replace private absolute paths with `<LOCAL_PATH>`; the original local logs are unchanged. No model output is rewritten to make it pass.

## Actual model evidence, kept separate

The already-installed Qwen3.5-4B BF16 profile used exact official revision `851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a`, vLLM0.25.1/g752a3a504, native PyTorch sampling, thinking disabled, 4 GiB CPU offload, context6144, one sequence, explicit512MiB cache, eager execution and seed42. Sampler: temperature0.7, top-p0.8, top-k20, min-p0, presence1.5, repetition1.0. Output cap1536; timeout300 seconds. Full portable settings and shard hashes are in `SETUP.md`. The original FlashInfer startup failure is retained locally; native sampling recovered the exact failing path without packages/drivers changed.

A bundled actual smoke review took **95.255 seconds** and identified omitted age18. Three later real-browser Qwen calls took **68.709**, **53.321** and **43.364 seconds**. The refinement rationale included an incorrect threshold statement; the subsequent Analyze abstained for insufficient citations. Raw responses are included under `tests/results/popos/qwen35_4b/`. Those calls are genuine model output, separate from deterministic samples.

The six frozen synthetic cases ran once per profile. Inputs/labels were frozen before Dolphin, excluded from model requests, and preserved; Qwen reused the set after labels were inspected. This is a **reused diagnostic comparison**, not new held-out accuracy, a representative dataset or independent adjudication. Same canonical app prompts/artifacts; runtime/precision/sampler/offload differ. No tuning followed the Qwen readout.

| Profile | Guarded matching labels | False support | False accusation | Unresolved | Latency |
| --- | ---: | ---: | ---: | ---: | --- |
| Dolphin3-8B Q4_K_M | 3/6 | 1 | 0 | 3 | median0.397s; 0.363–6.640s |
| Qwen3.5-4B BF16 | 3/6 | 0 | 3 | 0 | median47.784s; 37.669–92.378s |

Dolphin also had one malformed raw result rejected by guards. Qwen produced valid structured outputs but wrongly accused an explicitly retained empty-table case, an unspecified duplicate policy and a retained assertion with an injected comment. All six Qwen raw and guarded outcomes were potentially missing. Manual inspection found erroneous rationales even in a matching case. Exact quotations and narrow contradiction wording guards do not establish semantic truth. This is **not a clear reliability improvement**; neither profile is an approval gate.

Raw case outputs, scores, manual citation audits and original source snapshots are included without altering their judgments. Original seals reference additional full private launch/runtime protocols that are omitted from this public candidate. `SOURCE_MANIFEST.json` describes selected files and any metadata transformations. A public model-metadata copy removes only its local directory. Historic four-case development results and critic failures are also retained; they were used during tuning and must not be called held out.

## Remaining evidence limits

Single-analyst synthetic labels, single stochastic runs, no real-repository user study or competitor baseline, restricted context and latency, native Windows not verified, no public-service hardening. Models can invent policy, overlook table entries, misread assertions and follow misleading text despite prompts. Passing application tests says the implemented workflows behave as tested; it does not establish model correctness, novelty or adoption. Actual execution remains immutable bundled fixtures only.

## Submission form requirement correction —24 October2026

The live form at https://forms.gle/nMHp5owwYidszwt58 requires **Name, GitHub Repo URL, Demo Video URL and Google Slides URL**. Email is optional. Published URL (live app) is optional/highly recommended. The PDF does not explicitly require slides, but the form does. The required deck and verified viewer URL are pending with a separate worker. Narrated-video publication and authorized form submission also remain pending; prior technical validation and a packaged silent video do not establish final submission readiness. No application code or recorded evaluation result changes in this correction.
