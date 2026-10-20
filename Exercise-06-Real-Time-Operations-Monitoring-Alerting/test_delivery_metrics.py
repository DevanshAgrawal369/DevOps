import random
import unittest
from pathlib import Path

from prometheus_client import CollectorRegistry, generate_latest

from config_validation import validate_configuration
from delivery_metrics import DeliveryMetrics


class DeliveryMetricsTests(unittest.TestCase):
    def setUp(self):
        self.registry = CollectorRegistry()
        self.metrics = DeliveryMetrics(self.registry)
        self.rng = random.Random(42)

    def test_metrics_initialize_and_export_expected_names(self):
        exposition = generate_latest(self.registry).decode("utf-8")
        for name in ("total_deliveries", "pending_deliveries", "on_the_way_deliveries"):
            self.assertIn(f"# TYPE {name} gauge", exposition)
        self.assertIn("# TYPE average_delivery_time summary", exposition)
        self.assertIn("average_delivery_time_count 0.0", exposition)
        self.assertIn("average_delivery_time_sum 0.0", exposition)

    def test_initialization_and_simulation_keep_delivery_counts_valid(self):
        self.metrics.initialize(self.rng)
        self.assertGreaterEqual(self.metrics.state.pending, 2)
        self.assertGreaterEqual(self.metrics.state.on_the_way, 0)
        for _ in range(30):
            state = self.metrics.step(self.rng)
            self.assertGreaterEqual(state.pending, 0)
            self.assertGreaterEqual(state.on_the_way, 0)
            self.assertGreaterEqual(state.completed, 0)
        exposition = generate_latest(self.registry).decode("utf-8")
        self.assertIn("pending_deliveries", exposition)
        self.assertIn("on_the_way_deliveries", exposition)
        self.assertIn(f"total_deliveries {state.completed}.0", exposition)
        self.assertIn(f"pending_deliveries {state.pending}.0", exposition)
        self.assertIn(f"on_the_way_deliveries {state.on_the_way}.0", exposition)

    def test_summary_average_calculation_and_zero_count_guard(self):
        self.metrics.average_delivery_time.observe(10)
        self.metrics.average_delivery_time.observe(20)
        exposition = generate_latest(self.registry).decode("utf-8")
        self.assertIn("average_delivery_time_count 2.0", exposition)
        self.assertIn("average_delivery_time_sum 30.0", exposition)
        self.assertEqual(30 / 2, 15)
        self.assertGreaterEqual(30 / max(0, 1), 0)  # dashboard's clamp_min equivalent

    def test_alert_test_mode_is_explicit_and_reversible(self):
        self.metrics.initialize(self.rng)
        self.metrics.set_alert_test_mode(True)
        self.assertEqual(self.metrics.state.pending, 12)
        self.metrics.step(self.rng)
        self.assertEqual(self.metrics.state.pending, 12)
        self.metrics.set_alert_test_mode(False)
        self.assertLessEqual(self.metrics.state.pending, 10)

    def test_high_average_alert_mode_uses_explicit_synthetic_samples(self):
        self.metrics.set_high_average_test_mode()
        exposition = generate_latest(self.registry).decode("utf-8")
        self.assertIn("average_delivery_time_count 100.0", exposition)
        self.assertIn("average_delivery_time_sum 4500.0", exposition)
    def test_configuration_is_valid_and_has_required_alert_thresholds(self):
        self.assertEqual(validate_configuration(Path(__file__).parent), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
