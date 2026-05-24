import os
import pandas as pd
from db import query_df

def run_analysis(data_dir: str = None):
    logs = query_df("SELECT * FROM logs")

    logs.columns = logs.columns.str.lower().str.strip()
    logs["timestamp"] = pd.to_datetime(logs["timestamp"], errors="coerce")
    logs = logs.dropna(subset=["timestamp"])
    logs["hour"] = logs["timestamp"].dt.hour

    total_requests = len(logs)
    error_logs     = logs[logs["status_code"].astype(str).str.startswith(("4", "5"))]
    error_rate     = (len(error_logs) / total_requests) * 100

    status_dist    = logs["status_code"].value_counts()
    error_by_hour  = error_logs.groupby(error_logs["hour"]).size()
    ip_counts      = logs["ip_address"].value_counts()
    suspicious_ips = ip_counts[ip_counts > 100]

    threats_blocked = int(len(error_logs))
    security_score  = max(0, 100 - error_rate)

    attack_types = {
        "4xx Errors":     int(len(error_logs[error_logs["status_code"].astype(str).str.startswith("4")])),
        "5xx Errors":     int(len(error_logs[error_logs["status_code"].astype(str).str.startswith("5")])),
        "Suspicious IPs": int(len(suspicious_ips))
    }

    def get_level(count):
        if count == 0:    return "Low"
        elif count <= 5:  return "Medium"
        elif count <= 20: return "High"
        else:             return "Critical"

    failed_logins  = int(len(error_logs[error_logs["status_code"] == 401]))
    sql_injection  = int(len(logs[logs["request"].str.contains("SELECT", na=False)]))
    xss_attempts   = int(len(logs[logs["request"].str.contains("<script>", case=False, na=False)]))
    unusual_ip     = int(len(suspicious_ips))
    rate_limit     = int(len(logs[logs["status_code"] == 429]))
    csrf           = int(len(logs[logs["request"].str.contains("csrf", na=False)]))

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
        "threats_blocked": int(threats_blocked),
        "firewall_status": "Active",
        "critical_alerts": int(len(suspicious_ips)),
        "status_dist":     {str(k): int(v) for k, v in status_dist.to_dict().items()},
        "error_by_hour":   {int(k): int(v) for k, v in error_by_hour.to_dict().items()},
        "attack_types":    attack_types,
        "activity_log":    activity_log
    }