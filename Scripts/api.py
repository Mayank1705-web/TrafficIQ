import os
import mimetypes
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from auth import router as auth_router, init_db, decode_token

mimetypes.add_type("text/css",              ".css")
mimetypes.add_type("application/javascript", ".js")
mimetypes.add_type("text/html",             ".html")
mimetypes.add_type("image/jpeg",            ".enc")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

TEMPLATES_DIR = os.path.join(PROJECT_ROOT, "Dashboard", "pages")
STATIC_DIR = os.path.join(PROJECT_ROOT, "Dashboard")
DATA_DIR = os.environ.get(
    "DATA_DIR",
    os.path.join(PROJECT_ROOT, "Data", "Processed")
)
from traffic_analysis       import run_analysis as _traffic
from load_analysis          import run_analysis as _load
from ad_analytics           import run_analysis as _ads
from user_behavior_analysis import run_analysis as _users
from security_logs          import run_analysis as _security

def traffic_analysis():  return _traffic(DATA_DIR)
def load_analysis():     return _load(DATA_DIR)
def ads_analysis():      return _ads(DATA_DIR)
def user_analysis():     return _users(DATA_DIR)
def security_analysis(): return _security(DATA_DIR)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(lifespan=lifespan)
ALLOWED_ORIGINS = os.environ.get(
    "ALLOWED_ORIGINS",
    "http://127.0.0.1:8000, http://localhost:8000",
).split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

app.mount("/css",    StaticFiles(directory=os.path.join(STATIC_DIR, "css")), name="css")
app.mount("/js",     StaticFiles(directory=os.path.join(STATIC_DIR, "js")),  name="js")
app.mount("/assets", StaticFiles(directory=os.path.join(STATIC_DIR, "assets")), name="assets")
app.mount("/images", StaticFiles(directory=os.path.join(STATIC_DIR, "images")), name="images")
app.mount("/static", StaticFiles(directory=STATIC_DIR),                      name="static")


def require_auth(request: Request) -> str:
    token = request.cookies.get("session")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated.")
    try:
        payload = decode_token(token)
        return payload["sub"]
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired session.")


def html_file(name):
    path = os.path.join(TEMPLATES_DIR, name)
    if not os.path.exists(path):
        raise HTTPException(404)
    return FileResponse(path, media_type="text/html")


@app.get("/", include_in_schema=False)
def root():
    return html_file("login.html")

@app.get("/{page}.html", include_in_schema=False)
def serve_page(page: str):
    allowed = {"login","signup","index","traffic","load","ads","users","security","configuration", "about", "reports"}
    if page not in allowed:
        raise HTTPException(404)
    return html_file(f"{page}.html")

@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    path = os.path.join(TEMPLATES_DIR, "favicon.ico")
    if os.path.exists(path):
        return FileResponse(path)
    raise HTTPException(404)

@app.get("/system-status")
def system_status(_: str = Depends(require_auth)):
    return {"status": "operational"}

@app.get("/history")
def get_history(_: str = Depends(require_auth)):
    return [
        {"path": "/datasets/traffic.csv",  "records": 23995, "time": "2 mins ago",  "status": "Complete"},
        {"path": "/datasets/ads.json",      "records": 8412,  "time": "15 mins ago", "status": "Complete"},
        {"path": "/datasets/users.csv",     "records": 15230, "time": "1 hr ago",    "status": "Complete"},
        {"path": "/datasets/security.json", "records": 4801,  "time": "2 hrs ago",   "status": "Complete"},
    ]

@app.get("/traffic")
def traffic(_: str = Depends(require_auth)):
    try:    return traffic_analysis()
    except Exception as e: print(f"[traffic error] {e}"); raise HTTPException(500, str(e))

@app.get("/load")
def load(_: str = Depends(require_auth)):
    try:    return load_analysis()
    except Exception as e: print(f"[load error] {e}"); raise HTTPException(500, str(e))

@app.get("/ads")
def ads(_: str = Depends(require_auth)):
    try:    return ads_analysis()
    except Exception as e: print(f"[ads error] {e}"); raise HTTPException(500, str(e))

@app.get("/users")
def users(_: str = Depends(require_auth)):
    try:    return user_analysis()
    except Exception as e: print(f"[users error] {e}"); raise HTTPException(500, str(e))

@app.get("/security")
def security(_: str = Depends(require_auth)):
    try:    return security_analysis()
    except Exception as e: print(f"[security error] {e}"); raise HTTPException(500, str(e))

@app.get("/dashboard-data")
def dashboard_data(_: str = Depends(require_auth)):
    try:
        return {
            "traffic": traffic_analysis(),
            "load": load_analysis(),
            "ads": ads_analysis(),
            "users": user_analysis(),
            "security": security_analysis()
        }
    except Exception as e:
        print(f"[dashboard-data error] {e}")
        raise HTTPException(500, str(e))

@app.get("/api/report/download")
def download_report(_: str = Depends(require_auth)):
    try:
        from report_generator import generate_business_report
        import uuid
        import tempfile
        output_file = os.path.join(tempfile.gettempdir(), f"TrafficIQ_Report_{uuid.uuid4().hex}.pdf")
        generate_business_report(output_file, DATA_DIR)
        return FileResponse(output_file, media_type='application/pdf', filename="TrafficIQ_Business_Report.pdf")
    except Exception as e:
        print(f"[report download error] {e}")
        raise HTTPException(500, str(e))

@app.get("/api/report/summary")
def report_summary(_: str = Depends(require_auth)):
    try:
        import datetime
        traffic  = traffic_analysis()
        load     = load_analysis()
        users    = user_analysis()
        ads      = ads_analysis()
        security = security_analysis()

        # --- Traffic ---
        hourly       = traffic['hourly_traffic']
        peak_hour    = max(hourly, key=hourly.get)
        peak_traffic = hourly[peak_hour]
        low_hour     = min(hourly, key=hourly.get)
        low_traffic  = hourly[low_hour]
        sources      = traffic.get('traffic_sources', {})
        geo          = traffic.get('geo_distribution', {})
        total_sess   = int(traffic['total_sessions'])
        top_geo      = sorted(geo.items(), key=lambda x: x[1], reverse=True)[:5]
        top_src      = sorted(sources.items(), key=lambda x: x[1], reverse=True)

        # --- Load ---
        top_eps  = list(load.get('top_endpoints', {}).items())[:5]
        susp_ips = list(load.get('suspicious_ips', {}).items())[:4]

        # --- Users ---
        repeat_users  = users['buyers'].get('Repeat', 0)
        onetime_users = users['buyers'].get('One-time', 0)
        journey       = users.get('journey', {})
        category      = users.get('category', {})
        top_cat       = sorted(category.items(), key=lambda x: x[1], reverse=True)

        # --- Ads ---
        funnel     = ads.get('funnel', {})
        ad_formats = ads.get('ad_formats', {})
        ctr        = ads.get('ctr', 0)
        roas       = ads.get('roas', 0)
        cpc        = ads.get('cpc', 0)
        total_impressions = ads.get('total_impressions', 0)
        total_clicks      = funnel.get('clicks', 0)
        total_conversions = funnel.get('checkout', 0)
        conv_rate = round((total_conversions / total_clicks * 100), 2) if total_clicks else 0

        # --- Security ---
        attack_types    = security.get('attack_types', {})
        activity_log    = security.get('activity_log', [])
        threats_blocked = security.get('threats_blocked', 0)
        critical_alerts = security.get('critical_alerts', 0)
        firewall_status = security.get('firewall_status', 'Unknown')
        security_score  = security.get('security_score', 0)
        errors_4xx      = attack_types.get('4xx Errors', 0)
        errors_5xx      = attack_types.get('5xx Errors', 0)
        suspicious_ip_c = attack_types.get('Suspicious IPs', 0)
        failed_logins   = next((x['count'] for x in activity_log if x['name'] == 'Failed Logins'), 0)
        sql_inj         = next((x['count'] for x in activity_log if 'SQL' in x['name']), 0)
        xss_att         = next((x['count'] for x in activity_log if 'XSS' in x['name']), 0)

        def tbl_row(*cells):
            return "<tr>" + "".join(f"<td style='padding:10px 12px;border-bottom:1px solid rgba(255,255,255,0.05)'>{c}</td>" for c in cells) + "</tr>"

        def tbl(headers, rows_html):
            ths = "".join(f"<th style='text-align:left;padding:10px 12px;border-bottom:1px solid rgba(255,255,255,0.1);color:#94a3b8;font-size:0.8rem;text-transform:uppercase;letter-spacing:0.06em'>{h}</th>" for h in headers)
            return f"<table style='width:100%;border-collapse:collapse;margin-top:14px;font-size:0.9rem'><thead><tr>{ths}</tr></thead><tbody>{rows_html}</tbody></table>"

        def badge(txt, color):
            return f"<span style='background:{color}22;color:{color};padding:2px 8px;border-radius:99px;font-size:0.75rem;font-weight:600'>{txt}</span>"

        # Build table rows
        src_rows = "".join(tbl_row(s, f"{int(v):,}", f"{round(int(v)/total_sess*100,1)}%") for s, v in top_src)
        geo_rows = "".join(tbl_row(c, f"{int(v):,}", f"{round(int(v)/total_sess*100,1)}%") for c, v in top_geo)
        ep_rows  = "".join(tbl_row(f"<code style='color:#c084fc'>{ep}</code>", f"{int(h):,}") for ep, h in top_eps)
        susp_rows= "".join(tbl_row(f"<code style='color:#f87171'>{ip}</code>", f"{int(c):,} req") for ip, c in susp_ips)
        cat_rows = "".join(tbl_row(cat, f"${int(rev):,}") for cat, rev in top_cat)
        fmt_rows = "".join(tbl_row(fmt, f"{int(imp):,}", f"{round(int(imp)/total_impressions*100,1)}%") for fmt, imp in ad_formats.items())
        journey_vals = list(journey.values())
        jour_rows= "".join(tbl_row(stage, f"{int(cnt):,}", badge(f"{round((1 - cnt/journey_vals[0])*100,1)}% drop", "#f87171")) for stage, cnt in journey.items())
        act_rows = "".join(
            tbl_row(x['name'], x['count'],
                badge(x['level'], '#f87171' if x['level']=='Critical' else '#fb923c' if x['level']=='Medium' else '#86efac'))
            for x in activity_log
        )

        return {
            "generated_at": datetime.datetime.now().strftime("%B %d, %Y — %H:%M"),
            "kpis": {
                "total_sessions":  f"{total_sess:,}",
                "total_requests":  f"{load['total_requests']:,}",
                "total_orders":    f"{users['total_orders']:,}",
                "threats_blocked": f"{threats_blocked:,}",
                "avg_rating":      f"{users['avg_rating']}/5.0",
                "security_score":  f"{security_score:.1f}/100",
                "roas":            f"{roas}x",
                "retention_rate":  f"{users['retention_rate']}%",
            },
            "executive_summary": (
                f"This report provides a comprehensive overview of the TrafficIQ platform performance for the current reporting period. "
                f"The platform recorded <strong>{total_sess:,} total sessions</strong> with an average session duration of "
                f"<strong>{traffic['avg_session_duration']} seconds</strong> and <strong>{traffic['pages_per_session']} pages per session</strong>. "
                f"The overall bounce rate was <strong>{traffic['bounce_rate']}%</strong>. Server infrastructure processed "
                f"<strong>{load['total_requests']:,} requests</strong> with an average latency of <strong>{load['avg_response_time']:.0f}ms</strong> "
                f"and an error rate of <strong>{load['error_rate']:.2f}%</strong>. Ad campaigns delivered "
                f"<strong>{total_impressions:,} impressions</strong>, <strong>{total_clicks:,} clicks</strong>, and "
                f"<strong>{total_conversions:,} checkouts</strong> at a ROAS of <strong>{roas}x</strong>. "
                f"Security blocked <strong>{threats_blocked:,} threats</strong> with <strong>{critical_alerts} critical alert(s)</strong> and "
                f"a firewall status of <strong style='color:#86efac'>{firewall_status}</strong>."
            ),
            "traffic_analysis": (
                f"Traffic peaked at <strong>{peak_hour}:00</strong> ({int(peak_traffic):,} views) and was lowest at "
                f"<strong>{low_hour}:00</strong> ({int(low_traffic):,} views) — a {int(peak_traffic - low_traffic):,}-view daily swing. "
                f"Search drove the largest share of sessions at <strong>{round(sources.get('Search',0)/total_sess*100,1)}%</strong>, "
                f"followed by Direct ({round(sources.get('Direct',0)/total_sess*100,1)}%), "
                f"Social ({round(sources.get('Social',0)/total_sess*100,1)}%), and "
                f"Referral ({round(sources.get('Referral',0)/total_sess*100,1)}%)."
                + tbl(["Source", "Sessions", "Share"], src_rows)
            ),
            "geo_distribution": (
                f"The platform serves a global audience. India leads with "
                f"<strong>{round(int(top_geo[0][1])/total_sess*100,1)}%</strong> of total sessions, "
                f"with the top 5 countries accounting for the vast majority of traffic."
                + tbl(["Country", "Sessions", "Share"], geo_rows)
            ),
            "server_load": (
                f"The server handled <strong>{load['total_requests']:,} total requests</strong> at an average CPU of "
                f"<strong>{load['avg_cpu_usage']}%</strong>, memory of <strong>{load['memory_usage']:.0f}%</strong>, "
                f"network of <strong>{load['network_usage']}%</strong>, and response time of <strong>{load['avg_response_time']:.0f}ms</strong>. "
                f"The overall error rate was <strong>{load['error_rate']:.2f}%</strong>. "
                f"Below are the 5 most-hit endpoints:"
                + tbl(["Endpoint", "Requests"], ep_rows)
            ),
            "user_behavior": (
                f"<strong>{users['total_orders']:,} orders</strong> were placed with an average order value of "
                f"<strong>${users['avg_order_value']}</strong> and customer rating of <strong>{users['avg_rating']}/5.0</strong>. "
                f"Retention stands at <strong>{users['retention_rate']}%</strong> — {repeat_users:,} repeat vs {onetime_users:,} one-time buyers."
                + tbl(["Funnel Stage", "Users", "Drop-off"], jour_rows)
                + tbl(["Category", "Revenue"], cat_rows)
            ),
            "ad_performance": (
                f"Campaigns achieved a CTR of <strong>{ctr}%</strong>, CPC of <strong>${cpc}</strong>, ROAS of <strong>{roas}x</strong>. "
                f"From <strong>{total_impressions:,} impressions</strong> → <strong>{total_clicks:,} clicks</strong> → "
                f"<strong>{funnel.get('landing',0):,} landing</strong> → <strong>{funnel.get('add_to_cart',0):,} cart</strong> → "
                f"<strong>{total_conversions:,} checkout</strong>. End-to-end conversion rate: <strong>{conv_rate}%</strong>."
                + tbl(["Ad Format", "Impressions", "Share"], fmt_rows)
            ),
            "security_report": (
                f"Security score: <strong>{security_score:.1f}/100</strong>. Firewall: "
                f"<strong style='color:#86efac'>{firewall_status}</strong>. "
                f"Threats blocked: <strong>{threats_blocked:,}</strong>. Critical alerts: <strong>{critical_alerts}</strong>. "
                f"Client errors: <strong>{errors_4xx:,}</strong>. Server errors: <strong>{errors_5xx:,}</strong>. "
                f"Suspicious IPs: <strong>{suspicious_ip_c}</strong>. Failed logins: <strong>{failed_logins}</strong>. "
                f"SQL injection attempts: <strong>{sql_inj}</strong>. XSS attempts: <strong>{xss_att}</strong>."
                + tbl(["Security Event", "Count", "Severity"], act_rows)
                + tbl(["Flagged IP", "Activity"], susp_rows)
            ),
        }
    except Exception as e:
        print(f"[report summary error] {e}")
        import traceback; traceback.print_exc()
        raise HTTPException(500, str(e))

app.include_router(auth_router)
from dashboard_api import router as dashboard_router
app.include_router(dashboard_router)