# Phoenix result and provider visibility — 25 October 2026

The API now records its completed `/answer` or `/answer/evaluated` payload in
the HTTP request span's Output when `PHOENIX_CAPTURE_CONTENT=true`. With content
capture disabled it records no payload; OpenInference may display a redaction
sentinel. `/health` and `/ready` probes are excluded from new application traces.

`/answer/evaluated` computes metrics and publishes their four annotations in a
background task. The publisher retries span-not-yet-ingested 404 responses within
its existing bound and logs a collector failure without replacing the API result.
The standalone exporter remains available for recovery. Ordinary `/answer`
requests do not automatically compute Ragas metrics with default sampling.

## Where to look

| Project | Inspect | Verified span |
|---|---|---|
| `nexaassist-training` | HTTP request Output and Ragas annotations | `a649d98c799c0a52` |
| `nexaassist-gateway` | `litellm.provider.model` and `llm.provider` | Chat `547e5a0159084d4b`; embedding `233d1cbe8de68c07` |

Direct local links:

- [API result and Ragas](http://127.0.0.1:6006/redirects/spans/a649d98c799c0a52)
- [Ollama chat provider](http://127.0.0.1:6006/redirects/spans/547e5a0159084d4b)
- [Local embedding route](http://127.0.0.1:6006/redirects/spans/233d1cbe8de68c07)

The chat provider attribute is `ollama_chat/qwen3.5:9b-mlx`. The embedding route
attribute is `openai/qwen3-embedding:0.6b`: the `openai` prefix identifies the
OpenAI-compatible adapter targeting native Ollama, not an OpenAI cloud embedding
model. Requested aliases can remain in span titles and `llm.model_name`.
There is no configured Llama model route. Separate gateway and API traces are not
guaranteed to have shared trace IDs; do not infer fallback from nearby timestamps.

Gateway logging uses LiteLLM 1.106.2's official Phoenix OTEL v2 callback, with its
optional SDK and OTLP/HTTP exporter dependencies installed explicitly. Gateway
message capture is `no_content`: the observed output payloads contain only IDs
and model metadata, with no raw messages, vectors or credentials. Application
content capture remains an independent opt-in for synthetic data.

## Verification

- 394 offline tests passed, including real Phoenix instrumentation/client checks.
- Ruff and Mypy passed; 105 source files checked by Mypy.
- API and gateway Docker builds succeeded; model tracing imports are checked in
  the gateway image build.
- A fresh evaluated request had final answer and quality fields on its root
  span and four automatically published annotations.
- Its generation abstained: context recall was 1.0 and precision approximately
  0.20; faithfulness/relevancy remained unavailable with explicit reasons.
- A subsequent real policy request produced both local Qwen gateway spans.
- Gateway trace attributes were checked for absence of raw messages, embedding
  vectors and private credential values.

[Saved synthetic responses and verification](../evaluation/results/phoenix_visibility_20261025/)
and [test receipt](phoenix-visibility-tests.xml) retain the evidence.

## LiteLLM UI boundary

The gateway has no history `DATABASE_URL` and does not enable
`store_prompts_in_spend_logs`. LiteLLM UI Logs therefore does not retain model
response bodies. These changes use Phoenix as requested; they do not add a
second spend-log database or raw-response store.

These checks demonstrate visibility, not generation correctness or reliability.
Existing prompt, model routes, quality gates and corpus contents were preserved.
