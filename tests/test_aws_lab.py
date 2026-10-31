from __future__ import annotations

import argparse
import hashlib
import json
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
        lambda loader, tag, node: (
            loader.construct_scalar(node)
            if isinstance(node, yaml.ScalarNode)
            else loader.construct_sequence(node)
        ),
    )
    return yaml.load(Path(path).read_text(), Loader=Loader)


def test_release_contains_only_synthetic_corpus_and_digest_manifest(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
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
        chat_route="bedrock/converse/test",
        judge_route="bedrock/converse/test",
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
    s3.delete_objects.side_effect = lambda **_: calls.append("empty") or {}
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
    assert resources["Host"]["Properties"]["CreditSpecification"]["CPUCredits"] == "standard"
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
