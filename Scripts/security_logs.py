import os
import pandas as pd
from db import query_df


def run_analysis(data_dir: str = None):

    # ── Totals ────────────────────────────────────────────────────────────────
    totals = query_df("""
        SELECT
            COUNT(*)                                                             AS total_requests,
            SUM(CASE WHEN status_code::text LIKE '4%'
                       OR status_code::text LIKE '5%' THEN 1 ELSE 0 END)        AS total_errors,
            SUM(CASE WHEN status_code::text LIKE '4%' THEN 1 ELSE 0 END)        AS errors_4xx,
            SUM(CASE WHEN status_code::text LIKE '5%' THEN 1 ELSE 0 END)        AS errors_5xx,
            SUM(CASE WHEN status_code = 401              THEN 1 ELSE 0 END)      AS failed_logins,
            SUM(CASE WHEN status_code = 429              THEN 1 ELSE 0 END)      AS rate_limit,
            SUM(CASE WHEN request ILIKE '%SELECT%'       THEN 1 ELSE 0 END)      AS sql_injection,
            SUM(CASE WHEN request ILIKE '%<script>%'     THEN 1 ELSE 0 END)      AS xss_attempts,
            SUM(CASE WHEN request ILIKE '%csrf%'         THEN 1 ELSE 0 END)      AS csrf
        FROM logs
    """)

    total_requests = int(totals["total_requests"].iloc[0])
    total_errors   = int(totals["total_errors"].iloc[0])
    error_rate     = (total_errors / total_requests) * 100 if total_requests else 0
    security_score = max(0, 100 - error_rate)

    errors_4xx    = int(totals["errors_4xx"].iloc[0])
    errors_5xx    = int(totals["errors_5xx"].iloc[0])
    failed_logins = int(totals["failed_logins"].iloc[0])
    rate_limit    = int(totals["rate_limit"].iloc[0])
    sql_injection = int(totals["sql_injection"].iloc[0])
    xss_attempts  = int(totals["xss_attempts"].iloc[0])
    csrf          = int(totals["csrf"].iloc[0])

    # ── Suspicious IPs ────────────────────────────────────────────────────────
    suspicious = query_df("""
        SELECT COUNT(*) AS suspicious_count
        FROM (
            SELECT ip_address
            FROM logs
            WHERE ip_address IS NOT NULL
            GROUP BY ip_address
            HAVING COUNT(*) > 100
        ) sub
    """)
    unusual_ip = int(suspicious["suspicious_count"].iloc[0])

    # ── Status distribution ───────────────────────────────────────────────────
    status_dist_df = query_df("""
        SELECT status_code::text AS status_code, COUNT(*) AS cnt
        FROM logs
        GROUP BY status_code
        ORDER BY cnt DESC
        LIMIT 10
    """)
    status_dist = {r["status_code"]: int(r["cnt"]) for _, r in status_dist_df.iterrows()}

    # ── Errors by hour ────────────────────────────────────────────────────────
    errors_hourly = query_df("""
        SELECT
            EXTRACT(hour FROM timestamp::timestamp)::int AS hour,
            COUNT(*)                                      AS errors
        FROM logs
        WHERE timestamp IS NOT NULL
          AND (status_code::text LIKE '4%' OR status_code::text LIKE '5%')
        GROUP BY hour
        ORDER BY hour
    """)
    error_by_hour = {int(r["hour"]): int(r["errors"]) for _, r in errors_hourly.iterrows()}

    # ── Attack types ──────────────────────────────────────────────────────────
    attack_types = {
        "4xx Errors":     errors_4xx,
        "5xx Errors":     errors_5xx,
        "Suspicious IPs": unusual_ip
    }

    # ── Activity log ──────────────────────────────────────────────────────────
    def get_level(count):
        if count == 0:    return "Low"
        elif count <= 5:  return "Medium"
        elif count <= 20: return "High"
        else:             return "Critical"

    activity_log = [
        {"name": "Failed Logins",          "count": failed_logins, "level": get_level(failed_logins)},
        {"name": "SQL Injection Attempts",  "count": sql_injection, "level": get_level(sql_injection)},
        {"name": "XSS Attempts",           "count": xss_attempts,  "level": get_level(xss_attempts)},
        {"name": "Unusual IP Access",       "count": unusual_ip,    "level": get_level(unusual_ip)},
        {"name": "Rate Limit Exceeded",     "count": rate_limit,    "level": get_level(rate_limit)},
        {"name": "CSRF Attempts",          "count": csrf,           "level": get_level(csrf)},
    ]

    return {
        "security_score":  float(round(security_score, 2)),
        "threats_blocked": int(total_errors),
        "firewall_status": "Active",
        "critical_alerts": unusual_ip,
        "status_dist":     status_dist,
        "error_by_hour":   error_by_hour,
        "attack_types":    attack_types,
        "activity_log":    activity_log,
    }