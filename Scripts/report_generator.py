import os
import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus.flowables import Flowable

# Analysis imports
from traffic_analysis       import run_analysis as _traffic
from load_analysis          import run_analysis as _load
from user_behavior_analysis import run_analysis as _users
from ad_analytics           import run_analysis as _ads
from security_logs          import run_analysis as _security

# Colour palette
C_PURPLE  = colors.HexColor("#7c3aed")
C_BLUE    = colors.HexColor("#2563eb")
C_TEAL    = colors.HexColor("#0d9488")
C_ORANGE  = colors.HexColor("#d97706")
C_RED     = colors.HexColor("#dc2626")
C_PINK    = colors.HexColor("#db2777")
C_DARK    = colors.HexColor("#0f172a")
C_SLATE   = colors.HexColor("#1e293b")
C_MUTED   = colors.HexColor("#64748b")
C_LIGHT   = colors.HexColor("#f8fafc")
C_WHITE   = colors.white
C_BORDER  = colors.HexColor("#e2e8f0")
C_ROW_ALT = colors.HexColor("#f1f5f9")
C_GREEN   = colors.HexColor("#16a34a")
C_AMBER   = colors.HexColor("#b45309")
C_GOOD    = colors.HexColor("#dcfce7")
C_WARN    = colors.HexColor("#fef9c3")
C_BAD     = colors.HexColor("#fee2e2")
C_GOOD_T  = colors.HexColor("#166534")
C_WARN_T  = colors.HexColor("#854d0e")
C_BAD_T   = colors.HexColor("#991b1b")


# ── Inline bar chart using canvas ─────────────────────────────────────────────
class HBarChart(Flowable):
    """Horizontal bar chart rendered inline."""
    def __init__(self, data, width=440, bar_height=16, spacing=6, color=C_BLUE):
        Flowable.__init__(self)
        self.data     = data   # list of (label, value) tuples
        self.width    = width
        self.bar_h    = bar_height
        self.spacing  = spacing
        self.color    = color
        self.height   = (bar_height + spacing) * len(data) + 10

    def draw(self):
        c = self.canv
        if not self.data:
            return
        max_val = max(v for _, v in self.data) or 1
        bar_area = self.width * 0.55
        label_w  = self.width * 0.35
        val_w    = self.width * 0.10
        y = self.height - self.bar_h - 5

        for label, value in self.data:
            # Label
            c.setFont("Helvetica", 8)
            c.setFillColor(C_SLATE)
            c.drawRightString(label_w - 4, y + 3, str(label)[:28])
            # Bar background
            c.setFillColor(colors.HexColor("#e2e8f0"))
            c.roundRect(label_w, y, bar_area, self.bar_h, 3, fill=1, stroke=0)
            # Bar fill
            fill_w = max(4, bar_area * (value / max_val))
            c.setFillColor(self.color)
            c.roundRect(label_w, y, fill_w, self.bar_h, 3, fill=1, stroke=0)
            # Value
            c.setFont("Helvetica-Bold", 8)
            c.setFillColor(C_SLATE)
            c.drawString(label_w + bar_area + 4, y + 3, f"{int(value):,}")
            y -= (self.bar_h + self.spacing)


class DonutChart(Flowable):
    """Simple donut chart."""
    def __init__(self, data, size=120):
        Flowable.__init__(self)
        self.data   = data   # list of (label, value, color)
        self.size   = size
        self.width  = size * 2.5
        self.height = size + 20

    def draw(self):
        import math
        c = self.canv
        total = sum(v for _, v, _ in self.data) or 1
        cx, cy = self.size * 0.6, self.size * 0.5
        r_outer = self.size * 0.45
        r_inner = r_outer * 0.6
        angle = 90.0
        for label, value, col in self.data:
            sweep = 360 * value / total
            c.setFillColor(col)
            c.wedge(cx - r_outer, cy - r_outer, cx + r_outer, cy + r_outer,
                    angle, -sweep, fill=1, stroke=0)
            angle -= sweep
        # Punch hole
        c.setFillColor(C_WHITE)
        c.circle(cx, cy, r_inner, fill=1, stroke=0)
        # Legend
        lx = self.size * 1.35
        ly = cy + len(self.data) * 9
        for label, value, col in self.data:
            pct = round(value / total * 100, 1)
            c.setFillColor(col)
            c.roundRect(lx, ly, 10, 8, 2, fill=1, stroke=0)
            c.setFillColor(C_SLATE)
            c.setFont("Helvetica", 7.5)
            c.drawString(lx + 14, ly + 1, f"{label}: {pct}%")
            ly -= 16


def _styles():
    base = getSampleStyleSheet()

    def ps(name, **kw):
        return ParagraphStyle(name=name, parent=base["Normal"], **kw)

    return {
        "cover_title":  ps("CoverTitle", fontSize=32, textColor=C_WHITE,
                           alignment=TA_CENTER, spaceAfter=6, fontName="Helvetica-Bold"),
        "cover_sub":    ps("CoverSub",   fontSize=14, textColor=colors.HexColor("#cbd5e1"),
                           alignment=TA_CENTER, spaceAfter=4),
        "cover_meta":   ps("CoverMeta",  fontSize=10, textColor=colors.HexColor("#94a3b8"),
                           alignment=TA_CENTER),
        "section":      ps("Section",    fontSize=14, textColor=C_WHITE,
                           fontName="Helvetica-Bold", spaceBefore=14, spaceAfter=4),
        "subsection":   ps("SubSection", fontSize=11, textColor=C_SLATE,
                           fontName="Helvetica-Bold", spaceBefore=10, spaceAfter=4),
        "body":         ps("Body",       fontSize=9.5, textColor=C_SLATE,
                           leading=15, spaceAfter=7, alignment=TA_JUSTIFY),
        "insight":      ps("Insight",    fontSize=9, textColor=colors.HexColor("#1e3a5f"),
                           leading=14, spaceAfter=5, leftIndent=10,
                           borderPad=6),
        "table_hdr":    ps("TblHdr",     fontSize=8.5, textColor=C_WHITE,
                           fontName="Helvetica-Bold", alignment=TA_LEFT),
        "table_cell":   ps("TblCell",    fontSize=8.5, textColor=C_SLATE),
        "caption":      ps("Caption",    fontSize=7.5, textColor=C_MUTED,
                           spaceAfter=10, spaceBefore=2, alignment=TA_CENTER),
        "kpi_val":      ps("KpiVal",     fontSize=16, textColor=C_PURPLE,
                           fontName="Helvetica-Bold", alignment=TA_CENTER),
        "kpi_lbl":      ps("KpiLbl",     fontSize=7.5, textColor=C_MUTED,
                           alignment=TA_CENTER),
        "rec_good":     ps("RecGood",    fontSize=9, textColor=C_GOOD_T,
                           leading=14, spaceAfter=3, leftIndent=8),
        "rec_warn":     ps("RecWarn",    fontSize=9, textColor=C_WARN_T,
                           leading=14, spaceAfter=3, leftIndent=8),
        "rec_bad":      ps("RecBad",     fontSize=9, textColor=C_BAD_T,
                           leading=14, spaceAfter=3, leftIndent=8),
        "footer_txt":   ps("FooterTxt",  fontSize=7.5, textColor=C_MUTED,
                           alignment=TA_CENTER),
        "toc_entry":    ps("TocEntry",   fontSize=10, textColor=C_SLATE,
                           leading=18, leftIndent=10),
    }


def _tbl_style(header_color=C_PURPLE, alt=True):
    return TableStyle([
        ("BACKGROUND",     (0, 0), (-1,  0), header_color),
        ("TEXTCOLOR",      (0, 0), (-1,  0), C_WHITE),
        ("FONTNAME",       (0, 0), (-1,  0), "Helvetica-Bold"),
        ("FONTSIZE",       (0, 0), (-1, -1), 8.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [C_WHITE, C_ROW_ALT] if alt else [C_WHITE]),
        ("ALIGN",          (0, 0), (-1, -1), "LEFT"),
        ("VALIGN",         (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING",    (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",   (0, 0), (-1, -1), 8),
        ("TOPPADDING",     (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",  (0, 0), (-1, -1), 5),
        ("GRID",           (0, 0), (-1, -1), 0.3, C_BORDER),
    ])


def _section_banner(title, story, s, color=C_PURPLE, W=None):
    """Full-width colored section header banner."""
    if W is None:
        W = A4[0] - 4*cm
    banner = Table([[Paragraph(title, s["section"])]],
                   colWidths=[W])
    banner.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), color),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING",   (0, 0), (-1, -1), 12),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
        ("ROUNDEDCORNERS", [6]),
    ]))
    story.append(Spacer(1, 0.25*cm))
    story.append(banner)
    story.append(Spacer(1, 0.2*cm))


def _insight_box(text, story, s, bg=colors.HexColor("#eff6ff"),
                 border=colors.HexColor("#bfdbfe"), icon=""):
    """Styled insight/recommendation callout box."""
    content = f"<b>{icon}</b>  {text}" if icon else text
    box = Table([[Paragraph(content, s["insight"])]],
                colWidths=[A4[0] - 4*cm])
    box.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), bg),
        ("LINEAFTER",     (0, 0), (0, -1),  2, border),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
    ]))
    story.append(box)
    story.append(Spacer(1, 0.12*cm))


def _status_pill(label, value, status="neutral"):
    """Returns a small colored pill cell for status tables."""
    bg = {"good": C_GOOD, "warn": C_WARN, "bad": C_BAD}.get(status, C_LIGHT)
    tc = {"good": C_GOOD_T, "warn": C_WARN_T, "bad": C_BAD_T}.get(status, C_MUTED)
    style = ParagraphStyle("pill", fontSize=8, textColor=tc,
                            fontName="Helvetica-Bold", alignment=TA_CENTER)
    return Paragraph(value, style)


def generate_business_report(output_path: str, data_dir: str):
    # Use UTC time to avoid timezone confusion
    now = datetime.datetime.utcnow()
    date_str = now.strftime("%B %d, %Y")
    time_str = now.strftime("%H:%M UTC")

    # ── Fetch all analysis data ───────────────────────────────────────────────
    traffic  = _traffic(data_dir)
    load     = _load(data_dir)
    users    = _users(data_dir)
    ads      = _ads(data_dir)
    security = _security(data_dir)

    # ── Derived metrics ───────────────────────────────────────────────────────
    hourly       = traffic["hourly_traffic"]
    peak_hour    = max(hourly, key=hourly.get)
    peak_traffic = hourly[peak_hour]
    low_hour     = min(hourly, key=hourly.get)
    low_traffic  = hourly[low_hour]
    sources      = traffic.get("traffic_sources", {})
    geo          = traffic.get("geo_distribution", {})
    total_sess   = int(traffic["total_sessions"])
    top_geo      = sorted(geo.items(), key=lambda x: x[1], reverse=True)[:6]
    top_src      = sorted(sources.items(), key=lambda x: x[1], reverse=True)

    funnel       = ads.get("funnel", {})
    ad_formats   = ads.get("ad_formats", {})
    ctr          = ads.get("ctr", 0)
    roas         = ads.get("roas", 0)
    cpc          = ads.get("cpc", 0)
    total_impr   = ads.get("total_impressions", 0)
    total_clicks = funnel.get("clicks", 0)
    total_conv   = funnel.get("checkout", 0)
    conv_rate    = round(total_conv / total_clicks * 100, 2) if total_clicks else 0

    attack_types    = security.get("attack_types", {})
    activity_log    = security.get("activity_log", [])
    threats_blocked = security.get("threats_blocked", 0)
    critical_alerts = security.get("critical_alerts", 0)
    firewall_status = security.get("firewall_status", "Unknown")
    security_score  = security.get("security_score", 0)
    errors_4xx      = attack_types.get("4xx Errors", 0)
    errors_5xx      = attack_types.get("5xx Errors", 0)
    susp_ips        = attack_types.get("Suspicious IPs", 0)
    failed_logins   = next((x["count"] for x in activity_log if x["name"] == "Failed Logins"), 0)

    repeat_users  = users["buyers"].get("Repeat", 0)
    onetime_users = users["buyers"].get("One-time", 0)
    journey       = users.get("journey", {})
    category      = users.get("category", {})
    segments      = users.get("segments", {})
    top_cat       = sorted(category.items(), key=lambda x: x[1], reverse=True)[:6]
    top_eps       = list(load.get("top_endpoints", {}).items())[:6]
    susp_ip_list  = list(load.get("suspicious_ips", {}).items())[:6]

    s = _styles()

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2.2*cm, bottomMargin=2.2*cm,
        title="TrafficIQ Business Intelligence Report",
        author="TrafficIQ Analytics Platform",
    )
    story = []
    W = A4[0] - 4*cm

    # ══════════════════════════════════════════════════════════════════════════
    # COVER PAGE
    # ══════════════════════════════════════════════════════════════════════════
    story.append(Spacer(1, 1.5*cm))

    cover = Table(
        [[Paragraph("TrafficIQ", s["cover_title"])],
         [Spacer(1, 0.2*cm)],
         [Paragraph("Business Intelligence Report", s["cover_sub"])],
         [Paragraph("Executive Analytics &amp; Platform Summary", s["cover_sub"])],
         [Spacer(1, 0.6*cm)],
         [HRFlowable(width=W*0.5, thickness=1, color=colors.HexColor("#475569"),
                     hAlign="CENTER", spaceAfter=0)],
         [Spacer(1, 0.4*cm)],
         [Paragraph(f"Generated: {date_str}  |  {time_str}", s["cover_meta"])],
         [Paragraph("MediCaps University  |  TrafficIQ Analytics Platform", s["cover_meta"])],
         [Spacer(1, 0.3*cm)],
         [Paragraph("CONFIDENTIAL — FOR INTERNAL USE ONLY", ParagraphStyle(
             "conf", fontSize=9, textColor=colors.HexColor("#f87171"),
             alignment=TA_CENTER, fontName="Helvetica-Bold"))]],
        colWidths=[W]
    )
    cover.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), C_DARK),
        ("TOPPADDING",    (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("LEFTPADDING",   (0, 0), (-1, -1), 24),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 24),
        ("ROUNDEDCORNERS", [10]),
    ]))
    story.append(cover)
    story.append(Spacer(1, 0.8*cm))

    # ── KPI Scorecard ─────────────────────────────────────────────────────────
    def kpi_cell(label, val, color, bg=C_LIGHT):
        return Table(
            [[Paragraph(val, ParagraphStyle("kv", fontSize=17, textColor=color,
                        fontName="Helvetica-Bold", alignment=TA_CENTER))],
             [Paragraph(label, s["kpi_lbl"])]],
            colWidths=[W/4 - 2]
        )

    sec_color = C_GREEN if security_score >= 70 else (C_ORANGE if security_score >= 50 else C_RED)
    kpi_rows = [
        [kpi_cell("Total Sessions",  f"{total_sess:,}",               C_BLUE),
         kpi_cell("Total Requests",  f"{load['total_requests']:,}",    C_ORANGE),
         kpi_cell("Total Orders",    f"{users['total_orders']:,}",     C_TEAL),
         kpi_cell("Retention Rate",  f"{users['retention_rate']}%",    C_PURPLE)],
        [kpi_cell("Avg Rating",      f"{users['avg_rating']}/5.0",     C_ORANGE),
         kpi_cell("ROAS",            f"{roas}x",                       C_PINK),
         kpi_cell("Security Score",  f"{security_score:.1f}/100",      sec_color),
         kpi_cell("Threats Blocked", f"{threats_blocked:,}",           C_RED)],
    ]
    kpi_tbl = Table(kpi_rows, colWidths=[W/4]*4, rowHeights=[1.5*cm, 1.5*cm])
    kpi_tbl.setStyle(TableStyle([
        ("BOX",           (0, 0), (-1, -1), 0.5, C_BORDER),
        ("INNERGRID",     (0, 0), (-1, -1), 0.5, C_BORDER),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("ROWBACKGROUNDS",(0, 0), (-1, -1), [C_LIGHT, C_WHITE]),
    ]))
    story.append(kpi_tbl)
    story.append(Spacer(1, 0.5*cm))

    # ── Table of Contents ─────────────────────────────────────────────────────
    toc_items = [
        "1.  Executive Summary",
        "2.  Traffic Intelligence Analysis",
        "3.  Server Load &amp; Performance Analysis",
        "4.  User Behaviour &amp; Retention Analysis",
        "5.  Advertisement Performance Analysis",
        "6.  Security &amp; Threat Analysis",
        "7.  Key Findings &amp; Business Recommendations",
        "Appendix — Full KPI Reference Table",
    ]
    toc_data = [[Paragraph("Table of Contents", ParagraphStyle(
        "toch", fontSize=11, fontName="Helvetica-Bold", textColor=C_SLATE))]] + \
        [[Paragraph(f"   {item}", s["toc_entry"])] for item in toc_items]
    toc_tbl = Table(toc_data, colWidths=[W])
    toc_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (0, 0),  C_LIGHT),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING",   (0, 0), (-1, -1), 12),
        ("BOX",           (0, 0), (-1, -1), 0.5, C_BORDER),
        ("LINEBELOW",     (0, 0), (-1, 0),  0.5, C_BORDER),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [C_WHITE, C_LIGHT]),
    ]))
    story.append(toc_tbl)
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # 1. EXECUTIVE SUMMARY
    # ══════════════════════════════════════════════════════════════════════════
    _section_banner("1.  Executive Summary", story, s, C_DARK, W)

    story.append(Paragraph(
        f"This report provides a comprehensive data-driven performance overview of the "
        f"<b>TrafficIQ Analytics Platform</b> for the period ending <b>{date_str}</b>. "
        f"The analysis covers five core pillars: web traffic, server infrastructure, user behaviour, "
        f"advertising performance, and platform security.",
        s["body"]
    ))

    # Health scorecard table
    def health_row(metric, value, status, comment):
        bg = {"good": C_GOOD, "warn": C_WARN, "bad": C_BAD}.get(status, C_LIGHT)
        tc = {"good": C_GOOD_T, "warn": C_WARN_T, "bad": C_BAD_T}.get(status, C_SLATE)
        icon = {"good": "GOOD", "warn": "REVIEW", "bad": "ACTION"}.get(status, "")
        return [metric, value,
                Paragraph(f"<b>{icon}</b>",
                          ParagraphStyle("hs", fontSize=8, textColor=tc,
                                         fontName="Helvetica-Bold", alignment=TA_CENTER)),
                comment]

    health_data = [
        ["Metric", "Value", "Status", "Comment"],
        health_row("Total Sessions",       f"{total_sess:,}",                    "good", "Strong traffic volume"),
        health_row("Avg Session Duration", f"{traffic['avg_session_duration']}s", "good", "Users are engaged"),
        health_row("Server Error Rate",    f"{load['error_rate']:.1f}%",
                   "bad" if load['error_rate'] > 5 else "good",
                   "High — needs investigation" if load['error_rate'] > 5 else "Within threshold"),
        health_row("Ad CTR",               f"{ctr}%",
                   "bad" if ctr < 1 else ("warn" if ctr < 2 else "good"),
                   "Below industry avg (2%)" if ctr < 2 else "On target"),
        health_row("Security Score",       f"{security_score:.1f}/100",
                   "bad" if security_score < 50 else ("warn" if security_score < 70 else "good"),
                   "Critical — immediate action" if security_score < 50 else "Moderate risk"),
        health_row("Customer Retention",   f"{users['retention_rate']}%",        "good", "Excellent retention"),
        health_row("Avg Order Value",      f"${users['avg_order_value']}",        "good", "High-value customers"),
    ]

    ht = Table(health_data, colWidths=[W*0.26, W*0.16, W*0.14, W*0.44])
    ht_style = _tbl_style(C_DARK)
    for i, row in enumerate(health_data[1:], 1):
        status_text = row[2].text if hasattr(row[2], 'text') else ""
        if "ACTION" in str(row[2]):
            ht_style.add("BACKGROUND", (0, i), (-1, i), C_BAD)
        elif "REVIEW" in str(row[2]):
            ht_style.add("BACKGROUND", (0, i), (-1, i), C_WARN)
    ht.setStyle(ht_style)
    story.append(ht)
    story.append(Paragraph("Table 1.1 — Platform Health Scorecard", s["caption"]))

    story.append(Paragraph(
        f"<b>Overall Assessment:</b> The platform demonstrates strong user engagement with "
        f"{total_sess:,} total sessions and a {users['retention_rate']}% retention rate. "
        f"However, the server error rate of {load['error_rate']:.1f}% and security score of "
        f"{security_score:.1f}/100 require immediate attention. Ad performance shows near-zero "
        f"click-through rate, suggesting campaign optimisation is urgently needed.",
        s["body"]
    ))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # 2. TRAFFIC ANALYSIS
    # ══════════════════════════════════════════════════════════════════════════
    _section_banner("2.  Traffic Intelligence Analysis", story, s, C_BLUE, W)

    story.append(Paragraph("<b>2.1 Overview</b>", s["subsection"]))
    story.append(Paragraph(
        f"The platform recorded <b>{total_sess:,} total page views</b> across the analysis period. "
        f"Traffic follows a predictable diurnal pattern, peaking at <b>{peak_hour}:00</b> with "
        f"<b>{int(peak_traffic):,} views</b> and reaching its lowest point at <b>{low_hour}:00</b> "
        f"({int(low_traffic):,} views) — a daily swing of <b>{int(peak_traffic-low_traffic):,} views "
        f"({round((peak_traffic-low_traffic)/low_traffic*100,1)}% variance)</b>. "
        f"The bounce rate of <b>{traffic['bounce_rate']}%</b> is below industry average (40%), "
        f"indicating strong content relevance.",
        s["body"]
    ))

    # Hourly traffic bar chart
    story.append(Paragraph("<b>2.2 Hourly Traffic Distribution</b>", s["subsection"]))
    hourly_sorted = sorted(hourly.items(), key=lambda x: int(x[0]))
    story.append(HBarChart(
        [(f"{h}:00", v) for h, v in hourly_sorted],
        width=int(W), bar_height=10, spacing=3, color=C_BLUE
    ))
    story.append(Paragraph("Chart 2.1 — Page Views by Hour of Day", s["caption"]))

    # Insights
    _insight_box(
        f"Peak traffic at {peak_hour}:00 suggests your audience is most active during "
        f"{'business hours' if 9 <= int(peak_hour) <= 18 else 'evening hours'}. "
        f"Schedule content releases, email campaigns, and ad pushes around this window to maximise reach.",
        story, s, bg=colors.HexColor("#eff6ff"), border=C_BLUE, icon="INSIGHT"
    )

    story.append(Paragraph("<b>2.3 Traffic Sources</b>", s["subsection"]))
    src_data = [["Source", "Sessions", "Share %", "Trend"]] + [
        [src, f"{int(v):,}", f"{round(int(v)/total_sess*100,1)}%",
         "Primary" if v == max(sources.values()) else "Secondary"]
        for src, v in top_src
    ]
    src_tbl = Table(src_data, colWidths=[W*0.3, W*0.22, W*0.18, W*0.3])
    src_tbl.setStyle(_tbl_style(C_BLUE))
    story.append(src_tbl)
    story.append(Paragraph("Table 2.1 — Traffic by Acquisition Source", s["caption"]))

    story.append(Paragraph("<b>2.4 Geographic Distribution</b>", s["subsection"]))
    geo_data = [["Country", "Sessions", "Share %", "Market Tier"]] + [
        [c, f"{int(v):,}", f"{round(int(v)/total_sess*100,1)}%",
         "Primary" if i == 0 else ("Growth" if i <= 2 else "Emerging")]
        for i, (c, v) in enumerate(top_geo)
    ]
    geo_tbl = Table(geo_data, colWidths=[W*0.28, W*0.22, W*0.18, W*0.32])
    geo_tbl.setStyle(_tbl_style(C_BLUE))
    story.append(geo_tbl)
    story.append(Paragraph("Table 2.2 — Top Countries by Session Volume", s["caption"]))

    _insight_box(
        f"India accounts for the majority of traffic. Consider localising content, "
        f"adding regional language support, and tailoring ad creatives for the Indian market "
        f"to improve conversion rates in this primary segment.",
        story, s, bg=colors.HexColor("#eff6ff"), border=C_BLUE, icon="RECOMMENDATION"
    )

    story.append(Paragraph("<b>2.5 What is Going Wrong &amp; How to Fix It</b>", s["subsection"]))
    issues_data = [
        ["Issue", "Impact", "Root Cause", "Recommended Action"],
        ["Single dominant channel (Search 40%)",
         "High dependency risk", "Underinvestment in other channels",
         "Diversify: increase social & referral campaigns"],
        ["Traffic spike at single hour",
         "Server stress at peak", "No load distribution strategy",
         "Implement CDN & auto-scaling rules"],
        ["Low Referral share (10%)",
         "Missing organic growth", "No affiliate/partner programme",
         "Launch referral incentive programme"],
    ]
    it = Table(issues_data, colWidths=[W*0.22, W*0.18, W*0.28, W*0.32])
    it.setStyle(_tbl_style(C_RED))
    story.append(it)
    story.append(Paragraph("Table 2.3 — Traffic Issues &amp; Remediation Plan", s["caption"]))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # 3. SERVER LOAD & PERFORMANCE
    # ══════════════════════════════════════════════════════════════════════════
    _section_banner("3.  Server Load &amp; Performance Analysis", story, s, C_ORANGE, W)

    story.append(Paragraph("<b>3.1 Infrastructure Overview</b>", s["subsection"]))
    story.append(Paragraph(
        f"The server processed <b>{load['total_requests']:,} total requests</b> with an average CPU "
        f"utilisation of <b>{load['avg_cpu_usage']}%</b>, memory usage of <b>{load['memory_usage']:.0f}%</b>, "
        f"and average response time of <b>{load['avg_response_time']:.0f} ms</b>. "
        f"The overall error rate is <b>{load['error_rate']:.2f}%</b> — "
        f"{'this is critically high and indicates serious issues with the server or application logic' if load['error_rate'] > 10 else 'this requires investigation'}.",
        s["body"]
    ))

    # Performance metrics table
    perf_data = [
        ["Metric", "Value", "Benchmark", "Status"],
        ["Total Requests",    f"{load['total_requests']:,}", "N/A",      "INFO"],
        ["Avg CPU Usage",     f"{load['avg_cpu_usage']}%",
         "< 70%", "CRITICAL" if load['avg_cpu_usage'] > 90 else ("WARN" if load['avg_cpu_usage'] > 70 else "OK")],
        ["Memory Usage",      f"{load['memory_usage']:.0f}%",
         "< 75%", "CRITICAL" if load['memory_usage'] > 90 else ("WARN" if load['memory_usage'] > 75 else "OK")],
        ["Avg Response Time", f"{load['avg_response_time']:.0f} ms",
         "< 200 ms", "OK" if load['avg_response_time'] < 200 else "WARN"],
        ["Error Rate",        f"{load['error_rate']:.2f}%",
         "< 1%", "CRITICAL" if load['error_rate'] > 5 else ("WARN" if load['error_rate'] > 1 else "OK")],
    ]
    pt = Table(perf_data, colWidths=[W*0.32, W*0.18, W*0.18, W*0.32])
    pt_style = _tbl_style(C_ORANGE)
    for i, row in enumerate(perf_data[1:], 1):
        if row[3] == "CRITICAL":
            pt_style.add("BACKGROUND", (3, i), (3, i), C_BAD)
            pt_style.add("TEXTCOLOR",  (3, i), (3, i), C_BAD_T)
        elif row[3] == "WARN":
            pt_style.add("BACKGROUND", (3, i), (3, i), C_WARN)
            pt_style.add("TEXTCOLOR",  (3, i), (3, i), C_WARN_T)
        elif row[3] == "OK":
            pt_style.add("BACKGROUND", (3, i), (3, i), C_GOOD)
            pt_style.add("TEXTCOLOR",  (3, i), (3, i), C_GOOD_T)
    pt.setStyle(pt_style)
    story.append(pt)
    story.append(Paragraph("Table 3.1 — Performance Metrics vs Industry Benchmarks", s["caption"]))

    story.append(Paragraph("<b>3.2 Top Endpoints by Request Volume</b>", s["subsection"]))
    story.append(HBarChart(
        top_eps[:6], width=int(W), bar_height=12, spacing=4, color=C_ORANGE
    ))
    story.append(Paragraph("Chart 3.1 — Top 6 Most-Hit Endpoints", s["caption"]))

    ep_data = [["Endpoint", "Requests", "% of Total", "Avg Response (ms)"]] + [
        [ep, f"{int(h):,}", f"{round(int(h)/load['total_requests']*100,1)}%",
         f"{load.get('avg_response_by_endpoint', {}).get(ep, 0):.0f}"]
        for ep, h in top_eps
    ]
    et = Table(ep_data, colWidths=[W*0.38, W*0.18, W*0.18, W*0.26])
    et.setStyle(_tbl_style(C_ORANGE))
    story.append(et)
    story.append(Paragraph("Table 3.2 — Endpoint Performance Detail", s["caption"]))

    _insight_box(
        f"CPU and memory utilisation at {load['avg_cpu_usage']}% and {load['memory_usage']:.0f}% "
        f"respectively are critically high. The server is operating at near-capacity. "
        f"Without scaling, any traffic spike will cause service outages.",
        story, s, bg=colors.HexColor("#fff7ed"), border=C_ORANGE, icon="WARNING"
    )

    story.append(Paragraph("<b>3.3 Issues, Root Causes &amp; Fixes</b>", s["subsection"]))
    load_issues = [
        ["Issue", "Root Cause", "Immediate Fix", "Long-term Solution"],
        [f"Error rate {load['error_rate']:.1f}%",
         "Application errors / bad routes",
         "Review error logs, fix top 5 failing endpoints",
         "Implement circuit breakers & retry logic"],
        ["CPU at 95%",
         "No caching, all requests hit DB",
         "Add Redis caching for frequent queries",
         "Upgrade server tier or auto-scale"],
        ["Memory at 95%",
         "Memory leaks or large payload loading",
         "Profile application memory usage",
         "Implement pagination & lazy loading"],
        ["High /usr/login traffic",
         "Brute-force or bot traffic",
         "Add CAPTCHA & rate limiting",
         "Implement WAF & DDoS protection"],
    ]
    lit = Table(load_issues, colWidths=[W*0.18, W*0.22, W*0.28, W*0.32])
    lit.setStyle(_tbl_style(C_RED))
    story.append(lit)
    story.append(Paragraph("Table 3.3 — Load Issues &amp; Remediation Plan", s["caption"]))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # 4. USER BEHAVIOUR & RETENTION
    # ══════════════════════════════════════════════════════════════════════════
    _section_banner("4.  User Behaviour &amp; Retention Analysis", story, s, C_PURPLE, W)

    story.append(Paragraph("<b>4.1 Customer Overview</b>", s["subsection"]))
    story.append(Paragraph(
        f"The platform processed <b>{users['total_orders']:,} orders</b> with an average order value "
        f"of <b>${users['avg_order_value']}</b> and a customer satisfaction rating of "
        f"<b>{users['avg_rating']}/5.0</b>. Customer retention is exceptionally strong at "
        f"<b>{users['retention_rate']}%</b> — well above the e-commerce industry benchmark of 30-40%. "
        f"The platform has <b>{repeat_users:,} repeat buyers</b> vs only "
        f"<b>{onetime_users:,} one-time buyers</b>.",
        s["body"]
    ))

    # Buyer composition
    story.append(Paragraph("<b>4.2 Buyer Composition</b>", s["subsection"]))
    buyer_data = [
        ["Buyer Type", "Count", "Share %", "Avg Orders", "Business Value"],
        ["Repeat Buyers",  f"{repeat_users:,}",  f"{round(repeat_users/(repeat_users+onetime_users)*100,1)}%",
         "2+", "HIGH — Core revenue base"],
        ["One-time Buyers",f"{onetime_users:,}", f"{round(onetime_users/(repeat_users+onetime_users)*100,1)}%",
         "1",  "MEDIUM — Conversion opportunity"],
    ]
    bt = Table(buyer_data, colWidths=[W*0.22, W*0.14, W*0.14, W*0.16, W*0.34])
    bt.setStyle(_tbl_style(C_PURPLE))
    story.append(bt)
    story.append(Paragraph("Table 4.1 — Customer Segmentation by Purchase Behaviour", s["caption"]))

    story.append(Paragraph("<b>4.3 Revenue by Product Category</b>", s["subsection"]))
    story.append(HBarChart(
        top_cat[:6], width=int(W), bar_height=12, spacing=4, color=C_PURPLE
    ))
    story.append(Paragraph("Chart 4.1 — Revenue by Product Category", s["caption"]))

    cat_data = [["Category", "Revenue", "Share %", "Opportunity"]] + [
        [cat, f"${int(rev):,}",
         f"{round(int(rev)/sum(v for _,v in top_cat)*100,1)}%",
         "Scale" if i == 0 else ("Grow" if i <= 2 else "Niche")]
        for i, (cat, rev) in enumerate(top_cat)
    ]
    ct = Table(cat_data, colWidths=[W*0.28, W*0.22, W*0.18, W*0.32])
    ct.setStyle(_tbl_style(C_PURPLE))
    story.append(ct)
    story.append(Paragraph("Table 4.2 — Revenue by Product Category", s["caption"]))

    story.append(Paragraph("<b>4.4 Customer Conversion Funnel</b>", s["subsection"]))
    journey_vals = list(journey.values())
    journey_keys = list(journey.keys())
    funnel_data = [["Stage", "Users", "Conversion %", "Drop-off %", "Action Required"]] + [
        [stage,
         f"{int(cnt):,}",
         f"{round(cnt/journey_vals[0]*100,1)}%",
         f"{round((1-cnt/journey_vals[i-1 if i > 0 else 0])*100,1)}%" if i > 0 else "—",
         "Optimise UX" if round((1-(cnt/journey_vals[i-1 if i>0 else 0]))*100,1) > 40 and i > 0 else "Monitor"]
        for i, (stage, cnt) in enumerate(journey.items())
    ]
    ft = Table(funnel_data, colWidths=[W*0.22, W*0.16, W*0.16, W*0.16, W*0.30])
    ft.setStyle(_tbl_style(C_PURPLE))
    story.append(ft)
    story.append(Paragraph("Table 4.3 — Customer Conversion Funnel Analysis", s["caption"]))

    _insight_box(
        f"The largest drop-off occurs between 'Visited' and 'Viewed Product' (30%). "
        f"Improving homepage personalisation, featured product placement, and search relevance "
        f"could recover significant revenue.",
        story, s, bg=colors.HexColor("#faf5ff"), border=C_PURPLE, icon="INSIGHT"
    )

    # Age segments
    if segments:
        story.append(Paragraph("<b>4.5 Revenue by Age Segment</b>", s["subsection"]))
        seg_sorted = sorted(segments.items(), key=lambda x: x[1], reverse=True)
        seg_data = [["Age Group", "Revenue", "Share %", "Marketing Priority"]] + [
            [seg, f"${int(rev):,}", f"{round(rev/sum(segments.values())*100,1)}%",
             "Primary" if i == 0 else ("Secondary" if i == 1 else "Tertiary")]
            for i, (seg, rev) in enumerate(seg_sorted)
        ]
        st2 = Table(seg_data, colWidths=[W*0.2, W*0.22, W*0.18, W*0.40])
        st2.setStyle(_tbl_style(C_PURPLE))
        story.append(st2)
        story.append(Paragraph("Table 4.4 — Revenue by Customer Age Group", s["caption"]))

    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # 5. AD PERFORMANCE
    # ══════════════════════════════════════════════════════════════════════════
    _section_banner("5.  Advertisement Performance Analysis", story, s, C_PINK, W)

    story.append(Paragraph("<b>5.1 Campaign Overview</b>", s["subsection"]))
    story.append(Paragraph(
        f"Ad campaigns delivered <b>{total_impr:,} impressions</b> with a CTR of <b>{ctr}%</b>, "
        f"CPC of <b>${cpc}</b>, and ROAS of <b>{roas}x</b>. "
        f"<b>The CTR of {ctr}% is critically below the industry benchmark of 2-3%.</b> "
        f"This indicates a fundamental issue with ad creative quality, audience targeting, or "
        f"placement strategy that requires immediate corrective action.",
        s["body"]
    ))

    # Ad metrics benchmark
    ad_bench = [
        ["KPI", "Current Value", "Industry Benchmark", "Gap", "Priority"],
        ["CTR",             f"{ctr}%",     "2.0%",    f"{round(2.0-ctr,2)}%",    "CRITICAL"],
        ["CPC",             f"${cpc}",     "$0.50-2.00", "Within range",           "OK"],
        ["ROAS",            f"{roas}x",    "4x+",     "Above benchmark",           "GOOD"],
        ["Conversion Rate", f"{conv_rate}%","2-3%",   f"{round(2-conv_rate,1)}%", "HIGH"],
        ["Total Clicks",    f"{total_clicks:,}", "2,577+", f"{max(0,2577-total_clicks):,} short", "CRITICAL"],
    ]
    abt = Table(ad_bench, colWidths=[W*0.20, W*0.18, W*0.18, W*0.20, W*0.24])
    ab_style = _tbl_style(C_PINK)
    for i, row in enumerate(ad_bench[1:], 1):
        if row[4] == "CRITICAL":
            ab_style.add("BACKGROUND", (4, i), (4, i), C_BAD)
            ab_style.add("TEXTCOLOR",  (4, i), (4, i), C_BAD_T)
            ab_style.add("FONTNAME",   (4, i), (4, i), "Helvetica-Bold")
        elif row[4] == "HIGH":
            ab_style.add("BACKGROUND", (4, i), (4, i), C_WARN)
            ab_style.add("TEXTCOLOR",  (4, i), (4, i), C_WARN_T)
        elif row[4] == "GOOD":
            ab_style.add("BACKGROUND", (4, i), (4, i), C_GOOD)
            ab_style.add("TEXTCOLOR",  (4, i), (4, i), C_GOOD_T)
    abt.setStyle(ab_style)
    story.append(abt)
    story.append(Paragraph("Table 5.1 — Ad Performance vs Industry Benchmarks", s["caption"]))

    story.append(Paragraph("<b>5.2 Ad Format Distribution</b>", s["subsection"]))
    fmt_data = [["Format", "Impressions", "Share %", "Est. Clicks", "Recommendation"]] + [
        [fmt, f"{int(imp):,}", f"{round(imp/total_impr*100,1)}%",
         f"{int(imp*ctr/100):,}", "Scale" if fmt == "Video" else "Maintain"]
        for fmt, imp in ad_formats.items()
    ]
    fmtt = Table(fmt_data, colWidths=[W*0.18, W*0.18, W*0.14, W*0.16, W*0.34])
    fmtt.setStyle(_tbl_style(C_PINK))
    story.append(fmtt)
    story.append(Paragraph("Table 5.2 — Ad Format Performance Breakdown", s["caption"]))

    story.append(Paragraph("<b>5.3 Conversion Funnel Analysis</b>", s["subsection"]))
    funnel_steps = [
        ("Impressions", funnel.get("impressions", 0)),
        ("Clicks",      funnel.get("clicks", 0)),
        ("Landing",     funnel.get("landing", 0)),
        ("Add to Cart", funnel.get("add_to_cart", 0)),
        ("Checkout",    funnel.get("checkout", 0)),
        ("Purchase",    funnel.get("purchase", 0)),
    ]
    conv_data = [["Stage", "Users", "Conversion %", "Drop-off"]] + [
        [step, f"{int(val):,}",
         f"{round(val/funnel_steps[0][1]*100,2)}%" if funnel_steps[0][1] else "0%",
         f"-{round((1-val/funnel_steps[i-1][1])*100,1)}%" if i > 0 and funnel_steps[i-1][1] else "—"]
        for i, (step, val) in enumerate(funnel_steps)
    ]
    cvt = Table(conv_data, colWidths=[W*0.25, W*0.20, W*0.20, W*0.35])
    cvt.setStyle(_tbl_style(C_PINK))
    story.append(cvt)
    story.append(Paragraph("Table 5.3 — Ad Conversion Funnel Detail", s["caption"]))

    _insight_box(
        "CRITICAL: Near-zero CTR indicates the ad creative is not resonating with the target audience. "
        "Immediate A/B testing of ad copy and visuals is required. "
        "Consider pausing underperforming campaigns and reallocating budget to Video format "
        "which historically delivers 2-3x higher engagement than banner ads.",
        story, s, bg=colors.HexColor("#fff1f2"), border=C_RED, icon="ACTION REQUIRED"
    )

    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # 6. SECURITY ANALYSIS
    # ══════════════════════════════════════════════════════════════════════════
    _section_banner("6.  Security &amp; Threat Analysis", story, s, C_RED, W)

    story.append(Paragraph("<b>6.1 Security Posture Overview</b>", s["subsection"]))
    sec_rating = "CRITICAL" if security_score < 50 else ("MODERATE" if security_score < 70 else "GOOD")
    story.append(Paragraph(
        f"The platform security score is <b>{security_score:.1f}/100</b> — rated <b>{sec_rating}</b>. "
        f"The firewall is <b>{firewall_status}</b> and has blocked <b>{threats_blocked:,} threats</b>. "
        f"<b>{critical_alerts} critical alert(s)</b> are currently active. "
        f"The high error rate ({load['error_rate']:.1f}%) is partly attributed to security-related "
        f"rejections and bot traffic hitting protected endpoints.",
        s["body"]
    ))

    # Security metrics
    sec_metrics = [
        ["Security KPI", "Value", "Risk Level", "Description"],
        ["Security Score",     f"{security_score:.1f}/100",
         "CRITICAL" if security_score < 50 else "MODERATE",
         "Overall platform security health"],
        ["Threats Blocked",    f"{threats_blocked:,}", "INFO",
         "Total blocked malicious requests"],
        ["Critical Alerts",    str(critical_alerts),
         "HIGH" if critical_alerts > 0 else "OK",
         "Active unresolved security alerts"],
        ["4xx Client Errors",  f"{errors_4xx:,}",
         "HIGH" if errors_4xx > 10000 else "MODERATE",
         "Unauthorised / not-found requests"],
        ["5xx Server Errors",  f"{errors_5xx:,}",
         "CRITICAL" if errors_5xx > 10000 else "HIGH",
         "Server-side failures"],
        ["Suspicious IPs",     str(susp_ips),
         "HIGH" if susp_ips > 0 else "OK",
         "IPs with >100 requests"],
        ["Failed Logins",      str(failed_logins),
         "HIGH" if failed_logins > 10 else "OK",
         "Potential brute-force attempts"],
    ]
    smt = Table(sec_metrics, colWidths=[W*0.24, W*0.16, W*0.16, W*0.44])
    sm_style = _tbl_style(C_RED)
    for i, row in enumerate(sec_metrics[1:], 1):
        if row[2] == "CRITICAL":
            sm_style.add("BACKGROUND", (2, i), (2, i), C_BAD)
            sm_style.add("TEXTCOLOR",  (2, i), (2, i), C_BAD_T)
            sm_style.add("FONTNAME",   (2, i), (2, i), "Helvetica-Bold")
        elif row[2] in ("HIGH", "MODERATE"):
            sm_style.add("BACKGROUND", (2, i), (2, i), C_WARN)
            sm_style.add("TEXTCOLOR",  (2, i), (2, i), C_WARN_T)
        elif row[2] == "OK":
            sm_style.add("BACKGROUND", (2, i), (2, i), C_GOOD)
            sm_style.add("TEXTCOLOR",  (2, i), (2, i), C_GOOD_T)
    smt.setStyle(sm_style)
    story.append(smt)
    story.append(Paragraph("Table 6.1 — Security KPI Assessment", s["caption"]))

    story.append(Paragraph("<b>6.2 Security Activity Log</b>", s["subsection"]))
    act_data = [["Threat Type", "Count", "Severity", "Status", "Action Required"]] + [
        [x["name"], str(x["count"]), x["level"],
         "ACTIVE" if x["count"] > 0 else "CLEAR",
         "Investigate immediately" if x["level"] == "Critical" else
         ("Monitor closely" if x["level"] == "High" else "Log & review weekly")]
        for x in activity_log
    ]
    att = Table(act_data, colWidths=[W*0.26, W*0.10, W*0.14, W*0.12, W*0.38])
    at_style = _tbl_style(C_RED)
    for i, row in enumerate(act_data[1:], 1):
        if row[2] == "Critical":
            at_style.add("BACKGROUND", (0, i), (-1, i), C_BAD)
        elif row[2] == "High":
            at_style.add("BACKGROUND", (0, i), (-1, i), C_WARN)
    att.setStyle(at_style)
    story.append(att)
    story.append(Paragraph("Table 6.2 — Security Activity Log with Severity", s["caption"]))

    if susp_ip_list:
        story.append(Paragraph("<b>6.3 Flagged IP Addresses</b>", s["subsection"]))
        story.append(HBarChart(
            susp_ip_list, width=int(W), bar_height=12, spacing=4, color=C_RED
        ))
        susp_data = [["Flagged IP Address", "Request Count", "Risk Level", "Recommended Action"]] + [
            [ip, f"{int(cnt):,}",
             "CRITICAL" if cnt > 200 else "HIGH",
             "Block immediately" if cnt > 200 else "Rate limit & monitor"]
            for ip, cnt in susp_ip_list
        ]
        susp_t = Table(susp_data, colWidths=[W*0.28, W*0.18, W*0.18, W*0.36])
        st_style = _tbl_style(C_RED)
        for i in range(1, len(susp_data)):
            if "CRITICAL" in susp_data[i][2]:
                st_style.add("BACKGROUND", (0, i), (-1, i), C_BAD)
        susp_t.setStyle(st_style)
        story.append(susp_t)
        story.append(Paragraph("Table 6.3 — Top Flagged IPs &amp; Remediation", s["caption"]))

    _insight_box(
        f"IMMEDIATE ACTION: {errors_5xx:,} server-side errors represent a serious reliability risk. "
        f"Combined with a security score of {security_score:.1f}/100, the platform is vulnerable. "
        f"Prioritise: (1) Block flagged IPs via firewall rules, "
        f"(2) Fix top 5 error-generating endpoints, "
        f"(3) Enable real-time alerting for anomalous login attempts.",
        story, s, bg=colors.HexColor("#fff1f2"), border=C_RED, icon="CRITICAL ACTION"
    )

    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # 7. KEY FINDINGS & RECOMMENDATIONS
    # ══════════════════════════════════════════════════════════════════════════
    _section_banner("7.  Key Findings &amp; Business Recommendations", story, s, C_DARK, W)

    story.append(Paragraph("<b>7.1 Priority Action Matrix</b>", s["subsection"]))
    priority_data = [
        ["Priority", "Area", "Finding", "Recommended Action", "Timeline"],
        ["P1 — CRITICAL", "Security",     f"Score {security_score:.0f}/100, {errors_5xx:,} server errors",
         "Patch server vulnerabilities, block flagged IPs", "This week"],
        ["P1 — CRITICAL", "Ad Performance",f"CTR {ctr}% vs 2% benchmark",
         "A/B test creatives, review audience targeting", "This week"],
        ["P2 — HIGH",     "Infrastructure","CPU/Memory at 95%",
         "Add Redis caching, upgrade server tier", "This month"],
        ["P2 — HIGH",     "Traffic",       "90% from 2 sources only",
         "Invest in social & referral channels", "This month"],
        ["P3 — MEDIUM",   "Conversion",    "30% drop: visit to product view",
         "Improve homepage UX & product discovery", "Next quarter"],
        ["P3 — MEDIUM",   "User Behaviour","1,685 one-time buyers",
         "Launch re-engagement email campaigns", "Next quarter"],
        ["P4 — LOW",      "Traffic",       "Low Referral share (10%)",
         "Create partner & affiliate programme", "6 months"],
    ]
    pmt = Table(priority_data, colWidths=[W*0.16, W*0.14, W*0.28, W*0.28, W*0.14])
    pm_style = _tbl_style(C_DARK)
    for i, row in enumerate(priority_data[1:], 1):
        if "P1" in row[0]:
            pm_style.add("BACKGROUND", (0, i), (0, i), C_BAD)
            pm_style.add("TEXTCOLOR",  (0, i), (0, i), C_BAD_T)
            pm_style.add("FONTNAME",   (0, i), (0, i), "Helvetica-Bold")
        elif "P2" in row[0]:
            pm_style.add("BACKGROUND", (0, i), (0, i), C_WARN)
            pm_style.add("TEXTCOLOR",  (0, i), (0, i), C_WARN_T)
        elif "P3" in row[0]:
            pm_style.add("BACKGROUND", (0, i), (0, i), C_GOOD)
            pm_style.add("TEXTCOLOR",  (0, i), (0, i), C_GOOD_T)
    pmt.setStyle(pm_style)
    story.append(pmt)
    story.append(Paragraph("Table 7.1 — Prioritised Action Matrix", s["caption"]))

    story.append(Paragraph("<b>7.2 Strengths to Leverage</b>", s["subsection"]))
    strengths = [
        f"Exceptional customer retention at {users['retention_rate']}% — well above industry average",
        f"High average order value of ${users['avg_order_value']} indicates premium customer base",
        f"Strong ROAS of {roas}x means advertising spend is generating good returns when users do engage",
        f"Customer rating of {users['avg_rating']}/5.0 reflects high product/service satisfaction",
        f"Consistent traffic patterns enable predictable capacity planning",
    ]
    for s_item in strengths:
        _insight_box(s_item, story, s,
                     bg=C_GOOD, border=C_GREEN, icon="STRENGTH")

    story.append(Paragraph("<b>7.3 Critical Weaknesses to Address</b>", s["subsection"]))
    weaknesses = [
        f"Security score of {security_score:.0f}/100 puts the platform at significant risk of breach",
        f"Server error rate of {load['error_rate']:.1f}% is unacceptably high — users are experiencing failures",
        f"Ad CTR of {ctr}% means advertising budget is largely wasted — immediate creative overhaul needed",
        f"CPU/Memory at 95% means the platform is one traffic spike away from complete outage",
    ]
    for w_item in weaknesses:
        _insight_box(w_item, story, s,
                     bg=C_BAD, border=C_RED, icon="WEAKNESS")

    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # APPENDIX
    # ══════════════════════════════════════════════════════════════════════════
    _section_banner("Appendix — Full Key Performance Indicators", story, s, C_SLATE, W)

    kpi_full = [
        ["Category", "Metric", "Value", "Benchmark", "Status"],
        ["Traffic", "Total Sessions",      f"{total_sess:,}",                    "N/A",    "INFO"],
        ["Traffic", "Avg Session Duration",f"{traffic['avg_session_duration']}s","90-180s","OK"],
        ["Traffic", "Pages per Session",   str(traffic['pages_per_session']),    "3-5",    "OK"],
        ["Traffic", "Bounce Rate",         f"{traffic['bounce_rate']}%",         "< 40%",  "GOOD"],
        ["Traffic", "Peak Hour",           f"{peak_hour}:00 ({int(peak_traffic):,} views)", "N/A", "INFO"],
        ["Server",  "Total Requests",      f"{load['total_requests']:,}",         "N/A",    "INFO"],
        ["Server",  "Avg CPU Usage",       f"{load['avg_cpu_usage']}%",           "< 70%",  "CRITICAL"],
        ["Server",  "Memory Usage",        f"{load['memory_usage']:.1f}%",        "< 75%",  "CRITICAL"],
        ["Server",  "Avg Response Time",   f"{load['avg_response_time']:.0f} ms", "< 200ms","OK"],
        ["Server",  "Error Rate",          f"{load['error_rate']:.2f}%",          "< 1%",   "CRITICAL"],
        ["Users",   "Total Orders",        f"{users['total_orders']:,}",           "N/A",    "INFO"],
        ["Users",   "Avg Order Value",     f"${users['avg_order_value']}",         "N/A",    "INFO"],
        ["Users",   "Retention Rate",      f"{users['retention_rate']}%",          "> 30%",  "GOOD"],
        ["Users",   "Avg Customer Rating", f"{users['avg_rating']}/5.0",           "> 4.0",  "GOOD"],
        ["Users",   "Repeat Buyers",       f"{repeat_users:,}",                    "N/A",    "INFO"],
        ["Users",   "One-time Buyers",     f"{onetime_users:,}",                   "N/A",    "INFO"],
        ["Ads",     "Total Impressions",   f"{total_impr:,}",                      "N/A",    "INFO"],
        ["Ads",     "Total Clicks",        f"{total_clicks:,}",                    "N/A",    "INFO"],
        ["Ads",     "CTR",                 f"{ctr}%",                              "> 2%",   "CRITICAL"],
        ["Ads",     "CPC",                 f"${cpc}",                              "$0.5-2", "OK"],
        ["Ads",     "ROAS",                f"{roas}x",                             "> 4x",   "GOOD"],
        ["Ads",     "Conversion Rate",     f"{conv_rate}%",                        "2-3%",   "HIGH"],
        ["Security","Security Score",      f"{security_score:.1f}/100",            "> 70",   "CRITICAL"],
        ["Security","Threats Blocked",     f"{threats_blocked:,}",                 "N/A",    "INFO"],
        ["Security","Critical Alerts",     str(critical_alerts),                   "0",      "HIGH" if critical_alerts > 0 else "OK"],
        ["Security","4xx Client Errors",   f"{errors_4xx:,}",                      "< 1%",   "HIGH"],
        ["Security","5xx Server Errors",   f"{errors_5xx:,}",                      "< 0.1%", "CRITICAL"],
        ["Security","Suspicious IPs",      str(susp_ips),                          "0",      "HIGH" if susp_ips > 0 else "OK"],
        ["Security","Failed Logins",       str(failed_logins),                     "< 5",    "HIGH" if failed_logins > 5 else "OK"],
        ["Security","Firewall Status",     firewall_status,                        "Active", "GOOD" if firewall_status == "Active" else "CRITICAL"],
    ]

    app_t = Table(kpi_full, colWidths=[W*0.12, W*0.28, W*0.18, W*0.16, W*0.26])
    app_style = _tbl_style(C_SLATE)
    for i, row in enumerate(kpi_full[1:], 1):
        if len(row) >= 5:
            if row[4] == "CRITICAL":
                app_style.add("BACKGROUND", (4, i), (4, i), C_BAD)
                app_style.add("TEXTCOLOR",  (4, i), (4, i), C_BAD_T)
                app_style.add("FONTNAME",   (4, i), (4, i), "Helvetica-Bold")
            elif row[4] in ("HIGH", "MODERATE"):
                app_style.add("BACKGROUND", (4, i), (4, i), C_WARN)
                app_style.add("TEXTCOLOR",  (4, i), (4, i), C_WARN_T)
            elif row[4] == "GOOD":
                app_style.add("BACKGROUND", (4, i), (4, i), C_GOOD)
                app_style.add("TEXTCOLOR",  (4, i), (4, i), C_GOOD_T)
    app_t.setStyle(app_style)
    story.append(app_t)
    story.append(Paragraph("Table A.1 — Comprehensive KPI Reference with Benchmarks", s["caption"]))

    story.append(Spacer(1, 0.8*cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=C_BORDER))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        f"TrafficIQ Analytics Platform  |  MediCaps University  |  "
        f"Report generated {date_str} at {time_str}  |  CONFIDENTIAL",
        s["footer_txt"]
    ))

    doc.build(story)
    return output_path