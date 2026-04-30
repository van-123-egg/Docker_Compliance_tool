"""
Prometheus metrics exporter for the Docker CIS Compliance Scanner.

Exposes compliance scan results as Prometheus metrics on an HTTP endpoint.
Metrics are updated after each scan run.
"""

from prometheus_client import Gauge, start_http_server

# ─── Metric Definitions ─────────────────────────────────────────────

compliance_score_percent = Gauge(
    'compliance_score_percent',
    'Overall CIS compliance score as a percentage (0-100)'
)

compliance_checks_failed = Gauge(
    'compliance_checks_failed',
    'Total number of compliance checks that failed'
)

compliance_failures_by_severity = Gauge(
    'compliance_failures_by_severity',
    'Number of failed checks broken down by severity level',
    ['severity']
)

compliance_suite_duration_seconds = Gauge(
    'compliance_suite_duration_seconds',
    'Time taken to run each compliance check suite in seconds',
    ['suite']
)


def start_metrics_server(port=8000):
    """Start the Prometheus metrics HTTP server on the given port.
    
    This exposes all registered metrics at http://localhost:<port>/metrics
    """
    start_http_server(port)


def update_metrics(score_info, suite_durations=None):
    """Update all Prometheus metrics with the latest scan results.
    
    Args:
        score_info: The score dict returned by ReportEngine._compute_score().
        suite_durations: Optional dict mapping suite name -> duration in seconds.
                         e.g. {"Host_Configuration": 1.23, "Daemon_Configuration": 0.45}
    """
    # Core score metrics
    compliance_score_percent.set(score_info["score_pct"])
    compliance_checks_failed.set(score_info["failed"])

    # Failures broken down by severity
    for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
        count = score_info["severity_fails"].get(severity, 0)
        compliance_failures_by_severity.labels(severity=severity).set(count)

    # Per-suite scan durations
    if suite_durations:
        for suite_name, duration in suite_durations.items():
            compliance_suite_duration_seconds.labels(suite=suite_name).set(duration)
