"""Dependency-light structural checks; Compose and promtool parse YAML in CI."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def validate_configuration(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    try:
        prom = (root / "prometheus.yml").read_text(encoding="utf-8-sig")
        rules = (root / "alert_rules.yml").read_text(encoding="utf-8-sig")
        datasource = (root / "grafana/provisioning/datasources/prometheus.yml").read_text(encoding="utf-8-sig")
        provider = (root / "grafana/provisioning/dashboards/dashboards.yml").read_text(encoding="utf-8-sig")
        dashboard = json.loads((root / "grafana/dashboards/delivery-monitoring.json").read_text(encoding="utf-8-sig"))
        compose = (root / "docker-compose.yml").read_text(encoding="utf-8-sig")
    except (OSError, json.JSONDecodeError) as exc:
        return [f"Could not read monitoring configuration: {exc}"]

    checks = [
        (r"job_name:\s*prometheus\s+static_configs:\s+-\s+targets:\s*\[\"prometheus:9090\"\]", prom, "Prometheus self-scrape target missing"),
        (r"job_name:\s*delivery_service\s+static_configs:\s+-\s+targets:\s*\[\"delivery_service:8000\"\]", prom, "Delivery scrape target missing"),
        (r"-\s*/etc/prometheus/alert_rules\.yml", prom, "Prometheus alert rule file reference missing"),
        (r"alert:\s*HighPendingDeliveries\s+expr:\s*pending_deliveries > 10\s+for:\s*15s", rules, "HighPendingDeliveries threshold/duration incorrect"),
        (r"alert:\s*HighAverageDeliveryTime\s+expr:\s*average_delivery_time_count > 0 and \(average_delivery_time_sum / average_delivery_time_count\) > 30\s+for:\s*15s", rules, "HighAverageDeliveryTime zero-safe threshold/duration incorrect"),
        (r"url:\s*http://prometheus:9090", datasource, "Grafana datasource URL incorrect"),
        (r"path:\s*/var/lib/grafana/dashboards", provider, "Grafana dashboard provision path incorrect"),
    ]
    for pattern, content, message in checks:
        if not re.search(pattern, content):
            errors.append(message)

    if dashboard.get("title") != "ZAPPTTO Delivery Operations Monitoring":
        errors.append("Dashboard title is incorrect")
    panels = {panel.get("title"): panel for panel in dashboard.get("panels", [])}
    expected_panels = {
        "Total Deliveries": "total_deliveries",
        "Pending Deliveries": "pending_deliveries",
        "On-the-Way Deliveries": "on_the_way_deliveries",
        "Average Delivery Time": "average_delivery_time_sum / clamp_min(average_delivery_time_count, 1)",
    }
    for title, expr in expected_panels.items():
        panel = panels.get(title)
        if not panel or not any(target.get("expr") == expr for target in panel.get("targets", [])):
            errors.append(f"Dashboard query missing/incorrect: {title}")

    for service in ("delivery_service", "prometheus", "grafana"):
        if not re.search(rf"^  {service}:\s*$", compose, re.MULTILINE):
            errors.append(f"Compose service missing: {service}")
    if 'GF_SECURITY_ADMIN_PASSWORD: "${GRAFANA_ADMIN_PASSWORD:?Set a unique local-only GRAFANA_ADMIN_PASSWORD in .env}"' not in compose:
        errors.append("Grafana password is not required from a local environment file")
    return errors


if __name__ == "__main__":
    failures = validate_configuration()
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        raise SystemExit(1)
    print("PASS: Prometheus targets/rules references, alert expressions, Compose service declarations and Grafana JSON/provisioning structure")
