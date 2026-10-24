# Long-request usability and reliability validation

The local app now shows an active request and elapsed wait without invented percentages. Known provider failures have actionable, app-owned messages. A read-only **Check app status** action reports whether an application review is still active; no POST is automatically repeated. Model/demo judgments, static inspection without execution and separate bundled fixture evidence are explicitly labelled. This is a usability/transport improvement, **not a semantic model-accuracy improvement**.

## Changes and scope

- Elapsed seconds remain visible near Analyze, with mirrored feedback near Refine. Screen-reader status announces the action; the timer does not announce every second. Completed provider time remains distinct from browser wait.
- Browser duplicate actions stay disabled. A reload sees a running app review. An interrupted connection requires an explicit status check before another review; the check sends only GET/status. There is no misleading cancel control. App-idle status does not establish that a timed-out upstream provider stopped generating.
- Editing artifacts **or changing review mode** invalidates exports. A late response for changed inputs is discarded. Starting a new review marks prior output as previous; failure leaves it stale with exports disabled. Fixture responses also retain an input-version check.
- Timeout504, unavailable/missing-model503, rejected-input400, access/otherHTTP502 use static app-owned messages, not upstream exception text/bodies or credentials. Unexpected exceptions retain the generic sanitized502 response. Inputs remain in the form; no server input persistence was added.
- The synchronous server lock remains held until the application call actually returns, including after client disconnect. A real TCP-disconnect test verifies that a second request receives429 while work is active. This is distinct from the upstream provider possibly continuing after an app HTTP timeout.

Only this task's app was restarted, after its model metrics reported zero running/waiting requests. The existing Qwen engine/process, weights, sampler/settings and other services were unchanged. The previous verified source ZIP remains byte-identical. No frozen cases were rerun or used to tune prompts. `prompts.py`, `analysis.py`, `consistency.py`, `fixtures.py` and `ast_check.py` are unchanged from the previous snapshot.

## Tests and actual browser evidence

Test-first evidence: six backend lifecycle tests failed before safe errors/status were implemented; five frontend behaviors failed before the fixes (the existing late-response guard already passed). Red/green logs are retained. A seventh backend regression covers an actual client TCP disconnect with an isolated ephemeral loopback server and held synthetic analysis; no model is called by these tests.

- Final suite: **57 tests passed in 3.099 seconds** (3.314 seconds external wall time).
- Six deferred-fetch/clock UI regressions passed, including elapsed increments, duplicate-click suppression, AbortError/manual status recovery, old-export protection after failure, reload detection and review-mode staleness. DOM and clarification regressions also passed.
- Real Chrome149.0.7827.53 exercised delayed/cancelled/timed-out transports, stale responses and reload recovery on desktop/mobile. Those transport results are explicitly **simulated**, not inference or accuracy evidence. No page errors; mobile layout did not overflow.
- A complete separate labelled-demo browser smoke passed in3.020 seconds external wall time: all four examples, clarification on both buttons, prior context only on Refine, exact citations, stale exports, AST-only upload, immutable fixture execution and separate exports.
- Exactly **one genuine Qwen development-example review** ran with unchanged settings. Provider time **68.819 seconds**, browser wait68 seconds; active status and elapsed display were verified on desktop/mobile, raw output/export matched, and exactly one POST was sent. This run identified the omitted age18 check and the visible age17 assertion. Its raw response is retained; one familiar example does not establish semantic reliability.

Evidence: `tests/results/request_ux_v1/` contains test logs, source snapshots, browser summaries, screenshots, actual raw response/export and a final integrity receipt. Public log copies remove only private paths; model judgments are not rewritten. A dependency deprecation warning from the existing Starlette/HTTPX test client is retained; no packages were changed to hide it.

## Slurm verification (read-only)

The reported CPP RAM value is **not a default**. The raw QoS query columns are `Name|Flags|MaxWall|MaxTRESPJ|MaxTRESPU|MaxJobsPU|MaxSubmitPU`; row: `basic|OverPartQOS|10-00:00:00|cpu=4,gres/gpu=1,mem=4G|cpu=8,gres/gpu=1,mem=8G|2|8`. `AccountingStorageEnforce=associations,limits,qos`. Thus4GiB is the configured per-job MaxTRES under that QoS. Actual cgroup behavior was not probed and no job was submitted. Higher-memory access and site inference rules remain pending; no limit was bypassed.

## Remaining limits

Closing a tab does not guarantee upstream cancellation, and status cannot recover a disconnected response. Inference remains slow and semantically fallible; the earlier six-case diagnostic still has three Qwen false accusations. No accuracy, correctness, production readiness or adoption claim is added. The app stays single-process/single-user and loopback-only. No public publication, cluster job, download or upload was performed.
