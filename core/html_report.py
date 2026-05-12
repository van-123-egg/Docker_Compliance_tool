"""
HTML report generator using Chart.js for interactive charts.
Produces a single .html file with Chart.js loaded via CDN.
"""

import html
import json as json_lib
from datetime import datetime


def _status_badge(status):
    """Return colored badge HTML for a status."""
    if status == "WARN":
        status = "PARTIAL_COMPLIANCE"
    colors = {
        "PASS": ("#22c55e", "#052e16"),
        "FAIL": ("#ef4444", "#450a0a"),
        "WARN": ("#f59e0b", "#451a03"),
        "PARTIAL_COMPLIANCE": ("#f59e0b", "#451a03"),
        "N/A": ("#64748b", "#0f172a"),
        "ERROR": ("#a855f7", "#3b0764"),
        "MANUAL_REVIEW": ("#06b6d4", "#083344"),
    }
    bg, _ = colors.get(status, ("#64748b", "#0f172a"))
    return f'<span class="badge" style="background:{bg};">{html.escape(status)}</span>'


def _severity_badge(severity):
    """Return colored badge HTML for a severity level."""
    colors = {
        "CRITICAL": "#ef4444",
        "HIGH": "#f97316",
        "MEDIUM": "#f59e0b",
        "LOW": "#3b82f6",
        "INFO": "#64748b",
    }
    bg = colors.get(severity, "#64748b")
    return f'<span class="badge" style="background:{bg};">{html.escape(severity)}</span>'


CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background: #0a0f1a;
    color: #e2e8f0;
    line-height: 1.6;
    padding: 40px 20px;
}

.container { max-width: 1100px; margin: 0 auto; }

.header {
    text-align: center;
    margin-bottom: 40px;
    padding: 40px;
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    border-radius: 16px;
    border: 1px solid #334155;
}

.header h1 {
    font-size: 28px;
    font-weight: 700;
    background: linear-gradient(135deg, #60a5fa, #a78bfa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 8px;
}

.header .meta { color: #94a3b8; font-size: 14px; }

.dashboard {
    display: grid;
    grid-template-columns: 200px 1fr;
    gap: 30px;
    margin-bottom: 40px;
    padding: 30px;
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    border-radius: 16px;
    border: 1px solid #334155;
    align-items: center;
}

.score-gauge {
    text-align: center;
    position: relative;
    width: 180px;
    height: 180px;
}

.score-gauge canvas { display: block; }

.score-gauge .score-text {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    text-align: center;
}

.score-gauge .score-number {
    font-size: 36px;
    font-weight: 700;
    line-height: 1;
}

.score-gauge .score-label {
    font-size: 12px;
    color: #94a3b8;
    margin-top: 2px;
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(110px, 1fr));
    gap: 15px;
}

.stat-card {
    background: #0f172a;
    padding: 16px;
    border-radius: 12px;
    text-align: center;
    border: 1px solid #1e293b;
}

.stat-card .number { font-size: 28px; font-weight: 700; }
.stat-card .label { font-size: 11px; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; margin-top: 4px; }

.stat-pass .number { color: #22c55e; }
.stat-fail .number { color: #ef4444; }
.stat-warn .number { color: #f59e0b; }
.stat-na .number { color: #64748b; }

.charts-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 24px;
    margin-bottom: 40px;
}

.chart-card {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    padding: 24px;
    border-radius: 16px;
    border: 1px solid #334155;
    text-align: center;
    display: flex;
    flex-direction: column;
    align-items: center;
}

.chart-card h3 { font-size: 15px; color: #94a3b8; margin-bottom: 16px; font-weight: 500; }

.chart-container {
    position: relative;
    width: 280px;
    height: 280px;
}

.guide-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
    gap: 18px;
    margin-bottom: 32px;
}

.guide-card {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    border: 1px solid #334155;
    border-radius: 14px;
    padding: 18px;
}

.guide-card h3 {
    color: #cbd5e1;
    font-size: 15px;
    margin-bottom: 10px;
    font-weight: 600;
}

.guide-text {
    color: #94a3b8;
    font-size: 13px;
    margin-bottom: 10px;
}

.guide-list {
    margin: 0;
    padding-left: 18px;
    color: #cbd5e1;
    font-size: 13px;
}

.guide-list li { margin: 4px 0; }

.guide-card a {
    color: #7dd3fc;
    text-decoration: none;
}

.guide-card a:hover { text-decoration: underline; }

.legend-row {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 8px 0;
    color: #cbd5e1;
    font-size: 13px;
}

.suite-section {
    margin-bottom: 24px;
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    border-radius: 16px;
    border: 1px solid #334155;
    overflow: hidden;
}

.suite-section summary {
    padding: 18px 24px;
    cursor: pointer;
    font-size: 16px;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 12px;
    background: rgba(30, 41, 59, 0.5);
    border-bottom: 1px solid #334155;
    user-select: none;
}

.suite-section summary:hover { background: rgba(51, 65, 85, 0.4); }
.suite-section[open] summary { border-bottom: 1px solid #334155; }

table {
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
}

th {
    background: #0f172a;
    padding: 12px 16px;
    text-align: left;
    font-weight: 600;
    color: #94a3b8;
    text-transform: uppercase;
    font-size: 11px;
    letter-spacing: 0.5px;
}

td { padding: 12px 16px; border-bottom: 1px solid #1e293b; }
tr:hover td { background: rgba(51, 65, 85, 0.2); }

.badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 9999px;
    font-size: 11px;
    font-weight: 600;
    color: white;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.remediation-box {
    margin: 0 16px 16px;
    padding: 16px 20px;
    background: rgba(245, 158, 11, 0.08);
    border-left: 3px solid #f59e0b;
    border-radius: 0 8px 8px 0;
    font-size: 12px;
}

.remediation-box .rem-title {
    color: #f59e0b;
    font-weight: 600;
    font-size: 12px;
    margin-bottom: 6px;
}

.remediation-box pre {
    color: #e2e8f0;
    font-family: 'JetBrains Mono', 'Fira Code', monospace;
    font-size: 12px;
    white-space: pre-wrap;
    line-height: 1.5;
}

.remediation-box .ref { color: #64748b; font-size: 11px; margin-top: 8px; }

.footer {
    text-align: center;
    color: #475569;
    font-size: 12px;
    margin-top: 40px;
    padding-top: 20px;
    border-top: 1px solid #1e293b;
}

@media print {
    body { background: white; color: #0f172a; padding: 20px; }
    .header, .dashboard, .chart-card, .suite-section, .guide-card { background: white; border-color: #e2e8f0; }
    .header h1 { -webkit-text-fill-color: #1e293b; }
    .stat-card { background: #f8fafc; }
    th { background: #f1f5f9; }
    td { border-color: #e2e8f0; }
    .suite-section { break-inside: avoid; }
}
"""


def generate_html_report(data, score_info, output_file):
    """Generate a self-contained HTML compliance report with Chart.js."""
    s = score_info
    partial_count = s.get("partial_compliance", s.get("warned", 0))
    timestamp = s["timestamp"]

    # Prepare chart data as JSON for Chart.js
    pie_data = {
        "labels": [],
        "values": [],
        "colors": [],
    }
    status_map = [
        ("Pass", s["passed"], "#22c55e"),
        ("Fail", s["failed"], "#ef4444"),
        ("Partial Compliance", partial_count, "#f59e0b"),
        ("N/A", s["na"], "#64748b"),
    ]
    if s["errors"]:
        status_map.append(("Error", s["errors"], "#a855f7"))

    for label, count, color in status_map:
        if count > 0:
            pie_data["labels"].append(label)
            pie_data["values"].append(count)
            pie_data["colors"].append(color)

    # Severity bar chart data
    sev_labels = []
    sev_values = []
    sev_colors = []
    sev_color_map = {"CRITICAL": "#ef4444", "HIGH": "#f97316", "MEDIUM": "#f59e0b", "LOW": "#3b82f6", "INFO": "#64748b"}
    for sev in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]:
        count = s["severity_fails"].get(sev, 0)
        if count > 0:
            sev_labels.append(sev)
            sev_values.append(count)
            sev_colors.append(sev_color_map[sev])

    # Score gauge color
    if s["score_pct"] >= 90:
        score_color = "#22c55e"
    elif s["score_pct"] >= 70:
        score_color = "#3b82f6"
    elif s["score_pct"] >= 50:
        score_color = "#f59e0b"
    else:
        score_color = "#ef4444"

    # Action-oriented guidance for first-time users
    priority_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFO": 4}
    actionable_items = []
    for section, results in data.items():
        for res in results:
            raw_status = res.get("Status", "UNKNOWN")
            status = "PARTIAL_COMPLIANCE" if raw_status == "WARN" else raw_status
            if status not in ("FAIL", "PARTIAL_COMPLIANCE"):
                continue
            actionable_items.append({
                "section": section.replace("_", " "),
                "control_id": str(res.get("Control_ID", "N/A")),
                "severity": str(res.get("Severity", "INFO")),
                "status": status,
                "description": str(res.get("Description", "No description")),
            })

    actionable_items.sort(key=lambda x: (priority_order.get(x["severity"], 99), x["control_id"]))
    top_actions = actionable_items[:8]
    next_steps_html = ""
    if top_actions:
        action_rows = []
        for item in top_actions:
            action_rows.append(
                f"<tr>"
                f"<td><strong>{html.escape(item['control_id'])}</strong></td>"
                f"<td>{_severity_badge(item['severity'])}</td>"
                f"<td>{_status_badge(item['status'])}</td>"
                f"<td>{html.escape(item['description'])}</td>"
                f"<td>{html.escape(item['section'])}</td>"
                f"</tr>"
            )
        next_steps_html = (
            '<div class="guide-card" style="margin-bottom:32px;">'
            '<h3>Recommended First Fixes</h3>'
            '<p class="guide-text">Start with Critical and High issues first. These are the most security-impacting findings.</p>'
            '<table><thead><tr>'
            '<th>Control</th><th>Severity</th><th>Status</th><th>Why It Matters</th><th>Area</th>'
            '</tr></thead><tbody>'
            + "".join(action_rows) +
            '</tbody></table>'
            '</div>'
        )

    # Build suite sections
    suite_html_parts = []
    for section, results in data.items():
        if not results:
            continue

        section_title = section.replace('_', ' ')
        section_pass = sum(1 for r in results if r.get("Status") == "PASS")
        section_total = len(results)

        rows = []
        remediation_boxes = []

        for res in results:
            status = res.get("Status", "UNKNOWN")
            if status == "WARN":
                status = "PARTIAL_COMPLIANCE"
            control_id = html.escape(str(res.get("Control_ID", "N/A")))
            severity = res.get("Severity", "INFO")
            desc = html.escape(str(res.get("Description", "N/A")))
            details = html.escape(str(res.get("Details", "N/A")))

            rows.append(
                f'<tr>'
                f'<td><strong>{control_id}</strong></td>'
                f'<td>{_severity_badge(severity)}</td>'
                f'<td>{_status_badge(status)}</td>'
                f'<td>{desc}</td>'
                f'<td>{details}</td>'
                f'</tr>'
            )

            if status in ("FAIL", "WARN", "PARTIAL_COMPLIANCE") and res.get("Remediation"):
                rem_text = html.escape(res["Remediation"])
                ref_text = html.escape(res.get("Reference", ""))
                remediation_boxes.append(
                    f'<div class="remediation-box">'
                    f'<div class="rem-title">Remediation for {control_id}: {desc}</div>'
                    f'<pre>{rem_text}</pre>'
                    f'{"<div class=ref>Ref: " + ref_text + "</div>" if ref_text else ""}'
                    f'</div>'
                )

        table_html = (
            f'<table><thead><tr>'
            f'<th>Control</th><th>Severity</th><th>Status</th><th>Description</th><th>Details</th>'
            f'</tr></thead><tbody>{"".join(rows)}</tbody></table>'
        )

        rem_html = ''.join(remediation_boxes)

        suite_html_parts.append(
            f'<details class="suite-section" open>'
            f'<summary>{section_title} <span style="color:#64748b;font-size:13px;font-weight:400;">'
            f'({section_pass}/{section_total} passed)</span></summary>'
            f'{table_html}'
            f'{rem_html}'
            f'</details>'
        )

    suites_html = '\n'.join(suite_html_parts)
    report_guide_html = """
    <div class="guide-grid">
        <div class="guide-card">
            <h3>How to Read This Report</h3>
            <p class="guide-text">This report checks your Docker setup against CIS security best practices. Higher compliance means lower risk.</p>
            <ul class="guide-list">
                <li><strong>Compliance %</strong>: Percentage of checks currently passing.</li>
                <li><strong>Failures by Severity</strong>: Which failed checks are most urgent.</li>
                <li><strong>Section Tables</strong>: Exact controls, findings, and remediation steps.</li>
            </ul>
        </div>
        <div class="guide-card">
            <h3>Status Legend</h3>
            <div class="legend-row"><span class="badge" style="background:#22c55e;">PASS</span><span>Control meets expected security requirement.</span></div>
            <div class="legend-row"><span class="badge" style="background:#ef4444;">FAIL</span><span>Control is not compliant and should be fixed.</span></div>
            <div class="legend-row"><span class="badge" style="background:#f59e0b;">PARTIAL_COMPLIANCE</span><span>Partly compliant; more hardening is needed.</span></div>
            <div class="legend-row"><span class="badge" style="background:#64748b;">N/A</span><span>Check does not apply in this environment.</span></div>
            <div class="legend-row"><span class="badge" style="background:#06b6d4;">MANUAL_REVIEW</span><span>Needs human verification.</span></div>
        </div>
        <div class="guide-card">
            <h3>Severity Legend</h3>
            <div class="legend-row"><span class="badge" style="background:#ef4444;">CRITICAL</span><span>High probability of serious compromise impact.</span></div>
            <div class="legend-row"><span class="badge" style="background:#f97316;">HIGH</span><span>Serious exposure to prioritize quickly.</span></div>
            <div class="legend-row"><span class="badge" style="background:#f59e0b;">MEDIUM</span><span>Important hardening issue to schedule soon.</span></div>
            <div class="legend-row"><span class="badge" style="background:#3b82f6;">LOW</span><span>Lower risk improvement item.</span></div>
            <div class="legend-row"><span class="badge" style="background:#64748b;">INFO</span><span>Informational context, usually low risk.</span></div>
        </div>
        <div class="guide-card">
            <h3>References</h3>
            <ul class="guide-list">
                <li><a href="https://www.cisecurity.org/benchmark/docker" target="_blank" rel="noopener noreferrer">CIS Docker Benchmark</a></li>
                <li><a href="https://docs.docker.com/engine/security/" target="_blank" rel="noopener noreferrer">Docker Engine Security Documentation</a></li>
                <li><a href="https://owasp.org/www-project-docker-top-10/" target="_blank" rel="noopener noreferrer">OWASP Docker Top 10</a></li>
            </ul>
        </div>
    </div>
    """

    # Chart.js JavaScript
    chart_js = f"""
    // Score Gauge (Doughnut chart)
    const scoreCtx = document.getElementById('scoreGauge').getContext('2d');
    new Chart(scoreCtx, {{
        type: 'doughnut',
        data: {{
            datasets: [{{
                data: [{s["score_pct"]}, {100 - s["score_pct"]}],
                backgroundColor: ['{score_color}', '#1e293b'],
                borderWidth: 0,
                cutout: '78%',
            }}]
        }},
        options: {{
            responsive: false,
            plugins: {{
                tooltip: {{ enabled: false }},
                legend: {{ display: false }},
            }},
            animation: {{
                animateRotate: true,
                duration: 1500,
                easing: 'easeOutQuart',
            }}
        }}
    }});

    // Status Distribution Pie Chart
    const pieCtx = document.getElementById('statusPie').getContext('2d');
    new Chart(pieCtx, {{
        type: 'doughnut',
        data: {{
            labels: {json_lib.dumps(pie_data["labels"])},
            datasets: [{{
                data: {json_lib.dumps(pie_data["values"])},
                backgroundColor: {json_lib.dumps(pie_data["colors"])},
                borderWidth: 2,
                borderColor: '#0f172a',
                hoverOffset: 8,
            }}]
        }},
        options: {{
            responsive: true,
            maintainAspectRatio: true,
            plugins: {{
                legend: {{
                    position: 'bottom',
                    labels: {{
                        color: '#94a3b8',
                        font: {{ family: 'Inter', size: 12 }},
                        padding: 16,
                        usePointStyle: true,
                        pointStyle: 'circle',
                    }}
                }},
                tooltip: {{
                    backgroundColor: '#1e293b',
                    titleColor: '#e2e8f0',
                    bodyColor: '#94a3b8',
                    borderColor: '#334155',
                    borderWidth: 1,
                    cornerRadius: 8,
                    padding: 12,
                }}
            }},
            animation: {{
                animateRotate: true,
                duration: 1200,
                easing: 'easeOutQuart',
            }}
        }}
    }});

    // Severity Bar Chart
    const sevCtx = document.getElementById('severityBar').getContext('2d');
    new Chart(sevCtx, {{
        type: 'bar',
        data: {{
            labels: {json_lib.dumps(sev_labels)},
            datasets: [{{
                label: 'Failures',
                data: {json_lib.dumps(sev_values)},
                backgroundColor: {json_lib.dumps(sev_colors)},
                borderRadius: 6,
                borderSkipped: false,
                barThickness: 28,
            }}]
        }},
        options: {{
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: true,
            plugins: {{
                legend: {{ display: false }},
                tooltip: {{
                    backgroundColor: '#1e293b',
                    titleColor: '#e2e8f0',
                    bodyColor: '#94a3b8',
                    borderColor: '#334155',
                    borderWidth: 1,
                    cornerRadius: 8,
                }}
            }},
            scales: {{
                x: {{
                    beginAtZero: true,
                    ticks: {{
                        color: '#94a3b8',
                        font: {{ family: 'Inter', size: 11 }},
                        stepSize: 1,
                    }},
                    grid: {{ color: 'rgba(51,65,85,0.3)' }},
                }},
                y: {{
                    ticks: {{
                        color: '#94a3b8',
                        font: {{ family: 'Inter', size: 12, weight: 'bold' }},
                    }},
                    grid: {{ display: false }},
                }}
            }},
            animation: {{
                duration: 1000,
                easing: 'easeOutQuart',
            }}
        }}
    }});
    """

    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Docker CIS Compliance Report — {timestamp}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>
    <style>{CSS}</style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>Docker CIS Compliance Report</h1>
        <p class="meta">Generated on {timestamp}</p>
    </div>

    <div class="dashboard">
        <div class="score-gauge">
            <canvas id="scoreGauge" width="180" height="180"></canvas>
            <div class="score-text">
                <div class="score-number" style="color:{score_color};">{s['score_pct']}%</div>
                <div class="score-label">Compliance</div>
            </div>
        </div>
        <div class="stats-grid">
            <div class="stat-card stat-pass"><div class="number">{s['passed']}</div><div class="label">Passed</div></div>
            <div class="stat-card stat-fail"><div class="number">{s['failed']}</div><div class="label">Failed</div></div>
            <div class="stat-card stat-warn"><div class="number">{partial_count}</div><div class="label">Partial Compliance</div></div>
            <div class="stat-card stat-na"><div class="number">{s['na']}</div><div class="label">N/A</div></div>
        </div>
    </div>

    {report_guide_html}
    {next_steps_html}

    <div class="charts-row">
        <div class="chart-card">
            <h3>Status Distribution</h3>
            <div class="chart-container">
                <canvas id="statusPie"></canvas>
            </div>
        </div>
        <div class="chart-card">
            <h3>Failures by Severity</h3>
            <div class="chart-container">
                <canvas id="severityBar"></canvas>
            </div>
        </div>
    </div>

    {suites_html}

    <div class="footer">
        Docker CIS Benchmark Compliance Scanner &mdash; Report generated {timestamp}
    </div>
</div>
<script>{chart_js}</script>
</body>
</html>"""

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(full_html)
