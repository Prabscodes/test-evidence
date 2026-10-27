# Assignment checklist

Current finishing pass: **27 October 2026 UTC**. The assignment PDF says to check Canvas for the official deadline; earlier October 23–24 planning targets are historical. This document does not claim that the project has been submitted.

| Requirement | Verified evidence / remaining action |
| --- | --- |
| Practical AI MVP and usable interface | FastAPI/vanilla JS; Start → Inputs → Review, source/test comparison, citations, clarification and separate fixture exports. Current genuine 4B review/refinement completed. |
| At least two prompt patterns | Persona, few-shot examples and iterative refinement; [mapping](docs/PROMPT_PATTERNS.md), inspectable actual prompts. |
| Complete public source and documentation | Approved target: **https://github.com/Prabscodes/test-evidence**. Reviewed implementation commit `8762d8d18afbfe52b99759a0850b78a43057c805` published and anonymously verified on 27 October at 00:07 UTC; all 238 remote blobs matched. See [publication record](docs/PUBLICATION_VALIDATION.md). |
| Engineering and browser checks | **93 application tests pass**; Node regressions and desktop/mobile workflow, keyboard, stale/export, public admission/error and accessibility checks pass. [Evidence](docs/FINISHING_VALIDATION.md). Controlled-provider browser checks are distinguished from genuine inference. |
| Honest scope and evidence | Inputs, results and JSON/Markdown exports disclose partial review, at most three prompted obligations, and no coverage of unlisted requirements. No arbitrary uploaded Python execution. Prior model failures preserved. |
| Short demo | **110-second silent 1080p edit prepared**, current actual 4B footage, waits/paused frames labelled. [Narration and recording directions](docs/DEMO.md). User audio and final voiced export **pending**. |
| Published demo viewer URL | **Pending** user narration, confirmed publishing account/destination and viewer-access check. Must be strictly under 120 seconds. |
| Native Google Slides URL | Eight-slide deck prepared separately. Native import/connection and verified reviewer access **pending**; a PPTX alone is not the required URL. |
| Live presentation | Rehearse the problem, recorded real inference with actual latency, prompt patterns, clarification, citations, separate fixture and limitations. **Pending owner rehearsal.** |
| Course form | **Not submitted.** Required: **Name, GitHub Repo URL, Demo Video URL, Google Slides URL**. Email is optional. Published URL/live app is optional/highly recommended. Form: https://forms.gle/nMHp5owwYidszwt58 . Review links and obtain appropriate authorization before submission; retain receipt. |
| Public app | Optional rubric bonus. No public GPU endpoint, hosted-provider credential, paid hosting or PC exposure is provisioned. Temporary loopback inference is not public deployment. |

Current model: existing **Qwen3.5-4B BF16**, vLLM 0.25.1, thinking disabled, 4 GiB CPU offload. Actual current calls took **150.1 and 227.3 seconds** on one known development example. This is not broad accuracy evidence. Historical 27B results remain available, but its recorded weights path is absent and its full-GPU profile does not fit current shared headroom. See exact provenance and limitations in [finishing validation](docs/FINISHING_VALIDATION.md).

Source excludes weights, credentials, assignment PDF, private session data and unrelated projects. Application source license remains unselected; no unrestricted license is invented. Required narration/video/Slides/form steps above remain open even after source publication.
