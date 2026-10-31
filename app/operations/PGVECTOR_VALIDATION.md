# PostgreSQL / pgvector verification — 2026-10-25

The local Docker API on **http://127.0.0.1:8001** now uses pgvector. PostgreSQL
is published on localhost port **5433**, in container `litellm-gateway-postgres-1`.
Phoenix (6006), Guardrails (8101) and the gateway (4001) were reused. The native
API on 8000 was not restarted and retains its earlier backend configuration.

## Software checks

| Check | Result |
|---|---|
| Full offline suite, Phoenix/Ragas SDK fixtures and mock API | 385 passed; no failures or skips |
| Real pgvector integration | 7 passed; no failures or skips |
| Ruff (`app tests training`) | Passed |
| Mypy (`app training`) | Passed; 104 source files |
| Docker API image | Built successfully with the locked Psycopg driver |
| PostgreSQL extension/schema | Explicit initialization succeeded |
| Source ingestion | 8 documents; 177 chunks and 80 parent sections |
| API `/ready` | HTTP 200 |
| API `/retrieve`, maximum home loan, 2026-10-01 | 5 evidence hits |
| Operational Markdown links and shell syntax | Passed |

Receipts: [offline tests](pgvector-offline-tests.xml),
[integration tests](pgvector-integration-tests.xml).

Integration checks use isolated temporary namespaces with **no MongoDB URI**.
They cover six scope filters, exact cosine results, parent key ordering and
literal prefixes, immutable embedding profiles, scoped stale removal/retirement,
linked circular completeness, golden reference lookup, feedback idempotency and
review transitions, FastAPI readiness/retrieval, and unchanged/changed ingestion.
Their rows and corpus manifests are removed afterward.

## Live behavior and Phoenix

The synthetic maximum-loan question returned:

> The maximum loan amount for a NexaHome Loan is ₹7,50,00,000 [2].

Status was `answered`, with one citation and prompt version **1.2.0**. The gateway
reported its `nexa-chat` alias; that alias alone does not prove the underlying
provider deployment. Answer trace: `edfd1520ea5e823af0e138f3d9e793f5`.
Retrieval trace: `a51834c36a41a693cfbc5a4a79150926`.

A separate `/answer/evaluated` request returned `insufficient_evidence` **after
retrieving evidence and attempting generation**. This differs from the earlier
missing-index response, where no evidence reached generation. Ragas reported:

| Metric | Observed result |
|---|---|
| Context recall | 1.0 |
| Context precision | approximately 0.20 |
| Faithfulness | Unavailable: the answer abstained |
| Answer relevancy | Unavailable: the answer abstained |

All four score/status annotations were exported to Phoenix in project
`nexaassist-training`, trace `dc83e470950a325db21275bacde86482`,
span `a290f780fa2915c8`. No numeric answer-quality scores were invented.

The [saved responses](../evaluation/results/pgvector_live_20261025/)
include retrieval, answer and evaluated-answer JSON plus matching evaluation
headers. These observations demonstrate the storage change and trace/evaluation
workflow; they do not establish reliable generation quality.

## Limits

No Atlas connection or Atlas data migration was required. Existing Atlas records,
including earlier feedback, were not copied or deleted. The source register was
re-ingested into the new local database. Existing quality gates remain unchanged
placeholders, and model/prompt versions were not changed to improve these results.

The pgvector implementation supports dense exact search, with no ANN index or
connection pool. Hybrid retrieval is explicitly rejected. Production load,
database role separation, backup/restore and all-corpus transactional ingestion
were not qualified. The local owner account is for development/reference use.

This checkout has no Git metadata or remote; no commit, push or PR was created.
