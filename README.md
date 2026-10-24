# Test Evidence — CS4680 AI Assistant MVP

Test Evidence helps a reviewer compare an **explicit requirement** with before/after Python source and tests. It returns evidence-linked **supported**, **potentially missing**, or **unresolved** judgments, asks for clarification, and exports the review. Its practical goal is to make changed or missing checks easier to inspect. It does not prove correctness or replace human review.

The web UI uses a real open-source LLM through an OpenAI-compatible API. A separate, clearly labelled deterministic demo works without weights or credentials. Only immutable bundled fixtures can execute; uploaded code is AST-inspected and never run.

## Quick start: labelled demo

Python 3.11+; Linux is the verified platform. From this project directory:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
TE_PROVIDER=none .venv/bin/python -m uvicorn app:app --host 127.0.0.1 --port 8765
```

Open **http://127.0.0.1:8765**, load a sample, and select labelled demo. Demo judgments are hand-authored examples, **not model inference**. No model download, account or API key is needed for this mode. If the port is occupied, use another loopback port without stopping its owner.

## Actual model inference

The current local profile uses existing **Qwen3.5-27B compressed-tensors4-bit**, download revision `65497df9ca706cd6aa9cc8374fc259f39e78672d`, fully on the RTX 5090 with vLLM 0.25.1. Thinking is disabled; exact file pins/settings and retained failures are in [27B validation](docs/QWEN27_VALIDATION.md). The earlier4B profile remains documented for rollback. Weights/runtime are separate from source.

Select **LLM review** to inspect the actual model, provider time and raw output. Errors remain visible; there is no silent cloud fallback. Reviews show elapsed waiting without invented percentages and never retry automatically. [Local setup](docs/SETUP.md) · [Public deployment preparation](docs/PUBLIC_DEPLOYMENT.md). Public live inference requires an approved hosted provider; the prepared default is explicitly labelled demo with live inference unavailable. This PC/GPU is never exposed publicly.

## Workflow and course prompt patterns

Enter requirement → paste/upload four excerpts → review → inspect exact cited lines → clarify/refine → optionally run a trusted sample → export JSON/Markdown. Fixture execution has its own export and does not represent uploaded/edited code.

| Pattern | Implementation | User purpose |
| --- | --- | --- |
| Persona | Cautious evidence reviewer in `prompts.SYSTEM` | Keeps the requested role and evidence limits explicit |
| Few-shot | Three structured examples in `prompts.SYSTEM` | Demonstrates legitimate refactor, missing authority and limited gap responses |
| Iterative refinement | `prompts.REFINEMENT`, previous summary and visible clarification | Reassesses a review against explicit new authority |

All three are visible through **Inspect prompts** and `/api/prompts`. These patterns guide behavior; measured errors show they do not guarantee better judgments. [Detailed mapping](docs/PROMPT_PATTERNS.md) · [Architecture](docs/ARCHITECTURE.md)

## Verification and limitations

```bash
.venv/bin/python -m unittest discover -s tests -v
node tests/scripts/clarification-regression.js
node tests/scripts/dom-smoke.js
node tests/scripts/request-lifecycle.js
```

The application and isolated evaluation helper have 90 passing tests; mocked-provider tests are not model-accuracy evidence. Real browser workflows and actual GPU reviews were also exercised. [Release evidence](docs/SUBMISSION_VALIDATION.md) records exact runs and limitations.

On six synthetic diagnostic cases, the Qwen profile matched **3/6** expected labels, produced **three false accusations**, and took **37.7–92.4 seconds** per call (median 47.8). The set was frozen for an earlier profile and reused without tuning; it is not a new held-out accuracy estimate. Duplicate JSON keys now make the assessment unresolved while preserving exact raw output; see [parser and evaluation transport verification](docs/JSON_OUTPUT_VALIDATION.md). A valid line citation can still be misinterpreted. **Do not use this app as an approval gate.**

A new twelve-case author-created set was frozen before 27B calls: 4/4 gaps, 4/4 covered cases and 4/4 ambiguous abstentions matched, with median 4.43s warmed latency and no observed schema/citation failures. This meets a bounded demo gate, not an independent accuracy benchmark or production guarantee. Full raw outputs and failure history remain available.

Other limits: short Python excerpts only, restricted model context, single-request local service, stochastic outputs, no representative real-repository study and no production authentication/hardening. The runner is an immutable fixture allowlist, not an arbitrary-code sandbox. Local hosting stays loopback-only. Separate public cloud configuration has admission/consent/privacy bounds and fails closed without an approved hosted provider.

## Submission material

[Release checklist](RELEASE_CHECKLIST.md) · [100-second demo script](docs/DEMO.md) · [Dependencies and licenses](THIRD_PARTY_NOTICES.md)

The clean source package excludes credentials, weights, virtual environments, runtime caches, machine/session metadata and the assignment PDF. Historical failures remain in the local development tree; selected unaltered synthetic raw failures accompany the source release. GitHub publication and remaining assignment steps are tracked in [ASSIGNMENT_CHECKLIST.md](ASSIGNMENT_CHECKLIST.md). Video narration/publication and hosted live inference remain separate pending steps. An application source license has not yet been selected.
