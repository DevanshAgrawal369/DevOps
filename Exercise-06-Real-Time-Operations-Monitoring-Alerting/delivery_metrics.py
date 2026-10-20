"""Deterministic-friendly delivery simulator exporting Prometheus metrics."""
from __future__ import annotations

import logging
import os
import random
import signal
import threading
from dataclasses import dataclass

from prometheus_client import CollectorRegistry, Gauge, Summary, start_http_server

LOG = logging.getLogger("delivery_metrics")


@dataclass
class DeliveryState:
    completed: int = 0
    pending: int = 0
    on_the_way: int = 0


class DeliveryMetrics:
    """Owns a registry and simulator state, avoiding global metric duplication."""

    def __init__(self, registry: CollectorRegistry | None = None) -> None:
        self.registry = registry or CollectorRegistry()
        # A Gauge is used for the exported lifetime completed-delivery snapshot so
        # its exposition name is exactly `total_deliveries` as required by the lab.
        self.total_deliveries = Gauge(
            "total_deliveries", "Completed deliveries since this simulator started", registry=self.registry
        )
        self.pending_deliveries = Gauge(
            "pending_deliveries", "Deliveries awaiting processing", registry=self.registry
        )
        self.on_the_way_deliveries = Gauge(
            "on_the_way_deliveries", "Deliveries currently in transit", registry=self.registry
        )
        self.average_delivery_time = Summary(
            "average_delivery_time", "Observed delivery duration in seconds", registry=self.registry
        )

        self.state = DeliveryState()
        self.alert_test_mode = False
        self._publish_state()

    def _publish_state(self) -> None:
        self.total_deliveries.set(self.state.completed)
        self.pending_deliveries.set(self.state.pending)
        self.on_the_way_deliveries.set(self.state.on_the_way)

    def initialize(self, rng: random.Random) -> None:
        self.state = DeliveryState(pending=rng.randint(2, 6), on_the_way=rng.randint(0, 2))
        self._publish_state()

    def set_alert_test_mode(self, enabled: bool) -> None:
        self.alert_test_mode = enabled
        if enabled:
            self.state.pending = 12
            LOG.warning("Controlled alert-test mode enabled: pending deliveries fixed at 12")
        else:
            self.state.pending = min(self.state.pending, 4)
            LOG.info("Controlled alert-test mode disabled; normal simulation resumed")
        self._publish_state()

    def set_high_average_test_mode(self) -> None:
        # Explicit synthetic batch for a reversible alert demonstration.
        for _ in range(100):
            self.average_delivery_time.observe(45.0)
        LOG.warning("Controlled high-average alert test added 100 synthetic 45-second samples")
    def step(self, rng: random.Random) -> DeliveryState:
        if self.alert_test_mode:
            self.state.pending = 12
            self._publish_state()
            return self.state

        # Small randomized arrivals; a bounded number move forward each sample.
        self.state.pending += rng.choices((0, 1, 2), weights=(0.35, 0.55, 0.10), k=1)[0]
        moving = min(self.state.pending, rng.randint(0, 2))
        self.state.pending -= moving
        self.state.on_the_way += moving
        completed = min(self.state.on_the_way, rng.randint(0, 2))
        self.state.on_the_way -= completed
        for _ in range(completed):
            self.average_delivery_time.observe(rng.uniform(5.0, 25.0))
        self.state.completed += completed
        self._publish_state()
        return self.state


def _setting(name: str, default: str) -> str:
    return os.environ.get(name, default)


def main() -> int:
    logging.basicConfig(
        level=_setting("LOG_LEVEL", "INFO").upper(),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    port = int(_setting("METRICS_PORT", "8000"))
    interval = max(1.0, float(_setting("SAMPLE_INTERVAL_SECONDS", "2")))
    seed_value = _setting("RANDOM_SEED", "")
    rng = random.Random(int(seed_value)) if seed_value else random.Random()
    metrics = DeliveryMetrics()
    metrics.initialize(rng)
    if _setting("ALERT_TEST_MODE", "0").lower() in {"1", "true", "yes"}:
        metrics.set_alert_test_mode(True)

    stop = threading.Event()
    def request_stop(signum: int, _frame: object) -> None:
        LOG.info("Received signal %s; stopping simulator", signum)
        stop.set()
    def enable_alert_test(_signum: int, _frame: object) -> None:
        metrics.set_alert_test_mode(True)
    def disable_alert_test(_signum: int, _frame: object) -> None:
        metrics.set_alert_test_mode(False)

    signal.signal(signal.SIGTERM, request_stop)
    signal.signal(signal.SIGINT, request_stop)
    if hasattr(signal, 'SIGWINCH'):
        signal.signal(signal.SIGWINCH, lambda _signum, _frame: metrics.set_high_average_test_mode())
    if hasattr(signal, "SIGUSR1"):
        signal.signal(signal.SIGUSR1, enable_alert_test)
        signal.signal(signal.SIGUSR2, disable_alert_test)
    server, server_thread = start_http_server(port, addr="0.0.0.0", registry=metrics.registry)
    LOG.info("Metrics listening on 0.0.0.0:%d; sample interval %.1fs", port, interval)
    if hasattr(signal, "SIGUSR1"):
        LOG.info("Send SIGUSR1 to enable controlled pending alert mode; SIGUSR2 to restore normal mode; SIGWINCH adds a controlled high-average test batch")
    try:
        while not stop.wait(interval):
            state = metrics.step(rng)
            LOG.info(
                "completed=%d pending=%d on_the_way=%d alert_test=%s",
                state.completed, state.pending, state.on_the_way, metrics.alert_test_mode,
            )
    finally:
        server.shutdown()
        server.server_close()
        server_thread.join(timeout=2)
        LOG.info("Metrics server stopped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
