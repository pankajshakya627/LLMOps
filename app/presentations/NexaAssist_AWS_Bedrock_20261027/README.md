# NexaAssist AWS Bedrock LLMOps deployment deck

An **18-slide, editable 16:9 PowerPoint** for an instructor-led enterprise workshop. It shows the proposed AWS architecture, migration from Ollama/Qwen vectors to Bedrock/Titan, safety boundaries, Phoenix tracing, Ragas quality and incident analysis.

- [PowerPoint](exports/NexaAssist_AWS_Bedrock_20261027_223656.pptx)
- [Speaker notes](notes/total.md)
- [Companion workshop guide](AWS_LAB_GUIDE.md)
- [Full AWS deployment design](../../operations/AWS_DEPLOYMENT.md)

This is a design and training artifact. The current local application is still configured for Ollama; AWS Bedrock routes and Bedrock Guardrails calls are not implemented or tested.

This deck shows the earlier self-hosted Phoenix option. The updated [AWS deployment design](../../operations/AWS_DEPLOYMENT.md) uses Arize AX enterprise SaaS instead; its observability slides have not been regenerated.
