"""Exercise the pinned private proxy against local OpenAI and Anthropic HTTP fixtures."""

import json
import os
import subprocess
import sys
import tempfile
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, ClassVar

import httpx

from app.models.answer import AnswerDraft
from infra.aws.lab import gateway_profile

DRAFT = {
    "status": "answered",
    "answer": "The test limit is ten [1].",
    "evidence": [{"evidence_id": 1, "quote": "The test limit is ten."}],
}


class Upstream(BaseHTTPRequestHandler):
    calls: ClassVar[list[tuple[str, str]]] = []

    def log_message(self, *args: Any) -> None:
        pass

    def do_POST(self) -> None:
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        model = body["model"]
        self.calls.append((self.path.split("?")[0], model))
        if self.path.startswith("/v1/messages"):
            assert self.headers["x-api-key"] == "sk-ant-fixture"
            content: list[dict[str, Any]] = [{"type": "text", "text": json.dumps(DRAFT)}]
            reason = "end_turn"
            if body.get("tools"):
                content = [
                    {
                        "type": "tool_use",
                        "id": "toolu_fixture",
                        "name": body["tools"][0]["name"],
                        "input": DRAFT,
                    }
                ]
                reason = "tool_use"
            response = {
                "type": "message",
                "id": "msg_fixture",
                "role": "assistant",
                "model": model,
                "content": content,
                "stop_reason": reason,
                "usage": {"input_tokens": 3, "output_tokens": 3},
            }
        else:
            assert self.headers["Authorization"] == "Bearer sk-openai-fixture"
            if self.path == "/v1/embeddings":
                response = {
                    "object": "list",
                    "model": model,
                    "usage": {"prompt_tokens": 1, "total_tokens": 1},
                    "data": [{"object": "embedding", "index": 0, "embedding": [0.25] * 1536}],
                }
            else:
                assert self.path == "/v1/chat/completions"
                response = {
                    "id": "chatcmpl-fixture",
                    "object": "chat.completion",
                    "created": 1,
                    "model": model,
                    "choices": [
                        {
                            "index": 0,
                            "finish_reason": "stop",
                            "message": {"role": "assistant", "content": json.dumps(DRAFT)},
                        }
                    ],
                    "usage": {"prompt_tokens": 3, "completion_tokens": 3, "total_tokens": 6},
                }
        data = json.dumps(response).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def main() -> None:
    profile = gateway_profile("openai", "cloudwatch", "anthropic/claude-haiku-4-5-20251001")
    with (
        ThreadingHTTPServer(("127.0.0.1", 0), Upstream) as server,
        tempfile.TemporaryDirectory() as tmp,
    ):
        threading.Thread(target=server.serve_forever, daemon=True).start()
        origin = f"http://127.0.0.1:{server.server_port}"
        for entry in profile["model_list"]:
            params = entry["litellm_params"]
            params["api_base"] = (
                origin if entry["model_name"] == "nexa-chat-anthropic" else origin + "/v1"
            )
        path = Path(tmp, "gateway.yaml")
        path.write_text(json.dumps(profile))
        port = 14001
        proxy = subprocess.Popen(
            [
                str(Path(sys.executable).with_name("litellm")),
                "--config",
                str(path),
                "--host",
                "127.0.0.1",
                "--port",
                str(port),
            ],
            env={
                "PATH": os.environ["PATH"],
                "HOME": tmp,
                "OPENAI_API_KEY": "sk-openai-fixture",
                "ANTHROPIC_API_KEY": "sk-ant-fixture",
                "OPENAI_LITELLM_CHAT_MODEL": "openai/gpt-6-luna",
                "OPENAI_LITELLM_JUDGE_MODEL": "openai/gpt-6-luna",
                "LITELLM_MASTER_KEY": "sk-fixture",
                "LITELLM_LOCAL_MODEL_COST_MAP": "True",
                "LITELLM_TELEMETRY": "False",
            },
        )
        try:
            with httpx.Client(
                base_url=f"http://127.0.0.1:{port}", timeout=20, trust_env=False
            ) as client:
                for _ in range(120):
                    if proxy.poll() is not None:
                        raise RuntimeError("Proxy exited before readiness")
                    try:
                        if client.get("/health/liveliness").is_success:
                            break
                    except httpx.ConnectError:
                        pass
                    time.sleep(0.5)
                client.headers["Authorization"] = "Bearer sk-fixture"
                messages = [{"role": "user", "content": "Return the fixture"}]
                schema = AnswerDraft.model_json_schema()
                for alias in ("nexa-chat-openai", "nexa-chat-anthropic"):
                    result = (
                        client.post(
                            "/v1/chat/completions",
                            json={
                                "model": alias,
                                "messages": messages,
                                "response_format": {
                                    "type": "json_schema",
                                    "json_schema": {
                                        "name": "Fixture",
                                        "strict": True,
                                        "schema": schema,
                                    },
                                },
                            },
                        )
                        .raise_for_status()
                        .json()
                    )
                    draft = AnswerDraft.model_validate_json(
                        result["choices"][0]["message"]["content"]
                    )
                    assert draft.model_dump() == DRAFT
                result = client.post(
                    "/v1/embeddings", json={"model": "nexa-embed-openai", "input": ["x"]}
                )
                assert len(result.raise_for_status().json()["data"][0]["embedding"]) == 1536
                del client.headers["Authorization"]
                result = client.post(
                    "/v1/messages",
                    headers={"x-api-key": "sk-fixture", "anthropic-version": "2023-06-01"},
                    json={"model": "nexa-chat-anthropic", "messages": messages, "max_tokens": 32},
                )
                assert result.raise_for_status().json()["content"][0]["type"] == "text"
                assert Upstream.calls == [
                    ("/v1/chat/completions", "gpt-6-luna"),
                    ("/v1/messages", "claude-haiku-4-5-20251001"),
                    ("/v1/embeddings", "text-embedding-3-small"),
                    ("/v1/messages", "claude-haiku-4-5-20251001"),
                ], Upstream.calls
        finally:
            proxy.terminate()
            proxy.wait(timeout=20)
            server.shutdown()
    print("Four routed requests passed against credential-isolated upstream fixtures.")


if __name__ == "__main__":
    main()
