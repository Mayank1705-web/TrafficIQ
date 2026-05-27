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

from traffic_analysis       import run_analysis as _traffic
from load_analysis          import run_analysis as _load
from user_behavior_analysis import run_analysis as _users
from ad_analytics           import run_analysis as _ads
from security_logs          import run_analysis as _security

# Palette
C_PURPLE = colors.HexColor("#7c3aed")
C_BLUE   = colors.HexColor("#2563eb")
C_TEAL   = colors.HexColor("#0d9488")
C_ORANGE = colors.HexColor("#d97706")
C_RED    = colors.HexColor("#dc2626")
C_PINK   = colors.HexColor("#db2777")
C_DARK   = colors.HexColor("#0f172a")
C_NAVY   = colors.HexColor("#1e293b")
C_SLATE  = colors.HexColor("#334155")
C_MUTED  = colors.HexColor("#64748b")
C_LIGHT  = colors.HexColor("#f8fafc")
C_WHITE  = colors.white
C_BORDER = colors.HexColor("#e2e8f0")
C_ALT    = colors.HexColor("#f1f5f9")
C_GREEN  = colors.HexColor("#16a34a")
C_GOOD   = colors.HexColor("#dcfce7")
C_WARN   = colors.HexColor("#fef9c3")
C_BAD    = colors.HexColor("#fee2e2")
C_GOOD_T = colors.HexColor("#166534")
C_WARN_T = colors.HexColor("#854d0e")
C_BAD_T  = colors.HexColor("#991b1b")


# ── Horizontal bar chart ──────────────────────────────────────────────────────
class HBarChart(Flowable):
    def __init__(self, data, width=440, bar_height=14, spacing=5, color=C_BLUE):
        Flowable.__init__(self)
        self.data    = data
        self.width   = width
        self.bar_h   = bar_height
        self.spacing = spacing
        self.color   = color
        self.height  = (bar_height + spacing) * len(data) + 16

    def draw(self):
        c = self.canv
        if not self.data:
            return
        max_val  = max(v for _, v in self.data) or 1
        label_w  = self.width * 0.30
        bar_area = self.width * 0.54
        y = self.height - self.bar_h - 6
        for label, value in self.data:
            c.setFont("Helvetica", 8)
            c.setFillColor(C_NAVY)
            c.drawRightString(label_w - 5, y + 3, str(label)[:28])
            c.setFillColor(colors.HexColor("#e2e8f0"))
            c.roundRect(label_w, y, bar_area, self.bar_h, 3, fill=1, stroke=0)
            fill_w = max(6, bar_area * (value / max_val))
            c.setFillColor(self.color)
            c.roundRect(label_w, y, fill_w, self.bar_h, 3, fill=1, stroke=0)
            c.setFont("Helvetica-Bold", 8)
            c.setFillColor(C_MUTED)
            c.drawString(label_w + bar_area + 5, y + 3, f"{int(value):,}")
            y -= (self.bar_h + self.spacing)


# ── Cover page drawn with canvas ──────────────────────────────────────────────
class CoverPage(Flowable):
    def __init__(self, date_str, time_str, kpis, W, H):
        Flowable.__init__(self)
        self.date_str = date_str
        self.time_str = time_str
        self.kpis     = kpis
        self.width    = W
        self.height   = H

    def draw(self):
        c   = self.canv
        W   = self.width
        H   = self.height

        # ── Full dark background ──────────────────────────────────────────
        c.setFillColor(C_DARK)
        c.roundRect(0, 0, W, H, 10, fill=1, stroke=0)

        # ── Accent stripe ────────────────────────────────────────────────
        c.setFillColor(C_PURPLE)
        c.rect(0, H - 6, W, 6, fill=1, stroke=0)

        # ── Logo area ────────────────────────────────────────────────────
        logo_y = H - 80
        c.setFillColor(C_PURPLE)
        c.roundRect(W/2 - 28, logo_y, 56, 56, 10, fill=1, stroke=0)
        c.setFillColor(C_WHITE)
        c.setFont("Helvetica-Bold", 22)
        c.drawCentredString(W/2, logo_y + 16, "IQ")

        # ── Title ────────────────────────────────────────────────────────
        c.setFillColor(C_WHITE)
        c.setFont("Helvetica-Bold", 34)
        c.drawCentredString(W/2, logo_y - 42, "TrafficIQ")

        c.setFillColor(colors.HexColor("#94a3b8"))
        c.setFont("Helvetica", 15)
        c.drawCentredString(W/2, logo_y - 66, "Business Intelligence Report")

        c.setFont("Helvetica", 11)
        c.drawCentredString(W/2, logo_y - 86, "Executive Analytics & Platform Summary")

        # ── Divider ──────────────────────────────────────────────────────
        c.setStrokeColor(colors.HexColor("#334155"))
        c.setLineWidth(1)
        c.line(W * 0.2, logo_y - 104, W * 0.8, logo_y - 104)

        # ── Date & institute ─────────────────────────────────────────────
        c.setFillColor(colors.HexColor("#64748b"))
        c.setFont("Helvetica", 10)
        c.drawCentredString(W/2, logo_y - 120, f"Generated: {self.date_str}  |  {self.time_str}")
        c.drawCentredString(W/2, logo_y - 136, "MediCaps University  |  TrafficIQ Analytics Platform")

        # ── Confidential badge ────────────────────────────────────────────
        badge_y = logo_y - 160
        c.setFillColor(colors.HexColor("#7f1d1d"))
        c.roundRect(W/2 - 100, badge_y - 6, 200, 22, 6, fill=1, stroke=0)
        c.setFillColor(colors.HexColor("#fca5a5"))
        c.setFont("Helvetica-Bold", 9)
        c.drawCentredString(W/2, badge_y + 3, "CONFIDENTIAL — FOR INTERNAL USE ONLY")

        # ── KPI Grid (2 rows x 4 cols) ────────────────────────────────────
        kpi_start_y = badge_y - 30
        cols = 4
        cell_w = W / cols
        cell_h = 58

        for idx, (label, value, color) in enumerate(self.kpis):
            row = idx // cols
            col = idx % cols
            cx  = col * cell_w
            cy  = kpi_start_y - row * (cell_h + 6)

            # Cell background
            bg = colors.HexColor("#1e293b") if idx % 2 == 0 else colors.HexColor("#162032")
            c.setFillColor(bg)
            c.roundRect(cx + 3, cy - cell_h + 4, cell_w - 6, cell_h, 6, fill=1, stroke=0)

            # Top accent line
            c.setFillColor(color)
            c.roundRect(cx + 3, cy - cell_h + 4 + cell_h - 4, cell_w - 6, 4, 3, fill=1, stroke=0)

            # Value
            c.setFillColor(color)
            c.setFont("Helvetica-Bold", 16)
            c.drawCentredString(cx + cell_w/2, cy - cell_h + 30, str(value))

            # Label
            c.setFillColor(colors.HexColor("#94a3b8"))
            c.setFont("Helvetica", 8)
            c.drawCentredString(cx + cell_w/2, cy - cell_h + 14, label)


def _styles():
    base = getSampleStyleSheet()
    def ps(name, **kw):
        return ParagraphStyle(name=name, parent=base["Normal"], **kw)
    return {
        "section":    ps("Section",   fontSize=13, textColor=C_WHITE,
                         fontName="Helvetica-Bold", spaceBefore=10, spaceAfter=4),
        "subsec":     ps("SubSec",    fontSize=11, textColor=C_NAVY,
                         fontName="Helvetica-Bold", spaceBefore=10, spaceAfter=4),
        "body":       ps("Body",      fontSize=9.5, textColor=C_SLATE,
                         leading=15, spaceAfter=7, alignment=TA_JUSTIFY),
        "caption":    ps("Caption",   fontSize=7.5, textColor=C_MUTED,
                         spaceAfter=10, spaceBefore=2, alignment=TA_CENTER),
        "toc_h":      ps("TocH",      fontSize=11, textColor=C_NAVY,
                         fontName="Helvetica-Bold"),
        "toc_e":      ps("TocE",      fontSize=10, textColor=C_SLATE, leading=20, leftIndent=10),
        "insight":    ps("Insight",   fontSize=9, textColor=C_NAVY,
                         leading=14, spaceAfter=3),
        "footer":     ps("Footer",    fontSize=7.5, textColor=C_MUTED, alignment=TA_CENTER),
    }


def _tbl(hdr_color=C_PURPLE):
    return TableStyle([
        ("BACKGROUND",     (0,0), (-1, 0), hdr_color),
        ("TEXTCOLOR",      (0,0), (-1, 0), C_WHITE),
        ("FONTNAME",       (0,0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",       (0,0), (-1,-1), 8.5),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [C_WHITE, C_ALT]),
        ("ALIGN",          (0,0), (-1,-1), "LEFT"),
        ("VALIGN",         (0,0), (-1,-1), "MIDDLE"),
        ("LEFTPADDING",    (0,0), (-1,-1), 7),
        ("RIGHTPADDING",   (0,0), (-1,-1), 7),
        ("TOPPADDING",     (0,0), (-1,-1), 5),
        ("BOTTOMPADDING",  (0,0), (-1,-1), 5),
        ("GRID",           (0,0), (-1,-1), 0.3, C_BORDER),
    ])


def _banner(title, story, s, color, W):
    t = Table([[Paragraph(title, s["section"])]], colWidths=[W])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), color),
        ("TOPPADDING",    (0,0), (-1,-1), 9),
        ("BOTTOMPADDING", (0,0), (-1,-1), 9),
        ("LEFTPADDING",   (0,0), (-1,-1), 14),
        ("ROUNDEDCORNERS",[6]),
    ]))
    story.append(Spacer(1, 0.2*cm))
    story.append(t)
    story.append(Spacer(1, 0.2*cm))


def _callout(text, story, s, bg, border, icon=""):
    label = f"<b>{icon}</b>  {text}" if icon else text
    t = Table([[Paragraph(label, s["insight"])]], colWidths=[A4[0]-4*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",  (0,0), (-1,-1), bg),
        ("LINEAFTER",   (0,0), (0,-1),  3, border),
        ("TOPPADDING",  (0,0), (-1,-1), 7),
        ("BOTTOMPADDING",(0,0),(-1,-1), 7),
        ("LEFTPADDING", (0,0), (-1,-1), 10),
        ("RIGHTPADDING",(0,0), (-1,-1), 10),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.1*cm))


def _color_cell(text, status):
    bg = {"CRITICAL": C_BAD, "HIGH": C_WARN, "GOOD": C_GOOD, "OK": C_GOOD}.get(status, C_LIGHT)
    tc = {"CRITICAL": C_BAD_T, "HIGH": C_WARN_T, "GOOD": C_GOOD_T, "OK": C_GOOD_T}.get(status, C_MUTED)
    fn = "Helvetica-Bold" if status in ("CRITICAL","HIGH") else "Helvetica"
    return Paragraph(f"<b>{text}</b>" if fn == "Helvetica-Bold" else text,
                     ParagraphStyle("cs", fontSize=8, textColor=tc, fontName=fn,
                                    alignment=TA_CENTER, backColor=bg))


def generate_business_report(output_path: str, data_dir: str):
    now      = datetime.datetime.utcnow()
    date_str = now.strftime("%B %d, %Y")
    time_str = now.strftime("%H:%M UTC")

    traffic  = _traffic(data_dir)
    load     = _load(data_dir)
    users    = _users(data_dir)
    ads      = _ads(data_dir)
    security = _security(data_dir)

    # Derived
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

    attack       = security.get("attack_types", {})
    activity_log = security.get("activity_log", [])
    threats_blk  = security.get("threats_blocked", 0)
    crit_alerts  = security.get("critical_alerts", 0)
    fw_status    = security.get("firewall_status", "Unknown")
    sec_score    = security.get("security_score", 0)
    err_4xx      = attack.get("4xx Errors", 0)
    err_5xx      = attack.get("5xx Errors", 0)
    susp_ips_n   = attack.get("Suspicious IPs", 0)
    fail_logins  = next((x["count"] for x in activity_log if x["name"] == "Failed Logins"), 0)

    repeat_u     = users["buyers"].get("Repeat", 0)
    onetime_u    = users["buyers"].get("One-time", 0)
    journey      = users.get("journey", {})
    category     = users.get("category", {})
    segments     = users.get("segments", {})
    top_cat      = sorted(category.items(), key=lambda x: x[1], reverse=True)[:6]
    top_eps      = list(load.get("top_endpoints", {}).items())[:6]
    susp_ip_lst  = list(load.get("suspicious_ips", {}).items())[:6]

    s = _styles()
    doc = SimpleDocTemplate(output_path, pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm,
        title="TrafficIQ Business Intelligence Report",
        author="TrafficIQ Analytics Platform")
    story = []
    W = A4[0] - 4*cm
    H = A4[1] - 4*cm

    # ══════════════════════════════════════════════════════════════════════════
    # COVER PAGE
    # ══════════════════════════════════════════════════════════════════════════
    sec_col = C_GREEN if sec_score >= 70 else (C_ORANGE if sec_score >= 50 else C_RED)
    kpis = [
        ("Total Sessions",  f"{total_sess:,}",              C_BLUE),
        ("Total Requests",  f"{load['total_requests']:,}",  C_ORANGE),
        ("Total Orders",    f"{users['total_orders']:,}",   C_TEAL),
        ("Retention Rate",  f"{users['retention_rate']}%",  C_PURPLE),
        ("Avg Rating",      f"{users['avg_rating']}/5.0",   C_ORANGE),
        ("ROAS",            f"{roas}x",                     C_PINK),
        ("Security Score",  f"{sec_score:.1f}/100",         sec_col),
        ("Threats Blocked", f"{threats_blk:,}",             C_RED),
    ]
    cover_h = 420
    story.append(Spacer(1, 0.3*cm))
    story.append(CoverPage(date_str, time_str, kpis, W, cover_h))
    story.append(Spacer(1, 0.5*cm))

    # ── Table of Contents (kept together on same page) ────────────────────────
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
    toc_rows = [[Paragraph("Table of Contents", s["toc_h"])]] + \
               [[Paragraph(f"   {i}", s["toc_e"])] for i in toc_items]
    toc_t = Table(toc_rows, colWidths=[W])
    toc_t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(0,0), C_LIGHT),
        ("BACKGROUND",    (0,1),(-1,-1), C_WHITE),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [C_WHITE, C_ALT]),
        ("TOPPADDING",    (0,0),(-1,-1), 5),
        ("BOTTOMPADDING", (0,0),(-1,-1), 5),
        ("LEFTPADDING",   (0,0),(-1,-1), 12),
        ("BOX",           (0,0),(-1,-1), 0.5, C_BORDER),
        ("LINEBELOW",     (0,0),(-1,0),  0.5, C_BORDER),
    ]))
    story.append(KeepTogether(toc_t))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # 1. EXECUTIVE SUMMARY
    # ══════════════════════════════════════════════════════════════════════════
    _banner("1.  Executive Summary", story, s, C_DARK, W)
    story.append(Paragraph(
        f"This report provides a comprehensive data-driven performance overview of the "
        f"<b>TrafficIQ Analytics Platform</b> for the period ending <b>{date_str}</b>. "
        f"The analysis covers five core pillars: web traffic, server infrastructure, user behaviour, "
        f"advertising performance, and platform security.",
        s["body"]
    ))

    def h_row(metric, value, status, comment):
        return [metric, value, _color_cell(status, status), comment]

    health = [
        ["Metric", "Value", "Status", "Comment"],
        h_row("Total Sessions",       f"{total_sess:,}",                "GOOD",
              "Strong traffic volume"),
        h_row("Avg Session Duration", f"{traffic['avg_session_duration']}s", "GOOD",
              "Users are engaged"),
        h_row("Server Error Rate",    f"{load['error_rate']:.1f}%",
              "CRITICAL" if load['error_rate'] > 5 else "GOOD",
              "High — immediate fix needed" if load['error_rate'] > 5 else "Within threshold"),
        h_row("Ad CTR",               f"{ctr}%",
              "CRITICAL" if ctr < 1 else ("HIGH" if ctr < 2 else "GOOD"),
              "Below industry avg (2%)" if ctr < 2 else "On target"),
        h_row("Security Score",       f"{sec_score:.1f}/100",
              "CRITICAL" if sec_score < 50 else ("HIGH" if sec_score < 70 else "GOOD"),
              "Moderate risk" if sec_score >= 50 else "Critical — immediate action"),
        h_row("Customer Retention",   f"{users['retention_rate']}%",    "GOOD",
              "Excellent — above industry avg"),
        h_row("Avg Order Value",      f"${users['avg_order_value']}",   "GOOD",
              "High-value customer base"),
    ]
    ht = Table(health, colWidths=[W*0.26, W*0.16, W*0.15, W*0.43])
    ht.setStyle(_tbl(C_DARK))
    story.append(ht)
    story.append(Paragraph("Table 1.1 — Platform Health Scorecard", s["caption"]))

    story.append(Paragraph(
        f"<b>Overall Assessment:</b> The platform demonstrates strong user engagement with "
        f"{total_sess:,} total sessions and a {users['retention_rate']}% retention rate. "
        f"However, the server error rate of {load['error_rate']:.1f}% and security score of "
        f"{sec_score:.1f}/100 require immediate attention. Ad CTR needs urgent campaign optimisation.",
        s["body"]
    ))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # 2. TRAFFIC
    # ══════════════════════════════════════════════════════════════════════════
    _banner("2.  Traffic Intelligence Analysis", story, s, C_BLUE, W)
    story.append(Paragraph("<b>2.1  Overview</b>", s["subsec"]))
    story.append(Paragraph(
        f"The platform recorded <b>{total_sess:,} total page views</b>. "
        f"Traffic peaks at <b>{peak_hour}:00</b> with <b>{int(peak_traffic):,} views</b> "
        f"and drops to its lowest at <b>{low_hour}:00</b> ({int(low_traffic):,} views). "
        f"The bounce rate of <b>{traffic['bounce_rate']}%</b> is below the 40% industry average, "
        f"indicating strong content relevance and user engagement.",
        s["body"]
    ))

    story.append(Paragraph("<b>2.2  Hourly Traffic Distribution</b>", s["subsec"]))
    hourly_sorted = sorted(hourly.items(), key=lambda x: int(str(x[0])))
    story.append(HBarChart(
        [(f"{h}:00", v) for h, v in hourly_sorted],
        width=int(W), bar_height=11, spacing=3, color=C_BLUE
    ))
    story.append(Paragraph("Chart 2.1 — Page Views by Hour of Day", s["caption"]))

    _callout(
        f"Peak at {peak_hour}:00 = optimal window for content releases, email campaigns & ad pushes. "
        f"Schedule all major platform events around this window to maximise reach and conversion.",
        story, s, bg=colors.HexColor("#eff6ff"), border=C_BLUE, icon="INSIGHT"
    )

    story.append(Paragraph("<b>2.3  Traffic Sources</b>", s["subsec"]))
    src_d = [["Source", "Sessions", "Share %", "Trend"]] + [
        [src, f"{int(v):,}", f"{round(int(v)/total_sess*100,1)}%",
         "Primary" if v == max(sources.values()) else "Secondary"]
        for src, v in top_src
    ]
    st = Table(src_d, colWidths=[W*0.28, W*0.22, W*0.18, W*0.32])
    st.setStyle(_tbl(C_BLUE))
    story.append(st)
    story.append(Paragraph("Table 2.1 — Traffic by Acquisition Source", s["caption"]))

    story.append(Paragraph("<b>2.4  Geographic Distribution</b>", s["subsec"]))
    geo_d = [["Country", "Sessions", "Share %", "Market Tier"]] + [
        [c, f"{int(v):,}", f"{round(int(v)/total_sess*100,1)}%",
         "Primary" if i==0 else ("Growth" if i<=2 else "Emerging")]
        for i,(c,v) in enumerate(top_geo)
    ]
    gt = Table(geo_d, colWidths=[W*0.26, W*0.22, W*0.18, W*0.34])
    gt.setStyle(_tbl(C_BLUE))
    story.append(gt)
    story.append(Paragraph("Table 2.2 — Top Countries by Session Volume", s["caption"]))

    story.append(Paragraph("<b>2.5  Issues &amp; Remediation</b>", s["subsec"]))
    tr_issues = [
        ["Issue", "Impact", "Root Cause", "Recommended Action"],
        ["Search dominates at 40%", "Dependency risk", "Low investment in other channels",
         "Diversify: grow social & referral"],
        ["Traffic spike at single hour", "Server overload risk", "No load distribution",
         "Implement CDN & auto-scaling"],
        ["Low Referral (10%)", "Missing organic growth", "No affiliate programme",
         "Launch partner referral programme"],
    ]
    ti = Table(tr_issues, colWidths=[W*0.22, W*0.18, W*0.28, W*0.32])
    ti.setStyle(_tbl(C_RED))
    story.append(ti)
    story.append(Paragraph("Table 2.3 — Traffic Issues &amp; Remediation", s["caption"]))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # 3. SERVER LOAD
    # ══════════════════════════════════════════════════════════════════════════
    _banner("3.  Server Load &amp; Performance Analysis", story, s, C_ORANGE, W)
    story.append(Paragraph("<b>3.1  Infrastructure Overview</b>", s["subsec"]))
    story.append(Paragraph(
        f"The server processed <b>{load['total_requests']:,} total requests</b>. "
        f"CPU at <b>{load['avg_cpu_usage']}%</b>, memory at <b>{load['memory_usage']:.0f}%</b>, "
        f"avg response time <b>{load['avg_response_time']:.0f} ms</b>, "
        f"error rate <b>{load['error_rate']:.2f}%</b>. "
        f"The error rate is critically above the 1% industry threshold.",
        s["body"]
    ))

    perf = [
        ["Metric", "Value", "Benchmark", "Status"],
        ["Total Requests",    f"{load['total_requests']:,}",    "N/A",      "INFO"],
        ["Avg CPU Usage",     f"{load['avg_cpu_usage']}%",      "< 70%",
         "CRITICAL" if load['avg_cpu_usage']>90 else "HIGH"],
        ["Memory Usage",      f"{load['memory_usage']:.0f}%",   "< 75%",
         "CRITICAL" if load['memory_usage']>90 else "HIGH"],
        ["Avg Response Time", f"{load['avg_response_time']:.0f} ms", "< 200 ms",
         "OK" if load['avg_response_time']<200 else "HIGH"],
        ["Error Rate",        f"{load['error_rate']:.2f}%",     "< 1%",
         "CRITICAL" if load['error_rate']>5 else "HIGH"],
    ]
    pt = Table(perf, colWidths=[W*0.30, W*0.18, W*0.18, W*0.34])
    pt_s = _tbl(C_ORANGE)
    status_map = {1:"CRITICAL",2:"CRITICAL",3:"OK",4:"CRITICAL"}
    color_map  = {"CRITICAL":(C_BAD,C_BAD_T),"HIGH":(C_WARN,C_WARN_T),
                  "OK":(C_GOOD,C_GOOD_T),"INFO":(C_LIGHT,C_MUTED)}
    for i, row in enumerate(perf[1:], 1):
        bg, tc = color_map.get(row[3], (C_LIGHT, C_MUTED))
        pt_s.add("BACKGROUND", (3,i), (3,i), bg)
        pt_s.add("TEXTCOLOR",  (3,i), (3,i), tc)
    pt.setStyle(pt_s)
    story.append(pt)
    story.append(Paragraph("Table 3.1 — Performance Metrics vs Industry Benchmarks", s["caption"]))

    story.append(Paragraph("<b>3.2  Top Endpoints by Request Volume</b>", s["subsec"]))
    story.append(HBarChart(top_eps, width=int(W), bar_height=12, spacing=4, color=C_ORANGE))
    story.append(Paragraph("Chart 3.1 — Top Endpoints", s["caption"]))

    ep_d = [["Endpoint", "Requests", "% of Total", "Avg Response (ms)"]] + [
        [ep, f"{int(h):,}", f"{round(int(h)/load['total_requests']*100,1)}%",
         f"{load.get('avg_response_by_endpoint',{}).get(ep,0):.0f}"]
        for ep, h in top_eps
    ]
    et = Table(ep_d, colWidths=[W*0.38, W*0.18, W*0.18, W*0.26])
    et.setStyle(_tbl(C_ORANGE))
    story.append(et)
    story.append(Paragraph("Table 3.2 — Endpoint Performance Detail", s["caption"]))

    _callout(
        f"CPU & memory at 95% is a ticking time bomb. One traffic spike will take the platform offline. "
        f"Immediate actions: (1) Add Redis/Memcached caching, (2) Enable auto-scaling, "
        f"(3) Investigate the 49% error rate — fix top 5 failing endpoints first.",
        story, s, bg=colors.HexColor("#fff7ed"), border=C_ORANGE, icon="WARNING"
    )

    li = [
        ["Issue", "Root Cause", "Immediate Fix", "Long-term Solution"],
        [f"Error rate {load['error_rate']:.1f}%", "App errors/bad routes",
         "Fix top 5 failing endpoints", "Circuit breakers & retry logic"],
        ["CPU at 95%", "No caching, all DB hits",
         "Add Redis caching", "Auto-scale or upgrade tier"],
        ["Memory at 95%", "Memory leaks / large payloads",
         "Profile memory usage", "Pagination & lazy loading"],
        ["High /usr/login traffic", "Brute-force or bot traffic",
         "Add CAPTCHA & rate limiting", "WAF & DDoS protection"],
    ]
    lit = Table(li, colWidths=[W*0.18, W*0.22, W*0.28, W*0.32])
    lit.setStyle(_tbl(C_RED))
    story.append(lit)
    story.append(Paragraph("Table 3.3 — Load Issues &amp; Remediation Plan", s["caption"]))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # 4. USER BEHAVIOUR
    # ══════════════════════════════════════════════════════════════════════════
    _banner("4.  User Behaviour &amp; Retention Analysis", story, s, C_PURPLE, W)
    story.append(Paragraph("<b>4.1  Customer Overview</b>", s["subsec"]))
    story.append(Paragraph(
        f"The platform processed <b>{users['total_orders']:,} orders</b> at an average order value of "
        f"<b>${users['avg_order_value']}</b> with customer rating <b>{users['avg_rating']}/5.0</b>. "
        f"Retention is exceptional at <b>{users['retention_rate']}%</b> — "
        f"well above the 30-40% e-commerce benchmark. "
        f"<b>{repeat_u:,} repeat buyers</b> vs only <b>{onetime_u:,} one-time buyers</b>.",
        s["body"]
    ))

    buyer_d = [
        ["Buyer Type", "Count", "Share %", "Avg Orders", "Business Value"],
        ["Repeat Buyers",   f"{repeat_u:,}",
         f"{round(repeat_u/(repeat_u+onetime_u)*100,1)}%", "2+", "HIGH — Core revenue base"],
        ["One-time Buyers", f"{onetime_u:,}",
         f"{round(onetime_u/(repeat_u+onetime_u)*100,1)}%", "1",  "MEDIUM — Re-engage now"],
    ]
    bt = Table(buyer_d, colWidths=[W*0.22, W*0.14, W*0.14, W*0.16, W*0.34])
    bt.setStyle(_tbl(C_PURPLE))
    story.append(bt)
    story.append(Paragraph("Table 4.1 — Customer Segmentation", s["caption"]))

    story.append(Paragraph("<b>4.2  Revenue by Product Category</b>", s["subsec"]))
    story.append(HBarChart(top_cat, width=int(W), bar_height=12, spacing=4, color=C_PURPLE))
    story.append(Paragraph("Chart 4.1 — Revenue by Product Category", s["caption"]))

    cat_d = [["Category", "Revenue", "Share %", "Opportunity"]] + [
        [cat, f"${int(rev):,}", f"{round(rev/sum(v for _,v in top_cat)*100,1)}%",
         "Scale" if i==0 else ("Grow" if i<=2 else "Niche")]
        for i,(cat,rev) in enumerate(top_cat)
    ]
    ct = Table(cat_d, colWidths=[W*0.28, W*0.22, W*0.18, W*0.32])
    ct.setStyle(_tbl(C_PURPLE))
    story.append(ct)
    story.append(Paragraph("Table 4.2 — Revenue by Product Category", s["caption"]))

    story.append(Paragraph("<b>4.3  Conversion Funnel</b>", s["subsec"]))
    jkeys = list(journey.keys())
    jvals = list(journey.values())
    fun_d = [["Stage", "Users", "Conv %", "Drop-off %", "Action"]] + [
        [stage, f"{int(cnt):,}", f"{round(cnt/jvals[0]*100,1)}%",
         f"{round((1-cnt/jvals[i-1])*100,1)}%" if i>0 else "—",
         "Optimise UX" if i>0 and (1-cnt/jvals[i-1])>0.4 else "Monitor"]
        for i,(stage,cnt) in enumerate(journey.items())
    ]
    ft = Table(fun_d, colWidths=[W*0.20, W*0.16, W*0.14, W*0.16, W*0.34])
    ft.setStyle(_tbl(C_PURPLE))
    story.append(ft)
    story.append(Paragraph("Table 4.3 — Customer Conversion Funnel", s["caption"]))

    _callout(
        "30% drop-off between Visited and Viewed Product is the biggest revenue leak. "
        "Improve homepage personalisation, search relevance, and product recommendations "
        "to recover this segment.",
        story, s, bg=colors.HexColor("#faf5ff"), border=C_PURPLE, icon="INSIGHT"
    )

    if segments:
        story.append(Paragraph("<b>4.4  Revenue by Age Segment</b>", s["subsec"]))
        seg_s = sorted(segments.items(), key=lambda x: x[1], reverse=True)
        seg_d = [["Age Group", "Revenue", "Share %", "Marketing Priority"]] + [
            [sg, f"${int(rv):,}", f"{round(rv/sum(segments.values())*100,1)}%",
             "Primary" if i==0 else ("Secondary" if i==1 else "Tertiary")]
            for i,(sg,rv) in enumerate(seg_s)
        ]
        st2 = Table(seg_d, colWidths=[W*0.18, W*0.24, W*0.18, W*0.40])
        st2.setStyle(_tbl(C_PURPLE))
        story.append(st2)
        story.append(Paragraph("Table 4.4 — Revenue by Age Group", s["caption"]))

    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # 5. ADS
    # ══════════════════════════════════════════════════════════════════════════
    _banner("5.  Advertisement Performance Analysis", story, s, C_PINK, W)
    story.append(Paragraph("<b>5.1  Campaign Overview</b>", s["subsec"]))
    story.append(Paragraph(
        f"Campaigns delivered <b>{total_impr:,} impressions</b>, CTR <b>{ctr}%</b>, "
        f"CPC <b>${cpc}</b>, ROAS <b>{roas}x</b>. "
        f"While ROAS exceeds the 4x benchmark, the near-zero CTR indicates the creative is not "
        f"compelling users to click — the majority of ad spend is generating impressions without action.",
        s["body"]
    ))

    ab = [
        ["KPI", "Current", "Benchmark", "Gap", "Priority"],
        ["CTR",             f"{ctr}%",     "2.0%",       f"{round(2.0-ctr,2)}%",    "CRITICAL"],
        ["CPC",             f"${cpc}",     "$0.50-2.00", "Within range",             "OK"],
        ["ROAS",            f"{roas}x",    "4x+",        "Above benchmark",          "GOOD"],
        ["Conversion Rate", f"{conv_rate}%","2-3%",      f"{round(max(0,2-conv_rate),1)}%","HIGH"],
        ["Total Clicks",    f"{total_clicks:,}","2,577+", f"{max(0,2577-total_clicks):,} short","CRITICAL"],
    ]
    abt = Table(ab, colWidths=[W*0.20, W*0.16, W*0.18, W*0.20, W*0.26])
    ab_s = _tbl(C_PINK)
    for i, row in enumerate(ab[1:], 1):
        bg, tc = {"CRITICAL":(C_BAD,C_BAD_T),"HIGH":(C_WARN,C_WARN_T),
                  "GOOD":(C_GOOD,C_GOOD_T),"OK":(C_GOOD,C_GOOD_T)}.get(row[4],(C_LIGHT,C_MUTED))
        ab_s.add("BACKGROUND",(4,i),(4,i),bg)
        ab_s.add("TEXTCOLOR", (4,i),(4,i),tc)
    abt.setStyle(ab_s)
    story.append(abt)
    story.append(Paragraph("Table 5.1 — Ad KPIs vs Industry Benchmarks", s["caption"]))

    story.append(Paragraph("<b>5.2  Ad Format Distribution</b>", s["subsec"]))
    fmt_d = [["Format", "Impressions", "Share %", "Est. Clicks", "Recommendation"]] + [
        [fmt, f"{int(imp):,}", f"{round(imp/total_impr*100,1)}%",
         f"{int(imp*ctr/100):,}", "Scale up" if fmt=="Video" else "Maintain"]
        for fmt,imp in ad_formats.items()
    ]
    fmtt = Table(fmt_d, colWidths=[W*0.16, W*0.18, W*0.14, W*0.16, W*0.36])
    fmtt.setStyle(_tbl(C_PINK))
    story.append(fmtt)
    story.append(Paragraph("Table 5.2 — Ad Format Performance", s["caption"]))

    story.append(Paragraph("<b>5.3  Conversion Funnel</b>", s["subsec"]))
    fsteps = [("Impressions",funnel.get("impressions",0)),("Clicks",funnel.get("clicks",0)),
              ("Landing",funnel.get("landing",0)),("Add to Cart",funnel.get("add_to_cart",0)),
              ("Checkout",funnel.get("checkout",0)),("Purchase",funnel.get("purchase",0))]
    cv_d = [["Stage","Users","Conv %","Drop-off"]] + [
        [st, f"{int(v):,}", f"{round(v/fsteps[0][1]*100,2)}%" if fsteps[0][1] else "0%",
         f"-{round((1-v/fsteps[i-1][1])*100,1)}%" if i>0 and fsteps[i-1][1] else "—"]
        for i,(st,v) in enumerate(fsteps)
    ]
    cvt = Table(cv_d, colWidths=[W*0.24, W*0.20, W*0.20, W*0.36])
    cvt.setStyle(_tbl(C_PINK))
    story.append(cvt)
    story.append(Paragraph("Table 5.3 — Ad Conversion Funnel", s["caption"]))

    _callout(
        "ACTION REQUIRED: Near-zero organic CTR. Immediate steps: "
        "(1) A/B test at least 3 ad creatives per format, "
        "(2) Narrow audience targeting to match the 50+ age segment (highest revenue), "
        "(3) Increase Video budget — historically 2-3x better CTR than banners, "
        "(4) Add strong CTA (call-to-action) text to all creatives.",
        story, s, bg=colors.HexColor("#fff1f2"), border=C_RED, icon="ACTION REQUIRED"
    )
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # 6. SECURITY
    # ══════════════════════════════════════════════════════════════════════════
    _banner("6.  Security &amp; Threat Analysis", story, s, C_RED, W)
    story.append(Paragraph("<b>6.1  Security Posture Overview</b>", s["subsec"]))
    sec_rating = "CRITICAL" if sec_score<50 else ("MODERATE" if sec_score<70 else "GOOD")
    story.append(Paragraph(
        f"Security score <b>{sec_score:.1f}/100 — {sec_rating}</b>. "
        f"Firewall: <b>{fw_status}</b>. Blocked <b>{threats_blk:,} threats</b>. "
        f"<b>{crit_alerts} critical alert(s)</b> active. "
        f"The 49% error rate is partly driven by security rejections and bot traffic.",
        s["body"]
    ))

    sm = [
        ["Security KPI", "Value", "Risk", "Description"],
        ["Security Score",    f"{sec_score:.1f}/100",
         "CRITICAL" if sec_score<50 else "HIGH", "Overall security health"],
        ["Threats Blocked",   f"{threats_blk:,}",    "INFO",  "Blocked malicious requests"],
        ["Critical Alerts",   str(crit_alerts),
         "HIGH" if crit_alerts>0 else "OK",          "Active unresolved alerts"],
        ["4xx Client Errors", f"{err_4xx:,}",
         "HIGH" if err_4xx>10000 else "OK",           "Unauthorised / not-found"],
        ["5xx Server Errors", f"{err_5xx:,}",
         "CRITICAL" if err_5xx>10000 else "HIGH",     "Server-side failures"],
        ["Suspicious IPs",    str(susp_ips_n),
         "HIGH" if susp_ips_n>0 else "OK",            "IPs with >100 requests"],
        ["Failed Logins",     str(fail_logins),
         "HIGH" if fail_logins>10 else "OK",          "Potential brute-force"],
    ]
    smt = Table(sm, colWidths=[W*0.24, W*0.16, W*0.16, W*0.44])
    sm_s = _tbl(C_RED)
    color_map2 = {"CRITICAL":(C_BAD,C_BAD_T),"HIGH":(C_WARN,C_WARN_T),
                  "OK":(C_GOOD,C_GOOD_T),"INFO":(C_LIGHT,C_MUTED)}
    for i, row in enumerate(sm[1:], 1):
        bg, tc = color_map2.get(row[2],(C_LIGHT,C_MUTED))
        sm_s.add("BACKGROUND",(2,i),(2,i),bg)
        sm_s.add("TEXTCOLOR", (2,i),(2,i),tc)
    smt.setStyle(sm_s)
    story.append(smt)
    story.append(Paragraph("Table 6.1 — Security KPI Assessment", s["caption"]))

    story.append(Paragraph("<b>6.2  Security Activity Log</b>", s["subsec"]))
    act_d = [["Threat Type","Count","Severity","Status","Action Required"]] + [
        [x["name"], str(x["count"]), x["level"],
         "ACTIVE" if x["count"]>0 else "CLEAR",
         "Investigate immediately" if x["level"]=="Critical" else
         ("Monitor closely" if x["level"]=="High" else "Review weekly")]
        for x in activity_log
    ]
    att = Table(act_d, colWidths=[W*0.26, W*0.10, W*0.14, W*0.12, W*0.38])
    at_s = _tbl(C_RED)
    for i, row in enumerate(act_d[1:], 1):
        if row[2] == "Critical":
            at_s.add("BACKGROUND",(0,i),(-1,i),C_BAD)
        elif row[2] == "High":
            at_s.add("BACKGROUND",(0,i),(-1,i),C_WARN)
    att.setStyle(at_s)
    story.append(att)
    story.append(Paragraph("Table 6.2 — Security Activity Log", s["caption"]))

    if susp_ip_lst:
        story.append(Paragraph("<b>6.3  Flagged IP Addresses</b>", s["subsec"]))
        story.append(HBarChart(susp_ip_lst, width=int(W), bar_height=12, spacing=4, color=C_RED))
        story.append(Paragraph("Chart 6.1 — Flagged IPs by Request Count", s["caption"]))
        sp_d = [["IP Address","Requests","Risk","Recommended Action"]] + [
            [ip, f"{int(cnt):,}",
             "CRITICAL" if cnt>200 else "HIGH",
             "Block immediately" if cnt>200 else "Rate limit & monitor"]
            for ip,cnt in susp_ip_lst
        ]
        sp_t = Table(sp_d, colWidths=[W*0.28, W*0.16, W*0.18, W*0.38])
        sp_s = _tbl(C_RED)
        for i, row in enumerate(sp_d[1:], 1):
            if row[2]=="CRITICAL":
                sp_s.add("BACKGROUND",(0,i),(-1,i),C_BAD)
        sp_t.setStyle(sp_s)
        story.append(sp_t)
        story.append(Paragraph("Table 6.3 — Flagged IPs &amp; Remediation", s["caption"]))

    _callout(
        f"IMMEDIATE: Block IPs 222.110.193.108 (305 reqs) and 172.151.145.166 (270 reqs) via firewall. "
        f"Fix the {err_5xx:,} server errors — start with top 5 endpoints. "
        f"Enable real-time alerting for failed login spikes.",
        story, s, bg=colors.HexColor("#fff1f2"), border=C_RED, icon="CRITICAL ACTION"
    )
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # 7. RECOMMENDATIONS
    # ══════════════════════════════════════════════════════════════════════════
    _banner("7.  Key Findings &amp; Business Recommendations", story, s, C_DARK, W)

    story.append(Paragraph("<b>7.1  Priority Action Matrix</b>", s["subsec"]))
    pm = [
        ["Priority", "Area", "Finding", "Recommended Action", "Timeline"],
        ["P1 — CRITICAL","Security",
         f"Score {sec_score:.0f}/100, {err_5xx:,} server errors",
         "Patch vulnerabilities, block flagged IPs","This week"],
        ["P1 — CRITICAL","Ad Performance",
         f"CTR {ctr}% vs 2% benchmark",
         "A/B test creatives, refine targeting","This week"],
        ["P2 — HIGH","Infrastructure",
         "CPU/Memory at 95%",
         "Add Redis caching, upgrade server","This month"],
        ["P2 — HIGH","Traffic",
         "90% from 2 sources",
         "Invest in social & referral channels","This month"],
        ["P3 — MEDIUM","Conversion",
         "30% visit-to-product drop-off",
         "Improve homepage & product discovery","Next quarter"],
        ["P3 — MEDIUM","User Behaviour",
         f"{onetime_u:,} one-time buyers",
         "Launch re-engagement emails","Next quarter"],
        ["P4 — LOW","Traffic",
         "Referral only 10%",
         "Create partner affiliate programme","6 months"],
    ]
    pmt = Table(pm, colWidths=[W*0.16, W*0.14, W*0.26, W*0.28, W*0.16])
    pm_s = _tbl(C_DARK)
    for i, row in enumerate(pm[1:], 1):
        if "P1" in row[0]:
            pm_s.add("BACKGROUND",(0,i),(0,i),C_BAD)
            pm_s.add("TEXTCOLOR", (0,i),(0,i),C_BAD_T)
            pm_s.add("FONTNAME",  (0,i),(0,i),"Helvetica-Bold")
        elif "P2" in row[0]:
            pm_s.add("BACKGROUND",(0,i),(0,i),C_WARN)
            pm_s.add("TEXTCOLOR", (0,i),(0,i),C_WARN_T)
        elif "P3" in row[0]:
            pm_s.add("BACKGROUND",(0,i),(0,i),C_GOOD)
            pm_s.add("TEXTCOLOR", (0,i),(0,i),C_GOOD_T)
    pmt.setStyle(pm_s)
    story.append(pmt)
    story.append(Paragraph("Table 7.1 — Prioritised Action Matrix", s["caption"]))

    story.append(Paragraph("<b>7.2  Strengths to Leverage</b>", s["subsec"]))
    for txt in [
        f"Retention {users['retention_rate']}% — well above 30-40% industry average",
        f"Average order value ${users['avg_order_value']} — premium customer base",
        f"ROAS {roas}x — ad spend delivers strong returns when users engage",
        f"Customer rating {users['avg_rating']}/5.0 — high satisfaction",
        "Predictable traffic patterns enable reliable capacity planning",
    ]:
        _callout(txt, story, s, bg=C_GOOD, border=C_GREEN, icon="STRENGTH")

    story.append(Paragraph("<b>7.3  Critical Weaknesses to Address</b>", s["subsec"]))
    for txt in [
        f"Security score {sec_score:.0f}/100 — significant breach risk",
        f"Error rate {load['error_rate']:.1f}% — users experiencing failures right now",
        f"Ad CTR {ctr}% — ad budget largely wasted without clicks",
        "CPU/Memory at 95% — one traffic spike from full outage",
    ]:
        _callout(txt, story, s, bg=C_BAD, border=C_RED, icon="WEAKNESS")

    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # APPENDIX
    # ══════════════════════════════════════════════════════════════════════════
    _banner("Appendix — Full Key Performance Indicators", story, s, C_SLATE, W)

    kpi_full = [
        ["Category", "Metric", "Value", "Benchmark", "Status"],
        ["Traffic","Total Sessions",       f"{total_sess:,}",               "N/A",    "INFO"],
        ["Traffic","Avg Session Duration", f"{traffic['avg_session_duration']}s","90-180s","OK"],
        ["Traffic","Pages per Session",    str(traffic['pages_per_session']),"3-5",    "OK"],
        ["Traffic","Bounce Rate",          f"{traffic['bounce_rate']}%",    "< 40%",  "GOOD"],
        ["Traffic","Peak Hour",            f"{peak_hour}:00 ({int(peak_traffic):,} views)","N/A","INFO"],
        ["Server", "Total Requests",       f"{load['total_requests']:,}",   "N/A",    "INFO"],
        ["Server", "Avg CPU Usage",        f"{load['avg_cpu_usage']}%",     "< 70%",  "CRITICAL"],
        ["Server", "Memory Usage",         f"{load['memory_usage']:.1f}%",  "< 75%",  "CRITICAL"],
        ["Server", "Avg Response Time",    f"{load['avg_response_time']:.0f} ms","< 200ms","OK"],
        ["Server", "Error Rate",           f"{load['error_rate']:.2f}%",    "< 1%",   "CRITICAL"],
        ["Users",  "Total Orders",         f"{users['total_orders']:,}",    "N/A",    "INFO"],
        ["Users",  "Avg Order Value",      f"${users['avg_order_value']}",  "N/A",    "INFO"],
        ["Users",  "Retention Rate",       f"{users['retention_rate']}%",   "> 30%",  "GOOD"],
        ["Users",  "Avg Rating",           f"{users['avg_rating']}/5.0",    "> 4.0",  "GOOD"],
        ["Users",  "Repeat Buyers",        f"{repeat_u:,}",                 "N/A",    "INFO"],
        ["Users",  "One-time Buyers",      f"{onetime_u:,}",                "N/A",    "INFO"],
        ["Ads",    "Total Impressions",    f"{total_impr:,}",               "N/A",    "INFO"],
        ["Ads",    "Total Clicks",         f"{total_clicks:,}",             "N/A",    "INFO"],
        ["Ads",    "CTR",                  f"{ctr}%",                       "> 2%",   "CRITICAL"],
        ["Ads",    "CPC",                  f"${cpc}",                       "$0.5-2", "OK"],
        ["Ads",    "ROAS",                 f"{roas}x",                      "> 4x",   "GOOD"],
        ["Ads",    "Conversion Rate",      f"{conv_rate}%",                 "2-3%",   "HIGH"],
        ["Security","Security Score",      f"{sec_score:.1f}/100",          "> 70",   "CRITICAL"],
        ["Security","Threats Blocked",     f"{threats_blk:,}",              "N/A",    "INFO"],
        ["Security","Critical Alerts",     str(crit_alerts),                "0",      "HIGH" if crit_alerts>0 else "OK"],
        ["Security","4xx Client Errors",   f"{err_4xx:,}",                  "< 1%",   "HIGH"],
        ["Security","5xx Server Errors",   f"{err_5xx:,}",                  "< 0.1%", "CRITICAL"],
        ["Security","Suspicious IPs",      str(susp_ips_n),                 "0",      "HIGH" if susp_ips_n>0 else "OK"],
        ["Security","Failed Logins",       str(fail_logins),                "< 5",    "HIGH" if fail_logins>5 else "OK"],
        ["Security","Firewall Status",     fw_status,                       "Active", "GOOD" if fw_status=="Active" else "CRITICAL"],
    ]
    at = Table(kpi_full, colWidths=[W*0.12, W*0.28, W*0.18, W*0.16, W*0.26])
    at_s = _tbl(C_SLATE)
    for i, row in enumerate(kpi_full[1:], 1):
        bg, tc = color_map2.get(row[4], (C_LIGHT, C_MUTED))
        at_s.add("BACKGROUND",(4,i),(4,i),bg)
        at_s.add("TEXTCOLOR", (4,i),(4,i),tc)
    at.setStyle(at_s)
    story.append(at)
    story.append(Paragraph("Table A.1 — Comprehensive KPI Reference with Benchmarks &amp; Status", s["caption"]))

    story.append(Spacer(1, 0.6*cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=C_BORDER))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        f"TrafficIQ Analytics Platform  |  MediCaps University  |  "
        f"Report generated {date_str} at {time_str}  |  CONFIDENTIAL",
        s["footer"]
    ))

    doc.build(story)
    return output_path