# Dependencies and license notes

No model weights, runtime binaries, browser, virtual environment, third-party source repository or assignment PDF is bundled. The app's dependency declarations are in `requirements.txt`; pip obtains dependencies and their transitive packages separately. Offline use requires those packages to be available already.

| Dependency | Verified version | Declared license |
| --- | --- | --- |
| FastAPI | 0.141.1 | MIT |
| Uvicorn | 0.52.1 | BSD-3-Clause |
| HTTPX | 0.28.1 | BSD-3-Clause |
| Pydantic | 2.13.4 | MIT |

Declarations were checked in installed package metadata. Their license texts and any required notices accompany their own distributions; this table is not a complete transitive SBOM. Playwright/Chrome are optional development tools, not bundled dependencies.

The base Qwen3.5-27B and earlier Qwen3.5-4B model cards declare Apache-2.0; the exact quantizer repository identity for the existing 27B compressed files is not independently resolved, and weights are not distributed; vLLM declares Apache-2.0. The earlier Dolphin3-Llama3.1-8B Q4_K_M profile uses Llama 3.1 model terms. One historical Qwen2.5-Coder-3B experiment used the Qwen Research License, which has noncommercial restrictions. Do not infer a license from another size in a model family. Retained experimental text/results do not bundle those weights or grant redistribution rights to them. Review exact terms before distributing any model/runtime assets.

**Application source license:** no project license has been selected in this work. Public visibility does not by itself grant unrestricted reuse. The owner should choose a license intentionally before advertising this as reusable open-source software. No ownership or third-party distribution permission is invented here.

The course assignment PDF is private reference material and is excluded from the source package. Historical local machine/session inventories and original cloud transfer archives are likewise excluded.
