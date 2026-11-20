"""Enforce the AWS gateway's configured generation limits before calling a provider."""

from fastapi import HTTPException
from litellm.integrations.custom_logger import CustomLogger


class OutputLimit(CustomLogger):
    async def async_pre_call_hook(self, user_api_key_dict, cache, data, call_type):
        from litellm.proxy.proxy_server import llm_router

        model = data.get("model")
        if not isinstance(model, str) or not model.startswith(("nexa-chat-", "nexa-judge-")):
            return
        deployments = llm_router.get_model_list(model_name=model)
        if not deployments:
            return
        limit = min(deployment["litellm_params"]["max_tokens"] for deployment in deployments)
        # OpenAI-compatible clients can also supply provider parameters through extra_body.
        for params in (data, data.get("extra_body")):
            if not isinstance(params, dict):
                continue
            for field in ("max_tokens", "max_completion_tokens", "max_output_tokens"):
                requested = params.get(field)
                if requested is not None and (
                    type(requested) is not int or not 1 <= requested <= limit
                ):
                    raise HTTPException(400, f"{field} must be between 1 and {limit} for {model}")


output_limit = OutputLimit()
