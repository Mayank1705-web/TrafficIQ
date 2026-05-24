import warnings
warnings.filterwarnings(
    "ignore",
    message="Could not infer format",
    category=UserWarning
)

import pandas as pd
import re
import os


def main(data_dir: str = None):
    # Define base directories
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    RAW_DIR = os.path.join(BASE_DIR, "..", "Data", "Raw")
    PROCESSED_DIR = os.path.join(BASE_DIR, "..", "Data", "Processed")

    # Ensure processed directory exists
    os.makedirs(PROCESSED_DIR, exist_ok=True)

    # ---------------- TRAFFIC ----------------
    traffic_path = os.path.join(RAW_DIR, "traffic_data.csv")

    traffic = pd.read_csv(traffic_path)
    traffic.drop_duplicates(inplace=True)

    traffic['Timestamp'] = pd.to_datetime(traffic['Timestamp'], errors='coerce')
    traffic = traffic.dropna(subset=['Timestamp'])

    traffic.rename(columns={'TrafficCount': 'page_views'}, inplace=True)

    traffic['hour'] = traffic['Timestamp'].dt.hour
    traffic['day'] = traffic['Timestamp'].dt.day
    traffic['month'] = traffic['Timestamp'].dt.month

    traffic.to_csv(os.path.join(PROCESSED_DIR, "traffic_clean.csv"), index=False)

    # ---------------- ADS ----------------
    ads_path = os.path.join(RAW_DIR, "ad_data.csv")

    ads = pd.read_csv(ads_path)
    ads.drop_duplicates(inplace=True)

    ads['DateTime'] = pd.to_datetime(ads['DateTime'], errors='coerce')
    ads = ads.dropna(subset=['DateTime'])

    if 'is_click' in ads.columns:
        ads['is_click'] = ads['is_click'].fillna(0)
    elif 'Clicked' in ads.columns:
        ads['is_click'] = ads['Clicked'].fillna(0)
    elif 'click' in ads.columns:
        ads['is_click'] = ads['click'].fillna(0)
    elif 'label' in ads.columns:
        ads['is_click'] = ads['label'].fillna(0)
    else:
        ads['is_click'] = 0

    ads.to_csv(os.path.join(PROCESSED_DIR, "ads_clean.csv"), index=False)

    # ---------------- USERS ----------------
    users_path = os.path.join(RAW_DIR, "user_behaviour.csv")

    users = pd.read_csv(users_path)
    users.drop_duplicates(inplace=True)

    users.columns = users.columns.str.strip().str.lower()

    time_col = None
    for col in users.columns:
        if 'time' in col or 'date' in col:
            time_col = col
            break

    if time_col is None:
        users['event_time'] = pd.date_range(
            start="2023-01-01 00:00:00",
            periods=len(users),
            freq="min"
        )
    else:
        users['event_time'] = pd.to_datetime(users[time_col], errors='coerce')
        users = users.dropna(subset=['event_time'])

    if 'event_type' in users.columns:
        users['event_type'] = users['event_type'].str.lower().str.strip()
        users['event_type'] = users['event_type'].fillna("unknown")
    users.to_csv(os.path.join(PROCESSED_DIR, "user_behavior_clean.csv"), index=False)

    # ---------------- RETAIL ----------------
    retail_path = os.path.join(RAW_DIR, "online_retail_sales.csv")
    retail = pd.read_csv(retail_path)
    retail.drop_duplicates(inplace=True)
    retail['InvoiceDate'] = pd.to_datetime(retail['InvoiceDate'], errors='coerce')
    retail = retail.dropna(subset=['InvoiceDate'])
    retail['Quantity'] = retail['Quantity'].fillna(0)
    retail['UnitPrice'] = retail['UnitPrice'].fillna(0)
    retail['sales_amount'] = retail['Quantity'] * retail['UnitPrice']
    retail.to_csv(os.path.join(PROCESSED_DIR, "retail_clean.csv"), index=False)

    # ---------------- LOGS ----------------
    log_file_path = os.path.join(RAW_DIR, "logfiles.log")

    print("\nChecking Log File Path:", log_file_path)

    if not os.path.exists(log_file_path):
        raise FileNotFoundError("Log file not found. Please verify Raw folder.")

    log_data = []

    apache_pattern = r'(\d+\.\d+\.\d+\.\d+) - - \[(.*?)\] "(.*?)" (\d{3}) (\d+)'

    with open(log_file_path, "r", encoding="utf-8") as file:
        for line in file:
            match = re.search(apache_pattern, line)
            if match:
                log_data.append([
                    match.group(1),
                    match.group(2),
                    match.group(3),
                    match.group(4),
                    match.group(5)
                ])

    logs_df = pd.DataFrame(log_data, columns=[
        "ip_address", "timestamp", "request", "status_code", "response_size"
    ])

    logs_df["timestamp"] = pd.to_datetime(
        logs_df["timestamp"],
        format="%d/%b/%Y:%H:%M:%S %z",
        errors="coerce"
    )

    logs_df = logs_df.dropna(subset=["timestamp"])
    logs_df.drop_duplicates(inplace=True)
    logs_df.to_csv(os.path.join(PROCESSED_DIR, "logs_clean.csv"), index=False)

    print("\nParsed Log Records:", logs_df.shape)
    print("\n==============================================")
    print("DATA CLEANING COMPLETED SUCCESSFULLY")
    print("==============================================\n")

if __name__ == "__main__":
    main()