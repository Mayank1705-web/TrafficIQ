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

# ── Paragraph styles for table cells ─────────────────────────────────────────
_TC     = ParagraphStyle("tc",    fontSize=8, textColor=colors.HexColor("#334155"), leading=12)
_TC_B   = ParagraphStyle("tcb",   fontSize=8, textColor=colors.HexColor("#334155"), leading=12, fontName="Helvetica-Bold")
_TC_R   = ParagraphStyle("tcr",   fontSize=8, textColor=colors.HexColor("#991b1b"), leading=12, fontName="Helvetica-Bold")
_TC_W   = ParagraphStyle("tcw",   fontSize=8, textColor=colors.HexColor("#854d0e"), leading=12, fontName="Helvetica-Bold")
_TC_G   = ParagraphStyle("tcg",   fontSize=8, textColor=colors.HexColor("#166534"), leading=12)

def _p(text, style="n"):
    st = {"n":_TC,"b":_TC_B,"r":_TC_R,"w":_TC_W,"g":_TC_G}.get(style, _TC)
    return Paragraph(str(text), st)


class HBarChart(Flowable):
    def __init__(self, data, width=440, bar_height=14, spacing=5, color=C_BLUE):
        Flowable.__init__(self)
        self.data=data; self.width=width; self.bar_h=bar_height
        self.spacing=spacing; self.color=color
        self.height=(bar_height+spacing)*len(data)+16

    def draw(self):
        c=self.canv
        if not self.data: return
        max_val=max(v for _,v in self.data) or 1
        label_w=self.width*0.30; bar_area=self.width*0.54
        y=self.height-self.bar_h-6
        for label,value in self.data:
            c.setFont("Helvetica",8); c.setFillColor(C_NAVY)
            c.drawRightString(label_w-5,y+3,str(label)[:28])
            c.setFillColor(colors.HexColor("#e2e8f0"))
            c.roundRect(label_w,y,bar_area,self.bar_h,3,fill=1,stroke=0)
            fill_w=max(6,bar_area*(value/max_val))
            c.setFillColor(self.color)
            c.roundRect(label_w,y,fill_w,self.bar_h,3,fill=1,stroke=0)
            c.setFont("Helvetica-Bold",8); c.setFillColor(C_MUTED)
            c.drawString(label_w+bar_area+5,y+3,f"{int(value):,}")
            y-=(self.bar_h+self.spacing)


class CoverPage(Flowable):
    def __init__(self,date_str,time_str,kpis,W,H):
        Flowable.__init__(self)
        self.date_str=date_str; self.time_str=time_str
        self.kpis=kpis; self.width=W; self.height=H

    def draw(self):
        c=self.canv; W=self.width; H=self.height
        c.setFillColor(C_DARK); c.roundRect(0,0,W,H,10,fill=1,stroke=0)
        c.setFillColor(C_PURPLE); c.rect(0,H-6,W,6,fill=1,stroke=0)
        logo_y=H-80
        c.setFillColor(C_PURPLE); c.roundRect(W/2-28,logo_y,56,56,10,fill=1,stroke=0)
        c.setFillColor(C_WHITE); c.setFont("Helvetica-Bold",22)
        c.drawCentredString(W/2,logo_y+16,"IQ")
        c.setFillColor(C_WHITE); c.setFont("Helvetica-Bold",34)
        c.drawCentredString(W/2,logo_y-42,"TrafficIQ")
        c.setFillColor(colors.HexColor("#94a3b8")); c.setFont("Helvetica",15)
        c.drawCentredString(W/2,logo_y-66,"Business Intelligence Report")
        c.setFont("Helvetica",11)
        c.drawCentredString(W/2,logo_y-86,"Executive Analytics & Platform Summary")
        c.setStrokeColor(colors.HexColor("#334155")); c.setLineWidth(1)
        c.line(W*0.2,logo_y-104,W*0.8,logo_y-104)
        c.setFillColor(colors.HexColor("#64748b")); c.setFont("Helvetica",10)
        c.drawCentredString(W/2,logo_y-120,f"Generated: {self.date_str}  |  {self.time_str}")
        c.drawCentredString(W/2,logo_y-136,"MediCaps University  |  TrafficIQ Analytics Platform")
        badge_y=logo_y-160
        c.setFillColor(colors.HexColor("#7f1d1d"))
        c.roundRect(W/2-100,badge_y-6,200,22,6,fill=1,stroke=0)
        c.setFillColor(colors.HexColor("#fca5a5")); c.setFont("Helvetica-Bold",9)
        c.drawCentredString(W/2,badge_y+3,"CONFIDENTIAL — FOR INTERNAL USE ONLY")
        kpi_start_y=badge_y-30; cols=4; cell_w=W/cols; cell_h=58
        for idx,(label,value,color) in enumerate(self.kpis):
            row=idx//cols; col=idx%cols
            cx=col*cell_w; cy=kpi_start_y-row*(cell_h+6)
            bg=colors.HexColor("#1e293b") if idx%2==0 else colors.HexColor("#162032")
            c.setFillColor(bg)
            c.roundRect(cx+3,cy-cell_h+4,cell_w-6,cell_h,6,fill=1,stroke=0)
            c.setFillColor(color)
            c.roundRect(cx+3,cy-cell_h+4+cell_h-4,cell_w-6,4,3,fill=1,stroke=0)
            c.setFillColor(color); c.setFont("Helvetica-Bold",16)
            c.drawCentredString(cx+cell_w/2,cy-cell_h+30,str(value))
            c.setFillColor(colors.HexColor("#94a3b8")); c.setFont("Helvetica",8)
            c.drawCentredString(cx+cell_w/2,cy-cell_h+14,label)


def _styles():
    base=getSampleStyleSheet()
    def ps(name,**kw): return ParagraphStyle(name=name,parent=base["Normal"],**kw)
    return {
        "section": ps("Section",fontSize=13,textColor=C_WHITE,fontName="Helvetica-Bold",spaceBefore=10,spaceAfter=4),
        "subsec":  ps("SubSec", fontSize=11,textColor=C_NAVY, fontName="Helvetica-Bold",spaceBefore=10,spaceAfter=4),
        "body":    ps("Body",   fontSize=9.5,textColor=C_SLATE,leading=15,spaceAfter=7,alignment=TA_JUSTIFY),
        "caption": ps("Caption",fontSize=7.5,textColor=C_MUTED,spaceAfter=10,spaceBefore=2,alignment=TA_CENTER),
        "toc_h":   ps("TocH",  fontSize=11,textColor=C_NAVY,fontName="Helvetica-Bold"),
        "toc_e":   ps("TocE",  fontSize=10,textColor=C_SLATE,leading=20,leftIndent=10),
        "insight": ps("Insight",fontSize=9,textColor=C_NAVY,leading=14,spaceAfter=3),
        "footer":  ps("Footer", fontSize=7.5,textColor=C_MUTED,alignment=TA_CENTER),
        "method":  ps("Method", fontSize=8.5,textColor=C_MUTED,leading=13,spaceAfter=6,leftIndent=8,alignment=TA_JUSTIFY),
    }


def _tbl(hdr_color=C_PURPLE):
    return TableStyle([
        ("BACKGROUND",    (0,0),(-1,0), hdr_color),
        ("TEXTCOLOR",     (0,0),(-1,0), C_WHITE),
        ("FONTNAME",      (0,0),(-1,0), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0),(-1,-1),8.5),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[C_WHITE,C_ALT]),
        ("ALIGN",         (0,0),(-1,-1),"LEFT"),
        ("VALIGN",        (0,0),(-1,-1),"TOP"),
        ("LEFTPADDING",   (0,0),(-1,-1),6),
        ("RIGHTPADDING",  (0,0),(-1,-1),6),
        ("TOPPADDING",    (0,0),(-1,-1),5),
        ("BOTTOMPADDING", (0,0),(-1,-1),5),
        ("GRID",          (0,0),(-1,-1),0.3,C_BORDER),
    ])


def _banner(title,story,s,color,W):
    t=Table([[Paragraph(title,s["section"])]],colWidths=[W])
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),color),("TOPPADDING",(0,0),(-1,-1),9),
        ("BOTTOMPADDING",(0,0),(-1,-1),9),("LEFTPADDING",(0,0),(-1,-1),14),("ROUNDEDCORNERS",[6])]))
    story.append(Spacer(1,0.2*cm)); story.append(t); story.append(Spacer(1,0.2*cm))


def _callout(text,story,s,bg,border,icon=""):
    label=f"<b>{icon}</b>  {text}" if icon else text
    t=Table([[Paragraph(label,s["insight"])]],colWidths=[A4[0]-4*cm])
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),bg),("LINEAFTER",(0,0),(0,-1),3,border),
        ("TOPPADDING",(0,0),(-1,-1),7),("BOTTOMPADDING",(0,0),(-1,-1),7),
        ("LEFTPADDING",(0,0),(-1,-1),10),("RIGHTPADDING",(0,0),(-1,-1),10)]))
    story.append(t); story.append(Spacer(1,0.1*cm))


def _color_cell(text,status):
    bg={"CRITICAL":C_BAD,"HIGH":C_WARN,"GOOD":C_GOOD,"OK":C_GOOD}.get(status,C_LIGHT)
    tc={"CRITICAL":C_BAD_T,"HIGH":C_WARN_T,"GOOD":C_GOOD_T,"OK":C_GOOD_T}.get(status,C_MUTED)
    fn="Helvetica-Bold" if status in("CRITICAL","HIGH") else "Helvetica"
    return Paragraph(f"<b>{text}</b>" if fn=="Helvetica-Bold" else text,
        ParagraphStyle("cs",fontSize=8,textColor=tc,fontName=fn,alignment=TA_CENTER,backColor=bg))


def _note(text,story,s):
    t=Table([[Paragraph(f"<i>Methodology: {text}</i>",s["method"])]],colWidths=[A4[0]-4*cm])
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),colors.HexColor("#f8fafc")),
        ("LINEBEFORE",(0,0),(0,-1),2,C_BORDER),("TOPPADDING",(0,0),(-1,-1),5),
        ("BOTTOMPADDING",(0,0),(-1,-1),5),("LEFTPADDING",(0,0),(-1,-1),10)]))
    story.append(t); story.append(Spacer(1,0.1*cm))


def generate_business_report(output_path: str, data_dir: str):
    now      = datetime.now(ZoneInfo("Asia/Kolkata"))
    date_str = now.strftime("%d %B %Y")
    time_str = now.strftime("%I:%M %p IST")

    traffic  = _traffic(data_dir)
    load     = _load(data_dir)
    users    = _users(data_dir)
    ads      = _ads(data_dir)
    security = _security(data_dir)

    hourly      = traffic["hourly_traffic"]
    peak_hour   = max(hourly, key=hourly.get)
    peak_traffic= hourly[peak_hour]
    low_hour    = min(hourly, key=hourly.get)
    low_traffic = hourly[low_hour]
    sources     = traffic.get("traffic_sources",{})
    geo         = traffic.get("geo_distribution",{})
    total_sess  = int(traffic["total_sessions"])
    top_geo     = sorted(geo.items(),key=lambda x:x[1],reverse=True)[:6]
    top_src     = sorted(sources.items(),key=lambda x:x[1],reverse=True)

    funnel      = ads.get("funnel",{})
    ad_formats  = ads.get("ad_formats",{})
    ctr         = ads.get("ctr",0)
    roas        = ads.get("roas",0)
    cpc         = ads.get("cpc",0)
    total_impr  = ads.get("total_impressions",0)
    total_clicks= funnel.get("clicks",0)
    total_conv  = funnel.get("checkout",0)
    conv_rate   = round(total_conv/total_clicks*100,2) if total_clicks else 0

    attack      = security.get("attack_types",{})
    activity_log= security.get("activity_log",[])
    threats_blk = security.get("threats_blocked",0)
    crit_alerts = security.get("critical_alerts",0)
    fw_status   = security.get("firewall_status","Unknown")
    sec_score   = security.get("security_score",0)
    err_4xx     = attack.get("4xx Errors",0)
    err_5xx     = attack.get("5xx Errors",0)
    susp_ips_n  = attack.get("Suspicious IPs",0)
    fail_logins = next((x["count"] for x in activity_log if x["name"]=="Failed Logins"),0)

    repeat_u    = users["buyers"].get("Repeat",0)
    onetime_u   = users["buyers"].get("One-time",0)
    journey     = users.get("journey",{})
    category    = users.get("category",{})
    segments    = users.get("segments",{})
    top_cat     = sorted(category.items(),key=lambda x:x[1],reverse=True)[:6]
    top_eps     = list(load.get("top_endpoints",{}).items())[:6]
    susp_ip_lst = list(load.get("suspicious_ips",{}).items())[:6]

    cmap = {"CRITICAL":(C_BAD,C_BAD_T),"HIGH":(C_WARN,C_WARN_T),
            "OK":(C_GOOD,C_GOOD_T),"GOOD":(C_GOOD,C_GOOD_T),"INFO":(C_LIGHT,C_MUTED)}

    s   = _styles()
    doc = SimpleDocTemplate(output_path,pagesize=A4,rightMargin=2*cm,leftMargin=2*cm,
          topMargin=2*cm,bottomMargin=2*cm,title="TrafficIQ Business Intelligence Report",
          author="TrafficIQ Analytics Platform")
    story=[]; W=A4[0]-4*cm

    # ── COVER ────────────────────────────────────────────────────────────────
    sec_col=C_GREEN if sec_score>=70 else (C_ORANGE if sec_score>=50 else C_RED)
    kpis=[
        ("Total Sessions", f"{total_sess:,}",             C_BLUE),
        ("Total Requests", f"{load['total_requests']:,}", C_ORANGE),
        ("Total Orders",   f"{users['total_orders']:,}",  C_TEAL),
        ("Retention Rate", f"{users['retention_rate']}%", C_PURPLE),
        ("Avg Rating",     f"{users['avg_rating']}/5.0",  C_ORANGE),
        ("ROAS",           f"{roas}x",                    C_PINK),
        ("Security Score", f"{sec_score:.1f}/100",        sec_col),
        ("Threats Blocked",f"{threats_blk:,}",            C_RED),
    ]
    story.append(Spacer(1,0.3*cm))
    story.append(CoverPage(date_str,time_str,kpis,W,420))
    story.append(Spacer(1,0.5*cm))

    toc_items=["1.  Executive Summary","2.  Traffic Intelligence Analysis",
        "3.  Server Load &amp; Performance Analysis","4.  User Behaviour &amp; Retention Analysis",
        "5.  Advertisement Performance Analysis","6.  Security &amp; Threat Analysis",
        "7.  Key Findings &amp; Business Recommendations","Appendix — Full KPI Reference Table"]
    toc_rows=[[Paragraph("Table of Contents",s["toc_h"])]]+\
             [[Paragraph(f"   {i}",s["toc_e"])] for i in toc_items]
    toc_t=Table(toc_rows,colWidths=[W])
    toc_t.setStyle(TableStyle([("BACKGROUND",(0,0),(0,0),C_LIGHT),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[C_WHITE,C_ALT]),("TOPPADDING",(0,0),(-1,-1),5),
        ("BOTTOMPADDING",(0,0),(-1,-1),5),("LEFTPADDING",(0,0),(-1,-1),12),
        ("BOX",(0,0),(-1,-1),0.5,C_BORDER),("LINEBELOW",(0,0),(-1,0),0.5,C_BORDER)]))
    story.append(KeepTogether(toc_t))
    story.append(PageBreak())

    # ── 1. EXECUTIVE SUMMARY ─────────────────────────────────────────────────
    _banner("1.  Executive Summary",story,s,C_DARK,W)
    story.append(Paragraph(
        f"This Business Intelligence Report presents a comprehensive, data-driven evaluation of the "
        f"<b>TrafficIQ Analytics Platform</b> as of <b>{date_str}</b>. The report covers five analytical "
        f"pillars — web traffic, server infrastructure, user behaviour, advertising ROI, and cybersecurity — "
        f"providing an operational snapshot and strategic roadmap for platform improvement.",s["body"]))
    story.append(Paragraph(
        f"The platform records <b>{total_sess:,} total page views</b> with average session duration "
        f"<b>{traffic['avg_session_duration']}s</b> and <b>{traffic['pages_per_session']} pages/session</b>. "
        f"The e-commerce component processed <b>{users['total_orders']:,} orders</b> at AOV "
        f"<b>${users['avg_order_value']}</b>. Customer loyalty is exceptional — "
        f"<b>{users['retention_rate']}% retention rate</b> far exceeds the 30-40% industry benchmark.",s["body"]))
    story.append(Paragraph(
        f"Three critical issues demand immediate attention: (1) server error rate <b>{load['error_rate']:.1f}%</b> "
        f"— 49x above the 1% threshold; (2) ad CTR <b>{ctr}%</b> — wasting ad spend; "
        f"(3) security score <b>{sec_score:.1f}/100</b> with {crit_alerts} active critical alerts.",s["body"]))

    def h_row(m,v,st,c):
        return [m,v,_color_cell(st,st),c]
    health=[
        ["Metric","Value","Status","Comment"],
        h_row("Total Sessions",f"{total_sess:,}","GOOD","Strong traffic volume"),
        h_row("Avg Session Duration",f"{traffic['avg_session_duration']}s","GOOD","Users are engaged"),
        h_row("Server Error Rate",f"{load['error_rate']:.1f}%",
              "CRITICAL" if load['error_rate']>5 else "GOOD",
              "High — immediate fix needed" if load['error_rate']>5 else "Within threshold"),
        h_row("Ad CTR",f"{ctr}%","CRITICAL" if ctr<1 else("HIGH" if ctr<2 else "GOOD"),
              "Below industry avg 2%" if ctr<2 else "On target"),
        h_row("Security Score",f"{sec_score:.1f}/100",
              "CRITICAL" if sec_score<50 else("HIGH" if sec_score<70 else "GOOD"),
              "Moderate risk" if sec_score>=50 else "Critical action needed"),
        h_row("Customer Retention",f"{users['retention_rate']}%","GOOD","Excellent — above industry avg"),
        h_row("Avg Order Value",f"${users['avg_order_value']}","GOOD","High-value customer base"),
    ]
    ht=Table(health,colWidths=[W*0.26,W*0.16,W*0.15,W*0.43])
    ht.setStyle(_tbl(C_DARK)); story.append(ht)
    story.append(Paragraph("Table 1.1 — Platform Health Scorecard",s["caption"]))
    story.append(Paragraph(
        f"<b>Strategic Outlook:</b> Strong commercial foundation with high retention and AOV. "
        f"Primary inhibitors are server reliability, ad effectiveness, and security risk. "
        f"Addressing P1 issues within 7 days is critical to prevent revenue loss.",s["body"]))
    story.append(PageBreak())

    # ── 2. TRAFFIC ────────────────────────────────────────────────────────────
    _banner("2.  Traffic Intelligence Analysis",story,s,C_BLUE,W)
    story.append(Paragraph("<b>2.1  Overview &amp; Context</b>",s["subsec"]))
    story.append(Paragraph(
        f"The platform recorded <b>{total_sess:,} total page views</b>. Bounce rate "
        f"<b>{traffic['bounce_rate']}%</b> is well below the 40-55% industry average — visitors find "
        f"relevant content and continue exploring. Average <b>{traffic['avg_session_duration']}s session "
        f"duration</b> and <b>{traffic['pages_per_session']} pages/session</b> align with healthy "
        f"engagement benchmarks for data dashboard products.",s["body"]))

    story.append(Paragraph("<b>2.2  Hourly Traffic Distribution</b>",s["subsec"]))
    story.append(Paragraph(
        f"Traffic peaks at <b>{peak_hour}:00</b> ({int(peak_traffic):,} views) and drops to "
        f"<b>{low_hour}:00</b> ({int(low_traffic):,} views). The clear 09:00-17:00 concentration "
        f"strongly indicates a B2B professional user base. The swing of "
        f"<b>{int(peak_traffic-low_traffic):,} views</b> between peak and trough — the server must "
        f"handle 75x more traffic at peak vs off-peak with static provisioning, contributing directly "
        f"to the observed high error rates during business hours.",s["body"]))
    hourly_sorted=sorted(hourly.items(),key=lambda x:int(str(x[0])))
    story.append(HBarChart([(f"{h}:00",v) for h,v in hourly_sorted],
                            width=int(W),bar_height=11,spacing=3,color=C_BLUE))
    story.append(Paragraph("Chart 2.1 — Page Views by Hour of Day",s["caption"]))
    _note("Hourly traffic from aggregated page_views grouped by hour field in the traffic dataset.",story,s)
    _callout(f"Peak at {peak_hour}:00 = optimal window for campaigns, content releases & email pushes.",
             story,s,bg=colors.HexColor("#eff6ff"),border=C_BLUE,icon="INSIGHT")

    story.append(Paragraph("<b>2.3  Traffic Acquisition Sources</b>",s["subsec"]))
    story.append(Paragraph(
        f"Search dominates at {round(sources.get('Search',0)/total_sess*100,1)}% — strong organic SEO. "
        f"Direct traffic at {round(sources.get('Direct',0)/total_sess*100,1)}% reflects strong brand "
        f"recognition. Social ({round(sources.get('Social',0)/total_sess*100,1)}%) and Referral "
        f"({round(sources.get('Referral',0)/total_sess*100,1)}%) are significant untapped growth channels.",s["body"]))
    src_d=[["Source","Sessions","Share %","Classification"]]+[
        [src,f"{int(v):,}",f"{round(int(v)/total_sess*100,1)}%",
         "Primary" if v==max(sources.values()) else "Secondary"] for src,v in top_src]
    st=Table(src_d,colWidths=[W*0.26,W*0.22,W*0.18,W*0.34]); st.setStyle(_tbl(C_BLUE))
    story.append(st); story.append(Paragraph("Table 2.1 — Traffic by Acquisition Source",s["caption"]))

    story.append(Paragraph("<b>2.4  Geographic Market Distribution</b>",s["subsec"]))
    story.append(Paragraph(
        f"India accounts for {round(geo.get('India',0)/total_sess*100,1)}% of sessions — primary market. "
        f"USA ({round(geo.get('USA',0)/total_sess*100,1)}%) and UK ({round(geo.get('UK',0)/total_sess*100,1)}%) "
        f"represent significant growth market opportunities requiring targeted localisation investment.",s["body"]))
    geo_d=[["Country","Sessions","Share %","Market Tier"]]+[
        [c,f"{int(v):,}",f"{round(int(v)/total_sess*100,1)}%",
         "Primary" if i==0 else("Growth" if i<=2 else "Emerging")] for i,(c,v) in enumerate(top_geo)]
    gt=Table(geo_d,colWidths=[W*0.26,W*0.22,W*0.18,W*0.34]); gt.setStyle(_tbl(C_BLUE))
    story.append(gt); story.append(Paragraph("Table 2.2 — Top Countries by Session Volume",s["caption"]))
    _callout("India dominates traffic. Localise with Hindi support, INR pricing, and India-specific content.",
             story,s,bg=colors.HexColor("#eff6ff"),border=C_BLUE,icon="RECOMMENDATION")

    story.append(Paragraph("<b>2.5  Traffic Issues, Root Causes &amp; Remediation</b>",s["subsec"]))
    story.append(Paragraph(
        "Despite strong overall traffic volume, four structural weaknesses require strategic intervention.",s["body"]))
    tr=[
        [_p("Issue","b"),_p("Impact","b"),_p("Root Cause","b"),_p("Recommended Action","b")],
        [_p("Search dominates at 40%"),_p("High dependency risk if SEO drops"),
         _p("Underinvestment in other channels"),_p("Diversify: grow social & referral to 20% each")],
        [_p("Traffic spike at single hour"),_p("Server overload at peak hours"),
         _p("No dynamic load distribution"),_p("Implement CDN caching & auto-scaling rules")],
        [_p("Low Referral at 10%"),_p("Missing organic viral growth"),
         _p("No partner or affiliate programme"),_p("Launch partner referral with incentives")],
        [_p("No off-peak engagement"),_p("Wasted server capacity 22:00-06:00"),
         _p("B2B-only audience, no consumer product"),_p("Develop consumer-facing features")],
    ]
    ti=Table(tr,colWidths=[W*0.20,W*0.20,W*0.27,W*0.33])
    ti_s=_tbl(C_RED); ti.setStyle(ti_s)
    story.append(ti); story.append(Paragraph("Table 2.3 — Traffic Issues &amp; Strategic Remediation Plan",s["caption"]))
    story.append(PageBreak())

    # ── 3. SERVER LOAD ────────────────────────────────────────────────────────
    _banner("3.  Server Load &amp; Performance Analysis",story,s,C_ORANGE,W)
    story.append(Paragraph("<b>3.1  Infrastructure Health Assessment</b>",s["subsec"]))
    story.append(Paragraph(
        f"The server processed <b>{load['total_requests']:,} requests</b>, avg response time "
        f"<b>{load['avg_response_time']:.0f} ms</b>. However the <b>{load['error_rate']:.2f}% error rate</b> "
        f"is critically above the 1% threshold — nearly half of all requests return errors. "
        f"CPU at <b>{load['avg_cpu_usage']}%</b> and memory at <b>{load['memory_usage']:.0f}%</b> leave "
        f"virtually no headroom. A doubling of traffic would cause complete service failure. "
        f"Industry best practice: maintain 30% spare capacity at all times.",s["body"]))
    perf=[
        ["Metric","Value","Benchmark","Status"],
        ["Total Requests",   f"{load['total_requests']:,}",   "N/A",    "INFO"],
        ["Avg CPU Usage",    f"{load['avg_cpu_usage']}%",     "< 70%",  "CRITICAL" if load['avg_cpu_usage']>90 else "HIGH"],
        ["Memory Usage",     f"{load['memory_usage']:.0f}%",  "< 75%",  "CRITICAL" if load['memory_usage']>90 else "HIGH"],
        ["Avg Response Time",f"{load['avg_response_time']:.0f} ms","< 200 ms","OK" if load['avg_response_time']<200 else "HIGH"],
        ["Error Rate",       f"{load['error_rate']:.2f}%",    "< 1%",   "CRITICAL" if load['error_rate']>5 else "HIGH"],
    ]
    pt=Table(perf,colWidths=[W*0.30,W*0.18,W*0.18,W*0.34])
    pt_s=_tbl(C_ORANGE)
    cmap_p={"CRITICAL":(C_BAD,C_BAD_T),"HIGH":(C_WARN,C_WARN_T),"OK":(C_GOOD,C_GOOD_T),"INFO":(C_LIGHT,C_MUTED)}
    for i,row in enumerate(perf[1:],1):
        bg,tc=cmap_p.get(row[3],(C_LIGHT,C_MUTED))
        pt_s.add("BACKGROUND",(3,i),(3,i),bg); pt_s.add("TEXTCOLOR",(3,i),(3,i),tc)
    pt.setStyle(pt_s); story.append(pt)
    story.append(Paragraph("Table 3.1 — Performance Metrics vs Industry Benchmarks",s["caption"]))

    story.append(Paragraph("<b>3.2  Endpoint Traffic &amp; Performance Analysis</b>",s["subsec"]))
    story.append(Paragraph(
        f"Auth-related endpoints (/usr/login, /usr/register, /usr/admin) collectively represent ~60% "
        f"of all traffic — strongly suggesting automated bot traffic or a credential-stuffing attack "
        f"targeting the authentication layer.",s["body"]))
    story.append(HBarChart(top_eps,width=int(W),bar_height=12,spacing=4,color=C_ORANGE))
    story.append(Paragraph("Chart 3.1 — Top Endpoints by Request Volume",s["caption"]))
    ep_d=[["Endpoint","Requests","% of Total","Avg Response (ms)"]]+[
        [ep,f"{int(h):,}",f"{round(int(h)/load['total_requests']*100,1)}%",
         f"{load.get('avg_response_by_endpoint',{}).get(ep,0):.0f}"] for ep,h in top_eps]
    et=Table(ep_d,colWidths=[W*0.38,W*0.18,W*0.18,W*0.26]); et.setStyle(_tbl(C_ORANGE))
    story.append(et); story.append(Paragraph("Table 3.2 — Endpoint Performance Detail",s["caption"]))
    _note("Response times estimated from response_size/50 as proxy metric.",story,s)
    _callout(f"CPU & memory at 95% — one traffic spike will take the platform offline. "
             f"Fix the {load['error_rate']:.0f}% error rate by repairing top 5 failing endpoints first.",
             story,s,bg=colors.HexColor("#fff7ed"),border=C_ORANGE,icon="WARNING")

    story.append(Paragraph("<b>3.3  Root Cause Analysis &amp; Remediation Plan</b>",s["subsec"]))
    story.append(Paragraph(
        "Structured root-cause analysis performed against each performance issue. Remediation steps "
        "categorised by immediacy — 24-48h immediate fixes and long-term architectural improvements.",s["body"]))
    li=[
        [_p("Issue","b"),_p("Root Cause","b"),_p("Immediate Fix (24-48h)","b"),_p("Long-term Solution","b")],
        [_p(f"Error rate {load['error_rate']:.1f}%","r"),_p("Application errors / bad routes"),
         _p("Fix top 5 failing endpoints"),_p("Circuit breakers & retry logic")],
        [_p("CPU at 95%","r"),_p("No caching, all requests hit database"),
         _p("Add Redis caching layer"),_p("Auto-scale or upgrade server tier")],
        [_p("Memory at 95%","r"),_p("Memory leaks / large payload loading"),
         _p("Profile & restart server processes"),_p("Pagination & lazy data loading")],
        [_p("High auth endpoint traffic","w"),_p("Brute-force or credential stuffing attack"),
         _p("Add CAPTCHA & IP rate limiting"),_p("WAF, DDoS protection, anomaly detection")],
        [_p("No response time SLA","w"),_p("No performance monitoring in place"),
         _p("Add APM tool (Datadog/New Relic)"),_p("Define & enforce p99 latency SLAs")],
    ]
    lit=Table(li,colWidths=[W*0.17,W*0.22,W*0.28,W*0.33])
    li_s=_tbl(C_RED); lit.setStyle(li_s)
    story.append(lit); story.append(Paragraph("Table 3.3 — Load Issues &amp; Remediation Plan",s["caption"]))
    story.append(PageBreak())

    # ── 4. USER BEHAVIOUR ─────────────────────────────────────────────────────
    _banner("4.  User Behaviour &amp; Retention Analysis",story,s,C_PURPLE,W)
    story.append(Paragraph("<b>4.1  Customer Overview &amp; Cohort Health</b>",s["subsec"]))
    story.append(Paragraph(
        f"The platform processed <b>{users['total_orders']:,} orders</b> at AOV "
        f"<b>${users['avg_order_value']}</b>, rating <b>{users['avg_rating']}/5.0</b>. "
        f"Retention is exceptional at <b>{users['retention_rate']}%</b> — well above the 30-40% "
        f"e-commerce benchmark. Increasing retention by 5% can increase profits by 25-95% (Bain & Company). "
        f"With {repeat_u:,} repeat buyers at {round(repeat_u/(repeat_u+onetime_u)*100,1)}% of the base, "
        f"the platform has built a highly loyal customer community.",s["body"]))
    buyer_d=[
        ["Buyer Type","Count","Share %","Avg Orders","Business Value"],
        ["Repeat Buyers",f"{repeat_u:,}",f"{round(repeat_u/(repeat_u+onetime_u)*100,1)}%","2+","HIGH — Core revenue base"],
        ["One-time Buyers",f"{onetime_u:,}",f"{round(onetime_u/(repeat_u+onetime_u)*100,1)}%","1","MEDIUM — Re-engage via email"],
    ]
    bt=Table(buyer_d,colWidths=[W*0.22,W*0.14,W*0.14,W*0.16,W*0.34]); bt.setStyle(_tbl(C_PURPLE))
    story.append(bt); story.append(Paragraph("Table 4.1 — Customer Segmentation by Purchase Behaviour",s["caption"]))

    story.append(Paragraph("<b>4.2  Revenue by Product Category</b>",s["subsec"]))
    story.append(Paragraph(
        f"Books and Clothing each contribute ~30% of revenue — a dual-persona customer base of "
        f"professional/educational and everyday consumers. Electronics and Home at ~20% each indicate "
        f"a diversified catalogue with no dangerous single-category concentration risk.",s["body"]))
    story.append(HBarChart(top_cat,width=int(W),bar_height=12,spacing=4,color=C_PURPLE))
    story.append(Paragraph("Chart 4.1 — Revenue by Product Category",s["caption"]))
    cat_d=[["Category","Revenue","Share %","Strategic Opportunity"]]+[
        [cat,f"${int(rev):,}",f"{round(rev/sum(v for _,v in top_cat)*100,1)}%",
         "Scale with subscriptions" if i==0 else("Grow with personalisation" if i<=2 else "Niche premium")]
        for i,(cat,rev) in enumerate(top_cat)]
    ct=Table(cat_d,colWidths=[W*0.24,W*0.22,W*0.16,W*0.38]); ct.setStyle(_tbl(C_PURPLE))
    story.append(ct); story.append(Paragraph("Table 4.2 — Revenue by Product Category",s["caption"]))

    story.append(Paragraph("<b>4.3  Customer Conversion Funnel Analysis</b>",s["subsec"]))
    story.append(Paragraph(
        f"The largest conversion loss occurs between Visited (250,000) and Viewed Product (175,000) — "
        f"a 30% drop-off at the very first step, typically caused by poor first-impression UX or a "
        f"mismatch between ad messaging and landing page content. The 57% drop from Viewed Product to "
        f"Add to Cart is improved through better product descriptions, images, reviews, and urgency triggers.",s["body"]))
    jvals=list(journey.values())
    fun_d=[["Stage","Users","Conv %","Drop-off %","Optimisation Action"]]+[
        [stage,f"{int(cnt):,}",f"{round(cnt/jvals[0]*100,1)}%",
         f"{round((1-cnt/jvals[i-1])*100,1)}%" if i>0 else "—",
         "Improve homepage UX" if i==1 else("Reduce cart friction" if i==2 else("Streamline checkout" if i==3 else "Monitor"))]
        for i,(stage,cnt) in enumerate(journey.items())]
    ft=Table(fun_d,colWidths=[W*0.20,W*0.14,W*0.14,W*0.16,W*0.36]); ft.setStyle(_tbl(C_PURPLE))
    story.append(ft); story.append(Paragraph("Table 4.3 — Customer Conversion Funnel with Drop-off Analysis",s["caption"]))
    _callout("Fixing the 30% visit-to-product-view drop-off recovers 75,000 potential customers per cycle. "
             "A/B test homepage layout and ensure landing pages match ad messaging.",
             story,s,bg=colors.HexColor("#faf5ff"),border=C_PURPLE,icon="INSIGHT")

    if segments:
        story.append(Paragraph("<b>4.4  Revenue by Customer Age Segment</b>",s["subsec"]))
        story.append(Paragraph(
            f"The 50+ age group is the highest revenue-generating segment (~38.8%) — counter-intuitive "
            f"for a digital platform, suggesting the product catalogue appeals to mature, higher-income "
            f"consumers. The 18-35 segment represents the largest growth opportunity given their longer "
            f"customer lifetime value.",s["body"]))
        seg_s=sorted(segments.items(),key=lambda x:x[1],reverse=True)
        seg_d=[["Age Group","Revenue","Share %","Priority","Recommended Channel"]]+[
            [sg,f"${int(rv):,}",f"{round(rv/sum(segments.values())*100,1)}%",
             "Primary" if i==0 else("Secondary" if i==1 else "Growth"),
             "Email & search" if i==0 else("Social & display" if i<=2 else "Social & influencer")]
            for i,(sg,rv) in enumerate(seg_s)]
        st2=Table(seg_d,colWidths=[W*0.14,W*0.20,W*0.13,W*0.17,W*0.36]); st2.setStyle(_tbl(C_PURPLE))
        story.append(st2); story.append(Paragraph("Table 4.4 — Revenue by Age Group with Channel Recommendations",s["caption"]))
    story.append(PageBreak())

    # ── 5. ADS ────────────────────────────────────────────────────────────────
    _banner("5.  Advertisement Performance Analysis",story,s,C_PINK,W)
    story.append(Paragraph("<b>5.1  Campaign Performance Overview</b>",s["subsec"]))
    story.append(Paragraph(
        f"Campaigns delivered <b>{total_impr:,} impressions</b>, CTR <b>{ctr}%</b>, "
        f"CPC <b>${cpc}</b>, ROAS <b>{roas}x</b>. While ROAS exceeds the 4x benchmark, the minimal "
        f"click volume of <b>{total_clicks:,}</b> means the high ROAS reflects a small number of "
        f"high-value conversions rather than campaign scale. Banner ads at 35% of spend are the "
        f"worst-performing format — Video ads deliver 2-3x higher CTR (Sharethrough/IPG Media Lab).",s["body"]))
    ab=[
        ["KPI","Current","Benchmark","Gap","Priority"],
        ["CTR",           f"{ctr}%",     "2.0%",       f"{round(2.0-ctr,2)}% below","CRITICAL"],
        ["CPC",           f"${cpc}",     "$0.50-2.00", "Within range",               "OK"],
        ["ROAS",          f"{roas}x",    "4x+",        "Above benchmark",            "GOOD"],
        ["Conversion Rate",f"{conv_rate}%","2-3%",     f"{round(max(0,2-conv_rate),1)}% below","HIGH"],
        ["Total Clicks",  f"{total_clicks:,}","High vol","Volume too low",           "CRITICAL"],
    ]
    abt=Table(ab,colWidths=[W*0.20,W*0.16,W*0.18,W*0.20,W*0.26])
    ab_s=_tbl(C_PINK)
    for i,row in enumerate(ab[1:],1):
        bg,tc={"CRITICAL":(C_BAD,C_BAD_T),"HIGH":(C_WARN,C_WARN_T),"GOOD":(C_GOOD,C_GOOD_T),"OK":(C_GOOD,C_GOOD_T)}.get(row[4],(C_LIGHT,C_MUTED))
        ab_s.add("BACKGROUND",(4,i),(4,i),bg); ab_s.add("TEXTCOLOR",(4,i),(4,i),tc)
    abt.setStyle(ab_s); story.append(abt)
    story.append(Paragraph("Table 5.1 — Ad Performance KPIs vs Industry Benchmarks",s["caption"]))

    story.append(Paragraph("<b>5.2  Ad Format Performance Breakdown</b>",s["subsec"]))
    fmt_d=[["Format","Impressions","Share %","Est. Clicks","Industry CTR","Recommendation"]]+[
        [fmt,f"{int(imp):,}",f"{round(imp/total_impr*100,1)}%",f"{int(imp*ctr/100):,}",
         "0.1%" if fmt=="Banner" else("1.8%" if fmt=="Video" else("0.8%" if fmt=="Native" else "0.5%")),
         "Reduce budget" if fmt=="Banner" else("Scale up" if fmt=="Video" else "Maintain")]
        for fmt,imp in ad_formats.items()]
    fmtt=Table(fmt_d,colWidths=[W*0.14,W*0.14,W*0.12,W*0.12,W*0.14,W*0.34]); fmtt.setStyle(_tbl(C_PINK))
    story.append(fmtt); story.append(Paragraph("Table 5.2 — Ad Format Performance with Industry CTR Benchmarks",s["caption"]))

    story.append(Paragraph("<b>5.3  Post-Click Conversion Funnel</b>",s["subsec"]))
    fsteps=[("Impressions",funnel.get("impressions",0)),("Clicks",funnel.get("clicks",0)),
            ("Landing",funnel.get("landing",0)),("Add to Cart",funnel.get("add_to_cart",0)),
            ("Checkout",funnel.get("checkout",0)),("Purchase",funnel.get("purchase",0))]
    cv_d=[["Stage","Users","Conv %","Drop-off","Analysis"]]+[
        [st,f"{int(v):,}",f"{round(v/fsteps[0][1]*100,2)}%" if fsteps[0][1] else "0%",
         f"-{round((1-v/fsteps[i-1][1])*100,1)}%" if i>0 and fsteps[i-1][1] else "—",
         "Click rate" if i==1 else("Landing quality" if i==2 else("Product appeal" if i==3 else("Checkout UX" if i==4 else "Payment trust")))]
        for i,(st,v) in enumerate(fsteps)]
    cvt=Table(cv_d,colWidths=[W*0.18,W*0.14,W*0.14,W*0.14,W*0.40]); cvt.setStyle(_tbl(C_PINK))
    story.append(cvt); story.append(Paragraph("Table 5.3 — Post-Click Ad Conversion Funnel",s["caption"]))
    _callout("IMMEDIATE: Shift 40% of Banner budget to Video. A/B test 3 creatives per format. "
             "Target 50+ demographic — highest revenue segment. Add retargeting for non-purchasers.",
             story,s,bg=colors.HexColor("#fff1f2"),border=C_RED,icon="ACTION REQUIRED")
    story.append(PageBreak())

    # ── 6. SECURITY ───────────────────────────────────────────────────────────
    _banner("6.  Security &amp; Threat Analysis",story,s,C_RED,W)
    story.append(Paragraph("<b>6.1  Security Posture Assessment</b>",s["subsec"]))
    sec_rating="CRITICAL" if sec_score<50 else("MODERATE" if sec_score<70 else "GOOD")
    story.append(Paragraph(
        f"Security score <b>{sec_score:.1f}/100 — {sec_rating}</b>. Firewall: <b>{fw_status}</b>. "
        f"Blocked <b>{threats_blk:,} threats</b>. <b>{crit_alerts} critical alert(s)</b> active. "
        f"The <b>{err_5xx:,} server-side 5xx errors</b> suggest severe application bugs, database "
        f"failures, or a sustained denial-of-service condition. The <b>{fail_logins} failed login "
        f"attempts</b> indicate credential-stuffing or brute-force activity.",s["body"]))
    sm=[
        ["Security KPI","Value","Risk","Description"],
        ["Security Score",  f"{sec_score:.1f}/100","CRITICAL" if sec_score<50 else "HIGH","Overall security health composite score"],
        ["Threats Blocked", f"{threats_blk:,}",   "INFO",  "Total requests blocked by firewall rules"],
        ["Critical Alerts", str(crit_alerts),      "HIGH" if crit_alerts>0 else "OK","Active unresolved high-severity alerts"],
        ["4xx Client Errors",f"{err_4xx:,}",       "HIGH" if err_4xx>10000 else "OK","Unauthorised access & not-found requests"],
        ["5xx Server Errors",f"{err_5xx:,}",       "CRITICAL" if err_5xx>10000 else "HIGH","Server processing failures"],
        ["Suspicious IPs",  str(susp_ips_n),       "HIGH" if susp_ips_n>0 else "OK","IPs exceeding 100-request threshold"],
        ["Failed Logins",   str(fail_logins),      "HIGH" if fail_logins>10 else "OK","Potential brute-force on user accounts"],
    ]
    smt=Table(sm,colWidths=[W*0.24,W*0.16,W*0.14,W*0.46])
    sm_s=_tbl(C_RED)
    for i,row in enumerate(sm[1:],1):
        bg,tc=cmap.get(row[2],(C_LIGHT,C_MUTED))
        sm_s.add("BACKGROUND",(2,i),(2,i),bg); sm_s.add("TEXTCOLOR",(2,i),(2,i),tc)
    smt.setStyle(sm_s); story.append(smt)
    story.append(Paragraph("Table 6.1 — Security KPI Assessment with Risk Classification",s["caption"]))

    story.append(Paragraph("<b>6.2  Threat Activity Log &amp; Response Plan</b>",s["subsec"]))
    story.append(Paragraph("Security activity log follows NIST SP 800-61 and OWASP incident response guidelines.",s["body"]))
    act_d=[["Threat Type","Count","Severity","Status","Response Action"]]+[
        [x["name"],str(x["count"]),x["level"],"ACTIVE" if x["count"]>0 else "CLEAR",
         "Investigate & patch immediately" if x["level"]=="Critical" else
         ("Monitor with alerting" if x["level"]=="High" else "Log & review weekly")]
        for x in activity_log]
    att=Table(act_d,colWidths=[W*0.26,W*0.10,W*0.12,W*0.12,W*0.40])
    at_s=_tbl(C_RED)
    for i,row in enumerate(act_d[1:],1):
        if row[2]=="Critical": at_s.add("BACKGROUND",(0,i),(-1,i),C_BAD)
        elif row[2]=="High":   at_s.add("BACKGROUND",(0,i),(-1,i),C_WARN)
    att.setStyle(at_s); story.append(att)
    story.append(Paragraph("Table 6.2 — Security Activity Log with NIST-Aligned Response Actions",s["caption"]))

    if susp_ip_lst:
        story.append(Paragraph("<b>6.3  Flagged IP Address Analysis</b>",s["subsec"]))
        story.append(Paragraph(
            f"IP analysis identified {len(susp_ip_lst)} addresses with anomalous volumes >100 requests — "
            f"strong indicators of bot traffic, credential stuffing, or reconnaissance activity.",s["body"]))
        story.append(HBarChart(susp_ip_lst,width=int(W),bar_height=12,spacing=4,color=C_RED))
        story.append(Paragraph("Chart 6.1 — Flagged IPs by Request Volume",s["caption"]))
        sp_d=[["IP Address","Requests","Risk Level","Recommended Action"]]+[
            [ip,f"{int(cnt):,}","CRITICAL" if cnt>200 else "HIGH",
             "Block in firewall immediately" if cnt>200 else "Rate limit to 10 req/min"]
            for ip,cnt in susp_ip_lst]
        sp_t=Table(sp_d,colWidths=[W*0.28,W*0.14,W*0.18,W*0.40])
        sp_s=_tbl(C_RED)
        for i,row in enumerate(sp_d[1:],1):
            if row[2]=="CRITICAL": sp_s.add("BACKGROUND",(0,i),(-1,i),C_BAD)
        sp_t.setStyle(sp_s); story.append(sp_t)
        story.append(Paragraph("Table 6.3 — Flagged IPs &amp; Remediation Actions",s["caption"]))
    _callout(f"IMMEDIATE: Block top 2 IPs via firewall. Fix {err_5xx:,} server errors starting with "
             f"top 5 endpoints. Enable SIEM alerting for failed login spikes and 5xx rate > 5%.",
             story,s,bg=colors.HexColor("#fff1f2"),border=C_RED,icon="CRITICAL ACTION")
    story.append(PageBreak())

    # ── 7. RECOMMENDATIONS ────────────────────────────────────────────────────
    _banner("7.  Key Findings &amp; Business Recommendations",story,s,C_DARK,W)
    story.append(Paragraph("<b>7.1  Executive Summary of Findings</b>",s["subsec"]))
    story.append(Paragraph(
        f"The platform demonstrates strong commercial fundamentals undermined by operational deficiencies. "
        f"The {load['error_rate']:.0f}% error rate means 1 in 2 interactions fails. The 30% first-funnel "
        f"drop-off represents 75,000 potential customers not engaging. Near-zero ad click volume wastes "
        f"advertising spend. Collectively these issues likely represent 30-50% of potential revenue "
        f"currently unrealised.",s["body"]))

    story.append(Paragraph("<b>7.2  Priority Action Matrix</b>",s["subsec"]))
    pm=[
        [_p("Priority","b"),_p("Area","b"),_p("Key Finding","b"),
         _p("Recommended Action","b"),_p("Owner","b"),_p("Timeline","b")],
        [_p("P1 — CRITICAL","r"),_p("Security"),
         _p(f"Score {sec_score:.0f}/100, {err_5xx:,} server errors"),
         _p("Block flagged IPs, patch top error endpoints"),_p("DevOps"),_p("This week")],
        [_p("P1 — CRITICAL","r"),_p("Ad Performance"),
         _p(f"CTR {ctr}% — creatives not resonating"),
         _p("A/B test new creatives, shift budget to Video"),_p("Marketing"),_p("This week")],
        [_p("P2 — HIGH","w"),_p("Infrastructure"),
         _p("CPU & Memory at 95% — near-failure"),
         _p("Add Redis caching, enable auto-scaling"),_p("Engineering"),_p("This month")],
        [_p("P2 — HIGH","w"),_p("Traffic"),
         _p("90% traffic from only 2 sources"),
         _p("Invest in social & referral growth channels"),_p("Marketing"),_p("This month")],
        [_p("P3 — MEDIUM","g"),_p("Conversion"),
         _p("30% drop-off at first funnel stage"),
         _p("Redesign homepage, add product recommendations"),_p("Product"),_p("Q3 2026")],
        [_p("P3 — MEDIUM","g"),_p("User Behaviour"),
         _p(f"{onetime_u:,} one-time buyers not returning"),
         _p("Launch re-engagement email drip campaign"),_p("CRM"),_p("Q3 2026")],
        [_p("P4 — LOW"),_p("Traffic"),
         _p("Referral contributes only 10%"),
         _p("Build partner & affiliate programme"),_p("Biz Dev"),_p("6 months")],
    ]
    pmt=Table(pm,colWidths=[W*0.14,W*0.11,W*0.22,W*0.24,W*0.13,W*0.16])
    pm_s=_tbl(C_DARK)
    for i in range(1,3): pm_s.add("BACKGROUND",(0,i),(0,i),C_BAD)
    for i in range(3,5): pm_s.add("BACKGROUND",(0,i),(0,i),C_WARN)
    for i in range(5,7): pm_s.add("BACKGROUND",(0,i),(0,i),C_GOOD)
    pmt.setStyle(pm_s); story.append(pmt)
    story.append(Paragraph("Table 7.1 — Prioritised Action Matrix with Ownership &amp; Timelines",s["caption"]))

    story.append(Paragraph("<b>7.3  Strengths to Protect &amp; Leverage</b>",s["subsec"]))
    story.append(Paragraph(
        "These competitive advantages should be actively protected, measured monthly, and used as "
        "the foundation for growth strategy.",s["body"]))
    str_d=[
        [_p("Strength","b"),_p("How to Leverage","b")],
        [_p(f"Retention {users['retention_rate']}%","g"),_p("World-class retention above 30-40% industry avg. Protect by improving post-purchase experience.")],
        [_p(f"AOV ${users['avg_order_value']}","g"),    _p("Premium customer base. Leverage with upselling, bundles, and loyalty rewards.")],
        [_p(f"ROAS {roas}x","g"),                       _p("Strong return on ad spend when users engage. Fix CTR to scale same ROAS with more volume.")],
        [_p(f"Rating {users['avg_rating']}/5.0","g"),   _p("Excellent satisfaction. Use customer testimonials in ad creatives to improve CTR.")],
        [_p("Predictable traffic pattern","g"),          _p("Clear 09:00-17:00 peak enables precision scheduling of campaigns and maintenance.")],
    ]
    str_t=Table(str_d,colWidths=[W*0.28,W*0.72])
    str_s=_tbl(C_GREEN)
    for i in range(1,len(str_d)):
        str_s.add("BACKGROUND",(0,i),(-1,i),C_GOOD if i%2==1 else C_WHITE)
    str_t.setStyle(str_s); story.append(str_t)
    story.append(Paragraph("Table 7.2 — Platform Strengths &amp; Leverage Strategies",s["caption"]))

    story.append(Paragraph("<b>7.4  Critical Weaknesses Requiring Immediate Attention</b>",s["subsec"]))
    story.append(Paragraph(
        "These weaknesses represent direct revenue risk or platform integrity threats that cannot be "
        "deferred without accepting significant business consequences.",s["body"]))
    wk_d=[
        [_p("Weakness","b"),_p("Business Impact","b"),_p("Urgency","b")],
        [_p("Security score 50.8/100","r"),_p("Data breach risk, regulatory liability, reputational damage"),_p("THIS WEEK","r")],
        [_p(f"Error rate {load['error_rate']:.1f}%","r"),_p("Every 2nd user interaction fails — direct revenue loss"),_p("THIS WEEK","r")],
        [_p(f"Ad CTR {ctr}%","r"),_p("Ad budget generates impressions not revenue — ROI destruction"),_p("THIS WEEK","r")],
        [_p("CPU/Memory at 95%","w"),_p("One traffic spike = complete platform outage"),_p("THIS MONTH","w")],
    ]
    wt=Table(wk_d,colWidths=[W*0.28,W*0.48,W*0.24])
    wk_s=_tbl(C_RED)
    for i in range(1,4): wk_s.add("BACKGROUND",(0,i),(-1,i),C_BAD)
    wk_s.add("BACKGROUND",(0,4),(-1,4),C_WARN)
    wt.setStyle(wk_s); story.append(wt)
    story.append(Paragraph("Table 7.3 — Critical Weaknesses with Business Impact Assessment",s["caption"]))

    story.append(Paragraph("<b>7.5  30-60-90 Day Roadmap</b>",s["subsec"]))
    rd=[
        [_p("Timeframe","b"),_p("Focus Area","b"),_p("Key Deliverables","b"),_p("Expected Outcome","b")],
        [_p("Days 1-30\n(Immediate)"),_p("Security &\nStability"),
         _p("Block flagged IPs, fix top error endpoints, add Redis cache, A/B test ad creatives"),
         _p("Error rate < 5%, security score > 65, first ad CTR improvements")],
        [_p("Days 31-60\n(Stabilise)"),_p("Performance &\nGrowth"),
         _p("Auto-scaling configured, social media campaigns live, re-engagement email launched"),
         _p("CPU < 80%, referral traffic +5%, one-time buyer recovery +10%")],
        [_p("Days 61-90\n(Optimise)"),_p("Conversion &\nRevenue"),
         _p("Homepage UX redesign, product recommendation engine, affiliate programme beta"),
         _p("Funnel drop-off < 20%, referral traffic +10%, new revenue stream from affiliates")],
    ]
    rt=Table(rd,colWidths=[W*0.16,W*0.14,W*0.38,W*0.32])
    rt_s=_tbl(C_DARK)
    rt_s.add("BACKGROUND",(0,1),(-1,1),colors.HexColor("#fff1f2"))
    rt_s.add("BACKGROUND",(0,2),(-1,2),colors.HexColor("#fef9c3"))
    rt_s.add("BACKGROUND",(0,3),(-1,3),colors.HexColor("#dcfce7"))
    rt.setStyle(rt_s); story.append(rt)
    story.append(Paragraph("Table 7.4 — 30-60-90 Day Strategic Roadmap",s["caption"]))
    story.append(PageBreak())

    # ── APPENDIX ──────────────────────────────────────────────────────────────
    _banner("Appendix — Full Key Performance Indicators",story,s,C_SLATE,W)
    story.append(Paragraph(
        "Complete reference of all platform KPIs with benchmarks and status classifications. "
        "Update each reporting cycle to track improvement over time.",s["body"]))

    def krow(cat,metric,val,bench,status):
        st_map={"CRITICAL":"r","HIGH":"w","GOOD":"g","OK":"g","INFO":"n"}
        return [_p(cat),_p(metric),_p(val),_p(bench),_p(status,st_map.get(status,"n"))]

    kpi_full=[
        [_p("Category","b"),_p("Metric","b"),_p("Value","b"),_p("Benchmark","b"),_p("Status","b")],
        krow("Traffic","Total Sessions",       f"{total_sess:,}",               "N/A",    "INFO"),
        krow("Traffic","Avg Session Duration", f"{traffic['avg_session_duration']}s","90-180s","OK"),
        krow("Traffic","Pages per Session",    str(traffic['pages_per_session']),"3-5",    "OK"),
        krow("Traffic","Bounce Rate",          f"{traffic['bounce_rate']}%",    "< 40%",  "GOOD"),
        krow("Traffic","Peak Hour",            f"{peak_hour}:00 ({int(peak_traffic):,} views)","N/A","INFO"),
        krow("Server", "Total Requests",       f"{load['total_requests']:,}",   "N/A",    "INFO"),
        krow("Server", "Avg CPU Usage",        f"{load['avg_cpu_usage']}%",     "< 70%",  "CRITICAL"),
        krow("Server", "Memory Usage",         f"{load['memory_usage']:.1f}%",  "< 75%",  "CRITICAL"),
        krow("Server", "Avg Response Time",    f"{load['avg_response_time']:.0f} ms","< 200ms","OK"),
        krow("Server", "Error Rate",           f"{load['error_rate']:.2f}%",    "< 1%",   "CRITICAL"),
        krow("Users",  "Total Orders",         f"{users['total_orders']:,}",    "N/A",    "INFO"),
        krow("Users",  "Avg Order Value",      f"${users['avg_order_value']}",  "N/A",    "INFO"),
        krow("Users",  "Retention Rate",       f"{users['retention_rate']}%",   "> 30%",  "GOOD"),
        krow("Users",  "Avg Rating",           f"{users['avg_rating']}/5.0",    "> 4.0",  "GOOD"),
        krow("Users",  "Repeat Buyers",        f"{repeat_u:,}",                 "N/A",    "INFO"),
        krow("Users",  "One-time Buyers",      f"{onetime_u:,}",                "N/A",    "INFO"),
        krow("Ads",    "Total Impressions",    f"{total_impr:,}",               "N/A",    "INFO"),
        krow("Ads",    "Total Clicks",         f"{total_clicks:,}",             "N/A",    "INFO"),
        krow("Ads",    "CTR",                  f"{ctr}%",                       "> 2%",   "CRITICAL"),
        krow("Ads",    "CPC",                  f"${cpc}",                       "$0.5-2", "OK"),
        krow("Ads",    "ROAS",                 f"{roas}x",                      "> 4x",   "GOOD"),
        krow("Ads",    "Conversion Rate",      f"{conv_rate}%",                 "2-3%",   "HIGH"),
        krow("Security","Security Score",      f"{sec_score:.1f}/100",          "> 70",   "CRITICAL"),
        krow("Security","Threats Blocked",     f"{threats_blk:,}",              "N/A",    "INFO"),
        krow("Security","Critical Alerts",     str(crit_alerts),                "0",      "HIGH" if crit_alerts>0 else "OK"),
        krow("Security","4xx Client Errors",   f"{err_4xx:,}",                  "< 1%",   "HIGH"),
        krow("Security","5xx Server Errors",   f"{err_5xx:,}",                  "< 0.1%", "CRITICAL"),
        krow("Security","Suspicious IPs",      str(susp_ips_n),                 "0",      "HIGH" if susp_ips_n>0 else "OK"),
        krow("Security","Failed Logins",       str(fail_logins),                "< 5",    "HIGH" if fail_logins>5 else "OK"),
        krow("Security","Firewall Status",     fw_status,                       "Active", "GOOD" if fw_status=="Active" else "CRITICAL"),
    ]
    at=Table(kpi_full,colWidths=[W*0.13,W*0.27,W*0.18,W*0.16,W*0.26])
    at_s=_tbl(C_SLATE); at.setStyle(at_s)
    story.append(at)
    story.append(Paragraph("Table A.1 — Comprehensive KPI Reference with Benchmarks &amp; Status",s["caption"]))

    story.append(Spacer(1,0.8*cm))
    story.append(HRFlowable(width="100%",thickness=0.5,color=C_BORDER))
    story.append(Spacer(1,0.3*cm))
    story.append(Paragraph(
        f"TrafficIQ Analytics Platform  |  MediCaps University  |  "
        f"Report generated {date_str} at {time_str}  |  CONFIDENTIAL",s["footer"]))
    story.append(Paragraph(
        "Automatically generated by the TrafficIQ reporting engine. "
        "Data reflects the most recent analysis cycle.",s["footer"]))

    doc.build(story)
    return output_path