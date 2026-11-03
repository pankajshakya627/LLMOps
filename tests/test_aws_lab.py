from __future__ import annotations

import argparse
import fnmatch
import hashlib
import io
import json
import os
import re
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
        "DatadogKeySecretArn": "arn:aws:secretsmanager:ap-south-1:123456789012:secret:nexa-lab-datadog-ABC123",
        "DatadogSite": "datadoghq.com",
        "DatadogMlApp": "nexaassist",
        "Bucket": "session-bucket",
        "GuardrailId": "guardrail",
        "GuardrailVersion": "1",
        "ModelProvider": provider,
        "UiAllowedCidr": "8.8.8.8/32",
        "ApplicationUrl": "http://1.1.1.1:8501",
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


def test_session_exposes_only_restricted_ui_and_retains_no_paid_resources() -> None:
    config = template("infra/aws/session.yaml")
    resources = config["Resources"]
    assert not resources["SecurityGroup"]["Properties"].get("SecurityGroupIngress")
    assert resources["SecurityGroup"]["Properties"]["Tags"] == [
        {"Key": "Session", "Value": {"Ref": "AWS::StackName"}}
    ]
    ingress = [r for r in resources.values() if r["Type"] == "AWS::EC2::SecurityGroupIngress"]
    assert ingress == [
        {
            "Type": "AWS::EC2::SecurityGroupIngress",
            "Properties": {
                "GroupId": {"Ref": "SecurityGroup"},
                "IpProtocol": "tcp",
                "FromPort": 8501,
                "ToPort": 8501,
                "CidrIp": {"Ref": "UiAllowedCidr"},
            },
        }
    ]
    parameter = config["Parameters"]["UiAllowedCidr"]
    assert "Default" not in parameter
    assert re.fullmatch(parameter["AllowedPattern"], "8.8.8.8/32")
    for invalid in ("0.0.0.0/0", "8.8.8.0/24", "::/32", "999.1.1.1/32", "8.8.8.8"):
        assert not re.fullmatch(parameter["AllowedPattern"], invalid)
    assert config["Outputs"]["UiAllowedCidr"] == {"Value": {"Ref": "UiAllowedCidr"}}
    assert config["Outputs"]["ApplicationUrl"] == {
        "Value": {"Fn::Sub": "http://${Host.PublicIp}:8501"}
    }
    assert resources["Host"]["Properties"]["InstanceInitiatedShutdownBehavior"] == "terminate"
    assert "CreditSpecification" not in resources["Host"]["Properties"]
    assert all(resource.get("DeletionPolicy") != "Retain" for resource in resources.values())
    for resource in resources.values():
        if resource["Type"] == "AWS::ECR::Repository":
            assert resource["Properties"]["EmptyOnDelete"] is True
    compose = yaml.safe_load(Path("app/compose.aws.yaml").read_text())
    assert compose["services"]["ui"]["ports"] == ["0.0.0.0:8501:8501"]
    assert compose["services"]["api"]["ports"] == ["127.0.0.1:8000:8000"]
    assert "datadog-agent" not in compose["services"]
    for name in ("postgres", "gateway", "guardrails"):
        assert not compose["services"][name].get("ports")


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
        ui_allowed_cidr="8.8.8.8/32",
        openai_secret_arn="arn:aws:secretsmanager:ap-south-1:123456789012:secret:nexa-lab-openai-ABC123",
        datadog_secret_arn="arn:aws:secretsmanager:ap-south-1:123456789012:secret:nexa-lab-datadog-ABC123",
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


@pytest.mark.parametrize("action", ["evaluate", "destroy"])
def test_legacy_sessions_keep_evaluation_and_cleanup_available(
    monkeypatch: pytest.MonkeyPatch, action: str
) -> None:
    remote = Mock()
    cleanup = Mock()
    monkeypatch.setattr(lab, "run_remote", remote)
    monkeypatch.setattr(lab, "destroy_stack", cleanup)
    monkeypatch.setattr(
        lab,
        "stack_outputs",
        lambda _: {"ModelProvider": "openai", "InstanceId": "i-legacy", "Bucket": "legacy"},
    )
    monkeypatch.setattr(sys, "argv", ["lab", "--stack", "nexa-lab-training", action])
    lab.main()
    if action == "destroy":
        cleanup.assert_called_once_with("nexa-lab-training", None)
        remote.assert_not_called()
    else:
        remote.assert_called_once_with(
            "i-legacy", "set -eu; cd /opt/nexaassist/current; bash host.sh evaluate"
        )
        cleanup.assert_not_called()


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
            argparse.Namespace(
                provider=provider,
                openai_secret_arn=secret,
                model_resources=models,
                ui_allowed_cidr="8.8.8.8/32",
            )
        )
    aws.assert_not_called()


@pytest.mark.parametrize(
    "cidr",
    [
        "",
        "invalid",
        "8.8.8.8",
        "8.8.8.0/24",
        "0.0.0.0/0",
        "10.0.0.1/32",
        "172.16.0.1/32",
        "192.168.1.1/32",
        "127.0.0.1/32",
        "169.254.1.1/32",
        "100.64.0.1/32",
        "192.0.2.1/32",
        "224.0.0.1/32",
        "255.255.255.255/32",
        "::1/128",
        "2606:4700:4700::1111/128",
        "8.8.8.8/255.255.255.255",
    ],
)
def test_invalid_ui_cidr_fails_before_any_aws_client(
    monkeypatch: pytest.MonkeyPatch,
    cidr: str,
) -> None:
    aws = Mock(side_effect=AssertionError("Invalid CIDR must not reach AWS"))
    monkeypatch.setattr(lab, "client", aws)
    monkeypatch.setattr(lab.boto3.session, "Session", aws)
    with pytest.raises(ValueError, match="global IPv4 /32") as error:
        lab.create(
            argparse.Namespace(
                ui_allowed_cidr=cidr,
                provider="bedrock",
                model_resources="model",
                minutes=120,
                boundary_arn="boundary",
            )
        )
    if cidr:
        assert cidr not in str(error.value)
    aws.assert_not_called()


def test_create_requires_ui_cidr_and_passes_it_to_cloudformation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setenv("AWS_DEFAULT_REGION", "ap-south-1")
    cf = Mock()
    cf.create_stack.return_value = {"StackId": "new-stack-id"}
    monkeypatch.setattr(lab, "client", lambda _: cf)
    monkeypatch.setattr(lab, "stack_outputs", lambda _: {"UiAllowedCidr": "8.8.8.8/32"})
    argv = [
        "lab",
        "--stack",
        "nexa-lab-training",
        "create",
        "--provider",
        "bedrock",
        "--datadog-secret-arn",
        "arn:aws:secretsmanager:ap-south-1:123456789012:secret:nexa-lab-datadog-ABC123",
        "--model-resources",
        "model",
        "--boundary-arn",
        "boundary",
        "--cloudformation-role-arn",
        "role",
        "--receipt",
        str(tmp_path / "receipt"),
        "--output",
        str(tmp_path / "outputs"),
    ]
    monkeypatch.setattr(sys, "argv", argv)
    with pytest.raises(SystemExit) as stopped:
        lab.main()
    assert stopped.value.code == 2
    cf.create_stack.assert_not_called()
    monkeypatch.setattr(sys, "argv", [*argv, "--ui-allowed-cidr", "8.8.8.8/32"])
    lab.main()
    parameters = {
        p["ParameterKey"]: p["ParameterValue"]
        for p in cf.create_stack.call_args.kwargs["Parameters"]
    }
    assert parameters["UiAllowedCidr"] == "8.8.8.8/32"
    assert "8.8.8.8" not in capsys.readouterr().out


def test_only_cloudformation_role_can_manage_tagged_session_ui_ingress() -> None:
    config = template("infra/aws/github-oidc.yaml")
    actions = {"ec2:AuthorizeSecurityGroupIngress", "ec2:RevokeSecurityGroupIngress"}
    matches = []
    for name, resource in config["Resources"].items():
        props = resource.get("Properties", {})
        policies = [p["PolicyDocument"] for p in props.get("Policies", [])]
        if "PolicyDocument" in props:
            policies.append(props["PolicyDocument"])
        for policy in policies:
            for statement in policy["Statement"]:
                allowed = statement.get("Action", [])
                allowed = [allowed] if isinstance(allowed, str) else allowed
                assert "cloudformation:UpdateStack" not in allowed
                if actions.intersection(allowed):
                    matches.append((name, statement))
    assert matches == [
        (
            "CloudFormationRole",
            {
                "Effect": "Allow",
                "Action": ["ec2:AuthorizeSecurityGroupIngress", "ec2:RevokeSecurityGroupIngress"],
                "Resource": {
                    "Fn::Sub": "arn:${AWS::Partition}:ec2:${AWS::Region}:${AWS::AccountId}:security-group/*"
                },
                "Condition": {"StringLike": {"ec2:ResourceTag/Session": "nexa-lab-*"}},
            },
        )
    ]
    host = template("infra/aws/session.yaml")["Resources"]["HostRole"]
    assert not actions.intersection(re.findall(r"ec2:\w+", json.dumps(host)))


@pytest.mark.parametrize(
    "changes",
    [
        {},
        {"UiAllowedCidr": "8.8.8.8/32"},
        {"ApplicationUrl": "http://1.1.1.1:8501"},
        {"UiAllowedCidr": "0.0.0.0/0", "ApplicationUrl": "http://1.1.1.1:8501"},
        {"UiAllowedCidr": "8.8.8.8/32", "ApplicationUrl": "http://127.0.0.1:8501"},
        {"UiAllowedCidr": "8.8.8.8/32", "ApplicationUrl": "https://1.1.1.1:8501"},
    ],
)
def test_legacy_release_rejected_before_artifacts_or_aws(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    changes: dict[str, str],
) -> None:
    aws = Mock(side_effect=AssertionError("Legacy release must not reach AWS"))
    monkeypatch.setattr(lab, "client", aws)
    archive = tmp_path / "release.tar.gz"
    with pytest.raises(ValueError, match="destroy.*create"):
        lab.prepare_release(
            argparse.Namespace(provider="openai", archive=str(archive)),
            {"ModelProvider": "openai", **changes},
        )
    assert not archive.exists()
    aws.assert_not_called()


@pytest.mark.parametrize("provider", [None, "openai"])
@pytest.mark.parametrize("fresh", [False, True])
def test_status_checks_ui_only_for_release_and_keeps_saved_cidr_private(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    provider: str | None,
    fresh: bool,
) -> None:
    data = {"ModelProvider": "openai", "InstanceId": "i-lab"}
    if fresh:
        data.update(UiAllowedCidr="8.8.8.8/32", ApplicationUrl="http://1.1.1.1:8501")
    monkeypatch.setattr(lab, "stack_outputs", lambda _: data)
    argv = ["lab", "--stack", "nexa-lab-training", "status"]
    monkeypatch.setattr(sys, "argv", argv + (["--provider", provider] if provider else []))
    if provider and not fresh:
        with pytest.raises(SystemExit) as stopped:
            lab.main()
        assert stopped.value.code == 1
        assert "destroy" in capsys.readouterr().out
    else:
        lab.main()
        result = capsys.readouterr().out
        assert "i-lab" in result
        assert "8.8.8.8" not in result


def test_successful_deploy_reports_application_url(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    archive = tmp_path / "release.tar.gz"
    archive.write_bytes(b"fixture")
    monkeypatch.setattr(lab, "prepare_release", lambda args, data: (archive, "digest"))
    monkeypatch.setattr(lab, "client", lambda _: Mock())
    monkeypatch.setattr(lab, "run_remote", lambda instance, command: {})
    monkeypatch.setenv("AWS_DEFAULT_REGION", "ap-south-1")
    lab.deploy(
        argparse.Namespace(release_id="test"),
        {
            "ExpiresAt": "2099-01-01T00:00:00",
            "Bucket": "lab-bucket",
            "InstanceId": "i-lab",
            "UiAllowedCidr": "8.8.8.8/32",
            "ApplicationUrl": "http://1.1.1.1:8501",
        },
    )
    result = json.loads(capsys.readouterr().out)
    assert any("http://1.1.1.1:8501" in action for action in result["next_actions"])
    assert "8.8.8.8" not in json.dumps(result)


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
    env = {
        **env,
        "DD_API_KEY": "synthetic",
        "DD_SITE": "datadoghq.com",
        "DD_ENV": "test",
        "DD_LLMOBS_ENABLED": "true",
        "DD_LLMOBS_ML_APP": "nexaassist",
        "DD_CAPTURE_CONTENT": "false",
    }
    config = Settings(_env_file=None, **{key.lower(): value for key, value in env.items()})
    assert config.dd_capture_content is False
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
    datadog_file = tmp_path / "datadog-secret"
    datadog_file.write_text("a" * 32)
    monkeypatch.setattr(sys, "argv", [str(script), str(material), str(key_file), str(datadog_file)])
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


def test_aws_monitoring_uses_agentless_exports_and_layer_free_forwarder():
    compose = yaml.safe_load(Path("app/compose.aws.yaml").read_text())
    assert "datadog-agent" not in compose["services"]
    env = compose["services"]["api"]["environment"]
    assert env["DD_LLMOBS_AGENTLESS_ENABLED"] == "true"
    assert env["DD_METRICS_ENABLED"] == "true"
    assert env["DD_TRACE_ENABLED"] == "false"
    forwarder = template("infra/aws/datadog-forwarder.yaml")
    nested = forwarder["Resources"]["ForwarderStack"]["Properties"]
    assert nested["Parameters"]["InstallAsLayer"] == "false"
    assert nested["TemplateURL"].startswith(
        "https://datadog-cloudformation-template.s3.amazonaws.com/"
    )
    assert forwarder["Parameters"]["DdApiKey"]["NoEcho"] is True
    permission = forwarder["Resources"]["ForwarderLogPermission"]["Properties"]
    assert permission["SourceAccount"] == {"Ref": "AWS::AccountId"}
    assert "ApplicationLogGroupName" in permission["SourceArn"]["Fn::Sub"]


def test_application_logs_are_owned_by_the_session_and_writes_stay_scoped():
    config = template("infra/aws/session.yaml")
    assert "ApplicationLogGroupName" not in config["Parameters"]
    assert "Condition" not in config["Resources"]["Logs"]
    policies = config["Resources"]["HostRole"]["Properties"]["Policies"]
    statements = [
        s for p in policies for s in p["PolicyDocument"]["Statement"] if "Fn::If" not in s
    ]
    logs_write = next(
        s for s in statements if s["Action"] == ["logs:CreateLogStream", "logs:PutLogEvents"]
    )
    assert logs_write["Resource"] == {"Fn::GetAtt": "Logs.Arn"}


def test_session_boundary_allows_only_selected_log_group_families():
    bootstrap = template("infra/aws/github-oidc.yaml")
    statements = bootstrap["Resources"]["SessionBoundary"]["Properties"]["PolicyDocument"][
        "Statement"
    ]
    logs_write = next(
        s for s in statements if s.get("Action") == ["logs:CreateLogStream", "logs:PutLogEvents"]
    )
    resources = [s["Fn::Sub"].rsplit("log-group:", 1)[1] for s in logs_write["Resource"]]
    for group in (
        "/nexaassist/",
        "/nexaassist/nexa-lab-validation",
        "/aws/lambda/nexa-lab-validation-cleanup",
    ):
        assert any(fnmatch.fnmatchcase(group + ":stream", resource) for resource in resources)
    for group in ("/nexaassist/unrelated", "/other-app/", "/aws/lambda/unrelated"):
        assert not any(fnmatch.fnmatchcase(group + ":stream", resource) for resource in resources)


def test_host_corpus_is_readable_by_runtime_without_exposing_secrets():
    host = Path("infra/aws/host.sh").read_text()
    assert "chown -R 10001:10001 corpus" in host
    assert "chmod -R u=rwX,go= corpus" in host
    assert host.index("chmod -R u=rwX,go= corpus") < host.index("python -m app.services.ingestion")
    assert "chmod 600 .env" in host


def test_session_forwarder_owns_logs_and_uses_immutable_code_with_scoped_access():
    config = template("infra/aws/session.yaml")
    resources = config["Resources"]
    function = resources["DatadogForwarder"]["Properties"]
    assert function["Code"] == {
        "S3Bucket": {"Ref": "Artifacts"},
        "S3Key": "datadog/forwarder.zip",
        "S3ObjectVersion": {"Fn::GetAtt": "ForwarderCode.VersionId"},
    }
    assert function["Runtime"] == "python3.14" and function["Architectures"] == ["arm64"]
    role = resources["ForwarderRole"]["Properties"]
    assert role["PermissionsBoundary"] == {"Ref": "BoundaryArn"}
    assert "ManagedPolicyArns" not in role
    grants = role["Policies"][0]["PolicyDocument"]["Statement"]
    assert {s["Action"] for s in grants if isinstance(s["Action"], str)} == {
        "secretsmanager:GetSecretValue"
    }
    assert grants[0]["Resource"] == {"Ref": "DatadogKeySecretArn"}
    assert grants[1]["Resource"] == {"Fn::GetAtt": "ForwarderLogs.Arn"}
    assert function["Environment"]["Variables"]["DD_STORE_FAILED_EVENTS"] == "false"
    assert "DD_S3_BUCKET_NAME" not in function["Environment"]["Variables"]
    assert resources["LogSubscription"]["DependsOn"] == "ForwarderPermission"
    permission = resources["ForwarderPermission"]["Properties"]
    assert permission["SourceAccount"] == {"Ref": "AWS::AccountId"}
    assert permission["SourceArn"] == {"Fn::GetAtt": "Logs.Arn"}
    for name in ("ForwarderLogs", "ForwarderRole", "DatadogForwarder", "LogSubscription"):
        assert resources[name].get("DeletionPolicy", "Delete") == "Delete"


@pytest.mark.parametrize(
    "request_type,valid,version",
    [
        ("Create", True, "immutable-version"),
        ("Create", False, "immutable-version"),
        ("Create", True, None),
        ("Create", True, "null"),
        ("Delete", True, None),
    ],
)
def test_forwarder_code_preparation_signals_failure_and_never_updates_the_stack(
    tmp_path, monkeypatch, request_type, valid, version
):
    import urllib.request

    import boto3

    package = b"verified official package"
    code = template("infra/aws/session.yaml")["Resources"]["Cleanup"]["Properties"]["Code"][
        "ZipFile"
    ]
    script = tmp_path / "lifecycle.py"
    script.write_text(code)
    namespace = runpy.run_path(str(script))
    monkeypatch.setitem(
        namespace["handler"].__globals__, "FORWARDER_SHA256", hashlib.sha256(package).hexdigest()
    )
    download = Mock(
        side_effect=lambda *args, **kwargs: io.BytesIO(package if valid else b"tampered")
    )
    monkeypatch.setattr(urllib.request, "urlopen", download)
    s3 = Mock()
    s3.put_object.return_value = {"VersionId": version}
    clients = Mock(side_effect=lambda name: s3 if name == "s3" else pytest.fail(name))
    monkeypatch.setattr(boto3, "client", clients)
    response = Mock(SUCCESS="SUCCESS", FAILED="FAILED")
    monkeypatch.setitem(sys.modules, "cfnresponse", response)
    monkeypatch.setenv("BUCKET", "owned-bucket")
    event = {"RequestType": request_type}
    namespace["handler"](event, None)
    success = request_type == "Delete" or (valid and version not in (None, "null"))
    assert response.send.call_args.args[2] == ("SUCCESS" if success else "FAILED")
    if request_type == "Delete" or not valid:
        clients.assert_not_called()
    if request_type == "Delete":
        download.assert_not_called()
    elif valid:
        s3.put_object.assert_called_once_with(
            Bucket="owned-bucket", Key="datadog/forwarder.zip", Body=package
        )
    if success and request_type != "Delete":
        assert response.send.call_args.args[3] == {"VersionId": "immutable-version"}


def test_forwarder_provisioning_permissions_exclude_unrelated_functions_and_code():
    config = template("infra/aws/github-oidc.yaml")
    statements = config["Resources"]["CloudFormationRole"]["Properties"]["Policies"][0][
        "PolicyDocument"
    ]["Statement"]

    def allowed(action, arn):
        for statement in statements:
            actions = statement.get("Action", [])
            if isinstance(actions, str):
                actions = [actions]
            if not any(fnmatch.fnmatchcase(action, a) for a in actions):
                continue
            resources = statement["Resource"]
            if not isinstance(resources, list):
                resources = [resources]
            for resource in resources:
                pattern = resource if isinstance(resource, str) else resource["Fn::Sub"]
                for key, value in {
                    "Partition": "aws",
                    "Region": "ap-south-1",
                    "AccountId": "123456789012",
                }.items():
                    pattern = pattern.replace("${AWS::" + key + "}", value)
                if fnmatch.fnmatchcase(arn, pattern):
                    return True
        return False

    prefix = "arn:aws:lambda:ap-south-1:123456789012:function:"
    assert allowed("lambda:CreateFunction", prefix + "nexa-lab-check-datadog-forwarder")
    assert allowed("lambda:AddPermission", prefix + "nexa-lab-check-datadog-forwarder")
    assert not allowed("lambda:AddPermission", prefix + "nexa-lab-check-cleanup")
    assert allowed("lambda:InvokeFunction", prefix + "nexa-lab-check-cleanup")
    assert not allowed("lambda:InvokeFunction", prefix + "nexa-lab-check-datadog-forwarder")
    assert not allowed("lambda:CreateFunction", prefix + "unrelated-function")
    assert allowed("s3:GetObjectVersion", "arn:aws:s3:::nexa-lab-check/datadog/forwarder.zip")
    assert not allowed("s3:GetObjectVersion", "arn:aws:s3:::nexa-lab-check/reports/private.json")
