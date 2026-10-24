# Course prompt-pattern mapping

The assignment requires at least two patterns. Test Evidence implements three in `prompts.py`, rather than merely listing their names in the interface.

| Pattern | Concrete input to model | UI/action | Intended benefit and boundary |
| --- | --- | --- | --- |
| Persona | `SYSTEM` begins with a cautious test-evidence reviewer role and explicit authority/evidence rules | Inspect prompts → Persona | Focuses the assistant on limited evidence judgments, not correctness claims |
| Few-shot | Three JSON examples cover table refactor, missing authority and a missing equality test | Inspect prompts → Few-shot examples | Demonstrates the output schema and desired distinctions; examples are development material |
| Iterative refinement | `REFINEMENT` plus current artifacts, explicit clarification and a bounded prior summary | Enter clarification → Refine analysis | Reassesses the prior interpretation; previous output is context, never authority |

`prompts.messages()` puts stable line records in the submitted user payload. The system instruction defines the schema; uploaded text cannot create trusted record IDs. `provider.py` sends the resulting messages to the selected model. The browser's ordinary Analyze action also includes visible clarification, while Refine additionally includes the previous summary. Canonical prompt/artifact hashes in JSON exports record what was reviewed. `/api/prompts` exposes the actual template/version, `3.1-explicit-boundary-evidence`.

A missing specification should lead to a clarification question. A table-driven refactor should preserve support if the assertion actually consumes the required row. A changed source implementation is not itself an after-test assertion. These are prompt goals, not established guarantees: actual evaluations include errors in all of these distinctions. No ablation study isolates the effect of a pattern or supports a numerical improvement claim.
