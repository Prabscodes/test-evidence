# Duplicate-key rejection and durable evaluation transport

## Parser behavior

Previously, the live Pydantic JSON parser silently kept the last duplicate object member. Two conflicting `test_support` values could therefore yield a resolved judgment based on key order. Ignored nested citation/extension objects also passed through without a duplicate check.

The application now checks decoded object keys recursively before its unchanged schema validator. Duplicate keys at every depth, including escaped-equivalent names and identical repeated values, make the entire model assessment unresolved with an explicit duplicate-key warning. No conflicting judgment or citation is selected. Existing JSON/schema rules and the existing fenced-JSON path remain; no permissive repair was added and semantic prompts are unchanged. This is a parser contract, not a semantic truth verifier.

Rejected and valid raw output is returned unchanged in `provider.raw_response`, with `raw_response_sha256`. The former silent 20000-character truncation was removed so exports preserve the complete provider-returned text. Raw output remains untrusted, rendered as text, and never executed. Provider/model metadata, artifact hashes and actual prompt provenance remain available in JSON exports. Markdown reports show the unresolved finding; JSON is the complete audit export.

Nine focused tests cover contradictory status duplicates in either order, nested citation keys, escaped-equivalent keys, top-level duplicates, identical repeats, ordinary objects with the same names at distinct depths, existing fenced JSON, invalid JSON without repair, and long raw-output preservation. Before the fix: seven assertion failures across nine tests; after: all nine pass. The full suite now has 90 passing tests, including seven isolated durable-transport tests. These use synthetic responses, not accuracy evidence.

A real desktop/mobile browser exercised the app and provider HTTP path against a labelled synthetic loopback endpoint: valid review followed by duplicate-output abstention, visible warning, exact raw text/hash, JSON/Markdown exports, refinement and stale export blocking. No browser errors or mobile overflow; no LLM generation. Logs, screenshots and exports are in `tests/results/duplicate_json_v1/`. Historical semantic results/seals were not replayed or rescored under the new parser.

## Why the old evaluation lost a response

The old runner saved a request record only after `client.post()` returned and response JSON was parsed. It had no durable pre-dispatch intent, and its foreground client was attached to a tool session. After the previous turn ended, that session was unavailable and the process was absent; H04 had started but no response was saved. Its terminal exit status was not captured. No kernel OOM entry was found in the relevant window, which does not prove a particular termination signal. Tool/turn lifecycle termination is suspected, not established as the exact external cause. The proximate recording failure is established by the runner code: a client disappearance before the post-return save leaves no raw receipt.

The uncertain H04 request was never repeated. Its unavailable result remains in the original sealed evaluation, which failed its gate. No retrospective recovery or invented response is claimed.

## Future evaluation worker

`scripts/durable_request.py` sends exactly one explicitly configured loopback request. It creates a private new attempt directory, commits the request and dispatched state with fsync before sending, stores response-body bytes before downstream JSON/model interpretation, then commits a hashed receipt. HTTP success is not model-validation success. Transport failures remain uncertain; an existing attempt directory is always refused before any request, including completed or interrupted attempts. There is no automatic retry. Each frozen case/profile must keep the same unique attempt path; do not choose a new path to repeat an uncertain attempt.

Run future long evaluations under the existing user service manager, rather than a foreground tool session. For a previously prepared private request specification containing `url`, `body` and `timeout_seconds`:

```bash
systemd-run --user --collect --unit=test-evidence-eval-UNIQUE_ID \
  --property=RuntimeMaxSec=360 \
  /absolute/project/.venv/bin/python /absolute/project/scripts/durable_request.py \
  /absolute/private/request.json /absolute/private/new-attempt-directory
```

Use an existing loopback provider only; no URL credentials, external endpoints, redirects, label loading or GPU management are supported. Keep request/response artifacts private; they may contain submitted source. Inspect `state.json` and `response.body` before parsing/scoring. A dispatched/uncertain attempt without a receipt must not be repeated silently. The helper is not integrated into the opened historical experiment or live request path.

A synthetic smoke verified that the launcher returned before the worker began, the worker was parented by the existing user systemd manager in its own session, its raw receipt was committed and its transient unit ended inactive. No model call or GPU allocation was involved. Manager failure, host power loss or termination during an in-flight request can still leave an uncertain attempt; durable intent preserves that uncertainty rather than claiming exactly-once model execution.
