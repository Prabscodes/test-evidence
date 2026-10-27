# Finishing validation —26 October2026

## Current release scope

The published candidate includes the structural Start/Inputs/Review workflow fromc896f05 and a bounded scope-honesty correction. Every response now includes server-owned review_scope metadata. Inputs, review and JSON/Markdown exports disclose partial coverage; the LLM is instructed to return at most three obligations. Counts apply only to listed findings. No assessment of unlisted requirements or complete coverage is claimed. Extra model output is counted honestly rather than silently truncated. Semantic prompts and their version remain unchanged.

The notice is placed before judgment counts and associated with requirement input help. No additional redesign or speculative feature was added.

## Actual current model workflow

Only existing Qwen3.5-4B BF16 weights and vLLM0.25.1 were used, with4GiB CPU offload, thinking disabled,6144token context, one request,512MiB KV cache, native sampler and seed42. Exact pins/settings are in tests/results/finish_live_v1/model_profile_public.json and docs/SETUP.md. No weights/runtime download, driver/security change, ComfyUI interruption, borrowed project service or paid API occurred. The original27B directory is absent and the exact full-GPU profile would not fit the available shared GPU headroom;27B success records remain historical.

The task-owned service was capped at20GiB host memory,18GiB MemoryHigh, no swap, four CPU equivalents, low scheduling priority and two-hour lifetime. It loaded with about5.3GiB GPU allocation, leaving about9GiB free alongside ComfyUI. These are snapshots, not universal capacity guarantees. Read-only checks showed no cgroup OOM/kill. The task app alone was reloaded to the verified4B loopback endpoint.

Two actual browser requests on a known development example completed without retry:

| Request | HTTP | Browser wall | Provider time | Observed judgment |
| --- | --- | --- | --- | --- |
| Initial review |200 |150.062s |149.933s |Potentially missing age18 assertion |
| Authoritative clarification/refinement |200 |227.309s |227.211s |Potentially missing equality assertion; cites clarification |

All accepted citations match the submitted lines. Manual inspection of this example finds the reported missing equality check in AFTER tests. This is one known development example, not a held-out set or model accuracy claim. Earlier small-model semantic failures and historical27B evaluations are unchanged. CPU offload is slow; do not present historical27B warmed latency as current4B performance.

Actual browser scope: current three-view UI, real4B review and refinement, exact citations, visible partial scope, provider/raw/prompt inspection, review JSON/Markdown exports and separately executed immutable fixture/export. No page errors. Original footage and private execution export are retained locally; exact review/refinement responses and events are in tests/results/finish_live_v1. Fixture export is not a review of edited/uploaded code.

## Regression checks

93 application tests pass in 8.084 seconds from the working checkout and in 8.751 seconds from a clean source extraction, including three new scope contracts. Node clarification, DOM and seven request-lifecycle cases pass. Full structural browser regression checks scope in input/review/JSON/Markdown, back/forward, retained drafts, progressive citations, stale exports and interrupted/duplicate handling. Public-mode browser tests use a synthetic provider and remain distinct from the two real calls above. Accessibility/contrast/layout checks remain bounded rather than certification. Relevant summaries are in tests/results/finish_checks_v1.

## Demo and submission limits

The refreshed silent video uses current actual footage. Original waits of150.1s and227.3s are shortened with explicit labels. Paused explanation frames are labelled. It contains no AI voice or music; the user supplies narration. The final narrated export must remain strictly under120seconds. A known example and successful API responses do not prove correctness or production readiness.

Source publication is authorized to the existing public Prabscodes/test-evidence repository. Native Google Slides URL/access, user voiceover, final voiced video URL and form receipt remain pending/unverified. Public app hosting is optional and no hosted GPU/API resource or continuous public service was provisioned. Temporary local inference is not a public deployment.

The first clean-extraction run in the restricted executor stalled on its first in-process API test and was stopped. The identical tests passed through the approved local executor with a 60-second bound; no source change or model retry was involved.
