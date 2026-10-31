from __future__ import annotations

import argparse
import hashlib
import json
import os
import runpy
import sys
import tarfile
from pathlib import Path
from typing import Any
from unittest.mock import Mock

import pytest
import yaml

pytest.importorskip("boto3", reason="AWS tooling checks require uv sync --extra aws")
from infra.aws import lab


def template(path: str) -> dict[str, Any]:
    class Loader(yaml.SafeLoader):
        pass

    Loader.add_multi_constructor(
        "!",
        lambda loader, tag, node: {
            ("Ref" if tag == "Ref" else f"Fn::{tag}"): (
                loader.construct_scalar(node)
                if isinstance(node, yaml.ScalarNode)
                else loader.construct_sequence(node)
            )
        },
    )
    return yaml.load(Path(path).read_text(), Loader=Loader)


def test_host_uses_free_tier_eligible_x86_instance_without_t3_credit_options() -> None:
    config = template("infra/aws/session.yaml")
    assert config["Parameters"]["InstanceType"]["Default"] == "m7i-flex.large"
    assert config["Parameters"]["InstanceType"]["AllowedValues"] == ["m7i-flex.large"]
    assert config["Parameters"]["Ami"]["Default"].endswith("-x86_64")
    host = config["Resources"]["Host"]["Properties"]
    assert "CreditSpecification" not in host
    assert host["InstanceType"] == {"Ref": "InstanceType"}


def test_capacity_reads_memory_without_deployment_or_model_calls(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    ssm = Mock()
    ssm.send_command.return_value = {"Command": {"CommandId": "memory-check"}}
    ssm.get_command_invocation.return_value = {
        "Status": "Success",
        "StandardOutputContent": "Mem: total available\ncontainer memory snapshot",
    }
    monkeypatch.setattr(lab, "client", lambda service: ssm if service == "ssm" else None)
    monkeypatch.setattr(lab, "stack_outputs", lambda stack: {"InstanceId": "i-lab"})
    monkeypatch.setattr(lab.time, "sleep", lambda seconds: None)
    monkeypatch.setattr(sys, "argv", ["lab", "--stack", "nexa-lab-training", "capacity"])
    lab.main()
    assert ssm.send_command.call_args.kwargs["Parameters"]["commands"] == [
        "set -eu; free -b; docker stats --no-stream --format '{{json .}}'"
    ]
    assert "container memory snapshot" in capsys.readouterr().out


@pytest.mark.parametrize("provider", ["openai", "bedrock"])
def test_release_contains_only_synthetic_corpus_and_digest_manifest(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, provider: str
) -> None:
    monkeypatch.setenv("AWS_DEFAULT_REGION", "ap-south-1")
    data = {
        "AppRepository": "registry/app",
        "GatewayRepository": "registry/gateway",
        "GuardrailsRepository": "registry/guardrails",
        "SecretArn": "secret-id",
        "Bucket": "session-bucket",
        "GuardrailId": "guardrail",
        "GuardrailVersion": "1",
        "ModelProvider": provider,
        "OpenAIKeySecretArn": "arn:aws:secretsmanager:ap-south-1:123456789012:secret:nexa-lab-openai-ABC123",
    }
    images = tmp_path / "images.json"
    images.write_text(
        json.dumps(
            {
                k: v + "@sha256:" + "a" * 64
                for k, v in [
                    ("APP_IMAGE", "registry/app"),
                    ("GATEWAY_IMAGE", "registry/gateway"),
                    ("GUARDRAILS_IMAGE", "registry/guardrails"),
                ]
            }
        )
    )
    args = argparse.Namespace(
        release_id="commit-123",
        images=str(images),
        archive=str(tmp_path / "release.tar.gz"),
        provider=provider,
        chat_route="openai/test" if provider == "openai" else "bedrock/converse/test",
        judge_route="openai/test" if provider == "openai" else "bedrock/converse/test",
    )
    archive, digest = lab.prepare_release(args, data)
    assert digest == hashlib.sha256(archive.read_bytes()).hexdigest()
    with tarfile.open(archive) as tar:
        names = tar.getnames()
        assert "corpus/document_register.json" in names
        assert not any(".env" in name or "tests" in name for name in names)
        file = tar.extractfile("release.json")
        assert file is not None
        manifest = json.load(file)
        assert "PASSWORD" not in " ".join(manifest)
        assert manifest["APP_IMAGE"].endswith("@sha256:" + "a" * 64)
        assert manifest["MODEL_PROVIDER"] == provider
        assert "OPENAI_API_KEY" not in manifest
        assert ("compose.bedrock.yaml" in names) == (provider == "bedrock")
        assert any(key.startswith("BEDROCK_") for key in manifest) == (provider == "bedrock")
        assert ("OPENAI_API_KEY_SECRET_ARN" in manifest) == (provider == "openai")
    args.provider = "openai" if provider == "bedrock" else "bedrock"
    with pytest.raises(ValueError, match="Cannot change providers"):
        lab.prepare_release(args, data)
    args.provider = provider
    legacy = {key: value for key, value in data.items() if key != "ModelProvider"}
    if provider == "openai":
        with pytest.raises(ValueError, match="Cannot change providers"):
            lab.prepare_release(args, legacy)
    bad = json.loads(images.read_text())
    bad["APP_IMAGE"] = "registry/app:latest"
    images.write_text(json.dumps(bad))
    with pytest.raises(ValueError, match="digest"):
        lab.prepare_release(args, data)


def test_cleanup_stops_compute_then_empties_versions_then_deletes_only_its_stack(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import boto3

    code = template("infra/aws/session.yaml")["Resources"]["Cleanup"]["Properties"]["Code"][
        "ZipFile"
    ]
    calls: list[str] = []
    ec2, s3, cf = Mock(), Mock(), Mock()
    ec2.terminate_instances.side_effect = lambda **_: calls.append("terminate")
    ec2.get_waiter.return_value.wait.side_effect = lambda **_: calls.append("terminated")

    def paginator(name: str) -> Mock:
        pages = (
            [
                {
                    "Versions": [{"Key": "report", "VersionId": "1"}],
                    "DeleteMarkers": [{"Key": "report", "VersionId": "2"}],
                }
            ]
            if name == "list_object_versions"
            else [{}]
        )
        return Mock(paginate=Mock(return_value=pages))

    s3.get_paginator.side_effect = paginator

    def delete_objects(**_: Any) -> dict[str, Any]:
        calls.append("empty")
        return {}

    s3.delete_objects.side_effect = delete_objects
    cf.delete_stack.side_effect = lambda **_: calls.append("delete_stack")
    monkeypatch.setattr(
        boto3, "client", lambda name: {"ec2": ec2, "s3": s3, "cloudformation": cf}[name]
    )
    monkeypatch.setenv("BUCKET", "own-bucket")
    monkeypatch.setenv("STACK", "own-stack")
    monkeypatch.setenv("INSTANCE", "own-instance")
    namespace: dict[str, Any] = {}
    exec(compile(code, "cleanup", "exec"), namespace)  # noqa: S102 - test the checked-in Lambda.
    with pytest.raises(ValueError):
        namespace["handler"]({}, None)
    assert calls == []
    namespace["handler"]({"operation": "destroy", "stack": "unrelated-stack"}, None)
    assert calls == ["terminate", "terminated", "empty", "delete_stack"]
    cf.delete_stack.assert_called_once_with(StackName="own-stack")
    objects = s3.delete_objects.call_args.kwargs["Delete"]["Objects"]
    assert {item["VersionId"] for item in objects} == {"1", "2"}
    s3.delete_objects.side_effect = None
    s3.delete_objects.return_value = {"Errors": [{"Code": "AccessDenied"}]}
    cf.delete_stack.reset_mock()
    with pytest.raises(RuntimeError, match="cleanup incomplete"):
        namespace["handler"]({"operation": "destroy"}, None)
    cf.delete_stack.assert_not_called()
    # An independently terminated/expired host must not prevent the remaining cleanup.
    from botocore.exceptions import ClientError

    ec2.terminate_instances.side_effect = ClientError(
        {"Error": {"Code": "InvalidInstanceID.NotFound", "Message": "Already gone"}},
        "TerminateInstances",
    )
    s3.delete_objects.return_value = {}
    namespace["handler"]({"operation": "destroy"}, None)
    cf.delete_stack.assert_called_once_with(StackName="own-stack")


def test_session_has_no_inbound_ports_and_no_retained_paid_resources() -> None:
    resources = template("infra/aws/session.yaml")["Resources"]
    assert not resources["SecurityGroup"]["Properties"].get("SecurityGroupIngress")
    assert resources["Host"]["Properties"]["InstanceInitiatedShutdownBehavior"] == "terminate"
    assert "CreditSpecification" not in resources["Host"]["Properties"]
    assert all(resource.get("DeletionPolicy") != "Retain" for resource in resources.values())
    for resource in resources.values():
        if resource["Type"] == "AWS::ECR::Repository":
            assert resource["Properties"]["EmptyOnDelete"] is True
    compose = yaml.safe_load(Path("app/compose.aws.yaml").read_text())
    for service in compose["services"].values():
        assert all(port.startswith("127.0.0.1:") for port in service.get("ports", []))


def test_duplicate_start_never_creates_a_cleanup_receipt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from botocore.exceptions import ClientError

    cf = Mock()
    monkeypatch.setenv("AWS_DEFAULT_REGION", "ap-south-1")
    cf.create_stack.side_effect = ClientError(
        {"Error": {"Code": "AlreadyExistsException", "Message": "Stack already exists"}},
        "CreateStack",
    )
    monkeypatch.setattr(lab, "client", lambda _: cf)
    receipt = tmp_path / "receipt.json"
    args = argparse.Namespace(
        stack="nexa-lab-training",
        minutes=120,
        budget=5,
        boundary_arn="boundary",
        model_resources="model",
        provider="openai",
        openai_secret_arn="arn:aws:secretsmanager:ap-south-1:123456789012:secret:nexa-lab-openai-ABC123",
        cloudformation_role_arn="role",
        receipt=str(receipt),
    )
    with pytest.raises(ClientError):
        lab.create(args)
    assert not receipt.exists()
    cf.delete_stack.assert_not_called()
    # Once create succeeds, a later readiness failure must leave the receipt for cleanup.
    cf.create_stack.side_effect = None
    cf.create_stack.return_value = {"StackId": "new-stack-id"}
    cf.get_waiter.return_value.wait.side_effect = RuntimeError("initial creation failed")
    with pytest.raises(RuntimeError):
        lab.create(args)
    assert json.loads(receipt.read_text()) == {"stack_id": "new-stack-id"}


def test_failed_run_cleanup_refuses_a_replacement_session(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    cf = Mock()
    cf.describe_stacks.return_value = {"Stacks": [{"StackId": "replacement-id"}]}
    monkeypatch.setattr(lab, "client", lambda _: cf)
    cleanup = Mock()
    monkeypatch.setattr(lab, "destroy", cleanup)
    receipt = tmp_path / "receipt.json"
    receipt.write_text('{"stack_id":"original-id"}')
    with pytest.raises(ValueError, match="identity changed"):
        lab.destroy_stack("nexa-lab-training", str(receipt))
    cleanup.assert_not_called()
    cf.delete_stack.assert_not_called()


def test_default_evaluation_refuses_an_existing_bedrock_session(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(lab, "stack_outputs", lambda _: {"ModelProvider": "bedrock"})
    remote = Mock(side_effect=AssertionError("Default evaluation must not call Bedrock"))
    monkeypatch.setattr(lab, "run_remote", remote)
    monkeypatch.setattr(sys, "argv", ["lab", "--stack", "nexa-lab-training", "evaluate"])
    with pytest.raises(SystemExit) as stopped:
        lab.main()
    assert stopped.value.code == 1
    remote.assert_not_called()


@pytest.mark.parametrize(
    "provider,secret,models",
    [
        ("openai", "", ""),
        ("openai", "sk-not-an-arn", ""),
        ("bedrock", "", ""),
    ],
)
def test_missing_provider_credentials_fail_before_provisioning(
    monkeypatch: pytest.MonkeyPatch,
    provider: str,
    secret: str,
    models: str,
) -> None:
    aws = Mock(side_effect=AssertionError("Invalid input must not reach AWS"))
    monkeypatch.setattr(lab, "client", aws)
    with pytest.raises(ValueError):
        lab.create(
            argparse.Namespace(provider=provider, openai_secret_arn=secret, model_resources=models)
        )
    aws.assert_not_called()


@pytest.mark.usefixtures("settings")
def test_default_runtime_uses_openai_without_constructing_a_bedrock_client(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.core.config import Settings
    from app.evaluation.profiles import judge_settings, metric_settings
    from app.security import bedrock

    compose = yaml.safe_load(Path("app/compose.aws.yaml").read_text())
    ui_check = compose["services"]["ui"]["healthcheck"]["test"]
    assert "http://127.0.0.1:8501/_stcore/health" in ui_check[-1]
    gateway = compose["services"]["gateway"]
    assert "/opt/gateway/litellm_openai.yaml" in gateway["command"]
    env = compose["services"]["api"]["environment"]
    assert not any(key.startswith("BEDROCK_") for key in env)
    config = Settings(_env_file=None, **{key.lower(): value for key, value in env.items()})
    assert config.chat_model == "nexa-chat-openai"
    assert judge_settings(config).chat_model == "nexa-judge-openai"
    assert config.embedding_model == metric_settings(config).embedding_model == "nexa-embed-openai"
    assert config.embedding_dimensions == metric_settings(config).embedding_dimensions == 1536
    assert config.embedding_profile == "openai-3-small-gateway-v1"
    blocked = Mock(side_effect=AssertionError("Default OpenAI mode must not construct AWS runtime"))
    monkeypatch.setattr(bedrock, "runtime_client", blocked)
    bedrock.check_content("Synthetic query", "INPUT", config)
    bedrock.check_content("Synthetic answer", "OUTPUT", config)
    blocked.assert_not_called()
    routes = yaml.safe_load(Path("app/gateway/litellm_openai.yaml").read_text())
    assert {entry["model_name"] for entry in routes["model_list"]} == {
        config.chat_model,
        config.eval_judge_model,
        config.embedding_model,
    }
    assert "bedrock" not in json.dumps(routes).lower()
    assert routes["router_settings"]["max_fallbacks"] == 0


@pytest.mark.parametrize("enabled", [False, True])
def test_bedrock_resources_and_all_permissions_require_explicit_opt_in(enabled: bool) -> None:
    for path in ("infra/aws/session.yaml", "infra/aws/github-oidc.yaml"):
        config = template(path)
        values = {key: value.get("Default") for key, value in config["Parameters"].items()}
        if path.endswith("session.yaml"):
            assert values["ModelProvider"] == "openai"
            values["ModelProvider"] = "bedrock" if enabled else "openai"
            values["ModelResources"] = ["arn:aws:bedrock:ap-south-1::foundation-model/test"]
            values["OpenAIKeySecretArn"] = (
                "arn:aws:secretsmanager:ap-south-1:123456789012:secret:nexa-lab-openai-ABC123"
            )
        else:
            assert values["EnableBedrock"] == "false"
            values["EnableBedrock"] = "true" if enabled else "false"

        def resolve(
            value: Any, values: dict[str, Any] = values, config: dict[str, Any] = config
        ) -> Any:
            if not isinstance(value, dict):
                return value
            if "Ref" in value:
                return values[value["Ref"]]
            if "Fn::Condition" in value:
                return resolve(config["Conditions"][value["Fn::Condition"]])
            if "Fn::Equals" in value:
                left, right = value["Fn::Equals"]
                return resolve(left) == resolve(right)
            if "Fn::And" in value:
                return all(resolve(v) for v in value["Fn::And"])
            if "Fn::Not" in value:
                return not resolve(value["Fn::Not"][0])
            separator, items = value["Fn::Join"]
            return separator.join(resolve(items))

        conditions = {name: resolve(expr) for name, expr in config["Conditions"].items()}
        bedrock_actions: list[str] = []
        bedrock_resources = []
        for name, resource in config["Resources"].items():
            if resource.get("Condition") and not conditions[resource["Condition"]]:
                continue
            if resource["Type"].startswith("AWS::Bedrock::"):
                bedrock_resources.append(name)
            props = resource.get("Properties", {})
            policies = [p["PolicyDocument"] for p in props.get("Policies", [])]
            if "PolicyDocument" in props:
                policies.append(props["PolicyDocument"])
            for policy in policies:
                for statement in policy["Statement"]:
                    if "Fn::If" in statement:
                        condition, yes, no = statement["Fn::If"]
                        statement = yes if conditions[condition] else no
                    if statement == {"Ref": "AWS::NoValue"}:
                        continue
                    actions = statement["Action"]
                    if isinstance(actions, str):
                        actions = [actions]
                    bedrock_actions.extend(a for a in actions if a.startswith("bedrock:"))
        assert bool(bedrock_actions) is enabled
        if path.endswith("session.yaml"):
            assert bool(bedrock_resources) is enabled
            assert config["Outputs"]["GuardrailId"]["Condition"] == "UseBedrock"
            assert config["Outputs"]["GuardrailVersion"]["Condition"] == "UseBedrock"


@pytest.mark.parametrize(
    "provider,key",
    [
        ("openai", "sk-fixture"),
        ("openai", "wrong format"),
        ("openai", "sk-bad$key"),
        ("bedrock", None),
    ],
)
def test_host_loads_openai_secret_privately_and_fails_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    provider: str,
    key: str | None,
) -> None:
    source = Path("infra/aws/host.sh").read_text()
    code = source.split("<<'PY'\n", 1)[1].split("\nPY", 1)[0]
    script = tmp_path / "configure.py"
    script.write_text(code)
    (tmp_path / "release.json").write_text(json.dumps({"MODEL_PROVIDER": provider}))
    material = tmp_path / "runtime-secret"
    material.write_text("A" * 96)
    key_file = tmp_path / "openai-secret"
    if key is not None:
        key_file.write_text(key)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", [str(script), str(material), str(key_file)])
    previous_umask = os.umask(0o077)
    try:
        if provider == "openai" and key in ("wrong format", "sk-bad$key"):
            with pytest.raises(ValueError, match="only the API key in plaintext"):
                runpy.run_path(str(script))
            assert not (tmp_path / ".env").exists()
        else:
            runpy.run_path(str(script))
            env = tmp_path / ".env"
            exported = {
                name: json.loads(value)
                for name, value in (line.split("=", 1) for line in env.read_text().splitlines())
            }
            assert ("OPENAI_API_KEY" in exported) is (provider == "openai")
            if provider == "openai":
                assert exported["OPENAI_API_KEY"] == key
            assert env.stat().st_mode & 0o777 == 0o600
            assert not material.exists() and not key_file.exists()
    finally:
        os.umask(previous_umask)
