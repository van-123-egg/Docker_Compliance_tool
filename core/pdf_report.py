"""
PDF report generator using reportlab.
Produces a professional audit-ready PDF with charts, tables, and remediation guidance.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, mm
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether
)
from reportlab.graphics.shapes import Drawing, Wedge, Circle, String, Rect, Line
from reportlab.graphics import renderPDF
import math


# ─── Color Palette ───────────────────────────────────────────────────

COLORS = {
    "bg_dark": HexColor("#0f172a"),
    "bg_card": HexColor("#1e293b"),
    "border": HexColor("#334155"),
    "text_primary": HexColor("#e2e8f0"),
    "text_secondary": HexColor("#94a3b8"),
    "pass": HexColor("#22c55e"),
    "fail": HexColor("#ef4444"),
    "warn": HexColor("#f59e0b"),
    "na": HexColor("#64748b"),
    "error": HexColor("#a855f7"),
    "critical": HexColor("#ef4444"),
    "high": HexColor("#f97316"),
    "medium": HexColor("#f59e0b"),
    "low": HexColor("#3b82f6"),
    "info": HexColor("#64748b"),
    "accent": HexColor("#60a5fa"),
}

STATUS_COLORS = {
    "PASS": COLORS["pass"],
    "FAIL": COLORS["fail"],
    "WARN": COLORS["warn"],
    "PARTIAL_COMPLIANCE": COLORS["warn"],
    "N/A": COLORS["na"],
    "ERROR": COLORS["error"],
    "MANUAL_REVIEW": HexColor("#06b6d4"),
}

SEVERITY_COLORS = {
    "CRITICAL": COLORS["critical"],
    "HIGH": COLORS["high"],
    "MEDIUM": COLORS["medium"],
    "LOW": COLORS["low"],
    "INFO": COLORS["info"],
}


def _create_pie_chart(slices, size=200):
    """Create a reportlab Drawing with a pie chart."""
    d = Drawing(size, size)
    cx, cy = size / 2, size / 2
    r = size / 2 - 20

    total = sum(s[1] for s in slices)
    if total == 0:
        d.add(Circle(cx, cy, r, strokeColor=COLORS["border"], fillColor=None, strokeWidth=2))
        return d

    start_angle = 90  # Start from top
    for label, count, color in slices:
        if count == 0:
            continue
        pct = count / total
        sweep = pct * 360

        if pct >= 1.0:
            d.add(Circle(cx, cy, r, fillColor=color, strokeColor=None))
        else:
            d.add(Wedge(cx, cy, r, start_angle - sweep, start_angle,
                        fillColor=color, strokeColor=None, strokeWidth=0))
        start_angle -= sweep

    return d


def _create_score_gauge(score_pct, size=150):
    """Create a score gauge drawing."""
    d = Drawing(size, size + 30)
    cx, cy = size / 2, size / 2 + 15

    if score_pct >= 90:
        color = COLORS["pass"]
    elif score_pct >= 70:
        color = COLORS["accent"]
    elif score_pct >= 50:
        color = COLORS["warn"]
    else:
        color = COLORS["fail"]

    # Background circle
    d.add(Circle(cx, cy, size / 2 - 10, strokeColor=COLORS["border"], fillColor=None, strokeWidth=8))

    # Score arc
    sweep = score_pct / 100 * 360
    if sweep > 0:
        d.add(Wedge(cx, cy, size / 2 - 10, 90 - sweep, 90,
                     fillColor=None, strokeColor=color, strokeWidth=8))

    # Score text
    d.add(String(cx, cy - 5, f"{score_pct}%", fontSize=28, fontName="Helvetica-Bold",
                 fillColor=color, textAnchor="middle"))
    d.add(String(cx, cy - 22, "Compliance", fontSize=9, fontName="Helvetica",
                 fillColor=COLORS["text_secondary"], textAnchor="middle"))

    return d


def _hex_to_rl_color_str(hex_color):
    """Convert a HexColor to a reportlab XML color string."""
    return str(hex_color).replace("Color(", "").replace(")", "")


def generate_pdf_report(data, score_info, output_file):
    """Generate a PDF compliance report."""
    doc = SimpleDocTemplate(
        output_file,
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=25 * mm,
        bottomMargin=25 * mm,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle', parent=styles['Title'],
        fontSize=24, spaceAfter=6, textColor=HexColor("#1e293b"),
        fontName="Helvetica-Bold", alignment=TA_CENTER
    )
    subtitle_style = ParagraphStyle(
        'CustomSubtitle', parent=styles['Normal'],
        fontSize=11, textColor=HexColor("#64748b"),
        alignment=TA_CENTER, spaceAfter=20
    )
    heading_style = ParagraphStyle(
        'SuiteHeading', parent=styles['Heading2'],
        fontSize=14, textColor=HexColor("#1e293b"),
        fontName="Helvetica-Bold", spaceAfter=10, spaceBefore=16
    )
    body_style = ParagraphStyle(
        'BodyStyle', parent=styles['Normal'],
        fontSize=10, textColor=HexColor("#334155"),
        leading=14, spaceAfter=6
    )
    guide_list_style = ParagraphStyle(
        'GuideListStyle', parent=body_style,
        leftIndent=12
    )
    rem_style = ParagraphStyle(
        'Remediation', parent=styles['Normal'],
        fontSize=8, textColor=HexColor("#92400e"),
        fontName="Courier", leftIndent=10, spaceAfter=8,
        leading=11
    )

    # Table cell styles — these use Paragraph for auto text wrapping
    cell_style = ParagraphStyle(
        'CellStyle', parent=styles['Normal'],
        fontSize=8, fontName="Helvetica", textColor=HexColor("#334155"),
        leading=10, spaceBefore=0, spaceAfter=0
    )
    cell_style_bold = ParagraphStyle(
        'CellStyleBold', parent=cell_style,
        fontName="Helvetica-Bold"
    )
    cell_header_style = ParagraphStyle(
        'CellHeaderStyle', parent=cell_style,
        fontName="Helvetica-Bold", textColor=white, alignment=TA_CENTER
    )

    elements = []
    s = score_info
    partial_count = s.get("partial_compliance", s.get("warned", 0))

    # ─── Title Page ──────────────────────────────────────────────────

    elements.append(Spacer(1, 60))
    elements.append(Paragraph("Docker CIS Compliance Report", title_style))
    elements.append(Paragraph(f"Generated on {s['timestamp']}", subtitle_style))
    elements.append(Spacer(1, 30))

    # Score summary table
    score_data = [
        ["Compliance Score", f"{s['score_pct']}%"],
        ["Checks Passed", f"{s['passed']} / {s['passed'] + s['failed']}"],
        ["Status", f"PASS: {s['passed']}  |  FAIL: {s['failed']}  |  PARTIAL_COMPLIANCE: {partial_count}  |  N/A: {s['na']}"],
    ]

    if s['failed'] > 0:
        sev_parts = []
        for sev in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
            count = s['severity_fails'].get(sev, 0)
            if count > 0:
                sev_parts.append(f"{sev}: {count}")
        if sev_parts:
            score_data.append(["Failures by Severity", "  |  ".join(sev_parts)])

    score_table = Table(score_data, colWidths=[150, 310])
    score_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), HexColor("#f1f5f9")),
        ('TEXTCOLOR', (0, 0), (0, -1), HexColor("#334155")),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor("#e2e8f0")),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
    ]))
    elements.append(score_table)
    elements.append(Spacer(1, 20))

    # ─── Report Guide + Legends (beginner-friendly) ────────────────
    elements.append(Paragraph("How to Read This Report", heading_style))
    elements.append(Paragraph(
        "This report checks your Docker setup against CIS security best practices. "
        "Higher compliance means lower security risk.",
        body_style
    ))
    guide_points = [
        "<b>Compliance %</b>: Percentage of checks currently passing.",
        "<b>Failures by Severity</b>: Shows which failed checks are most urgent.",
        "<b>Section Tables</b>: Lists exact controls, findings, and remediation steps.",
    ]
    for point in guide_points:
        elements.append(Paragraph(f"• {point}", guide_list_style))
    elements.append(Spacer(1, 10))

    legend_header_style = ParagraphStyle(
        'LegendHeaderStyle', parent=cell_header_style, alignment=TA_LEFT
    )
    legend_label_style = ParagraphStyle(
        'LegendLabelStyle', parent=cell_style, fontName="Helvetica-Bold"
    )

    status_legend_rows = [
        [Paragraph("Status Legend", legend_header_style), ""],
        [Paragraph('<font color="#22c55e">PASS</font>', legend_label_style), Paragraph("Control meets expected security requirement.", cell_style)],
        [Paragraph('<font color="#ef4444">FAIL</font>', legend_label_style), Paragraph("Control is not compliant and should be fixed.", cell_style)],
        [Paragraph('<font color="#f59e0b">PARTIAL_COMPLIANCE</font>', legend_label_style), Paragraph("Partly compliant; more hardening is needed.", cell_style)],
        [Paragraph('<font color="#64748b">N/A</font>', legend_label_style), Paragraph("Check does not apply in this environment.", cell_style)],
        [Paragraph('<font color="#06b6d4">MANUAL_REVIEW</font>', legend_label_style), Paragraph("Needs human verification.", cell_style)],
    ]
    status_legend_table = Table(status_legend_rows, colWidths=[145, 315])
    status_legend_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor("#1e293b")),
        ('SPAN', (0, 0), (1, 0)),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor("#e2e8f0")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, HexColor("#f8fafc")]),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(status_legend_table)
    elements.append(Spacer(1, 10))

    severity_legend_rows = [
        [Paragraph("Severity Legend", legend_header_style), ""],
        [Paragraph('<font color="#ef4444">CRITICAL</font>', legend_label_style), Paragraph("High probability of serious compromise impact.", cell_style)],
        [Paragraph('<font color="#f97316">HIGH</font>', legend_label_style), Paragraph("Serious exposure to prioritize quickly.", cell_style)],
        [Paragraph('<font color="#f59e0b">MEDIUM</font>', legend_label_style), Paragraph("Important hardening issue to schedule soon.", cell_style)],
        [Paragraph('<font color="#3b82f6">LOW</font>', legend_label_style), Paragraph("Lower risk improvement item.", cell_style)],
        [Paragraph('<font color="#64748b">INFO</font>', legend_label_style), Paragraph("Informational context, usually low risk.", cell_style)],
    ]
    severity_legend_table = Table(severity_legend_rows, colWidths=[145, 315])
    severity_legend_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor("#1e293b")),
        ('SPAN', (0, 0), (1, 0)),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor("#e2e8f0")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, HexColor("#f8fafc")]),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(severity_legend_table)
    elements.append(Spacer(1, 10))

    elements.append(Paragraph("References", heading_style))
    refs = [
        "1. CIS Docker Benchmark: https://www.cisecurity.org/benchmark/docker",
        "2. Docker Engine Security Documentation: https://docs.docker.com/engine/security/",
        "3. OWASP Docker Top 10: https://owasp.org/www-project-docker-top-10/",
    ]
    for ref in refs:
        elements.append(Paragraph(ref, body_style))
    elements.append(Spacer(1, 20))

    # ─── Suite Detail Sections ───────────────────────────────────────

    # Color hex strings for Paragraph markup
    SEV_HEX = {
        "CRITICAL": "#ef4444", "HIGH": "#f97316", "MEDIUM": "#f59e0b",
        "LOW": "#3b82f6", "INFO": "#64748b"
    }
    STATUS_HEX = {
        "PASS": "#22c55e", "FAIL": "#ef4444", "WARN": "#f59e0b", "PARTIAL_COMPLIANCE": "#f59e0b",
        "N/A": "#64748b", "ERROR": "#a855f7", "MANUAL_REVIEW": "#06b6d4",
    }

    for section, results in data.items():
        if not results:
            continue

        section_title = section.replace('_', ' ')
        section_pass = sum(1 for r in results if r.get("Status") == "PASS")
        section_total = len(results)

        elements.append(Paragraph(
            f"{section_title} ({section_pass}/{section_total} passed)",
            heading_style
        ))

        # Build table with Paragraph cells for proper text wrapping
        header_row = [
            Paragraph("Control", cell_header_style),
            Paragraph("Severity", cell_header_style),
            Paragraph("Status", cell_header_style),
            Paragraph("Description", cell_header_style),
            Paragraph("Details", cell_header_style),
        ]
        table_data = [header_row]

        for res in results:
            control_id = str(res.get("Control_ID", "N/A"))
            severity = res.get("Severity", "INFO")
            status = res.get("Status", "UNKNOWN")
            if status == "WARN":
                status = "PARTIAL_COMPLIANCE"
            desc = str(res.get("Description", "N/A"))
            details = str(res.get("Details", "N/A"))

            # Color-coded severity and status via Paragraph markup
            sev_hex = SEV_HEX.get(severity, "#64748b")
            status_hex = STATUS_HEX.get(status, "#334155")

            row = [
                Paragraph(f"<b>{control_id}</b>", cell_style),
                Paragraph(f'<font color="{sev_hex}"><b>{severity}</b></font>', cell_style),
                Paragraph(f'<font color="{status_hex}"><b>{status}</b></font>', cell_style),
                Paragraph(desc, cell_style),
                Paragraph(details, cell_style),
            ]
            table_data.append(row)

        col_widths = [52, 52, 55, 165, 165]
        detail_table = Table(table_data, colWidths=col_widths, repeatRows=1)

        # Table styling (no per-cell text color needed — handled by Paragraph markup)
        detail_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor("#1e293b")),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor("#e2e8f0")),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, HexColor("#f8fafc")]),
        ]))

        elements.append(detail_table)
        elements.append(Spacer(1, 8))

        # Remediation guidance for failures
        for res in results:
            if res.get("Status") in ("FAIL", "WARN", "PARTIAL_COMPLIANCE") and res.get("Remediation"):
                control_id = res.get("Control_ID", "N/A")
                rem_text = res["Remediation"].replace("\n", "<br/>")
                ref_text = res.get("Reference", "")

                rem_para = Paragraph(
                    f"<b>Remediation for {control_id}:</b><br/>{rem_text}"
                    + (f"<br/><i>Ref: {ref_text}</i>" if ref_text else ""),
                    rem_style
                )
                elements.append(rem_para)

        elements.append(Spacer(1, 16))

    # ─── Footer ──────────────────────────────────────────────────────

    footer_style = ParagraphStyle(
        'Footer', parent=styles['Normal'],
        fontSize=8, textColor=HexColor("#94a3b8"),
        alignment=TA_CENTER, spaceBefore=30
    )
    elements.append(Paragraph(
        f"Docker CIS Benchmark Compliance Scanner — Report generated {s['timestamp']}",
        footer_style
    ))

    doc.build(elements)
