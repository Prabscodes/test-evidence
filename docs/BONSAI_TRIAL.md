# Bonsai 2 bounded local trial — 27 October 2026

The existing verified Ternary Bonsai 2 27B PQ2_0 file runs with the official PrismML runtime alongside the existing ComfyUI allocation. This is an experimental local profile; source prompts and application code are unchanged. No model weights, vision projector, driver, system package, public endpoint or paid API were installed.

## Verified identity and installation

- Model: `prism-ml/Ternary-Bonsai-2-27B-gguf`, existing `Ternary-Bonsai-2-27B-PQ2_0.gguf`, 7,206,168,928 bytes (6.71 GiB). SHA-256 `3907dc1658db1f78a9826bf8d5bcb8dc65db0d466388937af57f2294fae62ec1` matches the publisher file. Header/tensor directory is structurally complete. Original download revision is unavailable; do not invent it.
- Runtime: official `PrismML-Eng/llama.cpp` release `prism-b10826-c9c34bc`, exact source `c9c34bc9c4042c13a31598ebf43461cd0ad8f00d`, CUDA 12.8 Linux x64 prebuilt, SHA-256 `e4345c9fed6452701fd511f9837726f39a45bc95fe103b8cae55360562eadf7f`. Binary reports build 10826 / GNU 11.4.0. Published build workflow/config retained locally; no local compilation or system changes. Source/profile details: `tests/results/bonsai_trial_v1/profile.json`.
- PQ2 is a custom ternary packing with Hadamard transforms and needs the compatible fork. Existing stock binaries are not interchangeable. Official guidance: https://github.com/PrismML-Eng/Bonsai-demo and https://huggingface.co/prism-ml/Ternary-Bonsai-2-27B-gguf .

## Bounded profile and measured evidence

Context 6,144, one slot, batch/microbatch 128, four CPU threads, all layers on GPU, FlashAttention on, fit/context shift off, no vision/UI/tools, loopback only, thinking off with `deepseek` reasoning extraction. Sampler: temperature 0.7, top-p 0.8, top-k 20, min-p 0, presence penalty 1.5, repeat penalty 1.0 over 6,144 tokens, seed 42. This runtime differs from vLLM; the values do not establish identical decoding. App maximum 1,536 output tokens / 300-second timeout; no model/semantic prompt changes.

| Actual request | Wall seconds | Outcome |
| --- | --- | --- |
| Corrected simple JSON smoke | 0.257 | Valid expected JSON; initial 0.754-second smoke failed strict parsing because empty think tags were included |
| Known missing-boundary browser review | 4.726 | Missing age-18 assertion flagged; age-17/19 visible assertions supported |
| Authoritative clarification/refinement | 5.120 | Same boundary gap retained with clarification citation |
| Known legitimate refactor | 4.575 | Preserved age-17/18 checks recognized, plus an overbroad all-ages coverage warning; limitation retained |

No semantic reruns, cherry-picking or tuning followed these outcomes. Two known development inputs are not a benchmark. Exact responses, raw model output, prompt hashes and timings are retained in `tests/results/bonsai_trial_v1`. Every accepted citation quote matched its submitted lines; quote integrity does not prove semantic relevance or truth. The refactor warning remains a practical false-alarm risk.

Sampled trial GPU peak: 8,022 MiB (7.83 GiB); minimum sampled free VRAM 6,777 MiB (6.62 GiB) alongside the protected 16,786 MiB workload. Samples are one-second snapshots, not a hardware exact peak. Final service kernel memory.peak 6,051,913,728 bytes (warm mapped cache); earlier successful profile snapshot 7,556,775,936 bytes. This is not a universal cold-start/total-host requirement. Final cgroup has no OOM/max/high events and zero swap. Host limits 20 GiB / 18 GiB high/no swap/four CPU equivalents; temporary service lifetime two hours. Original 4B expired normally before this trial and its configuration is preserved. ComfyUI was untouched.

The actual browser checked review, refinement, exact citations, raw/prompt/provenance panels, review exports, mobile rendering and separate immutable fixture/export; no page errors. All 93 application regressions pass in 8.101 seconds with model inference disabled in the test process. Engineering checks and model behavior are distinct.

## Reproduce with the verified existing files

Use the verified existing files and pinned installed runtime. The instructions below start processes; they are not an installer. The measured trial additionally used the host and lifetime limits above. Check GPU and host headroom before each load; the file size alone is not a total-memory estimate. First inspect free GPU/host resources and check that the chosen port is unused. Do not start a second model beside a running trial. Adapt these paths:

```bash
export TE_BONSAI_RUNTIME_DIR=/absolute/path/to/official-prism-bin
export TE_BONSAI_MODEL_PATH=/absolute/path/to/Ternary-Bonsai-2-27B-PQ2_0.gguf
"$TE_BONSAI_RUNTIME_DIR/llama-server" -m "$TE_BONSAI_MODEL_PATH" \
  --alias te-bonsai2-27b-pq2 --host 127.0.0.1 --port 18084 \
  -ngl 99 -fa on -c 6144 -np 1 -b 128 -ub 128 -t 4 -tb 4 --threads-http 2 \
  --fit off --no-context-shift --jinja --reasoning off --reasoning-budget 0 \
  --reasoning-format deepseek --temp 0.7 --top-p 0.8 --top-k 20 --min-p 0 \
  --presence-penalty 1.5 --repeat-penalty 1 --repeat-last-n 6144 --seed 42 \
  --no-ui --offline --cors-origins http://127.0.0.1:8765 --no-cors-credentials
```

Once `/health` and `/v1/models` confirm the endpoint, start only the project app:

```bash
TE_PROVIDER=openai-compatible TE_API_BASE=http://127.0.0.1:18084/v1 \
TE_MODEL=te-bonsai2-27b-pq2 TE_ALLOW_REMOTE=1 TE_TEMPERATURE=0.7 \
TE_TIMEOUT_SECONDS=300 TE_MAX_TOKENS=1536 TE_PUBLIC=0 \
.venv/bin/python -m uvicorn app:app --host 127.0.0.1 --port 8765 --no-access-log
```

`TE_ALLOW_REMOTE` is the existing provider switch; the validated endpoint here is strictly loopback. No public deployment is implied. For labelled demo use `TE_PROVIDER=none`; for 4B rollback use the unchanged 4B profile in [SETUP.md](SETUP.md) after stopping only the task-owned Bonsai process. Never stop unrelated services to make room.

## Preserved failures and submission materials

Initial launch rejected an unsupported `--repeat-last-n -1` before loading. The first successful load then generated JSON prefixed with empty think tags under reasoning-format none; that failed strict parsing. Deepseek extraction fixes the transport shape without changing the semantic prompt. A restart port guard rejected a transient collision before load; a safe SO_REUSEADDR availability check corrected it. All raw evidence is retained, including the overbroad refactor warning.

The earlier 110-second narration-ready packet contains silent recorded 4B footage with its own 150/227-second timing disclosures. It is still an authentic historical recording; do not relabel it as Bonsai or current five-second inference. New actual Bonsai footage/screenshots are retained privately. User voiceover, published video link, native Slides URL/access and course receipt remain separate unverified submission steps. No video or form was published by this trial. The recorded trial service had a two-hour lifetime from 01:48:44 UTC; its health must be checked before a later live demo.
