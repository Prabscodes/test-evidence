# CS4680 presentation and final checks

## Product promise

Test Evidence helps students and developers inspect whether tests for one small Python change visibly check an explicit requirement. The next decision is which assertion to inspect or add, or which requirement to clarify. It does not review whole repositories, connect to GitHub, execute uploaded code, or establish complete coverage.

## A 110-second demonstration

Prepare the actual local model and app before recording or presenting. Check an actual review, not just the status badge. Record which model is running; never apply a new model name or latency to historical footage.

| Time | Show and explain |
| --- | --- |
| 0–15 s | State the problem: passing tests can omit a required boundary. Identify the user as someone reviewing a small Python change. |
| 15–30 s | Open the boundary example. Show the explicit age-18 requirement and the before/after test assertions. Loading the example does not run AI. |
| 30–50 s | Open “How the AI reviews your tests,” then Load prompt templates. Show the actual persona instruction and one complete few-shot example. Explain that the role limits the task and the example teaches the difference between a tested value and a missing boundary. |
| 50–75 s | Select LLM review and explicitly Review change. Show the genuine response and cited lines. Describe the returned finding, including an unexpected or unresolved answer, rather than promising a scripted result. |
| 75–95 s | Add an authoritative clarification, choose Refine review, and explain iterative refinement. The prior response is context, not ground truth. If the result stays the same, explain why; do not manufacture improvement. |
| 95–110 s | State the useful next action: inspect or add the required equality assertion. Mention short-excerpt scope and fallibility, then show the repository link. |

Actual latency may exceed this timing. The published video must remain strictly under 120 seconds; disclose any cuts to waiting time. A real-time classroom demonstration should actually run inference. A labelled hand-authored demo or recording is a fallback illustration, not a claim of live inference. Confirm with the instructor if it must substitute for the live demonstration.

## Readiness gates

- Source: publish the reviewed commit to the existing repository and verify anonymous access. Include reproducible setup documentation; no credentials, model weights or private session data.
- Actual inference: verify the intended model/profile, an actual review, clarification/refinement, and inspectable citations shortly before presentation. Status configuration alone is insufficient.
- Prompt evidence: show at least two actual course patterns and explain their intended user benefit. A controlled improvement study is not required by the assignment; do not invent numerical benefits.
- UI: verify the start, input, review and clarification flow; the prompt guide must be available before the first inference.
- Video: verify the exact published viewer URL, audio, duration below 120 seconds and visible prompt explanation. A prior report of an accessible 1:50 video does not establish that its content matches this revision.
- Published app URL: unresolved until a real deployed app URL is checked or the instructor clarifies the required form field. The assignment calls deployment a bonus; the form requires Published URL. Do not substitute repository or slides URLs without clarification.
- Form: Name, GitHub Repo URL, Demo Video URL and Published URL are currently required. Email is optional. No Slides field exists. Verify final values and retain a submission receipt when submission is authorized and completed.

## Evidence boundaries

Application regression tests exercise software behavior; they do not measure model accuracy. Historical model results apply only to their documented inputs and profiles. The Bonsai legitimate-refactor false alarm remains relevant. No broad accuracy, user-adoption or productivity claim is established.

This runbook is a preparation artifact, not confirmation that publication or submission has happened.
