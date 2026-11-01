#!/usr/bin/env bash
# Executed as root by SSM, from a verified release directory; never enable shell tracing.
set -euo pipefail
cd "$(dirname "$0")"
action="${1:-deploy}"
case "$action" in deploy|evaluate) ;; *) exit 2 ;; esac
test -f /opt/nexaassist/host-ready
region="$(python3 -c 'import json; print(json.load(open("release.json"))["AWS_REGION"])')"
export AWS_DEFAULT_REGION="$region"

if [ "$action" = deploy ]; then
  umask 077
  trap 'rm -f /run/nexaassist-secret /run/nexaassist-openai-key' EXIT
  secret_arn="$(python3 -c 'import json; print(json.load(open("release.json"))["SECRET_ARN"])')"
  aws secretsmanager get-secret-value --region "$region" --secret-id "$secret_arn" \
    --query SecretString --output text > /run/nexaassist-secret
  provider="$(python3 -c 'import json; print(json.load(open("release.json"))["MODEL_PROVIDER"])')"
  if [ "$provider" = openai ]; then
    openai_arn="$(python3 -c 'import json; print(json.load(open("release.json"))["OPENAI_API_KEY_SECRET_ARN"])')"
    aws secretsmanager get-secret-value --region "$region" --secret-id "$openai_arn" \
      --query SecretString --output text > /run/nexaassist-openai-key
  fi
  python3 - /run/nexaassist-secret /run/nexaassist-openai-key <<'PY'
import json
import re
import sys
from pathlib import Path

config = json.loads(Path('release.json').read_text())
material_path, key_path = map(Path, sys.argv[1:])
material = material_path.read_text().strip()
if len(material) != 96 or not material.isalnum():
    raise ValueError('Unexpected session secret format')
config.update(POSTGRES_PASSWORD=material[:32], LITELLM_MASTER_KEY='sk-'+material[32:64],
              FEEDBACK_REVIEWER_TOKEN=material[64:])
if config['MODEL_PROVIDER'] == 'openai':
    key = key_path.read_text().strip()
    if not re.fullmatch(r'sk-[A-Za-z0-9_-]+', key):
        raise ValueError('OpenAI secret must contain only the API key in plaintext')
    config['OPENAI_API_KEY'] = key
Path('.env').write_text(''.join(f'{k}={json.dumps(v)}\n' for k, v in config.items()))
material_path.unlink()
key_path.unlink(missing_ok=True)
PY
  chmod 600 .env
  registry="$(python3 -c 'import json; print(json.load(open("release.json"))["APP_IMAGE"].split("/")[0])')"
  aws ecr get-login-password --region "$region" | docker login --username AWS --password-stdin "$registry"
  install -d -o 10001 -g 10001 -m 700 reports
  docker compose pull
  previous=""
  if [ -L /opt/nexaassist/current ] && [ -d /opt/nexaassist/current ]; then
    previous="$(readlink -f /opt/nexaassist/current)"
  fi
  rollback() {
    if [ -n "$previous" ] && [ "$previous" != "$PWD" ]; then
      (cd "$previous" && docker compose up -d --wait --wait-timeout 300)
    else
      docker compose stop api ui || true
    fi
  }
  trap rollback ERR
  docker compose up -d --wait --wait-timeout 300 postgres phoenix gateway guardrails
  free -b > reports/memory-before-ingestion.txt
  docker compose run --rm --no-deps api python -m app.database.postgres init
  docker compose run --rm --no-deps api \
    python -m app.services.ingestion /data/document_register.json
  docker compose up -d --wait --wait-timeout 300
  curl --fail --silent http://127.0.0.1:8000/ready > reports/ready.json
  curl --fail --silent http://127.0.0.1:8000/metrics/http > reports/http-metrics.json
  curl --fail --silent --max-time 180 -H 'Content-Type: application/json' \
    -D reports/answer.headers \
    -d '{"query":"What is the maximum loan amount for a NexaHome Loan?","as_of":"2026-10-01","product_id":"NEXA-HL","top_k":5}' \
    http://127.0.0.1:8000/answer > reports/answer.json
  python3 - <<'PY'
import json
from pathlib import Path
r = json.loads(Path('reports/answer.json').read_text())
assert r['status'] == 'answered' and r['citations'], 'Live structured answer/citation smoke failed'
assert json.loads(Path('reports/ready.json').read_text())['status'] == 'ready'
routes = json.loads(Path('reports/http-metrics.json').read_text())['routes']
assert any(r['route'] == '/answer/evaluated' for r in routes), 'Missing all-route monitoring'
assert 'x-phoenix-span-id:' in Path('reports/answer.headers').read_text().lower()
PY
  free -b > reports/host-memory.txt
  docker stats --no-stream --format '{{json .}}' > reports/container-stats.jsonl
  ln -sfn "$PWD" /opt/nexaassist/current
  trap - ERR
else
  # One golden case per explicit evaluation; no automatic paid judge loop.
  set +e
  docker compose run --rm --no-deps api python -m app.evaluation.run \
    --limit 1 --output /reports/evaluation.json
  result=$?
  set -e
fi

bucket="$(python3 -c 'import json; print(json.load(open("release.json"))["BUCKET"])')"
release_id="$(python3 -c 'import json; print(json.load(open("release.json"))["RELEASE_ID"])')"
aws s3 cp reports/ "s3://$bucket/reports/$release_id/" --recursive --only-show-errors
exit "${result:-0}"
