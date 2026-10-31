# NexaAssist — gateways and guardrails presentation

[Open the editable 22-slide PowerPoint](exports/NexaAssist_Gateways_and_Guardrails.pptx)

Instructor-led enterprise LLMOps training, based on the repository snapshot of 25 October 2026. Covers only gateways/routing and security/guardrails; Phoenix and Ragas are supporting evidence.

- [Complete speaker notes](notes/total.md)
- [Canonical detailed Markdown guide](../../operations/GATEWAYS_AND_GUARDRAILS_GUIDE.md)
- [Recorded local deployment results](../../operations/PGVECTOR_VALIDATION.md)
- [Editable slide content](slide_content.json)
- [Delivery checks](validation/delivery_check.json)
- [PowerPoint postflight](validation/NexaAssist_Gateways_and_Guardrails.report.json)

## Slide index

| Slide | Topic | Source anchors |
| --- | --- | --- |
| 01 | Route reliably. Validate every answer. | `app/gateway/litellm.yaml:2`; `app/security/guardrails_service.py:20` |
| 02 | Choose the mechanism for the failure | `app/gateway/litellm.yaml:23`; `app/gateway/litellm_balanced.yaml:2`; `app/gateway/litellm_cache.yaml:31`; `app/chains/guardrails.py:9` |
| 03 | The gateway is inside the policy boundary | `app/compose.yaml:70`; `app/chains/llm.py:14`; `app/chains/guardrails.py:9` |
| 04 | Follow the request in execution order | `app/api/answer.py:45`; `app/services/answer.py:36`; `app/chains/retrieval.py:35`; `app/chains/answer.py:169` |
| 05 | Open these functions as the request runs | `app/api/answer.py:45`; `app/services/answer.py:36`; `app/services/retrieval.py:23`; `app/chains/retrieval.py:35`; `app/chains/answer.py:169` |
| 06 | Use stable aliases for four model routes | `app/gateway/litellm.yaml:2`; `app/chains/llm.py:14`; `app/chains/embeddings.py:44`; `app/compose.yaml:70` |
| 07 | Fail over chat; keep retrieval available | `app/gateway/litellm.yaml:23`; `app/chains/llm.py:14` |
| 08 | Fault drill: break only the chat address | `app/gateway/litellm.yaml:23`; `app/compose.yaml:70` |
| 09 | Balance across independent deployments | `app/gateway/litellm_balanced.yaml:2` |
| 10 | Cache matching generation, not the request | `app/gateway/litellm_cache.yaml:31`; `app/chains/llm.py:14`; `app/chains/answer.py:169` |
| 11 | Keep embedding families in separate corpora | `app/chains/embeddings.py:44`; `app/gateway/openai-embeddings.env.example:2` |
| 12 | Guard the input, draft and source claims | `app/security/input_policy.py:26`; `app/models/answer.py:18`; `app/chains/answer.py:184` |
| 13 | Redact PII before the provider sees it | `app/services/retrieval.py:23`; `app/chains/redaction.py:15`; `app/chains/ingestion.py:64` |
| 14 | Reject explicit instruction overrides early | `app/security/input_policy.py:26`; `app/main.py:31`; `app/chains/answer.py:147` |
| 15 | Treat schema validity as a contract | `app/models/answer.py:18`; `app/chains/answer.py:169`; `app/security/guardrails_service.py:20` |
| 16 | The validator returns a decision, not an answer | `app/security/guardrails_service.py:20`; `app/chains/guardrails.py:9` |
| 17 | Verify quotes before returning an answer | `app/chains/answer.py:184`; `app/chains/context.py:30` |
| 18 | Fail closed at a configured validator | `app/chains/guardrails.py:9`; `app/chains/answer.py:169` |
| 19 | Trace the security calls in this order | `app/services/retrieval.py:23`; `app/security/input_policy.py:26`; `app/models/answer.py:18`; `app/chains/guardrails.py:9`; `app/chains/answer.py:184` |
| 20 | Run one question through four demonstrations | `app/api/answer.py:45`; `app/security/guardrails_service.py:20` |
| 21 | Separate observed results from configured behavior | `app/core/phoenix.py:14`; `app/evaluation/phoenix_export.py:36` |
| 22 | Choose the control; show the evidence | `app/gateway/litellm.yaml:23`; `app/gateway/litellm_cache.yaml:31`; `app/security/input_policy.py:26`; `app/chains/answer.py:184` |

## Validation

All 22 SVG pages passed the final canonical layout gate with zero errors and warnings. Native export postflight passed. Package inspection confirmed 22 slides, 22 notes pages, 412 editable text runs, 488 native shapes and no raster picture elements.

Fault injection, load balancing and caching are documented classroom drills; they were not executed to create this deck. The observed baseline answer, injection rejection, validator decisions and evaluated abstention retain their original qualifiers. No application service configuration changed during slide authoring.

## Editable sources

`svg_output/` contains complete per-slide design sources. `svg_final/` holds self-contained previews. `build_slides.py` authors SVG sources from the page-specific `slide_content.json`; exporter dependencies live in an isolated presentation environment, not the app dependency lockfile. Regeneration must be followed by the documented PPT Master quality gate, notes split, preview finalization and native export.

Line references are snapshot-specific. No narration or custom animation was added. Native PowerPoint application rendering was not inspected.
