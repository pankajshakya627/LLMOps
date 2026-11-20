"""Provision, deploy, stop and resume AWS training sessions."""

from __future__ import annotations

import argparse
import hashlib
import io
import ipaddress
import json
import os
import re
import shlex
import tarfile
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import boto3
import yaml
from botocore.config import Config
from botocore.exceptions import ClientError

ROOT = Path(__file__).resolve().parents[2]


def client(service: str) -> Any:
    return boto3.client(
        service,
        config=Config(retries={"total_max_attempts": 3}, connect_timeout=5, read_timeout=200),
    )


def output(summary: str, artifacts: list[str], next_actions: list[str]) -> None:
    print(
        json.dumps(
            {
                "status": "success",
                "summary": summary,
                "artifacts": artifacts,
                "next_actions": next_actions,
            }
        )
    )


def stack_outputs(stack: str) -> dict[str, str]:
    data = client("cloudformation").describe_stacks(StackName=stack)["Stacks"][0]
    outputs = {entry["OutputKey"]: entry["OutputValue"] for entry in data["Outputs"]}
    if "StopSchedule" in outputs:
        host = describe_host(outputs["InstanceId"])
        outputs["HostState"] = host["State"]["Name"]
        if host.get("PublicIpAddress") and outputs["HostState"] == "running":
            outputs["ApplicationUrl"] = f"http://{host['PublicIpAddress']}:8501"
        schedule = client("scheduler").get_schedule(Name=outputs["StopSchedule"])
        expression = schedule["ScheduleExpression"]
        outputs["ExpiresAt"] = expression.removeprefix("at(").removesuffix(")")
    return outputs


def describe_host(instance: str) -> dict[str, Any]:
    reservations = client("ec2").describe_instances(InstanceIds=[instance])["Reservations"]
    return reservations[0]["Instances"][0]


def power(data: dict[str, str], action: str, minutes: int = 60) -> None:
    if not data.get("StopSchedule"):
        raise ValueError(
            "Stop/resume requires a resumable stack; legacy sessions expire by deletion"
        )
    instance = data["InstanceId"]
    ids = {"InstanceIds": [instance]}
    ec2 = client("ec2")
    state = data["HostState"]
    if action == "stop":
        if state in {"pending", "running"}:
            if state == "pending":
                ec2.get_waiter("instance_running").wait(**ids)
            ec2.stop_instances(**ids)
        elif state not in {"stopping", "stopped"}:
            raise ValueError(f"Cannot stop a host in state {state}")
        ec2.get_waiter("instance_stopped").wait(**ids)
        output("Host stopped; disk and release retained", [instance], [])
        return

    if state == "stopping":
        ec2.get_waiter("instance_stopped").wait(**ids)
        state = "stopped"
    if state == "stopped":
        # Arm the cloud-side safeguard before starting chargeable compute.
        scheduler = client("scheduler")
        name = data["StopSchedule"]
        schedule = scheduler.get_schedule(Name=name)
        deadline = (datetime.now(UTC) + timedelta(minutes=minutes)).strftime("%Y-%m-%dT%H:%M:%S")
        scheduler.update_schedule(
            Name=name,
            ScheduleExpression=f"at({deadline})",
            ScheduleExpressionTimezone="UTC",
            FlexibleTimeWindow=schedule["FlexibleTimeWindow"],
            Target={
                **schedule["Target"],
                "Input": json.dumps({"operation": "stop", "deadline": deadline}),
            },
        )
        ec2.start_instances(**ids)
    elif state not in {"running", "pending"}:
        raise ValueError(f"Cannot resume a host in state {state}")
    try:
        ec2.get_waiter("instance_running").wait(**ids)
        run_remote(
            instance,
            "set -eu; cd /opt/nexaassist/current; "
            "docker compose up -d --no-build --pull never --wait --wait-timeout 300; "
            "curl -fsS http://127.0.0.1:8000/ready >/dev/null; "
            "curl -fsS http://127.0.0.1:8501/_stcore/health >/dev/null",
        )
    except Exception:
        if state == "stopped":
            ec2.stop_instances(**ids)
        raise
    output("Current release ready", [instance], [])


def validate_ui_cidr(value: str) -> None:
    try:
        network = ipaddress.IPv4Network(value)
        if not value.endswith("/32") or not network.is_global or network.is_multicast:
            raise ValueError
    except ValueError:
        raise ValueError("UI access requires one global IPv4 /32 address") from None


def create(args: argparse.Namespace) -> None:
    validate_ui_cidr(args.ui_allowed_cidr)
    observability = getattr(args, "observability", "cloudwatch")
    anthropic_secret = getattr(args, "anthropic_secret_arn", "")
    if anthropic_secret:
        region = re.escape(str(boto3.session.Session().region_name))
        if args.provider != "openai" or not re.fullmatch(
            rf"arn:aws:secretsmanager:{region}:\d{{12}}:secret:nexa-lab-anthropic-[A-Za-z0-9]{{6}}",
            anthropic_secret,
        ):
            raise ValueError(
                "Use the same-Region nexa-lab-anthropic secret with the OpenAI profile"
            )
    if args.provider == "openai":
        if not re.fullmatch(
            r"arn:aws:secretsmanager:[a-z0-9-]+:[0-9]{12}:secret:nexa-lab-openai-[A-Za-z0-9]{6}",
            args.openai_secret_arn,
        ):
            raise ValueError("OpenAI requires the ARN of a plaintext secret named nexa-lab-openai")
        if args.openai_secret_arn.split(":")[3] != boto3.session.Session().region_name:
            raise ValueError("Store the OpenAI secret in the same AWS Region as the session")
    elif not args.model_resources:
        raise ValueError("Bedrock requires explicit approved model/profile ARNs")
    datadog_secret = getattr(args, "datadog_secret_arn", "")
    if observability == "datadog" and not re.fullmatch(
        r"arn:aws:secretsmanager:[a-z0-9-]+:[0-9]{12}:secret:nexa-lab-datadog-[A-Za-z0-9]{6}",
        datadog_secret,
    ):
        raise ValueError("Datadog requires a plaintext API key secret named nexa-lab-datadog")
    if observability == "datadog" and (
        datadog_secret.split(":")[3] != boto3.session.Session().region_name
    ):
        raise ValueError("Store the Datadog secret in the same AWS Region as the session")
    if args.provider == "bedrock":
        model_ids = {
            arn.split("/", 1)[1]
            for arn in args.model_resources.split(",")
            if ":foundation-model/" in arn
        }
        if not model_ids:
            raise ValueError("Include approved foundation-model ARNs for Bedrock access checks")
        for model in sorted(model_ids):
            access = client("bedrock").get_foundation_model_availability(modelId=model)
            if access.get("authorizationStatus") != "AUTHORIZED":
                raise ValueError(
                    f"Bedrock model {model} is not authorized; no session was created. "
                    "Resolve model/account access in AWS before retrying"
                )
    expires = datetime.now(UTC) + timedelta(minutes=args.minutes)
    parameters = {
        "SessionMinutes": str(args.minutes),
        "ExpiresAt": expires.strftime("%Y-%m-%dT%H:%M:%S"),
        "BoundaryArn": args.boundary_arn,
        "ModelProvider": args.provider,
        "Observability": observability,
        "AnthropicKeySecretArn": anthropic_secret,
        "UiAllowedCidr": args.ui_allowed_cidr,
        "OpenAIKeySecretArn": args.openai_secret_arn if args.provider == "openai" else "",
        "DatadogKeySecretArn": datadog_secret if observability == "datadog" else "",
        "DatadogSite": getattr(args, "datadog_site", "datadoghq.com"),
        "DatadogMlApp": getattr(args, "datadog_ml_app", "nexaassist"),
        "ModelResources": args.model_resources if args.provider == "bedrock" else "",
    }
    cf = client("cloudformation")
    created = cf.create_stack(
        StackName=args.stack,
        TemplateBody=(ROOT / "infra/aws/session.yaml").read_text(),
        RoleARN=args.cloudformation_role_arn,
        Capabilities=["CAPABILITY_NAMED_IAM"],
        Parameters=[{"ParameterKey": k, "ParameterValue": v} for k, v in parameters.items()],
        Tags=[
            {"Key": "Session", "Value": args.stack},
            {"Key": "BudgetUSD", "Value": str(args.budget)},
        ],
    )
    # A failed create on an already-live name must never trigger deletion of that session.
    Path(args.receipt).write_text(json.dumps({"stack_id": created["StackId"]}))
    cf.get_waiter("stack_create_complete").wait(
        StackName=args.stack, WaiterConfig={"Delay": 10, "MaxAttempts": 120}
    )
    data = stack_outputs(args.stack)
    Path(args.output).write_text(json.dumps(data, indent=2))
    output(
        "Session infrastructure created; application deployment is next",
        [args.output],
        ["Build and deploy release images; session expiry is already scheduled"],
    )


def require_provider(data: dict[str, str], provider: str) -> None:
    if provider != data.get("ModelProvider", "bedrock"):
        raise ValueError(
            "Cannot change providers within a session; destroy it and create a new one"
        )


def require_ui(data: dict[str, str]) -> None:
    if "HostState" in data and data["HostState"] != "running":
        raise ValueError("Host is not running; resume it before deployment")
    try:
        validate_ui_cidr(data.get("UiAllowedCidr", ""))
        address = re.fullmatch(r"http://([0-9.]+):8501", data.get("ApplicationUrl", ""))
        if not address:
            raise ValueError
        validate_ui_cidr(address[1] + "/32")
    except ValueError:
        raise ValueError(
            "Session lacks restricted public UI access; destroy it and create a fresh session"
        ) from None


def gateway_profile(provider: str, observability: str, anthropic_model: str) -> dict[str, Any]:
    profile = yaml.safe_load((ROOT / f"app/gateway/litellm_{provider}.yaml").read_text())
    if observability == "cloudwatch":
        profile["litellm_settings"].pop("callbacks")
        profile["litellm_settings"]["telemetry"] = False
    if anthropic_model:
        if provider != "openai" or not re.fullmatch(
            r"anthropic/claude-[a-zA-Z0-9.-]+", anthropic_model
        ):
            raise ValueError("Use a direct anthropic/claude-* model with the OpenAI profile")
        profile["model_list"].append(
            {
                "model_name": "nexa-chat-anthropic",
                "litellm_params": {
                    "model": anthropic_model,
                    "api_key": "os.environ/ANTHROPIC_API_KEY",
                    "max_tokens": 2000,
                },
            }
        )
    return profile


def prepare_release(args: argparse.Namespace, data: dict[str, str]) -> tuple[Path, str]:
    require_provider(data, args.provider)
    require_ui(data)
    if not re.fullmatch(r"[a-zA-Z0-9_-]{1,100}", args.release_id):
        raise ValueError("Invalid release ID")
    images = json.loads(Path(args.images).read_text())
    if set(images) != {"APP_IMAGE", "GATEWAY_IMAGE", "GUARDRAILS_IMAGE"}:
        raise ValueError("Image manifest must contain exactly the three release images")
    for key, repository in (
        ("APP_IMAGE", "AppRepository"),
        ("GATEWAY_IMAGE", "GatewayRepository"),
        ("GUARDRAILS_IMAGE", "GuardrailsRepository"),
    ):
        if not re.fullmatch(re.escape(data[repository]) + r"@sha256:[a-f0-9]{64}", images[key]):
            raise ValueError(f"{key} must be a digest in this session's ECR repository")
    prefix = "openai/" if args.provider == "openai" else "bedrock/converse/"
    for route in (args.chat_route, args.judge_route):
        if not re.fullmatch(re.escape(prefix) + r"[a-zA-Z0-9._:/-]+", route):
            raise ValueError(f"Use an approved {prefix} route for this session")
    config = {
        **images,
        "MODEL_PROVIDER": args.provider,
        "COMPOSE_FILE": "compose.yaml",
        "AWS_REGION": boto3.session.Session().region_name,
        "SECRET_ARN": data["SecretArn"],
        "OBSERVABILITY": data.get("Observability", "datadog"),
        "DD_CAPTURE_CONTENT": os.environ.get("DD_CAPTURE_CONTENT", "false"),
        "DD_TAGS": f"session:{data['SessionName']},lab_session_id:{data['SessionId']}",
        "DD_VERSION": args.release_id,
        "BUCKET": data["Bucket"],
        "RELEASE_ID": args.release_id,
    }
    if config["OBSERVABILITY"] == "datadog":
        config.update(
            DATADOG_API_KEY_SECRET_ARN=data["DatadogKeySecretArn"],
            DD_SITE=data["DatadogSite"],
            DD_LLMOBS_ML_APP=data["DatadogMlApp"],
        )
    anthropic_model = getattr(args, "anthropic_model", "")
    answer_model = getattr(args, "answer_model", "") or f"nexa-chat-{args.provider}"
    aliases = {f"nexa-chat-{args.provider}"}
    if anthropic_model:
        if not data.get("AnthropicKeySecretArn"):
            raise ValueError("Configure the Anthropic secret ARN before selecting a Claude model")
        config["ANTHROPIC_API_KEY_SECRET_ARN"] = data["AnthropicKeySecretArn"]
        aliases.add("nexa-chat-anthropic")
    if answer_model not in aliases:
        raise ValueError(
            "Selected CHAT_MODEL is unavailable; check the provider, Claude model ID and secret ARN"
        )
    config["CHAT_MODEL"] = answer_model
    gateway = gateway_profile(args.provider, config["OBSERVABILITY"], anthropic_model)
    if args.provider == "openai":
        config.update(
            OPENAI_API_KEY_SECRET_ARN=data["OpenAIKeySecretArn"],
            OPENAI_LITELLM_CHAT_MODEL=args.chat_route,
            OPENAI_LITELLM_JUDGE_MODEL=args.judge_route,
        )
    else:
        config.update(
            COMPOSE_FILE="compose.yaml:compose.bedrock.yaml",
            BEDROCK_GUARDRAIL_ID=data["GuardrailId"],
            BEDROCK_GUARDRAIL_VERSION=data["GuardrailVersion"],
            BEDROCK_CHAT_ROUTE=args.chat_route,
            BEDROCK_JUDGE_ROUTE=args.judge_route,
        )
    if config["OBSERVABILITY"] == "cloudwatch":
        config["COMPOSE_FILE"] += ":compose.cloudwatch.yaml"
    register = ROOT / "nexa_synthetic_data/document_register.json"
    archive = Path(args.archive)
    with tarfile.open(archive, "w:gz") as tar:
        for source, name in (
            (ROOT / "app/compose.aws.yaml", "compose.yaml"),
            (ROOT / "infra/aws/host.sh", "host.sh"),
            (register, "corpus/document_register.json"),
        ):
            tar.add(source, arcname=name)
        if args.provider == "bedrock":
            tar.add(ROOT / "app/compose.aws.bedrock.yaml", arcname="compose.bedrock.yaml")
        if config["OBSERVABILITY"] == "cloudwatch":
            tar.add(ROOT / "app/compose.aws.cloudwatch.yaml", arcname="compose.cloudwatch.yaml")
        for entry in json.loads(register.read_text()):
            relative = Path(entry["file"])
            if relative.is_absolute() or ".." in relative.parts:
                raise ValueError("Corpus paths must be relative without traversal")
            source = (register.parent / entry["file"]).resolve()
            if not source.is_relative_to(register.parent.resolve()) or not source.is_file():
                raise ValueError("Corpus file must be inside the synthetic-data directory")
            if hashlib.sha256(source.read_bytes()).hexdigest() != entry["sha256"]:
                raise ValueError("Corpus checksum mismatch")
            tar.add(source, arcname=f"corpus/{entry['file']}")
        # This manifest contains ARNs and image digests, never credentials.
        for name, document in (("release.json", config), ("gateway.yaml", gateway)):
            body = json.dumps(document).encode()  # JSON is valid YAML for the LiteLLM proxy.
            info = tarfile.TarInfo(name)
            info.size = len(body)
            tar.addfile(info, io.BytesIO(body))
    return archive, hashlib.sha256(archive.read_bytes()).hexdigest()


def run_remote(instance: str, command: str) -> dict[str, Any]:
    ssm = client("ssm")
    # Account for first boot and SSM registration; do not swallow authorization failures.
    for attempt in range(60):
        try:
            sent = ssm.send_command(
                InstanceIds=[instance],
                DocumentName="AWS-RunShellScript",
                Parameters={"commands": [command], "executionTimeout": ["1800"]},
                TimeoutSeconds=60,
            )
            break
        except ClientError as exc:
            if exc.response["Error"]["Code"] != "InvalidInstanceId" or attempt == 59:
                raise
            time.sleep(10)
    command_id = sent["Command"]["CommandId"]
    for _ in range(190):
        time.sleep(10)
        try:
            result = ssm.get_command_invocation(CommandId=command_id, InstanceId=instance)
        except ClientError as exc:
            if exc.response["Error"]["Code"] == "InvocationDoesNotExist":
                continue
            raise
        if result["Status"] in {"Pending", "InProgress", "Delayed"}:
            continue
        if result["Status"] != "Success":
            # Host commands contain no literal secret values. Keep provider output out of CI logs.
            raise RuntimeError(
                f"SSM command {command_id} {result['Status']}; inspect SSM/CloudWatch"
            )
        return result
    ssm.cancel_command(CommandId=command_id, InstanceIds=[instance])
    raise TimeoutError(
        f"SSM command {command_id} timed out; stop the lab and inspect host readiness"
    )


def deploy(args: argparse.Namespace, data: dict[str, str]) -> None:
    if datetime.fromisoformat(data["ExpiresAt"]).replace(tzinfo=UTC) <= datetime.now(
        UTC
    ) + timedelta(minutes=15):
        raise ValueError(
            "Less than 15 minutes remain in the deployment window; stop and resume a resumable host"
        )
    archive, digest = prepare_release(args, data)
    key = f"releases/{args.release_id}.tar.gz"
    client("s3").upload_file(str(archive), data["Bucket"], key)
    destination = f"/opt/nexaassist/releases/{args.release_id}"
    command = "\n".join(
        [
            "set -eu",
            "for n in $(seq 1 60); do test -f /opt/nexaassist/host-ready && break; sleep 5; done",
            "test -f /opt/nexaassist/host-ready",
            f"install -d -m 700 {shlex.quote(destination)}",
            f"cd {shlex.quote(destination)}",
            (
                f"aws s3 cp {shlex.quote('s3://' + data['Bucket'] + '/' + key)} release.tar.gz "
                f"--region {shlex.quote(str(boto3.session.Session().region_name))} --only-show-errors"
            ),
            f"echo '{digest}  release.tar.gz' | sha256sum --check -",
            "tar -xzf release.tar.gz",
            "bash host.sh deploy",
        ]
    )
    run_remote(data["InstanceId"], command)
    output(
        "Release deployed; live readiness and structured-answer smoke passed",
        [f"s3://{data['Bucket']}/reports/{args.release_id}/"],
        [f"Open {data['ApplicationUrl']}; stop the host when finished"],
    )


def destroy(data: dict[str, str]) -> None:
    result = client("lambda").invoke(
        FunctionName=data["CleanupFunction"], Payload=json.dumps({"operation": "destroy"}).encode()
    )
    if result.get("FunctionError"):
        raise RuntimeError("Cleanup Lambda failed; inspect logs, stop uploads and retry destroy")
    output(
        "Session deletion requested",
        [data["CleanupFunction"]],
        ["Wait for CloudFormation DELETE_COMPLETE; DELETE_FAILED requires remediation"],
    )


def destroy_stack(stack: str, receipt: str | None = None) -> None:
    cf = client("cloudformation")
    try:
        current = cf.describe_stacks(StackName=stack)["Stacks"][0]
    except ClientError as exc:
        if exc.response["Error"]["Code"] == "ValidationError" and "does not exist" in str(exc):
            output("Session already deleted", [stack], [])
            return
        raise
    if receipt and json.loads(Path(receipt).read_text())["stack_id"] != current["StackId"]:
        raise ValueError("Session identity changed; refusing to delete a replacement stack")
    try:
        destroy({"CleanupFunction": f"{stack}-cleanup"})
    except ClientError as exc:
        if exc.response["Error"]["Code"] != "ResourceNotFoundException":
            raise
        # Failed initial creation may have no cleanup function or outputs yet.
        cf.delete_stack(StackName=stack)
    cf.get_waiter("stack_delete_complete").wait(
        StackName=stack, WaiterConfig={"Delay": 10, "MaxAttempts": 120}
    )
    output("Session stack deleted", [stack], ["No session compute or storage is retained"])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stack", required=True)
    commands = parser.add_subparsers(dest="action", required=True)
    start = commands.add_parser("create")
    start.add_argument("--minutes", type=int, choices=[60, 120], default=60)
    start.add_argument("--budget", type=int, choices=range(2, 10), default=5)
    start.add_argument("--provider", choices=["openai", "bedrock"], default="openai")
    start.add_argument("--openai-secret-arn", default="")
    start.add_argument("--anthropic-secret-arn", default="")
    start.add_argument("--observability", choices=["cloudwatch", "datadog"], default="cloudwatch")
    start.add_argument("--datadog-secret-arn", default="")
    start.add_argument("--datadog-site", default="datadoghq.com")
    start.add_argument("--datadog-ml-app", default="nexaassist")
    start.add_argument("--model-resources", default="")
    start.add_argument("--ui-allowed-cidr", required=True)
    start.add_argument("--boundary-arn", required=True)
    start.add_argument("--cloudformation-role-arn", required=True)
    start.add_argument("--output", default="session-outputs.json")
    start.add_argument("--receipt", default="session-created.json")
    release = commands.add_parser("deploy")
    release.add_argument("--images", required=True)
    release.add_argument("--release-id", required=True)
    release.add_argument("--provider", choices=["openai", "bedrock"], default="openai")
    release.add_argument("--chat-route", default="openai/gpt-6-luna")
    release.add_argument("--judge-route", default="openai/gpt-6-luna")
    release.add_argument("--anthropic-model", default="")
    release.add_argument("--answer-model", default="")
    release.add_argument("--archive", default="release.tar.gz")
    evaluate = commands.add_parser("evaluate")
    evaluate.add_argument("--provider", choices=["openai", "bedrock"], default="openai")
    commands.add_parser("stop")
    resume = commands.add_parser("resume")
    resume.add_argument("--minutes", type=int, choices=[60, 120], default=60)
    stop = commands.add_parser("destroy")
    stop.add_argument("--receipt", help="Only destroy the stack ID recorded by this create")
    status = commands.add_parser("status")
    status.add_argument("--provider", choices=["openai", "bedrock"])
    commands.add_parser("capacity")
    args = parser.parse_args()
    if not re.fullmatch(r"nexa-lab-[a-z0-9-]{1,25}", args.stack):
        parser.error("Stack must match nexa-lab-[a-z0-9-]{1,25}")
    try:
        if args.action == "create":
            create(args)
            return
        if args.action == "destroy":
            destroy_stack(args.stack, args.receipt)
            return
        data = stack_outputs(args.stack)
        if args.action in {"stop", "resume"}:
            power(data, args.action, getattr(args, "minutes", 60))
        elif args.action == "deploy":
            deploy(args, data)
        elif args.action == "evaluate":
            require_provider(data, args.provider)
            run_remote(
                data["InstanceId"], "set -eu; cd /opt/nexaassist/current; bash host.sh evaluate"
            )
            output(
                "One-case evaluation gate passed",
                [f"s3://{data['Bucket']}/reports/"],
                [
                    "Inspect metric statuses and scores; example thresholds are not production approval"
                ],
            )
        elif args.action == "capacity":
            result = run_remote(
                data["InstanceId"],
                "set -eu; free -b; docker stats --no-stream --format '{{json .}}'",
            )
            print(result["StandardOutputContent"])
        else:
            if args.provider:
                require_provider(data, args.provider)
                require_ui(data)
            print(
                json.dumps(
                    {key: value for key, value in data.items() if key != "UiAllowedCidr"}, indent=2
                )
            )
    except Exception as exc:  # noqa: BLE001 - CLI failures share one sanitized recovery contract.
        summary = type(exc).__name__
        if isinstance(exc, (RuntimeError, ValueError, TimeoutError)):
            summary = str(exc)
        elif isinstance(exc, ClientError):
            summary += ": " + exc.response["Error"]["Code"]
        print(
            json.dumps(
                {
                    "status": "error",
                    "summary": summary,
                    "next_actions": [
                        "Inspect stack events and SSM/CloudWatch logs",
                        "Retry only after fixing the cause; destroy if the lab is not needed",
                    ],
                    "artifacts": [args.stack],
                }
            )
        )
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
