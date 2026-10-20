# Exercise 6 — Real-Time Operations Monitoring and Alerting

## Objective and architecture

This exercise simulates delivery operations, exposes their measurements to Prometheus, evaluates operational alerts, and displays the data in Grafana. A Jenkinsfile describes the automated validation and build pipeline.

```text
Python delivery simulator :8000/metrics
             │ (Compose DNS: delivery_service:8000)
             ▼
Prometheus :9090 ── scrapes itself and delivery metrics; evaluates alert_rules.yml
             │ (Compose DNS: prometheus:9090)
             ▼
Grafana :3000 ── provisioned Prometheus data source and dashboard
```

The three services share a dedicated Compose bridge network. Only loopback addresses on the Windows host are published. Prometheus and Grafana retain their own data in named volumes.

## Project structure

- `delivery_metrics.py` — reproducible-friendly simulator and metrics endpoint.
- `test_delivery_metrics.py`, `config_validation.py`, `stack_checks.py` — unit, structural, and live API checks.
- `Dockerfile`, `docker-compose.yml`, `.dockerignore`, `.gitignore` — image and local stack.
- `prometheus.yml`, `alert_rules.yml` — scrape/evaluation configuration and alerts.
- `grafana/provisioning/` — datasource and dashboard provider.
- `grafana/dashboards/delivery-monitoring.json` — provisioned dashboard.
- `Jenkinsfile` — CI pipeline for a Linux Jenkins agent.
- `evidence/` — actual outputs from this environment.

## Metrics and monitoring concepts

- `total_deliveries` is a Gauge containing the completed-delivery total since this simulator process started. The Gauge keeps the requested exact exposition name for the dashboard.
- `pending_deliveries` is a Gauge for deliveries awaiting processing.
- `on_the_way_deliveries` is a Gauge for deliveries in transit.
- `average_delivery_time` is a Summary observing each completed delivery duration in seconds. Prometheus exposes `average_delivery_time_sum` and `average_delivery_time_count`; PromQL divides the sum by the count to calculate the mean.

Normal simulation samples arrivals and completions every two seconds and records durations between 5 and 25 seconds. It uses a random generator, with an optional `RANDOM_SEED` for repeatable runs. `SAMPLE_INTERVAL_SECONDS`, `METRICS_PORT`, and `LOG_LEVEL` are configurable. The Summary count begins at zero; Grafana uses `average_delivery_time_sum / clamp_min(average_delivery_time_count, 1)` and the critical alert requires `average_delivery_time_count > 0` to avoid division by zero.

Prometheus scrapes both `prometheus:9090` and `delivery_service:8000` every five seconds. It evaluates rules every five seconds. PromQL turns the exported samples into queries, alert rules track threshold duration, and Grafana presents the time series and current values. Jenkins runs source/config validation and tests, then attempts image/Compose checks only when its agent has approved Docker access.

## Prerequisites

- Windows 10/11 with PowerShell and Docker Desktop using its Linux engine.
- Docker Compose plugin.
- Python 3.10 or newer for local tests and API verification.
- For Jenkins: an existing Linux Jenkins controller/agent with Python and Git. Docker stages require Docker CLI/Compose and a compatible Docker daemon already made available to that agent.

Ports 8000, 9090, and 3000 must be free. This environment had those ports available. Port 8080 was already used by a Minikube `kubectl port-forward`; no Jenkins service was running, and that port-forward was left untouched.

## Python setup and tests

From PowerShell in this folder:

```powershell
py -m pip install -r requirements.txt
py -m unittest -v test_delivery_metrics
py config_validation.py
```

The unit tests use isolated Prometheus registries and a seeded random generator. They check metric types/names and values, Summary sum/count and average calculation, simulator state updates, reversible alert mode, and configuration/dashboard structure.

For a local image build without starting the monitoring stack:

```powershell
docker build -t exercise6-delivery-metrics:local .
```

## Start and stop the Compose stack

The stack requires a local Grafana password and refuses to start with an empty value. Create a private local `.env` file and set a unique password; `.env` is ignored by Git and excluded from the Docker build context:

```powershell
Copy-Item .env.example .env
notepad .env
# Set GRAFANA_ADMIN_PASSWORD to a unique local-only value; save and close.
docker compose config --quiet
docker compose up -d --build
docker compose ps
```

Compose binds services to `127.0.0.1`, so they are not published on external interfaces. Open the local dashboard at `http://localhost:3000` and sign in with the user/password in your ignored `.env` file. Do not reuse these local credentials on a public deployment.

Stop only this project's containers and network while preserving its named data volumes:

```powershell
docker compose down
```

`docker compose down -v` also deletes this exercise's Prometheus and Grafana data volumes. Use it only when intentionally resetting this exercise's stored data. Do not remove unrelated containers or volumes.

## Check metrics and Prometheus

- Metrics endpoint: `http://localhost:8000/metrics`
- Prometheus readiness: `http://localhost:9090/-/ready`
- Prometheus health: `http://localhost:9090/-/healthy`
- Targets page: `http://localhost:9090/targets`
- Rules page: `http://localhost:9090/alerts`

Run the automated live checks:

```powershell
py stack_checks.py verify
docker compose exec -T prometheus promtool check config /etc/prometheus/prometheus.yml
docker compose exec -T prometheus promtool check rules /etc/prometheus/alert_rules.yml
```

`stack_checks.py` checks the actual HTTP metrics response, readiness/health, both active target health states, PromQL query responses, loaded rules, and Grafana APIs. It reads the ignored `.env` only to authenticate to the local Grafana API and never prints the password.

Useful PromQL queries:

```promql
total_deliveries
pending_deliveries
on_the_way_deliveries
average_delivery_time_sum / clamp_min(average_delivery_time_count, 1)
```

The alert rules are in the mounted `/etc/prometheus/alert_rules.yml` file:

- `HighPendingDeliveries`: `pending_deliveries > 10` for 15 seconds, severity `warning`.
- `HighAverageDeliveryTime`: average above 30 seconds for 15 seconds, severity `critical`; the expression checks count greater than zero first.

## Verify the alerts with controlled tests

The application has explicit signal-driven test modes; normal values are not forced high.

```powershell
# Pending delivery alert: set pending to 12 until disabled.
docker compose kill --signal SIGUSR1 delivery_service
py stack_checks.py verify
py stack_checks.py wait-pending-firing --timeout 50
docker compose kill --signal SIGUSR2 delivery_service
py stack_checks.py wait-pending-inactive --timeout 20

# Average delivery alert: add 100 explicitly synthetic 45-second observations.
docker compose kill --signal SIGWINCH delivery_service
py stack_checks.py verify
py stack_checks.py wait-average-firing --timeout 45

# Restore normal simulation and reset the in-memory Summary test samples.
docker compose restart delivery_service
py stack_checks.py wait-average-inactive --timeout 60
py stack_checks.py verify
```

Prometheus evaluates every five seconds and requires 15 seconds above the threshold, so the alert should appear as `pending` before `firing`. The pending test is reversed with `SIGUSR2`. The high-average test records synthetic test data in the in-memory Summary, so restart only `delivery_service` afterward; the Prometheus and Grafana volumes remain intact. Verify firing and resolution through the Prometheus Alerts API/UI, not from the signal command alone.

## Grafana dashboard

Grafana automatically provisions a Prometheus data source at `http://prometheus:9090` and the dashboard **ZAPPTTO Delivery Operations Monitoring**. It contains:

1. Total Deliveries — `total_deliveries`
2. Pending Deliveries — `pending_deliveries`
3. On-the-Way Deliveries — `on_the_way_deliveries`
4. Average Delivery Time — `average_delivery_time_sum / clamp_min(average_delivery_time_count, 1)`

The data source and dashboard can be checked in Grafana's HTTP API; the API check is included in `py stack_checks.py verify`. Dashboard JSON is parsed in the unit/structural tests. The provisioned data source and dashboard were also verified in rendered browser pages. See [`evidence/screenshot-checklist.md`](evidence/screenshot-checklist.md) and the nine inspected screenshots under [`evidence/screenshots/`](evidence/screenshots/).

## Jenkins pipeline

This environment now has a separate local Jenkins container for Exercise 7 at `http://localhost:8081`. The Exercise 6 pipeline was not run as a Jenkins job; it remains a configured pipeline definition and still requires a job and agent with appropriate tools.

To use it when Jenkins is available:

1. Create a Pipeline job configured **Pipeline script from SCM** for this repository and branch `main`.
2. Set the Script Path to `Exercise-06-Real-Time-Operations-Monitoring-Alerting/Jenkinsfile`.
3. Ensure the agent has Python 3, Git, and the repository checkout available.
4. Leave `RUN_STACK_INTEGRATION` off unless that agent has free local ports and an approved Docker setup. For that optional integration stage, create Jenkins string credential ID `exercise6-grafana-admin-password`; the pipeline cleans only its build-specific stack, image, and virtual environment.
5. Docker stages check for daemon access and skip with a diagnostic when unavailable. Do not mount the host Docker socket or use privileged mode without an approved setup.

This repository contains a pipeline definition but no real Jenkins build result; see `evidence/jenkins-test.txt`.

## Troubleshooting

- **Compose says Grafana password is missing:** copy `.env.example` to `.env` and enter a non-empty local-only password. Do not commit `.env`.
- **A port is occupied:** inspect the owning process/container. Do not stop an unrelated service to free it; change the host-side Compose port deliberately and update access URLs.
- **Prometheus target is down:** check `docker compose ps`, delivery health, Prometheus logs, and service-name DNS. Inside Prometheus, `localhost:8000` refers to Prometheus itself; use `delivery_service:8000`.
- **Prometheus config/rules fail:** use `promtool check config` and `promtool check rules`; confirm the mounted rule filename matches `alert_rules.yml`.
- **Grafana dashboard is missing:** check provisioning paths and Grafana logs; the JSON must be UTF-8 without a byte-order mark for Grafana's JSON decoder.
- **Windows or Docker Desktop networking:** browse via `localhost` on Windows; containers discover each other using Compose service names on the dedicated network.
- **Jenkins Docker stages skip/fail:** confirm that a trusted Linux Jenkins agent has Docker CLI/Compose and approved daemon access. No daemon socket is mounted by this project.

## Results from this environment (2026-10-20)

- Python unit tests: **6 passed**.
- Docker image `exercise6-delivery-metrics:local`: **built successfully**.
- Compose: **three services healthy**; ports 8000, 9090, 3000 published on loopback.
- Metrics endpoint: **HTTP 200** with all five expected series, including Summary `_sum` and `_count`.
- Prometheus: readiness and health **HTTP 200**; delivery and self-scrape targets **UP**; config and both alert rules passed `promtool` checks.
- Grafana: health **HTTP 200**; Prometheus data source and named dashboard both found by API.
- Alerts: on 2026-10-20, the controlled pending-delivery test observed `pending_deliveries=12`, then `HighPendingDeliveries` transitioned `inactive → pending → firing` through Prometheus. `SIGUSR2` restored normal mode; the rule returned to inactive. Browser captures show inactive, pending, firing, and resolved states. The high-average alert was not re-tested during this visual-verification run.
- Browser verification: the metrics endpoint, Prometheus query, both-UP targets page, alerts, provisioned Grafana data source, and rendered four-panel dashboard were captured from the live local services and visually inspected. See [`evidence/screenshot-checklist.md`](evidence/screenshot-checklist.md).
- Jenkins: Jenkins 2.580.1 runs separately on loopback port 8081; setup, dashboard, and version page were reached and visually verified for Exercise 7. No Exercise 6 pipeline job or build was run.

See the `evidence/` text files and screenshot checklist for command, API, and browser results and timestamps. The three Exercise 6 services remain running; existing containers and volumes were preserved.
