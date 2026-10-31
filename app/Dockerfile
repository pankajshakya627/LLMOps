FROM python:3.14-slim AS dependencies
COPY --from=ghcr.io/astral-sh/uv:0.13.1 /uv /usr/local/bin/uv
RUN apt-get update \
    && apt-get install -y --no-install-recommends g++ \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /opt/nexaassist
ENV UV_LINK_MODE=copy
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv uv sync --locked --no-dev --extra evaluation --extra ui --extra aws

FROM python:3.14-slim
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /opt/nexaassist
COPY --from=dependencies /opt/nexaassist/.venv ./.venv
COPY --chmod=u=rwX,go=rX app ./app
ENV PATH="/opt/nexaassist/.venv/bin:$PATH"
RUN useradd --system --no-create-home --uid 10001 nexaassist
USER nexaassist
EXPOSE 8000
# Liveness only; /ready also checks the selected database and is meant for the orchestrator's readiness probe.
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3)"]
CMD ["uvicorn", "app.phoenix_main:app", "--host", "0.0.0.0", "--port", "8000"]
