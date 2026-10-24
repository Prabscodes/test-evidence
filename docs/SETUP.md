# Setup and local inference

## Labelled demo

Use the README commands with the four pinned application requirements. The server exposes only loopback. Demo mode is deterministic and never calls an LLM. App dependencies are separate from model-serving dependencies. On Windows use WSL for the verified Linux resource-limit behavior; native Windows has not been validated.

## Portable equivalent with existing weights/runtime

This documents the verified configuration; it does not install or download the runtime or model. Set absolute paths to your existing compatible installations. The tested runtime was **vLLM 0.25.1 (g752a3a504)**, Python 3.12.13, PyTorch 2.11.0, Transformers 5.14.1, FlashInfer 0.6.13 and Triton 3.6.0. The optional `requirements-local.txt` belongs to the older CPU Transformers adapter and is not the vLLM server environment.

```bash
export MODEL_DIR=/absolute/path/to/existing/Qwen3.5-4B
export VLLM_BIN=/absolute/path/to/existing/vllm
export XDG_CACHE_HOME="$PWD/runtime-cache/qwen35"
export VLLM_CACHE_ROOT="$XDG_CACHE_HOME/vllm"
export TORCHINDUCTOR_CACHE_DIR="$XDG_CACHE_HOME/inductor"
export TORCH_EXTENSIONS_DIR="$XDG_CACHE_HOME/extensions"
export TRITON_CACHE_DIR="$XDG_CACHE_HOME/triton"
export CUDA_CACHE_PATH="$XDG_CACHE_HOME/cuda"
export FLASHINFER_WORKSPACE_BASE="$XDG_CACHE_HOME/flashinfer"
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 HF_DATASETS_OFFLINE=1 \
  PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=4 VLLM_USE_FLASHINFER_SAMPLER=0 \
  "$VLLM_BIN" serve "$MODEL_DIR" --served-model-name te-qwen35-4b-bf16 \
  --host 127.0.0.1 --port 18081 --language-model-only \
  --limit-mm-per-prompt '{"image":0,"video":0}' --mm-processor-cache-gb 0 \
  --dtype bfloat16 --max-model-len 6144 --max-num-seqs 1 \
  --max-num-batched-tokens 256 --enforce-eager --cpu-offload-gb 4 \
  --gpu-memory-utilization 0.25 --kv-cache-memory-bytes 536870912 \
  --default-chat-template-kwargs '{"enable_thinking":false}' \
  --generation-config vllm \
  --override-generation-config '{"temperature":0.7,"top_p":0.8,"top_k":20,"min_p":0,"presence_penalty":1.5,"repetition_penalty":1.0}' \
  --seed 42 --download-dir "$XDG_CACHE_HOME/huggingface"
```

The copied shell block uses line continuations; run it in bash. Once `http://127.0.0.1:18081/health` returns 200, start the app separately:

```bash
TE_PROVIDER=openai-compatible TE_API_BASE=http://127.0.0.1:18081/v1 \
TE_MODEL=te-qwen35-4b-bf16 TE_ALLOW_REMOTE=1 TE_TEMPERATURE=0.7 \
TE_TIMEOUT_SECONDS=300 TE_MAX_TOKENS=1536 \
.venv/bin/python -m uvicorn app:app --host 127.0.0.1 --port 8765
```

Here `TE_ALLOW_REMOTE=1` enables the HTTP adapter for its loopback address. It does not make this profile a cloud service; `/api/status` reports `processing_location=loopback_endpoint` and `remote_processing_enabled=false`. No API key is needed. Never transmit third-party source to an external endpoint without authorization.

Use the official **Qwen/Qwen3.5-4B** revision `851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a`, BF16 (not quantized). Two verified shard SHA-256 values are `26a93f066e1916adb13453dae5a0c707c0fbc71299ed98779571a907b8e74c61` and `cb544bd9bfae93dc59b0f22b292f5933573854a7f9b97835c67060d7d910e188`. Total shard size: 9,319,828,096 bytes. Native sampling avoids the observed FlashInfer JIT failure on the tested RTX 5090; this does not imply a universal runtime requirement.

The explicit 512 MiB cache overrides utilization-based cache sizing; 0.25 is not a total VRAM cap. Sampled process use was 5,306 MiB, alongside an existing workload. Verify your own headroom before starting; do not reuse these numbers as a peak guarantee. Context is 6,144 tokens including generation, so some app-valid long inputs will be rejected by this model endpoint. Thinking is disabled; CPU offload and sampling differ from author benchmarks.

## Optional browser check

The browser script uses Playwright with an existing Chrome/Chromium executable. Playwright is a development-only dependency, not required to run the app. No browser installation is automatic.

```bash
# In an environment where Playwright is already installed:
TE_APP_PYTHON="$PWD/.venv/bin/python" CHROMIUM_PATH=/absolute/path/to/chrome \
python3 tests/scripts/submission-smoke.py --output /tmp/test-evidence-ui-check
```

It starts a separate labelled-demo server on loopback port 8766 and stops only that process. It makes no model calls. Refuse occupied ports rather than stopping their owner. Earlier actual Qwen browser evidence remains separate.


## Slow or interrupted reviews

The active-request display shows elapsed browser wait, not model progress or a completion estimate. Provider time appears separately when the response arrives. Do not refresh to retry: a disconnected browser does not necessarily stop work. After an interrupted/timeout request, read the message and use **Check app status**. This performs only GET/status; a new review always requires an explicit click. Idle app status cannot verify that a timed-out provider has stopped generating, so check that provider before intentionally sending another request. Your input fields remain intact. There is no cancellation guarantee or automatic retry.

If a model is unavailable or its name is wrong, confirm the existing local serving process/alias; do not download another model as a default fix. For an input/context rejection, shorten excerpts or review the endpoint's supported settings. Credentials stay server-side and should never be entered in review text. Static inspection and model judgment do not execute code; only the separate bundled fixture button does.


## Current27B portable configuration

With the existing compatible runtime and the exact matching compressed-tensors files pinned in `tests/results/qwen27_v1/model_public.json`, adapt the earlier serve command: model directory to the existing 27B files, alias `te-qwen35-27b-ct4`, loopback port18083, CPU offload0, prefill128, explicit KV cache1073741824bytes and utilization0.80. Keep context6144, one sequence, eager/text-only, native sampler, thinkingfalse and the sampler unchanged. Quantization is detected from its compressed-tensors config; do not force ordinary AWQ because of a directory name. The0.80/cache settings are not a whole-process VRAM cap. Verify adequate measured headroom on your own machine.

Point the app to `http://127.0.0.1:18083/v1` with `TE_MODEL=te-qwen35-27b-ct4`; keep local temperature 0.7, timeout300 and output1536. Do not set `TE_PUBLIC` for this loopback profile. The prepared public mode rejects loopback inference and needs a separately approved hosted provider; see `PUBLIC_DEPLOYMENT.md`. No automatic installation/download or public exposure is performed.
