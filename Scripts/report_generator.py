import os
from datetime import datetime
from zoneinfo import ZoneInfo
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


class CoverPage(Flowable):
    def __init__(self, date_str, time_str, kpis, W, H):
        Flowable.__init__(self)
        self.date_str = date_str
        self.time_str = time_str
        self.kpis     = kpis
        self.width    = W
        self.height   = H

    def draw(self):
        c = self.canv
        W = self.width
        H = self.height
        c.setFillColor(C_DARK)
        c.roundRect(0, 0, W, H, 10, fill=1, stroke=0)
        c.setFillColor(C_PURPLE)
        c.rect(0, H - 6, W, 6, fill=1, stroke=0)
        logo_y = H - 80
        c.setFillColor(C_PURPLE)
        c.roundRect(W/2 - 28, logo_y, 56, 56, 10, fill=1, stroke=0)
        c.setFillColor(C_WHITE)
        c.setFont("Helvetica-Bold", 22)
        c.drawCentredString(W/2, logo_y + 16, "IQ")
        c.setFillColor(C_WHITE)
        c.setFont("Helvetica-Bold", 34)
        c.drawCentredString(W/2, logo_y - 42, "TrafficIQ")
        c.setFillColor(colors.HexColor("#94a3b8"))
        c.setFont("Helvetica", 15)
        c.drawCentredString(W/2, logo_y - 66, "Business Intelligence Report")
        c.setFont("Helvetica", 11)
        c.drawCentredString(W/2, logo_y - 86, "Executive Analytics & Platform Summary")
        c.setStrokeColor(colors.HexColor("#334155"))
        c.setLineWidth(1)
        c.line(W * 0.2, logo_y - 104, W * 0.8, logo_y - 104)
        c.setFillColor(colors.HexColor("#64748b"))
        c.setFont("Helvetica", 10)
        c.drawCentredString(W/2, logo_y - 120, f"Generated: {self.date_str}  |  {self.time_str}")
        c.drawCentredString(W/2, logo_y - 136, "MediCaps University  |  TrafficIQ Analytics Platform")
        badge_y = logo_y - 160
        c.setFillColor(colors.HexColor("#7f1d1d"))
        c.roundRect(W/2 - 100, badge_y - 6, 200, 22, 6, fill=1, stroke=0)
        c.setFillColor(colors.HexColor("#fca5a5"))
        c.setFont("Helvetica-Bold", 9)
        c.drawCentredString(W/2, badge_y + 3, "CONFIDENTIAL — FOR INTERNAL USE ONLY")
        kpi_start_y = badge_y - 30
        cols = 4
        cell_w = W / cols
        cell_h = 58
        for idx, (label, value, color) in enumerate(self.kpis):
            row = idx // cols
            col = idx % cols
            cx  = col * cell_w
            cy  = kpi_start_y - row * (cell_h + 6)
            bg = colors.HexColor("#1e293b") if idx % 2 == 0 else colors.HexColor("#162032")
            c.setFillColor(bg)
            c.roundRect(cx + 3, cy - cell_h + 4, cell_w - 6, cell_h, 6, fill=1, stroke=0)
            c.setFillColor(color)
            c.roundRect(cx + 3, cy - cell_h + 4 + cell_h - 4, cell_w - 6, 4, 3, fill=1, stroke=0)
            c.setFillColor(color)
            c.setFont("Helvetica-Bold", 16)
            c.drawCentredString(cx + cell_w/2, cy - cell_h + 30, str(value))
            c.setFillColor(colors.HexColor("#94a3b8"))
            c.setFont("Helvetica", 8)
            c.drawCentredString(cx + cell_w/2, cy - cell_h + 14, label)


def _styles():
    base = getSampleStyleSheet()
    def ps(name, **kw):
        return ParagraphStyle(name=name, parent=base["Normal"], **kw)
    return {
        "section":  ps("Section",  fontSize=13, textColor=C_WHITE,
                       fontName="Helvetica-Bold", spaceBefore=10, spaceAfter=4),
        "subsec":   ps("SubSec",   fontSize=11, textColor=C_NAVY,
                       fontName="Helvetica-Bold", spaceBefore=10, spaceAfter=4),
        "body":     ps("Body",     fontSize=9.5, textColor=C_SLATE,
                       leading=15, spaceAfter=7, alignment=TA_JUSTIFY),
        "body2":    ps("Body2",    fontSize=9, textColor=C_MUTED,
                       leading=14, spaceAfter=6, alignment=TA_JUSTIFY),
        "caption":  ps("Caption",  fontSize=7.5, textColor=C_MUTED,
                       spaceAfter=10, spaceBefore=2, alignment=TA_CENTER),
        "toc_h":    ps("TocH",     fontSize=11, textColor=C_NAVY,
                       fontName="Helvetica-Bold"),
        "toc_e":    ps("TocE",     fontSize=10, textColor=C_SLATE, leading=20, leftIndent=10),
        "insight":  ps("Insight",  fontSize=9, textColor=C_NAVY, leading=14, spaceAfter=3),
        "footer":   ps("Footer",   fontSize=7.5, textColor=C_MUTED, alignment=TA_CENTER),
        "method":   ps("Method",   fontSize=8.5, textColor=C_MUTED, leading=13,
                       spaceAfter=6, leftIndent=8, alignment=TA_JUSTIFY),
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
        ("WORDWRAP",       (0,0), (-1,-1), "CJK"),
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
        ("BACKGROUND",   (0,0), (-1,-1), bg),
        ("LINEAFTER",    (0,0), (0,-1),  3, border),
        ("TOPPADDING",   (0,0), (-1,-1), 7),
        ("BOTTOMPADDING",(0,0), (-1,-1), 7),
        ("LEFTPADDING",  (0,0), (-1,-1), 10),
        ("RIGHTPADDING", (0,0), (-1,-1), 10),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.1*cm))


def _color_cell(text, status):
    bg = {"CRITICAL":C_BAD,"HIGH":C_WARN,"GOOD":C_GOOD,"OK":C_GOOD}.get(status, C_LIGHT)
    tc = {"CRITICAL":C_BAD_T,"HIGH":C_WARN_T,"GOOD":C_GOOD_T,"OK":C_GOOD_T}.get(status, C_MUTED)
    fn = "Helvetica-Bold" if status in ("CRITICAL","HIGH") else "Helvetica"
    return Paragraph(f"<b>{text}</b>" if fn == "Helvetica-Bold" else text,
                     ParagraphStyle("cs", fontSize=8, textColor=tc, fontName=fn,
                                    alignment=TA_CENTER, backColor=bg))


def _methodology_note(text, story, s):
    """Small italic methodology/data note in muted style."""
    t = Table([[Paragraph(f"<i>Methodology: {text}</i>", s["method"])]], colWidths=[A4[0]-4*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",   (0,0),(-1,-1), colors.HexColor("#f8fafc")),
        ("LINEBEFORE",   (0,0),(0,-1),  2, C_BORDER),
        ("TOPPADDING",   (0,0),(-1,-1), 5),
        ("BOTTOMPADDING",(0,0),(-1,-1), 5),
        ("LEFTPADDING",  (0,0),(-1,-1), 10),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.1*cm))


def generate_business_report(output_path: str, data_dir: str):
    now = datetime.now(ZoneInfo("Asia/Kolkata"))
    date_str = now.strftime("%B %d, %Y")
    time_str = now.strftime("%I:%M:%S %p IST")

    traffic  = _traffic(data_dir)
    load     = _load(data_dir)
    users    = _users(data_dir)
    ads      = _ads(data_dir)
    security = _security(data_dir)

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

    color_map2 = {"CRITICAL":(C_BAD,C_BAD_T),"HIGH":(C_WARN,C_WARN_T),
                  "OK":(C_GOOD,C_GOOD_T),"GOOD":(C_GOOD,C_GOOD_T),"INFO":(C_LIGHT,C_MUTED)}

    s = _styles()
    doc = SimpleDocTemplate(output_path, pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm,
        title="TrafficIQ Business Intelligence Report",
        author="TrafficIQ Analytics Platform")
    story = []
    W = A4[0] - 4*cm

    # COVER PAGE
    sec_col = C_GREEN if sec_score >= 70 else (C_ORANGE if sec_score >= 50 else C_RED)
    kpis = [
        ("Total Sessions",  f"{total_sess:,}",             C_BLUE),
        ("Total Requests",  f"{load['total_requests']:,}", C_ORANGE),
        ("Total Orders",    f"{users['total_orders']:,}",  C_TEAL),
        ("Retention Rate",  f"{users['retention_rate']}%", C_PURPLE),
        ("Avg Rating",      f"{users['avg_rating']}/5.0",  C_ORANGE),
        ("ROAS",            f"{roas}x",                    C_PINK),
        ("Security Score",  f"{sec_score:.1f}/100",        sec_col),
        ("Threats Blocked", f"{threats_blk:,}",            C_RED),
    ]
    story.append(Spacer(1, 0.3*cm))
    story.append(CoverPage(date_str, time_str, kpis, W, 420))
    story.append(Spacer(1, 0.5*cm))

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
        ("BACKGROUND",    (0,0),(0,0),   C_LIGHT),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [C_WHITE, C_ALT]),
        ("TOPPADDING",    (0,0),(-1,-1), 5),
        ("BOTTOMPADDING", (0,0),(-1,-1), 5),
        ("LEFTPADDING",   (0,0),(-1,-1), 12),
        ("BOX",           (0,0),(-1,-1), 0.5, C_BORDER),
        ("LINEBELOW",     (0,0),(-1,0),  0.5, C_BORDER),
    ]))
    story.append(KeepTogether(toc_t))
    story.append(PageBreak())

    # 1. EXECUTIVE SUMMARY
    _banner("1.  Executive Summary", story, s, C_DARK, W)

    story.append(Paragraph(
        f"This Business Intelligence Report presents a comprehensive, data-driven evaluation of the "
        f"<b>TrafficIQ Analytics Platform</b> as of <b>{date_str}</b>. The report is structured across "
        f"five analytical pillars — web traffic behaviour, server infrastructure health, user "
        f"purchase patterns, advertising ROI, and cybersecurity posture — providing both an operational "
        f"snapshot and a strategic roadmap for platform improvement.",
        s["body"]
    ))
    story.append(Paragraph(
        f"The platform currently serves a substantial user base, recording <b>{total_sess:,} total "
        f"page views</b> with a healthy average session duration of "
        f"<b>{traffic['avg_session_duration']} seconds</b> and <b>{traffic['pages_per_session']} pages "
        f"per session</b>. The e-commerce component has processed <b>{users['total_orders']:,} orders</b> "
        f"at an average order value of <b>${users['avg_order_value']}</b>, generating substantial revenue "
        f"particularly from the Books and Clothing categories. Customer loyalty is a standout metric, "
        f"with a <b>{users['retention_rate']}% retention rate</b> that far exceeds the 30-40% "
        f"e-commerce industry benchmark — indicating strong product-market fit and customer satisfaction.",
        s["body"]
    ))
    story.append(Paragraph(
        f"However, three critical issues demand immediate executive attention. First, the server "
        f"infrastructure is operating at near-maximum capacity with CPU and memory both at "
        f"<b>{load['avg_cpu_usage']}%</b>, and an error rate of <b>{load['error_rate']:.1f}%</b> that "
        f"is approximately 49 times the industry-acceptable threshold of 1%. Second, the advertising "
        f"campaigns are generating <b>{total_impr:,} impressions</b> but achieving a CTR of only "
        f"<b>{ctr}%</b> — indicating creative or targeting misalignment that is wasting ad spend. "
        f"Third, the platform security score of <b>{sec_score:.1f}/100</b> represents a moderate-to-high "
        f"risk profile with {crit_alerts} active critical alerts and {susp_ips_n} suspicious IP addresses "
        f"requiring immediate remediation.",
        s["body"]
    ))

    def h_row(metric, value, status, comment):
        return [metric, value, _color_cell(status, status), comment]

    health = [
        ["Metric", "Value", "Status", "Comment"],
        h_row("Total Sessions",       f"{total_sess:,}",                    "GOOD",
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
        h_row("Customer Retention",   f"{users['retention_rate']}%",         "GOOD",
              "Excellent — above industry avg"),
        h_row("Avg Order Value",      f"${users['avg_order_value']}",        "GOOD",
              "High-value customer base"),
    ]
    ht = Table(health, colWidths=[W*0.26, W*0.16, W*0.15, W*0.43])
    ht.setStyle(_tbl(C_DARK))
    story.append(ht)
    story.append(Paragraph("Table 1.1 — Platform Health Scorecard", s["caption"]))

    story.append(Paragraph(
        f"<b>Strategic Outlook:</b> The platform has a strong commercial foundation — high retention, "
        f"high average order values, and a loyal repeat-buyer base. The primary growth inhibitors are "
        f"operational (server reliability), marketing (ad effectiveness), and security (risk exposure). "
        f"Addressing the P1 issues outlined in Section 7 within the next 7 days is recommended to "
        f"prevent revenue loss from server failures and security incidents.",
        s["body"]
    ))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # 2. TRAFFIC ANALYSIS
    # ══════════════════════════════════════════════════════════════════════════
    _banner("2.  Traffic Intelligence Analysis", story, s, C_BLUE, W)

    story.append(Paragraph("<b>2.1  Overview &amp; Context</b>", s["subsec"]))
    story.append(Paragraph(
        f"Web traffic analysis examines the volume, timing, source, and geographic distribution of "
        f"user sessions to understand audience behaviour and platform reach. The platform recorded "
        f"<b>{total_sess:,} total page views</b> across the analysis period. This figure represents "
        f"the aggregate of all page-level interactions, providing a baseline for engagement depth analysis.",
        s["body"]
    ))
    story.append(Paragraph(
        f"The platform's bounce rate of <b>{traffic['bounce_rate']}%</b> is significantly below the "
        f"industry average of 40-55% for analytics platforms, suggesting that visitors who land on the "
        f"platform find relevant content and continue exploring. The average session duration of "
        f"<b>{traffic['avg_session_duration']} seconds</b> and <b>{traffic['pages_per_session']} pages "
        f"per session</b> both align with healthy engagement benchmarks for data dashboard products.",
        s["body"]
    ))

    story.append(Paragraph("<b>2.2  Hourly Traffic Distribution</b>", s["subsec"]))
    story.append(Paragraph(
        f"Hourly traffic analysis reveals a clear bimodal pattern with a primary peak at "
        f"<b>{peak_hour}:00</b> ({int(peak_traffic):,} page views) and sustained high traffic from "
        f"09:00 through 17:00. This strongly indicates a B2B or professional user base accessing the "
        f"platform during standard business hours. The sharp decline after 18:00 and minimal traffic "
        f"between <b>{low_hour}:00</b> ({int(low_traffic):,} views) and 06:00 suggests the platform "
        f"is predominantly used as a work tool rather than a consumer product.",
        s["body"]
    ))
    story.append(Paragraph(
        f"The traffic swing of <b>{int(peak_traffic - low_traffic):,} views</b> between peak and "
        f"trough represents a significant infrastructure challenge — the server must accommodate nearly "
        f"75x more traffic at peak versus off-peak, yet resources are provisioned statically. "
        f"This mismatch is a primary contributor to the observed high error rates during business hours.",
        s["body"]
    ))
    hourly_sorted = sorted(hourly.items(), key=lambda x: int(str(x[0])))
    story.append(HBarChart(
        [(f"{h}:00", v) for h, v in hourly_sorted],
        width=int(W), bar_height=11, spacing=3, color=C_BLUE
    ))
    story.append(Paragraph("Chart 2.1 — Page Views by Hour of Day", s["caption"]))
    _methodology_note(
        "Hourly traffic derived from aggregated page_views column grouped by hour field in the "
        "traffic dataset. Values represent cumulative page views per hour across the full analysis period.",
        story, s
    )
    _callout(
        f"Peak at {peak_hour}:00 = optimal window for content releases, email campaigns & ad pushes. "
        f"Schedule all major platform events around this window to maximise reach and conversion.",
        story, s, bg=colors.HexColor("#eff6ff"), border=C_BLUE, icon="INSIGHT"
    )

    story.append(Paragraph("<b>2.3  Traffic Acquisition Sources</b>", s["subsec"]))
    story.append(Paragraph(
        f"Traffic source analysis identifies how users discover and arrive at the platform. "
        f"<b>Search engines</b> dominate at {round(sources.get('Search',0)/total_sess*100,1)}% of "
        f"all sessions, indicating strong organic SEO performance. <b>Direct traffic</b> at "
        f"{round(sources.get('Direct',0)/total_sess*100,1)}% suggests strong brand recognition — "
        f"users who type the URL directly or use bookmarks are typically the most loyal and "
        f"highest-converting segment. <b>Social media</b> contributes "
        f"{round(sources.get('Social',0)/total_sess*100,1)}% and <b>Referral</b> just "
        f"{round(sources.get('Referral',0)/total_sess*100,1)}%, both representing significant "
        f"untapped growth channels.",
        s["body"]
    ))
    src_d = [["Source", "Sessions", "Share %", "Trend"]] + [
        [src, f"{int(v):,}", f"{round(int(v)/total_sess*100,1)}%",
         "Primary" if v == max(sources.values()) else "Secondary"]
        for src, v in top_src
    ]
    st = Table(src_d, colWidths=[W*0.24, W*0.20, W*0.16, W*0.40])
    st.setStyle(_tbl(C_BLUE))
    story.append(st)
    story.append(Paragraph("Table 2.1 — Traffic by Acquisition Source", s["caption"]))

    story.append(Paragraph("<b>2.4  Geographic Market Distribution</b>", s["subsec"]))
    story.append(Paragraph(
        f"Geographic analysis reveals a strongly India-centric user base, with "
        f"<b>India accounting for {round(geo.get('India',0)/total_sess*100,1)}% of all sessions</b>. "
        f"This concentration aligns with the MediCaps University origin of the platform and suggests "
        f"the primary market is the Indian subcontinent. The <b>USA at "
        f"{round(geo.get('USA',0)/total_sess*100,1)}%</b> and "
        f"<b>UK at {round(geo.get('UK',0)/total_sess*100,1)}%</b> represent meaningful international "
        f"presence with significant growth potential. Germany, Canada, and Australia collectively "
        f"contribute approximately 23% of traffic, indicating early-stage international adoption.",
        s["body"]
    ))
    story.append(Paragraph(
        f"From a business strategy perspective, the geographic distribution presents a clear "
        f"tiered market opportunity: India as the primary market to dominate, USA and UK as "
        f"growth markets requiring localised investment, and Germany/Canada/Australia as "
        f"emerging markets for future expansion. Each tier requires different product, "
        f"pricing, and marketing strategies.",
        s["body"]
    ))
    geo_d = [["Country", "Sessions", "Share %", "Market Tier"]] + [
        [c, f"{int(v):,}", f"{round(int(v)/total_sess*100,1)}%",
         "Primary" if i==0 else ("Growth" if i<=2 else "Emerging")]
        for i,(c,v) in enumerate(top_geo)
    ]
    gt = Table(geo_d, colWidths=[W*0.26, W*0.22, W*0.18, W*0.34])
    gt.setStyle(_tbl(C_BLUE))
    story.append(gt)
    story.append(Paragraph("Table 2.2 — Top Countries by Session Volume", s["caption"]))
    _callout(
        "India dominates traffic. Localise content with Hindi language support, INR pricing, "
        "and India-specific case studies to deepen engagement in the primary market.",
        story, s, bg=colors.HexColor("#eff6ff"), border=C_BLUE, icon="RECOMMENDATION"
    )

    story.append(Paragraph("<b>2.5  Traffic Issues, Root Causes &amp; Remediation</b>", s["subsec"]))
    story.append(Paragraph(
        f"Despite strong overall traffic volume, three structural weaknesses in the traffic "
        f"profile require strategic intervention to ensure sustainable growth and platform resilience.",
        s["body"]
    ))
    tr_issues = [
        ["Issue", "Impact", "Root Cause", "Recommended Action"],
        ["Search dominates at 40%", "High dependency risk if SEO drops",
         "Underinvestment in other channels", "Diversify: grow social & referral to 20% each"],
        ["Traffic spike at single hour", "Server overload at peak hours",
         "No dynamic load distribution", "Implement CDN caching & auto-scaling rules"],
        ["Low Referral at 10%", "Missing organic viral growth",
         "No partner or affiliate programme", "Launch partner referral with incentives"],
        ["No off-peak engagement", "Wasted server capacity 22:00-06:00",
         "B2B-only audience, no consumer use case", "Develop consumer-facing features"],
    ]
    ti = Table(tr_issues, colWidths=[W*0.18, W*0.20, W*0.28, W*0.34])
    ti.setStyle(_tbl(C_RED))
    story.append(ti)
    story.append(Paragraph("Table 2.3 — Traffic Issues &amp; Strategic Remediation Plan", s["caption"]))
    story.append(PageBreak())

    # 3. SERVER LOAD
    _banner("3.  Server Load &amp; Performance Analysis", story, s, C_ORANGE, W)

    story.append(Paragraph("<b>3.1  Infrastructure Health Assessment</b>", s["subsec"]))
    story.append(Paragraph(
        f"Server performance analysis evaluates the platform's ability to reliably serve user "
        f"requests under current and projected load. The findings in this section represent "
        f"the most operationally critical issues in this report, as infrastructure failures "
        f"directly impact user experience, revenue, and platform credibility.",
        s["body"]
    ))
    story.append(Paragraph(
        f"The server processed <b>{load['total_requests']:,} total requests</b> with an average "
        f"response time of <b>{load['avg_response_time']:.0f} ms</b> — which is within the "
        f"acceptable sub-200ms threshold. However, this figure is misleading when considered "
        f"alongside the <b>{load['error_rate']:.2f}% error rate</b>. Nearly half of all requests "
        f"are returning error codes, meaning the response time metric only reflects the "
        f"performance of successful responses. The true user experience is significantly worse "
        f"than the response time figure suggests.",
        s["body"]
    ))
    story.append(Paragraph(
        f"CPU utilisation at <b>{load['avg_cpu_usage']}%</b> and memory at "
        f"<b>{load['memory_usage']:.0f}%</b> are both critically above safe operating thresholds "
        f"(70% and 75% respectively). Operating at 95% utilisation leaves virtually no headroom "
        f"for traffic spikes — a doubling of traffic, which is entirely plausible given the "
        f"hourly variance observed in Section 2, would cause complete service failure. "
        f"Industry best practice mandates maintaining at least 30% spare capacity at all times "
        f"to absorb unexpected load and allow for graceful degradation.",
        s["body"]
    ))

    perf = [
        ["Metric", "Value", "Benchmark", "Status"],
        ["Total Requests",    f"{load['total_requests']:,}",    "N/A",     "INFO"],
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
    color_map = {"CRITICAL":(C_BAD,C_BAD_T),"HIGH":(C_WARN,C_WARN_T),
                 "OK":(C_GOOD,C_GOOD_T),"INFO":(C_LIGHT,C_MUTED)}
    for i, row in enumerate(perf[1:], 1):
        bg, tc = color_map.get(row[3], (C_LIGHT, C_MUTED))
        pt_s.add("BACKGROUND",(3,i),(3,i),bg)
        pt_s.add("TEXTCOLOR", (3,i),(3,i),tc)
    pt.setStyle(pt_s)
    story.append(pt)
    story.append(Paragraph("Table 3.1 — Performance Metrics vs Industry Benchmarks", s["caption"]))

    story.append(Paragraph("<b>3.2  Endpoint Traffic &amp; Performance Analysis</b>", s["subsec"]))
    story.append(Paragraph(
        f"Endpoint analysis identifies which API routes or pages are generating the most load "
        f"on the server. The top 6 endpoints account for a disproportionate share of total "
        f"requests, with the authentication-related endpoints (/usr/login, /usr/register, "
        f"/usr/admin) collectively representing nearly 60% of all traffic. This pattern is "
        f"highly unusual for a production analytics platform and strongly suggests the presence "
        f"of automated bot traffic or a credential-stuffing attack targeting the authentication layer.",
        s["body"]
    ))
    story.append(HBarChart(top_eps, width=int(W), bar_height=12, spacing=4, color=C_ORANGE))
    story.append(Paragraph("Chart 3.1 — Top Endpoints by Request Volume", s["caption"]))

    ep_d = [["Endpoint", "Requests", "% of Total", "Avg Response (ms)"]] + [
        [ep, f"{int(h):,}", f"{round(int(h)/load['total_requests']*100,1)}%",
         f"{load.get('avg_response_by_endpoint',{}).get(ep,0):.0f}"]
        for ep, h in top_eps
    ]
    et = Table(ep_d, colWidths=[W*0.38, W*0.18, W*0.18, W*0.26])
    et.setStyle(_tbl(C_ORANGE))
    story.append(et)
    story.append(Paragraph("Table 3.2 — Endpoint Performance Detail", s["caption"]))
    _methodology_note(
        "Endpoint request counts derived from parsing the request field in the logs dataset. "
        "Response times estimated from response_size / 50 as a proxy metric.",
        story, s
    )
    _callout(
        f"CPU & memory at 95% is a ticking time bomb. One traffic spike will take the platform offline. "
        f"Immediate actions: (1) Add Redis/Memcached caching, (2) Enable auto-scaling, "
        f"(3) Investigate the {load['error_rate']:.0f}% error rate — fix top 5 failing endpoints first.",
        story, s, bg=colors.HexColor("#fff7ed"), border=C_ORANGE, icon="WARNING"
    )

    story.append(Paragraph("<b>3.3  Root Cause Analysis &amp; Remediation Plan</b>", s["subsec"]))
    story.append(Paragraph(
        f"A structured root-cause analysis was performed against each performance issue identified. "
        f"The following table provides actionable remediation steps categorised by immediacy — "
        f"immediate fixes that can be deployed within 24-48 hours, and long-term architectural "
        f"improvements for sustainable performance.",
        s["body"]
    ))
    li = [
        ["Issue", "Root Cause", "Immediate Fix (24-48h)", "Long-term Solution"],
        [f"Error rate {load['error_rate']:.1f}%", "App errors / bad routes",
         "Fix top 5 failing endpoints", "Circuit breakers & retry logic"],
        ["CPU at 95%", "No request caching, all DB hits",
         "Add Redis caching layer", "Auto-scale or upgrade server tier"],
        ["Memory at 95%", "Memory leaks / large payloads",
         "Profile & restart server processes", "Pagination & lazy data loading"],
        ["High auth endpoint traffic", "Brute-force or credential stuffing",
         "Add CAPTCHA & IP rate limiting", "WAF, DDoS protection, anomaly detection"],
        ["No response time SLA", "No performance monitoring",
         "Add APM tool (Datadog/New Relic)", "Define & enforce p99 latency SLAs"],
    ]
    lit = Table(li, colWidths=[W*0.16, W*0.20, W*0.30, W*0.34])
    lit.setStyle(_tbl(C_RED))
    story.append(lit)
    story.append(Paragraph("Table 3.3 — Load Issues &amp; Remediation Plan", s["caption"]))
    story.append(PageBreak())

    # 4. USER BEHAVIOUR
    _banner("4.  User Behaviour &amp; Retention Analysis", story, s, C_PURPLE, W)

    story.append(Paragraph("<b>4.1  Customer Overview &amp; Cohort Health</b>", s["subsec"]))
    story.append(Paragraph(
        f"User behaviour analysis examines purchase patterns, product preferences, demographic "
        f"segmentation, and the customer journey from first visit to purchase conversion. "
        f"This analysis is based on <b>{users['total_orders']:,} order records</b> spanning "
        f"multiple product categories and customer demographics.",
        s["body"]
    ))
    story.append(Paragraph(
        f"The headline metric is the <b>{users['retention_rate']}% customer retention rate</b> — "
        f"one of the strongest performance indicators in this report. In e-commerce, increasing "
        f"retention by just 5% can increase profits by 25-95% (Bain & Company benchmark). "
        f"With {repeat_u:,} repeat buyers representing {round(repeat_u/(repeat_u+onetime_u)*100,1)}% "
        f"of the customer base, the platform has built a highly loyal customer community. "
        f"This metric should be actively protected as a core competitive advantage.",
        s["body"]
    ))
    story.append(Paragraph(
        f"The average order value of <b>${users['avg_order_value']}</b> indicates a premium "
        f"customer segment with high purchasing power. Combined with the customer satisfaction "
        f"rating of <b>{users['avg_rating']}/5.0</b> — which exceeds the 4.0 benchmark for "
        f"high-performing e-commerce platforms — this suggests strong product-market fit and "
        f"an opportunity to introduce higher-margin premium offerings or subscription tiers.",
        s["body"]
    ))

    buyer_d = [
        ["Buyer Type", "Count", "Share %", "Avg Orders", "Business Value"],
        ["Repeat Buyers",   f"{repeat_u:,}",
         f"{round(repeat_u/(repeat_u+onetime_u)*100,1)}%", "2+", "HIGH — Core revenue base"],
        ["One-time Buyers", f"{onetime_u:,}",
         f"{round(onetime_u/(repeat_u+onetime_u)*100,1)}%", "1",  "MEDIUM — Re-engage via email"],
    ]
    bt = Table(buyer_d, colWidths=[W*0.22, W*0.14, W*0.14, W*0.16, W*0.34])
    bt.setStyle(_tbl(C_PURPLE))
    story.append(bt)
    story.append(Paragraph("Table 4.1 — Customer Segmentation by Purchase Behaviour", s["caption"]))

    story.append(Paragraph("<b>4.2  Revenue by Product Category</b>", s["subsec"]))
    story.append(Paragraph(
        f"Category revenue analysis reveals two dominant categories — <b>Books</b> and "
        f"<b>Clothing</b> — contributing approximately 30% each of total revenue. This near-equal "
        f"split between a knowledge product (Books) and a lifestyle product (Clothing) suggests "
        f"a dual-persona customer base: professional/educational buyers and everyday consumers. "
        f"Electronics and Home categories contribute approximately 20% each, indicating a "
        f"diversified product catalogue with no dangerous single-category concentration risk.",
        s["body"]
    ))
    story.append(HBarChart(top_cat, width=int(W), bar_height=12, spacing=4, color=C_PURPLE))
    story.append(Paragraph("Chart 4.1 — Revenue by Product Category", s["caption"]))
    cat_d = [["Category", "Revenue", "Share %", "Strategic Opportunity"]] + [
        [cat, f"${int(rev):,}", f"{round(rev/sum(v for _,v in top_cat)*100,1)}%",
         "Scale with subscriptions" if i==0 else ("Grow with personalisation" if i<=2 else "Niche premium")]
        for i,(cat,rev) in enumerate(top_cat)
    ]
    ct = Table(cat_d, colWidths=[W*0.24, W*0.22, W*0.16, W*0.38])
    ct.setStyle(_tbl(C_PURPLE))
    story.append(ct)
    story.append(Paragraph("Table 4.2 — Revenue by Product Category with Strategic Classification", s["caption"]))

    story.append(Paragraph("<b>4.3  Customer Conversion Funnel Analysis</b>", s["subsec"]))
    story.append(Paragraph(
        f"Conversion funnel analysis tracks the customer journey from initial platform visit "
        f"through to completed purchase, identifying at which stage the most significant "
        f"drop-offs occur and where optimisation effort will generate the highest ROI.",
        s["body"]
    ))
    jkeys = list(journey.keys())
    jvals = list(journey.values())
    fun_d = [["Stage", "Users", "Conv %", "Drop-off %", "Optimisation Action"]] + [
        [stage, f"{int(cnt):,}", f"{round(cnt/jvals[0]*100,1)}%",
         f"{round((1-cnt/jvals[i-1])*100,1)}%" if i>0 else "—",
         "Improve homepage UX" if i==1 else
         ("Reduce cart friction" if i==2 else
          ("Streamline checkout" if i==3 else "Monitor"))]
        for i,(stage,cnt) in enumerate(journey.items())
    ]
    ft = Table(fun_d, colWidths=[W*0.20, W*0.14, W*0.14, W*0.16, W*0.36])
    ft.setStyle(_tbl(C_PURPLE))
    story.append(ft)
    story.append(Paragraph("Table 4.3 — Customer Conversion Funnel with Drop-off Analysis", s["caption"]))
    story.append(Paragraph(
        f"The most significant conversion loss occurs between <b>Visited (250,000) and Viewed "
        f"Product (175,000)</b> — a 30% drop-off at the very first step. This indicates that "
        f"30% of visitors who reach the platform immediately leave without engaging with any "
        f"product. This is typically caused by poor first-impression UX, irrelevant landing "
        f"page content, or a mismatch between the ad/search message that drove the visit "
        f"and the actual page the user lands on. The second largest drop-off (57%) from "
        f"Viewed Product to Add to Cart represents the consideration-to-intent barrier "
        f"and is typically improved through better product descriptions, images, reviews, "
        f"and urgency triggers.",
        s["body"]
    ))
    _callout(
        "HIGHEST IMPACT OPPORTUNITY: Fixing the 30% visit-to-product-view drop-off "
        "would recover 75,000 potential customers per cycle. A/B test homepage layout, "
        "add personalised product recommendations, and ensure landing pages match ad messaging.",
        story, s, bg=colors.HexColor("#faf5ff"), border=C_PURPLE, icon="INSIGHT"
    )

    if segments:
        story.append(Paragraph("<b>4.4  Revenue by Customer Age Segment</b>", s["subsec"]))
        story.append(Paragraph(
            f"Demographic revenue segmentation reveals the <b>50+ age group as the highest "
            f"revenue-generating segment</b> at approximately 38.8% of total revenue. "
            f"This is a counter-intuitive finding for a digital platform and suggests the "
            f"product catalogue (Books, Home, Electronics) strongly appeals to mature, "
            f"higher-income consumers. The 36-50 segment contributes 28.2%, while "
            f"younger segments (18-35) collectively contribute approximately 33% — "
            f"representing the largest growth opportunity given their longer customer lifetime value.",
            s["body"]
        ))
        seg_s = sorted(segments.items(), key=lambda x: x[1], reverse=True)
        seg_d = [["Age Group", "Revenue", "Share %", "Marketing Priority", "Recommended Channel"]] + [
            [sg, f"${int(rv):,}", f"{round(rv/sum(segments.values())*100,1)}%",
             "Primary" if i==0 else ("Secondary" if i==1 else "Growth"),
             "Email & search" if i==0 else ("Social & display" if i<=2 else "Social & influencer")]
            for i,(sg,rv) in enumerate(seg_s)
        ]
        st2 = Table(seg_d, colWidths=[W*0.14, W*0.20, W*0.14, W*0.20, W*0.32])
        st2.setStyle(_tbl(C_PURPLE))
        story.append(st2)
        story.append(Paragraph("Table 4.4 — Revenue by Age Group with Channel Recommendations", s["caption"]))
    story.append(PageBreak())

    # 5. ADS
    _banner("5.  Advertisement Performance Analysis", story, s, C_PINK, W)

    story.append(Paragraph("<b>5.1  Campaign Performance Overview</b>", s["subsec"]))
    story.append(Paragraph(
        f"Advertising performance analysis evaluates the effectiveness of paid campaigns across "
        f"all ad formats in driving user engagement and conversion. The analysis covers "
        f"<b>{total_impr:,} total impressions</b> delivered across Banner, Video, Native, "
        f"and Social formats during the analysis period.",
        s["body"]
    ))
    story.append(Paragraph(
        f"The headline finding is deeply concerning from an ROI perspective. Despite "
        f"delivering {total_impr:,} impressions, the campaigns achieved a "
        f"<b>CTR of {ctr}%</b> — which, while appearing to meet the 2% benchmark, "
        f"represents a near-zero absolute click volume of just <b>{total_clicks:,} clicks</b>. "
        f"The ROAS of <b>{roas}x</b> (meaning every $1 spent generates ${roas} in revenue) "
        f"appears strong in isolation, but must be contextualised against the minimal click "
        f"volume — the high ROAS may reflect a small number of high-value conversions rather "
        f"than campaign scale. Without volume, ROAS is not a reliable performance indicator.",
        s["body"]
    ))
    story.append(Paragraph(
        f"The CPC of <b>${cpc}</b> falls within the acceptable $0.50-$2.00 range for digital "
        f"display advertising. However, the extremely low click volume means the absolute "
        f"cost-per-acquisition (CPA) is likely very high. If the platform is spending on CPM "
        f"(cost-per-thousand impressions) rather than CPC bidding, the majority of ad spend "
        f"is being consumed by impressions that generate no return.",
        s["body"]
    ))

    ab = [
        ["KPI", "Current", "Benchmark", "Gap", "Priority"],
        ["CTR",             f"{ctr}%",      "2.0%",       f"{round(2.0-ctr,2)}% below", "CRITICAL"],
        ["CPC",             f"${cpc}",      "$0.50-2.00", "Within range",                "OK"],
        ["ROAS",            f"{roas}x",     "4x+",        "Above benchmark",             "GOOD"],
        ["Conversion Rate", f"{conv_rate}%","2-3%",       f"{round(max(0,2-conv_rate),1)}% below","HIGH"],
        ["Total Clicks",    f"{total_clicks:,}","High volume","Volume too low",           "CRITICAL"],
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
    story.append(Paragraph("Table 5.1 — Ad Performance KPIs vs Industry Benchmarks", s["caption"]))

    story.append(Paragraph("<b>5.2  Ad Format Performance Breakdown</b>", s["subsec"]))
    story.append(Paragraph(
        f"Banner ads dominate impression volume at 35% share, followed by Video (25%), "
        f"Native (20%), and Social (20%). This format mix is sub-optimal given current "
        f"industry research: <b>Video ads consistently achieve 2-3x higher CTR than banner "
        f"ads</b>, and Native ads outperform display banners by 8.8x in click-through rate "
        f"(Sharethrough/IPG Media Lab research). The current heavy weighting toward Banner "
        f"ads — the worst-performing format — is a structural issue in the campaign strategy "
        f"that directly depresses overall CTR.",
        s["body"]
    ))
    fmt_d = [["Format", "Impressions", "Share %", "Est. Clicks", "Industry CTR", "Recommendation"]] + [
        [fmt, f"{int(imp):,}", f"{round(imp/total_impr*100,1)}%",
         f"{int(imp*ctr/100):,}",
         "0.1%" if fmt=="Banner" else ("1.8%" if fmt=="Video" else ("0.8%" if fmt=="Native" else "0.5%")),
         "Reduce budget" if fmt=="Banner" else ("Scale up — best ROI" if fmt=="Video" else "Maintain")]
        for fmt,imp in ad_formats.items()
    ]
    fmtt = Table(fmt_d, colWidths=[W*0.14, W*0.14, W*0.12, W*0.12, W*0.14, W*0.34])
    fmtt.setStyle(_tbl(C_PINK))
    story.append(fmtt)
    story.append(Paragraph("Table 5.2 — Ad Format Performance with Industry CTR Benchmarks", s["caption"]))

    story.append(Paragraph("<b>5.3  Post-Click Conversion Funnel</b>", s["subsec"]))
    story.append(Paragraph(
        f"The post-click funnel tracks user behaviour from the moment they click an ad "
        f"through to completed purchase. Understanding this funnel is essential for "
        f"identifying where ad-driven revenue is being lost after the initial click is captured.",
        s["body"]
    ))
    fsteps = [("Impressions",funnel.get("impressions",0)),("Clicks",funnel.get("clicks",0)),
              ("Landing",funnel.get("landing",0)),("Add to Cart",funnel.get("add_to_cart",0)),
              ("Checkout",funnel.get("checkout",0)),("Purchase",funnel.get("purchase",0))]
    cv_d = [["Stage","Users","Conv %","Drop-off","Analysis"]] + [
        [st, f"{int(v):,}", f"{round(v/fsteps[0][1]*100,2)}%" if fsteps[0][1] else "0%",
         f"-{round((1-v/fsteps[i-1][1])*100,1)}%" if i>0 and fsteps[i-1][1] else "—",
         "Click rate" if i==1 else
         ("Landing quality" if i==2 else
          ("Product appeal" if i==3 else
           ("Checkout UX" if i==4 else "Payment trust")))]
        for i,(st,v) in enumerate(fsteps)
    ]
    cvt = Table(cv_d, colWidths=[W*0.18, W*0.14, W*0.14, W*0.14, W*0.40])
    cvt.setStyle(_tbl(C_PINK))
    story.append(cvt)
    story.append(Paragraph("Table 5.3 — Post-Click Ad Conversion Funnel", s["caption"]))
    _callout(
        "IMMEDIATE ACTION: (1) Shift 40% of Banner budget to Video format. "
        "(2) A/B test 3 creatives per format with different CTAs. "
        "(3) Target the 50+ demographic — highest revenue segment. "
        "(4) Ensure ad landing pages match the specific product shown in the creative. "
        "(5) Add retargeting campaigns for users who visited but did not purchase.",
        story, s, bg=colors.HexColor("#fff1f2"), border=C_RED, icon="ACTION REQUIRED"
    )
    story.append(PageBreak())

    # 6. SECURITY
    _banner("6.  Security &amp; Threat Analysis", story, s, C_RED, W)

    story.append(Paragraph("<b>6.1  Security Posture Assessment</b>", s["subsec"]))
    sec_rating = "CRITICAL" if sec_score<50 else ("MODERATE" if sec_score<70 else "GOOD")
    story.append(Paragraph(
        f"Platform security analysis evaluates the current threat exposure, active incident "
        f"status, and defensive capability of the TrafficIQ infrastructure. The overall "
        f"security posture is rated <b>{sec_rating}</b> with a composite score of "
        f"<b>{sec_score:.1f}/100</b>. A score of 70+ is considered acceptable for a production "
        f"platform; the current score of {sec_score:.1f} indicates meaningful risk that requires "
        f"structured remediation.",
        s["body"]
    ))
    story.append(Paragraph(
        f"The firewall is <b>{fw_status}</b> and has successfully blocked "
        f"<b>{threats_blk:,} malicious requests</b> — demonstrating that basic perimeter "
        f"defences are functioning. However, the presence of <b>{crit_alerts} critical "
        f"unresolved alerts</b> and <b>{susp_ips_n} suspicious IP addresses</b> with "
        f"abnormal request volumes indicates that some threats are penetrating the perimeter "
        f"and require active investigation. The <b>{fail_logins} failed login attempts</b> "
        f"suggest credential-stuffing or brute-force activity targeting user accounts.",
        s["body"]
    ))
    story.append(Paragraph(
        f"The most alarming finding is the <b>{err_5xx:,} server-side (5xx) errors</b> — "
        f"these represent cases where the server received a request but failed to process it "
        f"correctly. At this volume, 5xx errors suggest either severe application bugs, "
        f"database connectivity failures, or a sustained denial-of-service condition. "
        f"Combined with the {err_4xx:,} client-side (4xx) errors (unauthorised access "
        f"attempts, not-found requests), the total error volume of {err_4xx+err_5xx:,} "
        f"accounts for nearly the entirety of the {load['error_rate']:.1f}% overall error rate.",
        s["body"]
    ))

    sm = [
        ["Security KPI", "Value", "Risk", "Description"],
        ["Security Score",    f"{sec_score:.1f}/100",
         "CRITICAL" if sec_score<50 else "HIGH", "Overall security health composite score"],
        ["Threats Blocked",   f"{threats_blk:,}",    "INFO",
         "Total requests blocked by firewall rules"],
        ["Critical Alerts",   str(crit_alerts),
         "HIGH" if crit_alerts>0 else "OK",   "Active unresolved high-severity alerts"],
        ["4xx Client Errors", f"{err_4xx:,}",
         "HIGH" if err_4xx>10000 else "OK",   "Unauthorised access & not-found requests"],
        ["5xx Server Errors", f"{err_5xx:,}",
         "CRITICAL" if err_5xx>10000 else "HIGH", "Server processing failures"],
        ["Suspicious IPs",    str(susp_ips_n),
         "HIGH" if susp_ips_n>0 else "OK",   "IP addresses exceeding 100 requests threshold"],
        ["Failed Logins",     str(fail_logins),
         "HIGH" if fail_logins>10 else "OK", "Potential brute-force on user accounts"],
    ]
    smt = Table(sm, colWidths=[W*0.24, W*0.16, W*0.14, W*0.46])
    sm_s = _tbl(C_RED)
    for i, row in enumerate(sm[1:], 1):
        bg, tc = color_map2.get(row[2],(C_LIGHT,C_MUTED))
        sm_s.add("BACKGROUND",(2,i),(2,i),bg)
        sm_s.add("TEXTCOLOR", (2,i),(2,i),tc)
    smt.setStyle(sm_s)
    story.append(smt)
    story.append(Paragraph("Table 6.1 — Security KPI Assessment with Risk Classification", s["caption"]))

    story.append(Paragraph("<b>6.2  Threat Activity Log &amp; Response Plan</b>", s["subsec"]))
    story.append(Paragraph(
        f"The security activity log catalogues all detected threat types during the analysis "
        f"period, their observed frequency, and assigned severity. For each threat category, "
        f"a response action has been assigned based on industry-standard incident response "
        f"frameworks (NIST SP 800-61, OWASP guidelines).",
        s["body"]
    ))
    act_d = [["Threat Type","Count","Severity","Status","Response Action"]] + [
        [x["name"], str(x["count"]), x["level"],
         "ACTIVE" if x["count"]>0 else "CLEAR",
         "Investigate & patch immediately" if x["level"]=="Critical" else
         ("Monitor with alerting" if x["level"]=="High" else "Log & review weekly")]
        for x in activity_log
    ]
    att = Table(act_d, colWidths=[W*0.26, W*0.10, W*0.12, W*0.12, W*0.40])
    at_s = _tbl(C_RED)
    for i, row in enumerate(act_d[1:], 1):
        if row[2] == "Critical":
            at_s.add("BACKGROUND",(0,i),(-1,i),C_BAD)
        elif row[2] == "High":
            at_s.add("BACKGROUND",(0,i),(-1,i),C_WARN)
    att.setStyle(at_s)
    story.append(att)
    story.append(Paragraph("Table 6.2 — Security Activity Log with NIST-Aligned Response Actions", s["caption"]))

    if susp_ip_lst:
        story.append(Paragraph("<b>6.3  Flagged IP Address Analysis</b>", s["subsec"]))
        story.append(Paragraph(
            f"IP reputation analysis identified <b>{len(susp_ip_lst)} IP addresses</b> "
            f"exhibiting anomalous request volumes exceeding the 100-request threshold. "
            f"High-volume requests from a single IP are a strong indicator of automated "
            f"bot traffic, credential stuffing, web scraping, or reconnaissance activity. "
            f"The top offending IPs should be immediately added to the firewall blocklist "
            f"while further investigation is conducted to determine the nature and origin "
            f"of the traffic.",
            s["body"]
        ))
        story.append(HBarChart(susp_ip_lst, width=int(W), bar_height=12, spacing=4, color=C_RED))
        story.append(Paragraph("Chart 6.1 — Flagged IP Addresses by Request Volume", s["caption"]))
        sp_d = [["IP Address","Requests","Risk Level","Geo Lookup","Recommended Action"]] + [
            [ip, f"{int(cnt):,}",
             "CRITICAL" if cnt>200 else "HIGH",
             "Investigate", "Block in firewall immediately" if cnt>200 else "Rate limit to 10 req/min"]
            for ip,cnt in susp_ip_lst
        ]
        sp_t = Table(sp_d, colWidths=[W*0.24, W*0.12, W*0.14, W*0.14, W*0.36])
        sp_s = _tbl(C_RED)
        for i, row in enumerate(sp_d[1:], 1):
            if row[2]=="CRITICAL":
                sp_s.add("BACKGROUND",(0,i),(-1,i),C_BAD)
        sp_t.setStyle(sp_s)
        story.append(sp_t)
        story.append(Paragraph("Table 6.3 — Flagged IP Addresses &amp; Remediation Actions", s["caption"]))
    _callout(
        f"IMMEDIATE: Block top 2 IPs via firewall rules within 24 hours. "
        f"Fix {err_5xx:,} server errors — start with top 5 endpoints from Section 3. "
        f"Enable real-time SIEM alerting for: failed login spikes, new suspicious IPs, "
        f"and 5xx error rate exceeding 5%.",
        story, s, bg=colors.HexColor("#fff1f2"), border=C_RED, icon="CRITICAL ACTION"
    )
    story.append(PageBreak())

    # 7. RECOMMENDATIONS
    _banner("7.  Key Findings &amp; Business Recommendations", story, s, C_DARK, W)

    story.append(Paragraph("<b>7.1  Executive Summary of Findings</b>", s["subsec"]))
    story.append(Paragraph(
        f"Across all five analytical pillars, the platform demonstrates a clear duality: "
        f"<b>strong commercial fundamentals undermined by operational and technical deficiencies</b>. "
        f"The business has built an exceptional customer base — high retention, high average order "
        f"values, strong product satisfaction — that is currently being constrained by infrastructure "
        f"fragility, ineffective advertising, and security exposure. The good news is that all "
        f"identified issues are fixable with targeted investment and focused engineering effort.",
        s["body"]
    ))
    story.append(Paragraph(
        f"The estimated revenue impact of the identified issues is significant. The "
        f"{load['error_rate']:.0f}% server error rate means approximately 1 in 2 user "
        f"interactions fails, directly causing session abandonment and lost sales. "
        f"The 30% first-funnel drop-off in user behaviour represents 75,000 potential "
        f"customers per analysis cycle who are not engaging with products. "
        f"The near-zero ad click volume means advertising spend is generating minimal "
        f"incremental revenue. Collectively, these three issues alone likely represent "
        f"30-50% of potential platform revenue that is currently unrealised.",
        s["body"]
    ))

    story.append(Paragraph("<b>7.2  Priority Action Matrix</b>", s["subsec"]))
    pm = [
        ["Priority", "Area", "Key Finding", "Recommended Action", "Owner", "Timeline"],
        ["P1 — CRITICAL","Security",
         f"Score {sec_score:.0f}/100, {err_5xx:,} server errors",
         "Block flagged IPs, patch top error endpoints", "DevOps", "This week"],
        ["P1 — CRITICAL","Ad Performance",
         f"CTR {ctr}% — creatives not resonating",
         "A/B test new creatives, shift budget to Video", "Marketing", "This week"],
        ["P2 — HIGH","Infrastructure",
         "CPU & Memory at 95% — near-failure",
         "Add Redis caching, enable auto-scaling", "Engineering", "This month"],
        ["P2 — HIGH","Traffic",
         "90% traffic from only 2 sources",
         "Invest in social & referral growth channels", "Marketing", "This month"],
        ["P3 — MEDIUM","Conversion",
         "30% drop-off at first funnel stage",
         "Redesign homepage, add product recommendations", "Product", "Q3 2026"],
        ["P3 — MEDIUM","User Behaviour",
         f"{onetime_u:,} one-time buyers not returning",
         "Launch re-engagement email drip campaign", "CRM", "Q3 2026"],
        ["P4 — LOW","Traffic",
         "Referral contributes only 10%",
         "Build partner & affiliate programme", "Business Dev", "6 months"],
    ]
    pmt = Table(pm, colWidths=[W*0.14, W*0.12, W*0.22, W*0.24, W*0.12, W*0.16])
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
    story.append(Paragraph("Table 7.1 — Prioritised Action Matrix with Ownership &amp; Timelines", s["caption"]))

    story.append(Paragraph("<b>7.3  Strengths to Protect &amp; Leverage</b>", s["subsec"]))
    story.append(Paragraph(
        f"The following platform strengths represent competitive advantages that should be "
        f"actively protected, measured monthly, and used as the foundation for growth strategy.",
        s["body"]
    ))
    strengths_detail = [
        (f"Retention {users['retention_rate']}%",
         f"World-class retention well above 30-40% industry avg. Protect by improving post-purchase experience."),
        (f"AOV ${users['avg_order_value']}",
         f"Premium customer base. Leverage with upselling, bundles, and loyalty rewards."),
        (f"ROAS {roas}x",
         f"Strong return on ad spend when users do engage. Scale by fixing CTR issue — same ROAS with more volume = major revenue."),
        (f"Rating {users['avg_rating']}/5.0",
         f"Excellent customer satisfaction. Use testimonials in ad creatives to improve CTR."),
        ("Predictable traffic pattern",
         "Clear 09:00-17:00 peak enables precision scheduling of campaigns, releases, and maintenance."),
    ]
    str_data = [["Strength", "Value", "How to Leverage"]] + \
               [[s_name, val, tip] for s_name, val, tip in
                [(n.split(" ")[0], n, t) for n, t in strengths_detail]]
    str_data = [["Strength", "How to Leverage"]] + \
               [[name, tip] for name, tip in strengths_detail]
    str_t = Table(str_data, colWidths=[W*0.26, W*0.74])
    str_s = _tbl(C_GREEN)
    for i in range(1, len(str_data)):
        str_s.add("BACKGROUND",(0,i),(-1,i), C_GOOD if i%2==0 else C_WHITE)
    str_t.setStyle(str_s)
    story.append(str_t)
    story.append(Paragraph("Table 7.2 — Platform Strengths &amp; Leverage Strategies", s["caption"]))

    story.append(Paragraph("<b>7.4  Critical Weaknesses Requiring Immediate Attention</b>", s["subsec"]))
    story.append(Paragraph(
        f"The following weaknesses represent direct revenue risk or platform integrity threats "
        f"that cannot be deferred without accepting significant business consequences.",
        s["body"]
    ))
    weak_data = [["Weakness", "Business Impact", "Urgency"]] + [
        ["Security score 50.8/100",
         "Data breach risk, regulatory liability, reputational damage", "THIS WEEK"],
        [f"Error rate {load['error_rate']:.1f}%",
         "Every 2nd user interaction fails — direct revenue loss", "THIS WEEK"],
        [f"Ad CTR {ctr}%",
         "Ad budget generates impressions not revenue — ROI destruction", "THIS WEEK"],
        ["CPU/Memory at 95%",
         "One traffic spike = complete platform outage", "THIS MONTH"],
    ]
    wt = Table(weak_data, colWidths=[W*0.30, W*0.46, W*0.24])
    wk_s = _tbl(C_RED)
    for i in range(1, len(weak_data)):
        wk_s.add("BACKGROUND",(0,i),(-1,i), C_BAD if i<=3 else C_WARN)
        wk_s.add("TEXTCOLOR", (2,i),(2,i),  C_BAD_T if i<=3 else C_WARN_T)
        wk_s.add("FONTNAME",  (2,i),(2,i),  "Helvetica-Bold")
    wt.setStyle(wk_s)
    story.append(wt)
    story.append(Paragraph("Table 7.3 — Critical Weaknesses with Business Impact Assessment", s["caption"]))

    story.append(Paragraph("<b>7.5  30-60-90 Day Roadmap</b>", s["subsec"]))
    roadmap = [
        ["Timeframe", "Focus Area", "Key Deliverables", "Expected Outcome"],
        ["Days 1-30\n(Immediate)", "Security & Stability",
         "Block flagged IPs, fix top error endpoints, add Redis cache, A/B test ad creatives",
         "Error rate < 5%, security score > 65, first ad CTR improvements"],
        ["Days 31-60\n(Stabilise)", "Performance & Growth",
         "Auto-scaling configured, social media campaigns live, re-engagement email launched",
         "CPU < 80%, referral traffic +5%, one-time buyer recovery +10%"],
        ["Days 61-90\n(Optimise)", "Conversion & Revenue",
         "Homepage UX redesign, product recommendation engine, affiliate programme beta",
         "Funnel drop-off < 20%, referral traffic +10%, new revenue stream from affiliates"],
    ]
    rt = Table(roadmap, colWidths=[W*0.16, W*0.16, W*0.38, W*0.30])
    rt_s = _tbl(C_DARK)
    rt_s.add("BACKGROUND",(0,1),(-1,1), colors.HexColor("#fee2e2"))
    rt_s.add("BACKGROUND",(0,2),(-1,2), colors.HexColor("#fef9c3"))
    rt_s.add("BACKGROUND",(0,3),(-1,3), colors.HexColor("#dcfce7"))
    rt.setStyle(rt_s)
    story.append(rt)
    story.append(Paragraph("Table 7.4 — 30-60-90 Day Strategic Roadmap", s["caption"]))
    story.append(PageBreak())

    # APPENDIX
    _banner("Appendix — Full Key Performance Indicators", story, s, C_SLATE, W)

    story.append(Paragraph(
        f"The following table provides a complete reference of all platform KPIs measured "
        f"during the analysis period, alongside industry benchmarks and status classifications. "
        f"This table is intended as a quick-reference dashboard for executive review and "
        f"should be updated with each reporting cycle to track improvement over time.",
        s["body"]
    ))

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
    story.append(Paragraph("Table A.1 — Comprehensive KPI Reference with Benchmarks &amp; Status Classification", s["caption"]))

    story.append(Spacer(1, 0.8*cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=C_BORDER))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        f"TrafficIQ Analytics Platform  |  MediCaps University  |  "
        f"Report generated {date_str} at {time_str}  |  CONFIDENTIAL — FOR INTERNAL USE ONLY",
        s["footer"]
    ))
    story.append(Paragraph(
        "This report was automatically generated by the TrafficIQ reporting engine. "
        "Data reflects the most recent analysis cycle. For questions contact the platform administrator.",
        s["footer"]
    ))

    doc.build(story)
    return output_path