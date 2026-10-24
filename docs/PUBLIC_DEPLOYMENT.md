# Public deployment preparation

No public service has been created. Render is the prepared web-host option; GitHub repository, Render account/service destination and approved hosted inference remain pending confirmation. This configuration never exposes the personal PC/GPU. Public mode rejects local-model and loopback providers and does not download weights. Its default is clearly labelled demo with live inference unavailable, not a substitute presented as real inference.

## Confirmed safeguards

- 110 KB body cap including streamed bodies; 10 second public body-read timeout.
- One shared expensive-work slot across reviews and immutable fixture runs. Busy requests get 429; no work queue or automatic retry.
- Single-process 60 second sliding budgets: 6 admitted POSTs per transport peer, 20 globally. Peer identities are salted hashes in bounded volatile memory, not logged. Arbitrary `Forwarded`/`X-Forwarded-For` headers do not select identity. Deployment disables proxy-header trust. Shared proxies/NATs can share a budget; this conservative MVP limit is not distributed abuse protection. One worker/one instance is required. Revisit with a verified edge proxy and shared limiter before scaling.
- Hosted inference requires server-owned HTTPS URL/model/key, explicit external-call enablement, provider display name/policy URL, valid timeout configuration and browser consent bound to that configuration. Missing/mismatched consent or missing configuration fails closed; inputs cannot supply an upstream URL.
- Public provider timeout is 30–90 seconds; generation is capped at 1024 output tokens. A timeout cannot prove the remote provider stopped; warning/recovery requires a deliberate user action.
- Server credentials are never part of prompts/status/exports. HTTP/input-validation errors are app-owned and do not echo input/upstream bodies. If an upstream echoes the configured server key in model content, the request fails without returning that content.
- No source/request-body logging or persistence in the live app; deployment disables access logs. Cloud host and external provider have separate processing/technical-log policies. Successful review exports intentionally contain the submitting user's artifacts and raw model output for their own audit; review them before sharing. The app does not redact secrets the user elects to put in their own source. Do not submit private material without permission.
- Uploaded Python is AST-inspected only. Only immutable bundled fixtures execute under the existing allowlist and bounds. No arbitrary-code sandbox or new execution path is provided.

## Review and deploy to the confirmed destination

1. Use the audited clean source candidate, not the full working tree. It excludes weights, caches, credentials, raw private machine/session metadata and this assignment PDF. Source license selection remains the owner's decision.
2. In the confirmed Render account, create the approved Web Service from the confirmed GitHub repository using `render.yaml`/Docker. The container listens on Render's `PORT` (default 10000); health check is `/healthz`. Do not run this public bind directly on the PC. [Render FastAPI instructions](https://render.com/docs/deploy-fastapi), [web-service port contract](https://render.com/docs/web-services).
3. Free web hosting has cold-start/resource limitations and no GPU model here. Render documents spin-down after 15 minutes idle and a roughly minute-long wakeup; free filesystems are ephemeral. It is suitable for a bounded demo, not an uptime promise. Confirm actual eligibility/quotas in the account; do not select paid compute without authorization. [Free-service limitations](https://render.com/docs/free).
4. For real public inference, first approve a hosted provider/model, cost/usage limits and processing terms. Then set server dashboard variables: `TE_PROVIDER=openai-compatible`, approved HTTPS `TE_API_BASE`, actual `TE_MODEL`, `TE_ALLOW_REMOTE=1`, secret `TE_API_KEY`, `TE_PUBLIC_PROVIDER_NAME`, provider's HTTPS `TE_PUBLIC_PROVIDER_POLICY_URL`, `TE_TIMEOUT_SECONDS=90`, `TE_MAX_TOKENS=1024`. Do not commit credentials or use the PC's endpoint. Groq was proposed for consideration; no account/key, allowance, model or data-processing approval has been verified. No paid API call is authorized.
5. Check `/healthz`, status/privacy labels, demo, explicit live consent, real review/refinement and exports, invalid-input/error paths, busy/rate responses and mobile layout. View signed out. If provider configuration is absent, verify a live request returns 503 and the UI clearly offers labelled demo only.
6. Publish the actual app/GitHub/video URLs only after destination confirmation and successful link checks. Submit the course form only after final fields are reviewed. No public resource or account has been changed by these files.

## Optional isolated container check

Build/run only on loopback for local QA; no model or API key is needed for the labelled demo:

```bash
docker build -t test-evidence:public-candidate .
docker run --rm --read-only --tmpfs /tmp:size=64m,mode=1777 \
  --memory=512m --cpus=0.5 --pids-limit=64 --cap-drop=ALL \
  --security-opt=no-new-privileges -p 127.0.0.1:18765:10000 \
  test-evidence:public-candidate
```

This container example is a local QA command, not a public deployment. The cloud account/provider/key/destination remain the publication blockers. There is no tunnel, firewall change, GPU sharing or automatic cloud fallback.
