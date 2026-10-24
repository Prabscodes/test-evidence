# Architecture and trust boundaries

Browser → FastAPI validation → isolated static parser + optional model inference → schema/citation guard → evidence cards/export.

A separate button → fixed bundled fixture ID → immutable app-owned source/tests → fresh temporary directory → fixed Python unittest command → structured results.

## Modules

- `app.py`: API, streamed body limit, static assets, single analysis concurrency.
- `analysis.py`: typed inputs/model response, exact full-line quote validation, mandatory authority/after-test citations for non-unresolved claims, hashes, deterministic demo distinction.
- `ast_check.py`: syntax-only worker, bounded CPU/memory/length; parent wall timeout.
- `provider.py`: local Transformers or explicitly opted-in OpenAI-compatible provider; no model tools/actions; secrets server-side.
- `prompts.py`: persona, few-shot, iterative refinement visible through `/api/prompts`.
- `fixtures.py`: trusted finite execution, fixed commands, environment stripping, timeout, output caps and assertion/error distinctions.
- `samples.py`: four synthetic demonstration cases, including benign refactor and no-spec control.
- `static/`: dependency-free editable UI and safe text-only rendering.

## Important non-guarantees

Citation validation ensures literal grounding, not semantic entailment. A supported LLM interpretation can still be wrong. Exact input hashes establish identity, not correctness. Passing finite tests is not exhaustive. Two independently implemented checks may share a mistaken requirement interpretation. No model confidence percentage is returned.

The fixture runner is not a security sandbox; its safety depends on the immutable app-owned allowlist. Do not add a route accepting source, paths, shell text, or import/plugin names. Real repository execution requires a separate hardened design before any collection/install/test run.

Local service has no authentication and is intended for loopback single-user use. Inference loading and large local models can consume significant resources. HTTP provider timeout and generation limits are bounded, but model loading is not a hard wall-time-isolated operation. No claim of production security is made.

## Model contract v2: server-owned evidence IDs

Model input consists of structured line records (`id`, `text`). Stable IDs such as `requirement:L1` are generated only from original artifact position. IDs appearing inside text do not create records or authority. Model output selects `evidence_ids`; the server resolves each to the exact original nonblank line. Foreign artifact names, malformed IDs, absent lines and blank lines cause abstention. Non-unresolved assessments still require both authority and after-test citations.

The model emits `test_support: checked|gap|unknown`, explicitly about **after-test support**, not whether a bug claim has evidence. The server maps this to the UI's supported/potentially_missing/unresolved vocabulary. Resolved citations do not establish semantic entailment, and the model can still misinterpret correct lines. Earlier actual 0.5B and 3B failures are preserved under `tests/results/` rather than discarded.

## Audit safeguards

Editing any analyzed input (including clarification) marks the report stale and disables export/citation navigation until reassessment. Controls are disabled during requests and response versions are checked before rendering. Fixture displays name the immutable bundled ID, never imply edited snippets were run. Only one trusted fixture can execute at a time.

Only explicit app-authored validation messages are returned; arbitrary provider exceptions, including ValueError, receive a generic error. HTML angle brackets are escaped in Markdown exports, while in-app content uses text nodes.

A narrow check additionally abstains from `supported` when cited after-test evidence contains no explicit assertion/expected-exception signal. Imports/comments alone are not sufficient after-test evidence. This is deliberately an **evidence limitation**, not a semantic weakness detector: helper, implicit and unusual valid oracles may require human review. The guard does not establish that a cited assertion checks the right value. If both requirement and clarification are absent, a deterministic authority guard withholds model-invented obligations and asks for expected behavior; raw inference remains inspectable.

Prompt v3.1 explicitly separates equality-boundary obligations from flanking-region checks and requires actual equality-case evidence before reporting the boundary checked. This is a general prompt criterion, not a hardcoded domain detector. A development failure motivated the refinement; only new, separately held-out evaluation could assess generalization.

## Narrow rationale consistency guard

If the model's own rationale explicitly states that a requirement/specification/contract does not specify an outcome, is ambiguous, or leaves behavior undefined (or says an expected policy/outcome is unspecified), a deterministic wording guard withholds the judgment. The UI shows unresolved with a neutral policy-clarification label, a mandatory question and `deterministic_consistency_guard` origin. Original raw output remains inspectable. It matches no development-case names or numeric thresholds.

This catches a limited internal contradiction; it does not verify authority, entailment or correctness, can miss paraphrases, and may abstain unnecessarily. It must not be counted as improved model accuracy or evidence that the original model judgment was correct. Positive tests use delivery, retries, image size, caching and bookings; negative tests distinguish missing test coverage and explicit negation from missing authority.


## Request lifecycle and evidence labels

`/api/status` includes only whether the app review lock is held and elapsed seconds from a monotonic start time. It does not expose submitted content, probe provider readiness or promise that an upstream generation stopped. The synchronous review retains its lock after the client disconnects until that application call actually returns; another review receives429. An actual loopback TCP-disconnect regression verifies this behavior. After an HTTP provider timeout, upstream work may still continue even though the application call ended.

The browser disables duplicate actions, displays elapsed wait (no percentage), and never automatically retries a POST. Uncertain transport loss and provider failures require an explicit read-only status check before another review. App-idle status is not proof that a timed-out provider has stopped. Reloading can reveal an active app request but does not recover its response. There is no unsupported cancel button. Changes to artifacts or review mode invalidate old exports; late responses for edited inputs are discarded. A failed new request leaves the old review labelled previous/stale with export disabled.

Known HTTP provider failures map to fixed app-owned messages/status codes: timeout504, unreachable/model-not-found503, input rejection400, and access/otherHTTP failures502. Provider bodies, URLs and credential exceptions are not echoed. Unknown errors retain the generic sanitized502 behavior. The output groups explicitly distinguish fallible model/demo judgments, syntax/assertion-count static inspection without execution, and separate immutable bundled execution evidence.
