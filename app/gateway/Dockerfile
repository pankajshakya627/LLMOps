FROM python:3.13-slim
COPY --from=ghcr.io/astral-sh/uv:0.13.1 /uv /usr/local/bin/uv
ENV LITELLM_LOCAL_MODEL_COST_MAP=True
WORKDIR /opt/gateway
COPY app/gateway/requirements.txt ./requirements.txt
RUN uv pip install --system --no-cache -r requirements.txt
RUN python -c "from litellm.integrations.otel.logger import OpenTelemetryV2"
COPY app/gateway/*.yaml ./
RUN useradd --system --create-home --uid 10001 gateway \
    && chown -R gateway:gateway /opt/gateway
USER gateway
EXPOSE 4000
CMD ["litellm", "--config", "/opt/gateway/litellm.yaml", "--host", "0.0.0.0", "--port", "4000", "--num_workers", "1"]
