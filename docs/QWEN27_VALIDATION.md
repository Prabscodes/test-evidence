# Current local 27B profile and evidence

Existing model directory is labelled AWQ, but verified configuration is **Qwen3.5-27B, compressed-tensors symmetric 4-bit, group 32, pack-quantized**, architecture `Qwen3_5ForConditionalGeneration`. All four indexed shards are complete: 20,058,008,400bytes. Their independently computed SHA256 values match existing download metadata revision `65497df9ca706cd6aa9cc8374fc259f39e78672d`. Upstream quantizer repository identity was not independently resolved; exact local file pins are supplied, not an invented repository URL. No weights were downloaded or bundled.

Installed serving runtime is vLLM 0.25.1(g752a3a504), PyTorch 2.11.0, Transformers 5.14.1, native sampler. Current profile: full GPU/no CPU parameter offload, text only, thinking disabled, 6144 token context, one sequence, 128 token prefill batches, eager execution, 1 GiB explicit KV cache, temperature 0.7, topP 0.8, topK 20, minP 0, presence penalty 1.5, repeat penalty 1.0, seed 42; local output budget 1536 and HTTP timeout 300s. Loopback model port18083; app port8765. Public hosted inference is separate and unconfigured.

Model loading reported 17.94GiB. Sampled total GPU use 20,192 MiB with 11,918 MiB free on the RTX 5090; these are snapshots, not a measured maximum. Initial 512 MiB cache failed validation because the runtime needed 0.53 GiB for 6144 context. A single diagnosed correction to 1 GiB succeeded; the failed log/profile is preserved. Earlier 4B full-GPU starts stopped at port checks before model loading; they were not model OOMs. Only task-owned inference/app processes changed; no ComfyUI or Ollama controls or Claude messages were sent. Conservative 4B launch/source evidence remains as rollback.

## Reused development diagnostics

All six known development labels matched, raw and accepted, with zero observed false support/accusations. These cases were already used to diagnose earlier models, so this is **not independent accuracy**. First cold request 53.306s; later five 4.577–5.793s; median across six 5.401s. Earlier 4B comparisons differ in model, quantization, offload/cache, parser version and warmup/time; do not infer a controlled causal speed/quality estimate.

Real browser review/refinement took 8.493s and 8.948s, on an existing bundled development example. Exact citation selection, raw/provenance exports, clarification/prior context, stale exports, separate immutable fixture execution and mobile layout passed. One earlier harness run saved a completed review/export then stalled on a closed prompt panel; that failure and footage are preserved. Its selector was corrected and the disclosed development UI check repeated. No uncertain/frozen request was retried. Genuine recorded footage is the basis of the silent narration handoff.

## New twelve-case frozen readout

Inputs and author labels were frozen before requests, with four gaps, four covered changes and four ambiguous requirements. Cases cover inclusive boundaries, parametrization, expected exceptions, refactor retention, changed expected values and irrelevant evidence. The unchanged baseline prompt, parser and runtime were pinned. Labels/group names were excluded from model messages; each input ran once in a durable worker with a 30 minute total budget and 300 second per-call timeout. No new snippets were executed; existing allowlisted fixture testing is separate evidence and does not validate these labels.

All 12 responses were saved and sealed. Results:

| Outcome | Count |
| --- | ---: |
| Genuine gaps identified |4/4|
| Missed gaps / false support on gap cases |0 /0|
| Correct supports |4/4|
| False alarms |0|
| Appropriate ambiguous abstentions |4/4|
| Schema failures / invalid citations / quote mismatches |0 /0 /0|

Median latency 4.429s; range 3.119–5.502s on the warmed local model. Manual audit found no invented approved policy in the ambiguous cases and no silent parse/citation failure. The requested **bounded tonight-demo gate passes**. This small synthetic set shares categories with known failures and was authored/audited by the same person: it is exploratory, not an independent benchmark, representative accuracy estimate, novelty claim or production reliability proof. Nothing was tuned after opening the results. Previous failures remain.

Public input/label/protocol files: `tests/qwen27_frozen_v2/`. Exact synthetic HTTP response copies and final score/audit: `tests/results/qwen27_v2/public_responses/`, `score_final.json`, `manual_audit.json`. Original per-process receipts/full protocols with machine paths stay private locally; copied raw bytes have their own manifest. Older seals refer to their own historical source snapshots and are not regenerated under the new parser.
