# **LLMOps | Platform-Agnostic Topic Syllabus** 

_Operational disciplines for production large language model systems_ 

## **Scope** 

Focuses on operational lifecycle, evaluation, monitoring, security, cost, reliability and governance. The topics are independent of any cloud provider, model vendor, observability product or orchestration framework. General DevOps, foundational machine learning and application-building tutorials are outside scope. 

## **01. LLM lifecycle and release management** 

- Model inventory and metadata 

- Model selection criteria and baseline benchmarks 

- Model and configuration versioning 

- Model compatibility and provider changes 

- Model promotion, deprecation and retirement 

- Migration planning and rollback validation 

## **02. PromptOps** 

- Prompt registry and ownership 

- Prompt templates and parameter versioning 

- Prompt test cases and baselines 

- Prompt experiments and comparison 

- Prompt regression detection 

- Prompt releases, approvals and rollback 

## **03. Evaluation operations (EvalOps)** 

- Evaluation dataset design and versioning 

- Golden test sets and adversarial cases 

- Reference-based and reference-free evaluation 

- LLM-as-a-judge calibration and bias 

- Human review and annotation workflows 

- Quality metrics, thresholds and release gates 

- Continuous offline and online evaluation 

## **04. LLM tracing and observability** 

- Request, response and model-call traces 

- Prompt, retrieval and tool spans 

- Trace correlation across workflows 

- Token accounting and model metadata 

- Latency: TTFT, TPOT and percentiles 

- Error taxonomy and failure analysis 

LLMOps topic syllabus  |  Platform agnostic 

- Trace sampling, retention and redaction 

## **05. Production quality monitoring** 

- Response correctness and relevance 

- Groundedness and hallucination signals 

- Safety and refusal behavior 

- Structured-output and tool-call validity 

- Production sampling and human feedback 

- Quality regressions and drift alerts 

- Quality dashboards and triage 

## **06. Inference endpoint operations** 

- Endpoint provisioning and configuration 

- Concurrency, batching and streaming 

- Throughput, queueing and tail latency 

- Context and output limit management 

- Caching and capacity planning 

- Autoscaling and cold-start management 

- Endpoint health and benchmarking 

## **07. LLM gateway operations** 

- Unified provider access and routing 

- Rate limits, quotas and token limits 

- Per-tenant access policies 

- Fallback, retry and timeout policies 

- Request and usage logging 

- Model routing and failover validation 

- Gateway availability and policy audits 

## **08. LLM FinOps** 

- Input, output and cached token accounting 

- Cost per request, user and completed task 

- Cost allocation by team and application 

- Budget thresholds and enforcement 

- Cost-aware model selection and routing 

- Usage anomaly detection and forecasting 

- Unit economics and cost-quality tradeoffs 

## **09. LLM security operations** 

- Prompt injection and jailbreak testing 

- Input/output guardrails and validation 

- Secrets and endpoint authentication 

- Tool permissions and least privilege 

- Sensitive-data redaction in traces 

LLMOps topic syllabus  |  Platform agnostic 

- Data exfiltration and abuse monitoring 

- Security evaluation and incident response 

## **10. LLM governance and auditability** 

- Approved model inventory and ownership 

- Model provenance and provider risk 

- Prompt and inference audit trails 

- Data retention and residency controls 

- Access review and policy enforcement 

- Lifecycle and retirement controls 

- Compliance evidence and change history 

## **11. LLM CI/CD and release validation** 

- Prompt and configuration pipelines 

- Automated evaluation in pull requests 

- Model/provider compatibility checks 

- Golden-set regression gates 

- Shadow traffic and canary evaluations 

- Production promotion and rollback 

- Release evidence and reproducibility 

## **12. RAG operations (RAGOps)** 

- Ingestion freshness and failure monitoring 

- Document, chunk and embedding versions 

- Index rebuilds and embedding migrations 

- Retrieval quality: Recall@K, MRR, NDCG 

- Reranker and grounded-answer evaluation 

- Permission-aware retrieval verification 

- Retrieval latency, cost and incident triage 

## **13. Agent operations (AgentOps)** 

- Agent and tool contract versioning 

- Execution traces and trajectory evaluation 

- Tool availability, failures and retries 

- Checkpoint, state and memory lifecycle 

- Loop detection and execution budgets 

- Human approval and authorization controls 

- Multi-agent reliability and cost attribution 

## **14. LLM reliability and incident response** 

- LLM-specific SLIs, SLOs and error budgets 

- Provider outage and degraded-mode handling 

- Rate-limit and timeout incidents 

- Quality and safety incident triage 

LLMOps topic syllabus  |  Platform agnostic 

- Token spikes and cost incidents 

- Runbooks, rollback and recovery testing 

- Post-incident analysis and prevention 

## **15. LLMOps platform capabilities** 

- Shared prompt and model registries 

- Reusable evaluation services 

- Centralized trace and usage pipelines 

- Self-service model onboarding 

- Standard policy and deployment templates 

- Automated lifecycle checks 

- Platform adoption and operational metrics 

## **Suggested study sequence** 

Core: lifecycle management, PromptOps, EvalOps, tracing, quality monitoring, gateway operations and release validation. Next: security, governance, FinOps and reliability. Specialize in inference operations, RAGOps, AgentOps and platform engineering according to deployment responsibilities. 

LLMOps topic syllabus  |  Platform agnostic 

