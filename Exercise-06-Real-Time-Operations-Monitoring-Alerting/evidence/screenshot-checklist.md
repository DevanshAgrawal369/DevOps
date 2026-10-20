# Exercise 6 screenshot checklist

Captured from the locally running Compose stack with Microsoft Edge headless via Playwright on 2026-10-20. Every listed image was opened and visually inspected for the correct rendered page, readable content, and visible credentials.

| File | Evidence | Status |
|---|---|---|
| `screenshots/01-metrics-endpoint.png` | Rendered `/metrics` text including delivery gauges and Summary sum/count | PASS — inspected |
| `screenshots/02-prometheus-query.png` | Prometheus graph query with a returned `total_deliveries` series | PASS — inspected |
| `screenshots/03-prometheus-targets.png` | Delivery and Prometheus scrape targets both UP | PASS — inspected |
| `screenshots/04-prometheus-alerts-inactive.png` | Both alert rules inactive in normal mode | PASS — inspected |
| `screenshots/05-grafana-prometheus-datasource.png` | Provisioned Prometheus data source and internal URL | PASS — inspected |
| `screenshots/06-grafana-dashboard.png` | Four-panel dashboard rendered with live values | PASS — inspected |
| `screenshots/07-prometheus-alerts-pending.png` | HighPendingDeliveries in pending state | PASS — inspected |
| `screenshots/08-prometheus-alerts-firing.png` | HighPendingDeliveries firing | PASS — inspected |
| `screenshots/09-prometheus-alerts-resolved.png` | Alert inactive after test mode restored | PASS — inspected |

These are browser-rendered captures from this repository's live services. They are not API-response substitutes. The controlled test used the application's documented reversible `SIGUSR1`/`SIGUSR2` mode; it was restored and Prometheus returned to inactive.
