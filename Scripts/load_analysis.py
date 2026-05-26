import os
import pandas as pd
from db import query_df


def run_analysis(data_dir: str = None):

    # ── Totals ────────────────────────────────────────────────────────────────
    totals = query_df("""
        SELECT
            COUNT(*)                                                        AS total_requests,
            SUM(CASE WHEN status_code::text LIKE '4%'
                       OR status_code::text LIKE '5%' THEN 1 ELSE 0 END)  AS total_errors,
            AVG(response_size::float / 50.0)                               AS avg_response_time
        FROM logs
    """)

    total_requests    = int(totals["total_requests"].iloc[0])
    total_errors      = int(totals["total_errors"].iloc[0])
    error_rate        = round((total_errors / total_requests) * 100, 2) if total_requests else 0
    avg_response_time = round(float(totals["avg_response_time"].iloc[0] or 0), 2)

    avg_cpu_usage  = min(95, round((total_requests / 1000) * 10, 2))
    memory_usage   = min(95, round((total_requests / 1000) * 12, 2))
    network_usage  = min(95, round((total_requests / 1000) * 8,  2))

    # ── Requests by hour ──────────────────────────────────────────────────────
    hourly = query_df("""
        SELECT
            EXTRACT(hour FROM timestamp::timestamp)::int AS hour,
            COUNT(*)                                      AS requests
        FROM logs
        WHERE timestamp IS NOT NULL
        GROUP BY hour
        ORDER BY hour
    """)
    requests_by_hour = {int(r["hour"]): int(r["requests"]) for _, r in hourly.iterrows()}

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
    errors_by_hour = {int(r["hour"]): int(r["errors"]) for _, r in errors_hourly.iterrows()}

    # ── Top endpoints ─────────────────────────────────────────────────────────
    endpoints = query_df("""
        SELECT
            SPLIT_PART(request, ' ', 2)  AS endpoint,
            COUNT(*)                      AS hits
        FROM logs
        WHERE request IS NOT NULL
        GROUP BY endpoint
        ORDER BY hits DESC
        LIMIT 5
    """)
    top_endpoints = {r["endpoint"]: int(r["hits"]) for _, r in endpoints.iterrows()}

    # ── Avg response time by endpoint ─────────────────────────────────────────
    avg_resp = query_df("""
        SELECT
            SPLIT_PART(request, ' ', 2)        AS endpoint,
            AVG(response_size::float / 50.0)   AS avg_rt
        FROM logs
        WHERE request IS NOT NULL
        GROUP BY endpoint
        ORDER BY avg_rt DESC
        LIMIT 5
    """)
    avg_response_by_endpoint = {r["endpoint"]: round(float(r["avg_rt"]), 2) for _, r in avg_resp.iterrows()}

    # ── P95 response time by endpoint ─────────────────────────────────────────
    p95_resp = query_df("""
        SELECT
            SPLIT_PART(request, ' ', 2)                          AS endpoint,
            PERCENTILE_CONT(0.95) WITHIN GROUP (
                ORDER BY response_size::float / 50.0
            )                                                    AS p95_rt
        FROM logs
        WHERE request IS NOT NULL
        GROUP BY endpoint
        ORDER BY p95_rt DESC
        LIMIT 5
    """)
    p95_response_by_endpoint = {r["endpoint"]: round(float(r["p95_rt"]), 2) for _, r in p95_resp.iterrows()}

    # ── Suspicious IPs (>100 requests) ───────────────────────────────────────
    suspicious = query_df("""
        SELECT ip_address, COUNT(*) AS hits
        FROM logs
        WHERE ip_address IS NOT NULL
        GROUP BY ip_address
        HAVING COUNT(*) > 100
        ORDER BY hits DESC
        LIMIT 20
    """)
    suspicious_ips = {r["ip_address"]: int(r["hits"]) for _, r in suspicious.iterrows()}

    return {
        "total_requests":           total_requests,
        "error_rate":               error_rate,
        "avg_cpu_usage":            avg_cpu_usage,
        "memory_usage":             memory_usage,
        "network_usage":            network_usage,
        "avg_response_time":        avg_response_time,
        "requests_by_hour":         requests_by_hour,
        "errors_by_hour":           errors_by_hour,
        "top_endpoints":            top_endpoints,
        "avg_response_by_endpoint": avg_response_by_endpoint,
        "p95_response_by_endpoint": p95_response_by_endpoint,
        "suspicious_ips":           suspicious_ips,
    }