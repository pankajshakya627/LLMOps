FROM python:3.13-slim
COPY --from=ghcr.io/astral-sh/uv:0.13.1 /uv /usr/local/bin/uv
ENV OTEL_SDK_DISABLED=true LITELLM_LOCAL_MODEL_COST_MAP=True
WORKDIR /opt/nexaassist
COPY --chmod=u=rw,go=r app/security/requirements.txt ./requirements.txt
RUN uv pip install --system --no-cache -r requirements.txt
COPY --chmod=u=rw,go=r app/__init__.py ./app/__init__.py
COPY --chmod=u=rwX,go=rX app/models ./app/models
COPY --chmod=u=rwX,go=rX app/security ./app/security
RUN useradd --system --create-home --uid 10001 guardrails
USER guardrails
EXPOSE 8101
HEALTHCHECK --interval=15s --timeout=5s --retries=5 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8101/health', timeout=3)"]
CMD ["uvicorn", "app.security.guardrails_service:app", "--host", "0.0.0.0", "--port", "8101"]
