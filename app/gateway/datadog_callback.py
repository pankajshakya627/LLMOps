"""Keep provider error content out of the pinned LiteLLM Datadog callback."""

from litellm.integrations.datadog.datadog_llm_obs import DataDogLLMObsLogger


class PrivateDatadogLogger(DataDogLLMObsLogger):
    def _assemble_error_info(self, standard_logging_payload):
        error = super()._assemble_error_info(standard_logging_payload)
        if error is not None:
            error.update(message="", stack="")
        return error


datadog_callback = PrivateDatadogLogger()
