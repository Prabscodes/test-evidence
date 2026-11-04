> Current form correction, 4 November: required Name, GitHub Repo URL, Demo Video URL and **Published URL**; Email optional; no Slides field. The PDF describes public app hosting as bonus. Resolve that discrepancy using a verified app deployment URL or instructor clarification before submission.

# Submission and live-presentation runbook

Reviewed 4 November 2026. Source, a published short video, a prepared Google Slides presentation supporting the live demo, and an in-class live demonstration are separate deliverables. The PDF calls public hosting of the app an optional bonus; the current form nevertheless requires a Published URL, which needs an actual reviewed app URL or instructor clarification. The PDF gives the official deadline only as “See the date in Canvas”.

## What to demonstrate

| Time | Show | Explain |
| --- | --- | --- |
|0–10s | Requirement and bundled before/after test excerpts | Passing tests can omit the required age 18 boundary. Test Evidence helps a reviewer locate evidence; it does not prove correctness. |
|10–25s | Actual template in Inspect prompts or `prompts.py` | **Persona:** cautious evidence reviewer and authority rules. Intended role: focus the task and avoid unapproved policy. |
|25–40s | One complete few-shot input/output example | **Few-shot:** show shipping100 versus150 or a retained table assertion. Intended role: demonstrate structure and a concrete judgment distinction. |
|40–60s | Genuine review, then a citation | Actual model interpretation; exact quoted lines come from the server. State the model/wait accurately. |
|60–80s | Enter authoritative clarification and Refine | **Iterative refinement:** current artifacts, clarification and prior summary are reconsidered. Same finding is allowed; no numerical accuracy benefit is claimed. |
|80–95s | Current review export; optionally separate fixture result | Uploaded Python is never executed. Only immutable bundled fixtures run, with a separate export. |
|95–108s | Limits and next step | Partial review, up to three prompted obligations, possible false alarms and essential human review. |

Target 108 seconds and verify the actual final export is strictly less than 120 seconds. The schedule is a guide, not permission to relabel prerecorded output as a live call. If waits are shortened, label the edit; if a model call fails, disclose it. No AI replacement narration is required: the user supplies their own voice.

## Existing recording versus re-recording

An earlier 110-second silent 4B edit and narration materials remain preserved. A later narrated storyboard v2 file was located during this review, so do not assume narration must be recorded again. Its actual duration/audio/content and published viewer URL still need verification in the owner's selected recording. Keep the existing recording if it is accurate, intelligible, under 120 seconds and visibly demonstrates at least two prompt patterns with their intended purpose.

If that evidence is missing, replace a short section rather than necessarily re-recording everything. Suggested 30-second explanation while showing the real templates:

> I use a persona to frame the model as a cautious test-evidence reviewer. Few-shot examples show the difference between a preserved assertion, a missing boundary and an unspecified requirement. Iterative refinement adds authoritative clarification and the previous review summary so the model can reconsider its judgment. These patterns guide the response; they do not prove correctness. The actual templates and provenance are inspectable.

Do not paste this voiceover onto unrelated visuals. Show the actual persona/few-shot text and the clarification action. Keep the total final video below two minutes. Historical 4B footage and its150/227second timings must not be relabelled as the faster Bonsai profile.

## Live readiness and safe operation

The existing Bonsai 2 27B PQ2_0 profile was restored on 4 November using verified files and the pinned PrismML runtime. Genuine API review/refinement took4.511 / 5.187 seconds on one known example, with exact accepted quotes; the fixed fixture separately produced the expected boundary disagreement. This is not accuracy evidence. All 93 application tests passed in 7.645 seconds, plus Node regressions.

The local app is at `http://127.0.0.1:8765`. Check both app status and the configured model's health before presentation; a configured model name does not establish readiness. Temporary inference has a two-hour bound and must not be assumed to remain available. Follow [Bonsai setup](BONSAI_TRIAL.md) if a later restart is needed; inspect current resources first and never interrupt unrelated workloads. No new weights or public GPU endpoint are needed for the required local live demonstration.

## Final field review

The form requires Name, GitHub Repo URL, Demo Video URL and Published URL. Email is optional. Published URL is required by the current form; it is not the Google Slides link. Use the verified final viewer links, not a private video draft or local file path. Confirm reviewer access and retain a submission receipt. Preparation and an available form are not proof of submission.
