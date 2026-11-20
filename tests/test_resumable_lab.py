"""Contracts for the non-destructive AWS lifecycle and optional provider."""

import json
from unittest.mock import Mock

import pytest

boto3 = pytest.importorskip("boto3")

from infra.aws import lab
from tests.test_aws_lab import template


def test_optional_claude_uses_its_own_key_without_changing_embeddings():
    base = lab.gateway_profile("openai", "cloudwatch", "")
    dual = lab.gateway_profile("openai", "cloudwatch", "anthropic/claude-example")
    assert dual["model_list"][:-1] == base["model_list"]
    assert dual["model_list"][-1] == {
        "model_name": "nexa-chat-anthropic",
        "litellm_params": {
            "model": "anthropic/claude-example",
            "api_key": "os.environ/ANTHROPIC_API_KEY",
            "max_tokens": 4096,
        },
    }
    assert dual["router_settings"]["max_fallbacks"] == 0
    with pytest.raises(ValueError, match="direct anthropic"):
        lab.gateway_profile("bedrock", "cloudwatch", "anthropic/claude-example")


def test_stop_waits_for_compute_without_touching_data(monkeypatch):
    ec2 = Mock()
    monkeypatch.setattr(lab, "client", lambda service: {"ec2": ec2}[service])
    data = {"InstanceId": "i-fixture", "StopSchedule": "session-expiry", "HostState": "running"}
    lab.power(data, "stop")
    lab.power({**data, "HostState": "stopped"}, "stop")
    ec2.stop_instances.assert_called_once_with(InstanceIds=["i-fixture"])
    assert ec2.get_waiter.return_value.wait.call_count == 2
    with pytest.raises(ValueError, match="legacy"):
        lab.power({"InstanceId": "i-legacy"}, "resume")


def test_resume_arms_before_start_and_reuses_release(monkeypatch):
    events = []
    ec2, scheduler = Mock(), Mock()
    scheduler.get_schedule.return_value = {
        "FlexibleTimeWindow": {"Mode": "OFF"},
        "Target": {"Arn": "function", "RoleArn": "role"},
    }
    scheduler.update_schedule.side_effect = lambda **kwargs: events.append(("arm", kwargs))
    ec2.start_instances.side_effect = lambda **kwargs: events.append(("start", kwargs))
    monkeypatch.setattr(lab, "client", lambda name: {"ec2": ec2, "scheduler": scheduler}[name])
    remote = Mock()
    monkeypatch.setattr(lab, "run_remote", remote)
    data = {"InstanceId": "i-fixture", "StopSchedule": "session-expiry", "HostState": "stopped"}
    lab.power(data, "resume", 120)
    lab.power({**data, "HostState": "running"}, "resume")
    assert [e[0] for e in events] == ["arm", "start"]
    schedule = events[0][1]
    event = json.loads(schedule["Target"]["Input"])
    assert (
        event["operation"] == "stop"
        and schedule["ScheduleExpression"] == f"at({event['deadline']})"
    )
    command = remote.call_args.args[1]
    assert (
        "/opt/nexaassist/current" in command and "--pull never" in command and "/ready" in command
    )
    assert all(term not in command for term in ("ingestion", "/answer", "evaluate", "docker build"))
    remote.side_effect = RuntimeError("unhealthy")
    with pytest.raises(RuntimeError, match="unhealthy"):
        lab.power(data, "resume")
    ec2.stop_instances.assert_called_once_with(InstanceIds=["i-fixture"])


def test_expiry_ignores_stale_delivery_and_stops_only_its_host(monkeypatch):
    resources = template("infra/aws/session.yaml")["Resources"]
    target = resources["Expiry"]["Properties"]["Target"]["Input"]["Fn::Sub"]
    assert json.loads(target)["operation"] == "stop"
    monkeypatch.setenv("SCHEDULE", "own-schedule")
    monkeypatch.setenv("INSTANCE", "i-own")
    ec2, scheduler = Mock(), Mock()
    scheduler.get_schedule.return_value = {"ScheduleExpression": "at(2024-01-01T02:00:00)"}
    monkeypatch.setattr(boto3, "client", lambda name: {"ec2": ec2, "scheduler": scheduler}[name])
    namespace = {}
    exec(resources["Cleanup"]["Properties"]["Code"]["ZipFile"], namespace)  # noqa: S102 - exercise the deployed Lambda source.
    handler = namespace["handler"]
    assert (
        handler({"operation": "stop", "deadline": "2024-01-01T01:00:00"}, None)["status"] == "stale"
    )
    ec2.stop_instances.assert_not_called()
    handler({"operation": "stop", "deadline": "2024-01-01T02:00:00", "instance": "other"}, None)
    ec2.stop_instances.assert_called_once_with(InstanceIds=["i-own"])
    ec2.terminate_instances.assert_not_called()
