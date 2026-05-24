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
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

# ── Analysis imports ──────────────────────────────────────────────────────────
from traffic_analysis       import run_analysis as _traffic
from load_analysis          import run_analysis as _load
from user_behavior_analysis import run_analysis as _users
from ad_analytics           import run_analysis as _ads
from security_logs          import run_analysis as _security

# ── Colour palette ────────────────────────────────────────────────────────────
C_PURPLE   = colors.HexColor("#7c3aed")
C_BLUE     = colors.HexColor("#3b82f6")
C_TEAL     = colors.HexColor("#10b981")
C_ORANGE   = colors.HexColor("#f59e0b")
C_RED      = colors.HexColor("#ef4444")
C_PINK     = colors.HexColor("#ec4899")
C_DARK     = colors.HexColor("#0f172a")
C_SLATE    = colors.HexColor("#334155")
C_MUTED    = colors.HexColor("#64748b")
C_LIGHT    = colors.HexColor("#f8fafc")
C_WHITE    = colors.white
C_BORDER   = colors.HexColor("#e2e8f0")
C_ROW_ALT  = colors.HexColor("#f1f5f9")


def _styles():
    base = getSampleStyleSheet()

    def ps(name, **kw):
        return ParagraphStyle(name=name, parent=base["Normal"], **kw)

    return {
        "cover_title": ps("CoverTitle", fontSize=30, textColor=C_WHITE,
                          alignment=TA_CENTER, spaceAfter=8, fontName="Helvetica-Bold"),
        "cover_sub":   ps("CoverSub",   fontSize=13, textColor=colors.HexColor("#cbd5e1"),
                          alignment=TA_CENTER, spaceAfter=4),
        "cover_meta":  ps("CoverMeta",  fontSize=10, textColor=colors.HexColor("#94a3b8"),
                          alignment=TA_CENTER),
        "section":     ps("Section",    fontSize=15, textColor=C_PURPLE,
                          fontName="Helvetica-Bold", spaceBefore=18, spaceAfter=6),
        "body":        ps("Body",       fontSize=10, textColor=C_SLATE,
                          leading=16, spaceAfter=8),
        "table_hdr":   ps("TblHdr",     fontSize=9, textColor=C_WHITE,
                          fontName="Helvetica-Bold", alignment=TA_LEFT),
        "table_cell":  ps("TblCell",    fontSize=9, textColor=C_SLATE),
        "caption":     ps("Caption",    fontSize=8, textColor=C_MUTED,
                          spaceAfter=12, spaceBefore=2),
        "kpi_val":     ps("KpiVal",     fontSize=14, textColor=C_PURPLE,
                          fontName="Helvetica-Bold", alignment=TA_CENTER),
        "kpi_lbl":     ps("KpiLbl",     fontSize=8,  textColor=C_MUTED,
                          alignment=TA_CENTER),
    }


def _tbl_style(header_color=C_PURPLE, alt=True):
    cmds = [
        ("BACKGROUND",    (0, 0), (-1,  0), header_color),
        ("TEXTCOLOR",     (0, 0), (-1,  0), C_WHITE),
        ("FONTNAME",      (0, 0), (-1,  0), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [C_WHITE, C_ROW_ALT] if alt else [C_WHITE]),
        ("ALIGN",         (0, 0), (-1, -1), "LEFT"),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("GRID",          (0, 0), (-1, -1), 0.4, C_BORDER),
        ("ROWBACKGROUND", (0, 0), (-1,  0), header_color),
    ]
    return TableStyle(cmds)


def _hr(color=C_BORDER):
    return HRFlowable(width="100%", thickness=0.5, color=color, spaceAfter=8, spaceBefore=4)


def _section(title, story, s, color=C_PURPLE):
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(title, s["section"]))
    story.append(_hr(color))


def generate_business_report(output_path: str, data_dir: str):
    now = datetime.datetime.now()

    # ── Fetch data ────────────────────────────────────────────────────────────
    traffic  = _traffic(data_dir)
    load     = _load(data_dir)
    users    = _users(data_dir)
    ads      = _ads(data_dir)
    security = _security(data_dir)

    # ── Derived values ────────────────────────────────────────────────────────
    hourly       = traffic["hourly_traffic"]
    peak_hour    = max(hourly, key=hourly.get)
    peak_traffic = hourly[peak_hour]
    low_hour     = min(hourly, key=hourly.get)
    low_traffic  = hourly[low_hour]
    sources      = traffic.get("traffic_sources", {})
    geo          = traffic.get("geo_distribution", {})
    total_sess   = int(traffic["total_sessions"])
    top_geo      = sorted(geo.items(), key=lambda x: x[1], reverse=True)[:5]
    top_src      = sorted(sources.items(), key=lambda x: x[1], reverse=True)

    funnel          = ads.get("funnel", {})
    ad_formats      = ads.get("ad_formats", {})
    ctr             = ads.get("ctr", 0)
    roas            = ads.get("roas", 0)
    cpc             = ads.get("cpc", 0)
    total_impr      = ads.get("total_impressions", 0)
    total_clicks    = funnel.get("clicks", 0)
    total_conv      = funnel.get("checkout", 0)
    conv_rate       = round(total_conv / total_clicks * 100, 2) if total_clicks else 0

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

    repeat_users    = users["buyers"].get("Repeat", 0)
    onetime_users   = users["buyers"].get("One-time", 0)
    journey         = users.get("journey", {})
    category        = users.get("category", {})
    top_cat         = sorted(category.items(), key=lambda x: x[1], reverse=True)
    top_eps         = list(load.get("top_endpoints", {}).items())[:5]
    susp_ip_list    = list(load.get("suspicious_ips", {}).items())[:4]

    s = _styles()

    # ── Doc setup ─────────────────────────────────────────────────────────────
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm,   bottomMargin=2*cm,
        title="TrafficIQ Business Intelligence Report",
        author="TrafficIQ Analytics Platform",
    )
    story = []
    W = A4[0] - 4*cm   # usable width

    # ════════════════════════════════════════════════════════════════════════
    # COVER PAGE
    # ════════════════════════════════════════════════════════════════════════
    cover_tbl = Table(
        [[Paragraph("TrafficIQ", s["cover_title"])],
         [Paragraph("Business Intelligence Report", s["cover_sub"])],
         [Paragraph("Executive Analytics &amp; Platform Summary", s["cover_sub"])],
         [Spacer(1, 0.4*cm)],
         [Paragraph(f"Generated: {now.strftime('%B %d, %Y  |  %H:%M')}", s["cover_meta"])],
         [Paragraph("MediCaps University · TrafficIQ Analytics Platform", s["cover_meta"])]],
        colWidths=[W]
    )
    cover_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), C_DARK),
        ("TOPPADDING",    (0, 0), (-1, -1), 14),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
        ("LEFTPADDING",   (0, 0), (-1, -1), 20),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 20),
        ("ROUNDEDCORNERS", [8]),
    ]))
    story.append(cover_tbl)
    story.append(Spacer(1, 1*cm))

    # ── KPI Scorecard grid (2 rows × 4 cols) ──────────────────────────────
    kpis = [
        ("Total Sessions",   f"{total_sess:,}",              C_BLUE),
        ("Total Requests",   f"{load['total_requests']:,}",  C_ORANGE),
        ("Total Orders",     f"{users['total_orders']:,}",   C_TEAL),
        ("Retention Rate",   f"{users['retention_rate']}%",  C_PURPLE),
        ("Avg Rating",       f"{users['avg_rating']}/5.0",   C_ORANGE),
        ("ROAS",             f"{roas}x",                     C_PINK),
        ("Security Score",   f"{security_score:.1f}/100",    C_TEAL),
        ("Threats Blocked",  f"{threats_blocked:,}",         C_RED),
    ]

    def kpi_cell(val, lbl, color):
        return [Paragraph(val, ParagraphStyle("kv", fontSize=15, textColor=color,
                          fontName="Helvetica-Bold", alignment=TA_CENTER)),
                Paragraph(lbl, s["kpi_lbl"])]

    kpi_data = [
        [kpi_cell(v, l, c) for l, v, c in kpis[:4]],
        [kpi_cell(v, l, c) for l, v, c in kpis[4:]],
    ]
    kpi_tbl = Table(kpi_data, colWidths=[W/4]*4, rowHeights=[1.4*cm, 1.4*cm])
    kpi_tbl.setStyle(TableStyle([
        ("BOX",          (0, 0), (-1, -1), 0.5, C_BORDER),
        ("INNERGRID",    (0, 0), (-1, -1), 0.5, C_BORDER),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",   (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 6),
        ("ROWBACKGROUNDS",(0, 0), (-1, -1), [C_LIGHT, C_WHITE]),
    ]))
    story.append(kpi_tbl)
    story.append(PageBreak())

    # ════════════════════════════════════════════════════════════════════════
    # 1. EXECUTIVE SUMMARY
    # ════════════════════════════════════════════════════════════════════════
    _section("1.  Executive Summary", story, s, C_PURPLE)
    story.append(Paragraph(
        f"This report provides a comprehensive performance overview of the TrafficIQ Analytics Platform. "
        f"During the reporting period the platform recorded <b>{total_sess:,} total sessions</b> with an "
        f"average session duration of <b>{traffic['avg_session_duration']} seconds</b> and "
        f"<b>{traffic['pages_per_session']} pages per session</b>. The bounce rate stood at "
        f"<b>{traffic['bounce_rate']}%</b>. Server infrastructure processed <b>{load['total_requests']:,} "
        f"requests</b> at an average latency of <b>{load['avg_response_time']:.0f} ms</b> with an error rate "
        f"of <b>{load['error_rate']:.2f}%</b>. Ad campaigns delivered <b>{total_impr:,} impressions</b>, "
        f"<b>{total_clicks:,} clicks</b>, and <b>{total_conv:,} conversions</b> at a ROAS of <b>{roas}x</b>. "
        f"Security systems blocked <b>{threats_blocked:,} threats</b>; firewall is <b>{firewall_status}</b>.",
        s["body"]
    ))

    # ════════════════════════════════════════════════════════════════════════
    # 2. TRAFFIC ANALYSIS
    # ════════════════════════════════════════════════════════════════════════
    _section("2.  Traffic Analysis", story, s, C_BLUE)
    story.append(Paragraph(
        f"Traffic peaked at <b>{peak_hour}:00</b> with <b>{int(peak_traffic):,} page views</b> and was "
        f"lowest at <b>{low_hour}:00</b> ({int(low_traffic):,} views) — a swing of "
        f"<b>{int(peak_traffic - low_traffic):,} views</b>. "
        f"Search was the dominant channel at "
        f"<b>{round(sources.get('Search',0)/total_sess*100,1)}%</b>, followed by Direct "
        f"({round(sources.get('Direct',0)/total_sess*100,1)}%), Social "
        f"({round(sources.get('Social',0)/total_sess*100,1)}%), and Referral "
        f"({round(sources.get('Referral',0)/total_sess*100,1)}%).",
        s["body"]
    ))

    # Traffic sources table
    src_data = [["Source", "Sessions", "Share %"]] + [
        [src, f"{int(v):,}", f"{round(int(v)/total_sess*100,1)}%"] for src, v in top_src
    ]
    src_tbl = Table(src_data, colWidths=[W*0.4, W*0.3, W*0.3])
    src_tbl.setStyle(_tbl_style(C_BLUE))
    story.append(src_tbl)
    story.append(Paragraph("Table 2.1 — Traffic by Source", s["caption"]))

    # Geo table
    geo_data = [["Country", "Sessions", "Share %"]] + [
        [c, f"{int(v):,}", f"{round(int(v)/total_sess*100,1)}%"] for c, v in top_geo
    ]
    geo_tbl = Table(geo_data, colWidths=[W*0.4, W*0.3, W*0.3])
    geo_tbl.setStyle(_tbl_style(C_BLUE))
    story.append(geo_tbl)
    story.append(Paragraph("Table 2.2 — Top 5 Countries by Session Volume", s["caption"]))

    # ════════════════════════════════════════════════════════════════════════
    # 3. SERVER LOAD & PERFORMANCE
    # ════════════════════════════════════════════════════════════════════════
    _section("3.  Server Load &amp; Performance", story, s, C_ORANGE)
    story.append(Paragraph(
        f"The platform handled <b>{load['total_requests']:,} requests</b> with an average CPU utilisation "
        f"of <b>{load['avg_cpu_usage']}%</b>, memory <b>{load['memory_usage']:.0f}%</b>, network "
        f"<b>{load['network_usage']}%</b>, and average response time <b>{load['avg_response_time']:.0f} ms</b>. "
        f"The overall error rate was <b>{load['error_rate']:.2f}%</b>.",
        s["body"]
    ))

    ep_data = [["Endpoint", "Requests"]] + [
        [ep, f"{int(h):,}"] for ep, h in top_eps
    ]
    ep_tbl = Table(ep_data, colWidths=[W*0.65, W*0.35])
    ep_tbl.setStyle(_tbl_style(C_ORANGE))
    story.append(ep_tbl)
    story.append(Paragraph("Table 3.1 — Top 5 Most-Hit Endpoints", s["caption"]))

    # ════════════════════════════════════════════════════════════════════════
    # 4. USER BEHAVIOUR & RETENTION
    # ════════════════════════════════════════════════════════════════════════
    _section("4.  User Behaviour &amp; Retention", story, s, C_PURPLE)
    story.append(Paragraph(
        f"The platform processed <b>{users['total_orders']:,} orders</b> with an average order value of "
        f"<b>${users['avg_order_value']}</b> and a customer rating of <b>{users['avg_rating']}/5.0</b>. "
        f"Retention stands at <b>{users['retention_rate']}%</b> — "
        f"<b>{repeat_users:,} repeat buyers</b> vs <b>{onetime_users:,} one-time buyers</b>.",
        s["body"]
    ))

    # Funnel table
    journey_vals = list(journey.values())
    jour_data = [["Funnel Stage", "Users", "Drop-off"]] + [
        [stage, f"{int(cnt):,}", f"{round((1 - cnt/journey_vals[0])*100,1)}%"]
        for stage, cnt in journey.items()
    ]
    jour_tbl = Table(jour_data, colWidths=[W*0.4, W*0.3, W*0.3])
    jour_tbl.setStyle(_tbl_style(C_PURPLE))
    story.append(jour_tbl)
    story.append(Paragraph("Table 4.1 — Customer Conversion Funnel", s["caption"]))

    # Category revenue table
    cat_data = [["Category", "Revenue"]] + [
        [cat, f"${int(rev):,}"] for cat, rev in top_cat
    ]
    cat_tbl = Table(cat_data, colWidths=[W*0.5, W*0.5])
    cat_tbl.setStyle(_tbl_style(C_PURPLE))
    story.append(cat_tbl)
    story.append(Paragraph("Table 4.2 — Revenue by Product Category", s["caption"]))

    # ════════════════════════════════════════════════════════════════════════
    # 5. AD PERFORMANCE
    # ════════════════════════════════════════════════════════════════════════
    _section("5.  Ad Performance", story, s, C_PINK)
    story.append(Paragraph(
        f"Ad campaigns achieved a CTR of <b>{ctr}%</b>, CPC of <b>${cpc}</b>, and ROAS of <b>{roas}x</b>. "
        f"From <b>{total_impr:,} impressions</b> the funnel delivered <b>{total_clicks:,} clicks</b> → "
        f"<b>{funnel.get('landing',0):,} landing page visits</b> → "
        f"<b>{funnel.get('add_to_cart',0):,} cart adds</b> → "
        f"<b>{total_conv:,} checkouts</b>. "
        f"End-to-end conversion rate: <b>{conv_rate}%</b>.",
        s["body"]
    ))

    fmt_data = [["Ad Format", "Impressions", "Share %"]] + [
        [fmt, f"{int(imp):,}", f"{round(int(imp)/total_impr*100,1)}%"]
        for fmt, imp in ad_formats.items()
    ]
    fmt_tbl = Table(fmt_data, colWidths=[W*0.4, W*0.3, W*0.3])
    fmt_tbl.setStyle(_tbl_style(C_PINK))
    story.append(fmt_tbl)
    story.append(Paragraph("Table 5.1 — Impressions by Ad Format", s["caption"]))

    # ════════════════════════════════════════════════════════════════════════
    # 6. SECURITY REPORT
    # ════════════════════════════════════════════════════════════════════════
    _section("6.  Security Report", story, s, C_RED)
    story.append(Paragraph(
        f"The platform's security score is <b>{security_score:.1f}/100</b>. Firewall: <b>{firewall_status}</b>. "
        f"<b>{threats_blocked:,} threats</b> were blocked with <b>{critical_alerts} critical alert(s)</b>. "
        f"Client-side (4xx) errors: <b>{errors_4xx:,}</b>. Server-side (5xx) errors: <b>{errors_5xx:,}</b>. "
        f"Suspicious IPs detected: <b>{susp_ips}</b>. Failed logins: <b>{failed_logins}</b>.",
        s["body"]
    ))

    act_data = [["Security Event", "Count", "Severity"]] + [
        [x["name"], str(x["count"]), x["level"]] for x in activity_log
    ]
    act_tbl = Table(act_data, colWidths=[W*0.5, W*0.2, W*0.3])
    act_tbl.setStyle(_tbl_style(C_RED))
    story.append(act_tbl)
    story.append(Paragraph("Table 6.1 — Security Activity Log", s["caption"]))

    if susp_ip_list:
        susp_data = [["Flagged IP Address", "Request Count"]] + [
            [ip, f"{int(cnt):,}"] for ip, cnt in susp_ip_list
        ]
        susp_tbl = Table(susp_data, colWidths=[W*0.6, W*0.4])
        susp_tbl.setStyle(_tbl_style(C_RED))
        story.append(susp_tbl)
        story.append(Paragraph("Table 6.2 — Top Flagged IPs", s["caption"]))

    # ════════════════════════════════════════════════════════════════════════
    # APPENDIX — Full KPI Table
    # ════════════════════════════════════════════════════════════════════════
    story.append(PageBreak())
    _section("Appendix — Full Key Performance Indicators", story, s, C_SLATE)

    kpi_full = [
        ["Category",     "Metric",                     "Value"],
        ["Traffic",      "Total Sessions",              f"{total_sess:,}"],
        ["Traffic",      "Avg Session Duration",        f"{traffic['avg_session_duration']} sec"],
        ["Traffic",      "Pages per Session",           str(traffic['pages_per_session'])],
        ["Traffic",      "Bounce Rate",                 f"{traffic['bounce_rate']}%"],
        ["Traffic",      "Peak Hour",                   f"{peak_hour}:00  ({int(peak_traffic):,} views)"],
        ["Server Load",  "Total Requests",              f"{load['total_requests']:,}"],
        ["Server Load",  "Avg CPU Usage",               f"{load['avg_cpu_usage']}%"],
        ["Server Load",  "Memory Usage",                f"{load['memory_usage']:.1f}%"],
        ["Server Load",  "Avg Response Time",           f"{load['avg_response_time']:.0f} ms"],
        ["Server Load",  "Error Rate",                  f"{load['error_rate']:.2f}%"],
        ["Users",        "Total Orders",                f"{users['total_orders']:,}"],
        ["Users",        "Avg Order Value",             f"${users['avg_order_value']}"],
        ["Users",        "Retention Rate",              f"{users['retention_rate']}%"],
        ["Users",        "Avg Customer Rating",         f"{users['avg_rating']}/5.0"],
        ["Users",        "Repeat Buyers",               f"{repeat_users:,}"],
        ["Users",        "One-time Buyers",             f"{onetime_users:,}"],
        ["Ads",          "Total Impressions",           f"{total_impr:,}"],
        ["Ads",          "Clicks",                      f"{total_clicks:,}"],
        ["Ads",          "Checkouts (Conversions)",     f"{total_conv:,}"],
        ["Ads",          "CTR",                         f"{ctr}%"],
        ["Ads",          "CPC",                         f"${cpc}"],
        ["Ads",          "ROAS",                        f"{roas}x"],
        ["Ads",          "Conversion Rate",             f"{conv_rate}%"],
        ["Security",     "Security Score",              f"{security_score:.1f}/100"],
        ["Security",     "Threats Blocked",             f"{threats_blocked:,}"],
        ["Security",     "Critical Alerts",             str(critical_alerts)],
        ["Security",     "4xx Client Errors",           f"{errors_4xx:,}"],
        ["Security",     "5xx Server Errors",           f"{errors_5xx:,}"],
        ["Security",     "Suspicious IPs",              str(susp_ips)],
        ["Security",     "Failed Logins",               str(failed_logins)],
        ["Security",     "Firewall Status",             firewall_status],
    ]

    app_tbl = Table(kpi_full, colWidths=[W*0.22, W*0.48, W*0.30])
    app_tbl.setStyle(_tbl_style(C_SLATE))
    story.append(app_tbl)
    story.append(Paragraph("Table A.1 — Comprehensive KPI Reference", s["caption"]))

    story.append(Spacer(1, 1*cm))
    story.append(_hr(C_BORDER))
    story.append(Paragraph(
        f"TrafficIQ Analytics Platform  ·  MediCaps University  ·  "
        f"Report generated {now.strftime('%B %d, %Y at %H:%M')}",
        ParagraphStyle("footer", fontSize=8, textColor=C_MUTED, alignment=TA_CENTER)
    ))

    doc.build(story)
    return output_path
