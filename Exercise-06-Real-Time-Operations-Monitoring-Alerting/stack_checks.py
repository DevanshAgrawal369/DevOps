"""Read-only HTTP/API checks for the local Compose stack; never prints credentials."""
from __future__ import annotations

import argparse
import base64
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROM = "http://127.0.0.1:9090"
GRAFANA = "http://127.0.0.1:3000"
EXPECTED_METRICS = (
    "total_deliveries", "pending_deliveries", "on_the_way_deliveries",
    "average_delivery_time_count", "average_delivery_time_sum",
)


def request(url: str, auth: tuple[str, str] | None = None) -> tuple[int, object]:
    headers = {}
    if auth:
        token = base64.b64encode(f"{auth[0]}:{auth[1]}".encode()).decode()
        headers["Authorization"] = f"Basic {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=5) as response:
        body = response.read().decode("utf-8", errors="replace")
        content_type = response.headers.get("Content-Type", "")
        return response.status, json.loads(body) if "json" in content_type else body


def env_credentials() -> tuple[str, str]:
    values = {}
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            key, value = line.split("=", 1)
            values[key] = value
    return values["GRAFANA_ADMIN_USER"], values["GRAFANA_ADMIN_PASSWORD"]


def instant_query(expr: str) -> dict:
    query = urllib.parse.urlencode({"query": expr})
    status, payload = request(f"{PROM}/api/v1/query?{query}")
    if status != 200 or payload.get("status") != "success":
        raise RuntimeError(f"Prometheus query failed: {expr}")
    return payload


def verify_stack() -> None:
    stamp = datetime.now(timezone.utc).isoformat()
    status, metrics = request("http://127.0.0.1:8000/metrics")
    print(f"{stamp} GET /metrics HTTP {status}")
    missing = [name for name in EXPECTED_METRICS if name not in metrics]
    if status != 200 or missing:
        raise RuntimeError(f"Metrics endpoint missing expected names: {missing}")
    print("PASS metrics names: " + ", ".join(EXPECTED_METRICS))
    for endpoint in ("/-/healthy", "/-/ready"):
        code, _ = request(PROM + endpoint)
        print(f"Prometheus {endpoint}: HTTP {code}")

    _, targets_doc = request(PROM + "/api/v1/targets?state=active")
    targets = targets_doc["data"]["activeTargets"]
    relevant = [target for target in targets if target.get("labels", {}).get("job") in {"prometheus", "delivery_service"}]
    for target in relevant:
        labels = target["labels"]
        print(f"target job={labels.get('job')} scrapeUrl={target.get('scrapeUrl')} health={target.get('health')} lastError={target.get('lastError')!r}")
    if {target.get("labels", {}).get("job") for target in relevant if target.get("health") == "up"} != {"prometheus", "delivery_service"}:
        raise RuntimeError("Both configured Prometheus targets are not UP")

    for expr in ("total_deliveries", "pending_deliveries", "on_the_way_deliveries", "average_delivery_time_count", "average_delivery_time_sum", "average_delivery_time_sum / clamp_min(average_delivery_time_count, 1)"):
        doc = instant_query(expr)
        results = doc["data"]["result"]
        value = results[0]["value"][1] if results else "no sample"
        print(f"PromQL {expr} => {value}")

    _, rules_doc = request(PROM + "/api/v1/rules")
    loaded = {}
    for group in rules_doc["data"]["groups"]:
        for rule in group["rules"]:
            if rule.get("name") in {"HighPendingDeliveries", "HighAverageDeliveryTime"}:
                loaded[rule["name"]] = rule
                print(f"rule {rule['name']} health={rule.get('health')} state={rule.get('state')} query={rule.get('query')}")
    if set(loaded) != {"HighPendingDeliveries", "HighAverageDeliveryTime"}:
        raise RuntimeError("Prometheus did not load both expected alert rules")

    user, password = env_credentials()
    code, health = request(GRAFANA + "/api/health")
    print(f"Grafana /api/health: HTTP {code} version={health.get('version')} database={health.get('database')}")
    code, datasource = request(GRAFANA + "/api/datasources/uid/prometheus", (user, password))
    print(f"Grafana datasource UID={datasource.get('uid')} name={datasource.get('name')} type={datasource.get('type')} url={datasource.get('url')} HTTP {code}")
    code, dashboards = request(GRAFANA + "/api/search?query=ZAPPTTO", (user, password))
    matches = [item for item in dashboards if item.get("title") == "ZAPPTTO Delivery Operations Monitoring"]
    print(f"Grafana provisioned dashboard matches={len(matches)} title={matches[0].get('title') if matches else None} uid={matches[0].get('uid') if matches else None} HTTP {code}")
    if datasource.get("url") != "http://prometheus:9090" or len(matches) != 1:
        raise RuntimeError("Grafana datasource/dashboard provisioning did not verify")


def wait_alert(name: str, desired: str, timeout: int) -> None:
    deadline = time.monotonic() + timeout
    observed = []
    while time.monotonic() < deadline:
        _, doc = request(PROM + "/api/v1/alerts")
        active = [alert for alert in doc["data"]["alerts"] if alert.get("labels", {}).get("alertname") == name]
        state = active[0].get("state", "inactive") if active else "inactive"
        now = datetime.now(timezone.utc).isoformat()
        print(f"{now} {name} state={state} count={len(active)}")
        observed.append(state)
        if desired == "firing" and state == "firing":
            print(f"PASS: Prometheus API confirms {name} is firing")
            return
        if desired == "inactive" and state == "inactive":
            print(f"PASS: {name} is inactive after restoring normal simulator state")
            return
        time.sleep(5)
    raise RuntimeError(f"Timed out waiting for {name} {desired}; observed={observed}")
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("verify", "wait-pending-firing", "wait-average-firing", "wait-pending-inactive", "wait-average-inactive"))
    parser.add_argument("--timeout", type=int, default=50)
    args = parser.parse_args()
    if args.command == "verify":
        verify_stack()
    else:
        wait_alert("HighAverageDeliveryTime" if "average" in args.command else "HighPendingDeliveries", "firing" if args.command.endswith("firing") else "inactive", args.timeout)
