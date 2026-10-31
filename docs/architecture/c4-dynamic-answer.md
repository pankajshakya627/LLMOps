# Dynamic view — answer lifecycle

```mermaid
sequenceDiagram
    actor Staff
    participant UI as Streamlit
    participant API as FastAPI route
    participant Service as Answer service
    participant Chain as LCEL answer chain
    participant Atlas as MongoDB Atlas
    participant Model as Model provider
    Staff->>UI: Question + policy date
    UI->>API: POST /answer
    API->>API: Validate request and quota
    API->>Service: answer_policy
    Service->>Service: Scrub query and start usage tracking
    Service->>Chain: ainvoke
    Chain->>Atlas: Scoped retrieval and parent lookup
    Atlas-->>Chain: Evidence + amendments
    alt Evidence missing or required amendment cannot fit
        Chain-->>Service: Safe abstention
    else Context available
        Chain->>Model: Prompt + evidence + strict schema
        Model-->>Chain: Draft
        Chain->>Chain: Output PII and citation validation
        opt Citation invalid, first attempt only
            Chain->>Model: One citation repair
            Model-->>Chain: Revised draft
        end
        Chain-->>Service: Validated answer or safe abstention
    end
    Service-->>API: Answer + provenance + timings
    API-->>UI: JSON response
    opt Sampled answered request
        API->>Model: Background quality judging
    end
```

Evidence: `app/api/answer.py`, `app/services/answer.py`, `app/chains/answer.py`, `app/services/retrieval.py` and `app/services/evaluation.py`. The real chain returns a fixed clarification when scope is ambiguous. This simplified view omits optional reranking and detailed model/provider retries; it does not imply a streaming response or a durable conversational session.
