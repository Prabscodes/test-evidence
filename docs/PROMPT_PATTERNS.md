# Course prompt-pattern mapping

The assignment requires at least two patterns. Test Evidence implements three in `prompts.py`, rather than merely listing their names in the interface.

| Pattern | Concrete input to model | UI/action | Intended benefit and boundary |
| --- | --- | --- | --- |
| Persona | `SYSTEM` begins with a cautious test-evidence reviewer role and explicit authority/evidence rules | Inspect prompts → Persona | Focuses the assistant on limited evidence judgments, not correctness claims |
| Few-shot | Three JSON examples cover table refactor, missing authority and a missing equality test | Inspect prompts → Few-shot examples | Demonstrates the output schema and desired distinctions; examples are development material |
| Iterative refinement | `REFINEMENT` plus current artifacts, explicit clarification and a bounded prior summary | Enter clarification → Refine analysis | Reassesses the prior interpretation; previous output is context, never authority |

`prompts.messages()` puts stable line records in the submitted user payload. The system instruction defines the schema; uploaded text cannot create trusted record IDs. `provider.py` sends the resulting messages to the selected model. The browser's ordinary Analyze action also includes visible clarification, while Refine additionally includes the previous summary. Canonical prompt/artifact hashes in JSON exports record what was reviewed. `/api/prompts` exposes the actual template/version, `3.1-explicit-boundary-evidence`.

A missing specification should lead to a clarification question. A table-driven refactor should preserve support if the assertion actually consumes the required row. A changed source implementation is not itself an after-test assertion. These are prompt goals, not established guarantees: actual evaluations include errors in all of these distinctions. No ablation study isolates the effect of a pattern or supports a numerical improvement claim.

## Evidence the instructor can inspect

The assignment asks for at least two patterns and an explanation of their intended performance and user-experience purpose. The three patterns above are implemented, rather than decorative labels. Verify the correspondence directly:

1. Open the UI's provider/prompts section and click **Inspect prompts**, or read `/api/prompts`. The returned `system` and `refinement` fields are the actual templates from `prompts.py`, with version `3.1-explicit-boundary-evidence`.
2. Point to the persona's cautious reviewer role and authority/evidence rules. Explain that they focus the task and preserve uncertainty; they cannot guarantee obedience or correctness.
3. Point to a complete few-shot input/output example. The shipping example distinguishes checking 150 from checking the explicitly inclusive boundary of 100; the table-refactor example shows a retained assertion. Explain the intended output format and decision distinction.
4. Run a genuine LLM review, add explicit clarification and choose Refine. The message builder includes the refinement instruction and current artifacts; the UI additionally supplies the previous review summary. Explain how the user can resolve ambiguity. The answer may keep the same finding; do not invent an improvement or force an answer change.
5. Inspect the exported prompt version/hash, raw model response and new clarification citation where present. These establish provenance, not accuracy.

A read-only source inspection and two genuine local API calls on 4 November verified this path without changing the templates. Review/refinement took4.511 / 5.187 seconds on the known bundled boundary example. This is integration/rehearsal evidence, not an unseen evaluation or a controlled measurement of each pattern's benefit. Prior Bonsai false-positive and other model failures remain relevant.

For a short recording, show at least the persona instruction and one full few-shot example on screen, then demonstrate or explain refinement. Merely saying the pattern names is weaker evidence than showing the actual inputs and their intended role. See [presentation runbook](PRESENTATION_RUNBOOK.md). The existing Slides deck already has an explicit pattern slide; video visibility must be checked separately.
