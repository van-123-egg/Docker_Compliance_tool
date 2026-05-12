import json
import sys
from datetime import datetime

try:
    from tabulate import tabulate
except ImportError:
    tabulate = None


class ReportEngine:
    def __init__(self, format_type, output_file=None):
        self.format_type = format_type
        self.output_file = output_file

    def generate(self, data):
        # Always print the compliance summary to stdout
        score_info = self._compute_score(data)
        self._render_summary(score_info)

        if self.format_type == 'json':
            self._generate_json(data, score_info)
        elif self.format_type == 'table':
            self._generate_table(data)
        elif self.format_type == 'html':
            self._generate_html(data, score_info)
        elif self.format_type == 'pdf':
            self._generate_pdf(data, score_info)

        return score_info

    # ─── Score Computation ───────────────────────────────────────────

    def _compute_score(self, data):
        """Compute compliance score from all results."""
        total = 0
        passed = 0
        failed = 0
        partial_compliance = 0
        errors = 0
        na = 0
        manual = 0
        severity_fails = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "INFO": 0}

        for section, results in data.items():
            for res in results:
                status = res.get("Status", "UNKNOWN")
                severity = res.get("Severity", "INFO")

                if status == "PASS":
                    total += 1
                    passed += 1
                elif status == "FAIL":
                    total += 1
                    failed += 1
                    severity_fails[severity] = severity_fails.get(severity, 0) + 1
                elif status in ("WARN", "PARTIAL_COMPLIANCE"):
                    total += 1
                    failed += 1
                    partial_compliance += 1
                    severity_fails[severity] = severity_fails.get(severity, 0) + 1
                elif status == "ERROR":
                    errors += 1
                elif status in ("N/A",):
                    na += 1
                elif status == "MANUAL_REVIEW":
                    manual += 1

        scorable = passed + failed
        score_pct = round((passed / scorable) * 100) if scorable > 0 else 100

        return {
            "score_pct": score_pct,
            "total": total,
            "passed": passed,
            "failed": failed,
            "warned": partial_compliance,
            "partial_compliance": partial_compliance,
            "errors": errors,
            "na": na,
            "manual": manual,
            "severity_fails": severity_fails,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    def _render_summary(self, s):
        """Print a colored ASCII compliance dashboard."""
        # Determine overall indicator
        if s["score_pct"] >= 90:
            indicator = "EXCELLENT"
        elif s["score_pct"] >= 70:
            indicator = "GOOD"
        elif s["score_pct"] >= 50:
            indicator = "NEEDS IMPROVEMENT"
        else:
            indicator = "CRITICAL"

        width = 58
        border = "=" * width
        divider = "-" * width

        lines = [
            "",
            f"  +{border}+",
            f"  |{'Docker CIS Compliance Report':^{width}}|",
            f"  +{divider}+",
            f"  |{'Scan Time:  ' + s['timestamp']:^{width}}|",
            f"  |{'':^{width}}|",
            f"  |{'Score:  ' + str(s['score_pct']) + '% (' + str(s['passed']) + '/' + str(s['passed'] + s['failed']) + ' checks passed)  —  ' + indicator:^{width}}|",
            f"  |{'':^{width}}|",
        ]

        partial_count = s.get("partial_compliance", s.get("warned", 0))
        status_line = f"PASS: {s['passed']}  |  FAIL: {s['failed']}  |  PARTIAL_COMPLIANCE: {partial_count}  |  N/A: {s['na']}"
        if s['errors']:
            status_line += f"  |  ERROR: {s['errors']}"
        if s['manual']:
            status_line += f"  |  MANUAL: {s['manual']}"
        lines.append(f"  |{status_line:^{width}}|")

        # Severity breakdown if there are failures
        if s['failed'] > 0:
            lines.append(f"  |{'':^{width}}|")
            lines.append(f"  |{'Failures by Severity:':^{width}}|")
            sev_parts = []
            for sev in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
                count = s['severity_fails'].get(sev, 0)
                if count > 0:
                    sev_parts.append(f"{sev}: {count}")
            if sev_parts:
                sev_line = "  |  ".join(sev_parts)
                lines.append(f"  |{sev_line:^{width}}|")

        lines.append(f"  +{border}+")
        lines.append("")

        print("\n".join(lines))

    # ─── JSON Output ─────────────────────────────────────────────────

    def _generate_json(self, data, score_info):
        output_data = {
            "summary": score_info,
            "results": data
        }
        output = json.dumps(output_data, indent=4)
        if self.output_file:
            with open(self.output_file, 'w') as f:
                f.write(output)
            print(f"[*] JSON report saved to {self.output_file}")
        else:
            print(output)

    # ─── Table Output ────────────────────────────────────────────────

    def _generate_table(self, data):
        if not tabulate:
            print("[!] 'tabulate' library not found. Falling back to JSON.")
            self._generate_json(data, self._compute_score(data))
            return

        output_lines = []
        for section, results in data.items():
            if not results:
                continue

            # Format the section header
            output_lines.append(f"\n=== {section.replace('_', ' ')} ===")

            headers = ["Control ID", "Severity", "Status", "Control Name", "Details"]
            table_data = []

            for res in results:
                if res.get("Status") == "ERROR":
                    table_data.append(["ERROR", "—", "ERROR", res.get("Module", "Unknown"), res.get("Details", "N/A")])
                else:
                    # Truncate long descriptions/details so the table doesn't break the terminal width
                    desc = res.get("Description", "N/A")
                    desc = desc[:45] + "..." if len(desc) > 45 else desc

                    details = str(res.get("Details", "N/A"))
                    details = details[:55] + "..." if len(details) > 55 else details

                    severity = res.get("Severity", "INFO")

                    status = res.get("Status", "UNKNOWN")
                    if status == "WARN":
                        status = "PARTIAL_COMPLIANCE"

                    table_data.append([
                        res.get("Control_ID", "N/A"),
                        severity,
                        status,
                        desc,
                        details
                    ])

            # Generate the grid
            table_str = tabulate(table_data, headers=headers, tablefmt="grid")
            output_lines.append(table_str)

            # Show remediation for failed checks
            for res in results:
                if res.get("Status") in ("FAIL", "WARN", "PARTIAL_COMPLIANCE") and res.get("Remediation"):
                    output_lines.append(f"\n  >> Remediation for {res.get('Control_ID')}:")
                    for line in res["Remediation"].split("\n"):
                        output_lines.append(f"     {line}")
                    if res.get("Reference"):
                        output_lines.append(f"     Ref: {res['Reference']}")

        final_output = "\n".join(output_lines)

        if self.output_file:
            with open(self.output_file, 'w') as f:
                f.write(final_output)
            print(f"[*] Table report saved to {self.output_file}")
        else:
            print(final_output)

    # ─── HTML Output ─────────────────────────────────────────────────

    def _generate_html(self, data, score_info):
        from core.html_report import generate_html_report
        output_file = self.output_file or "compliance_report.html"
        generate_html_report(data, score_info, output_file)
        print(f"[*] HTML report saved to {output_file}")

    # ─── PDF Output ──────────────────────────────────────────────────

    def _generate_pdf(self, data, score_info):
        from core.pdf_report import generate_pdf_report
        output_file = self.output_file or "compliance_report.pdf"
        generate_pdf_report(data, score_info, output_file)
        print(f"[*] PDF report saved to {output_file}")
