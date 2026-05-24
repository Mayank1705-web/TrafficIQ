import pandas as pd
import os


def run_analysis(data_dir: str = None):
    if data_dir is None:
        data_dir = os.path.join(os.path.dirname(__file__), "..", "Data", "Processed")

    users = pd.read_csv(os.path.join(data_dir, "user_behavior_clean.csv"))

    if users.empty:
        raise ValueError("user_behavior_clean.csv is empty.")

    users.columns = users.columns.str.lower().str.strip()
    required_cols = [
        "purchase date",
        "total purchase amount",
        "customer id",
        "product category",
        "age"
    ]
    for col in required_cols:
        if col not in users.columns:
            raise ValueError(f"Missing required column: {col}")

    users["purchase date"] = pd.to_datetime(
        users["purchase date"], errors="coerce"
    )

    users = users.dropna(subset=["purchase date"])

    # KPI VALUES
    total_orders = len(users)
    avg_order_value = users["total purchase amount"].mean()

    purchase_freq = users["customer id"].value_counts()

    repeat_customers = purchase_freq[purchase_freq > 1].count()
    one_time_customers = purchase_freq[purchase_freq == 1].count()

    retention_rate = (
        (repeat_customers / len(purchase_freq)) * 100
        if len(purchase_freq) > 0 else 0
    )

    avg_rating = 4.6   # static

    # CHART DATA

    # Hourly purchase
    users["hour"] = users["purchase date"].dt.hour
    hourly = users.groupby("hour").size()

    # Category revenue
    category = users.groupby("product category")[
        "total purchase amount"
    ].sum()

    # Customer segments (age group)
    bins = [18, 25, 35, 50, 100]
    labels = ["18-25", "26-35", "36-50", "50+"]

    users["age_group"] = pd.cut(users["age"], bins=bins, labels=labels)

    segments = users.groupby("age_group")[
        "total purchase amount"
    ].sum()

    # Buyer type
    buyers = {
        "Repeat": int(repeat_customers),
        "One-time": int(one_time_customers)
    }

    # Journey funnel
    journey = {
        "Visited": total_orders,
        "Viewed Product": int(total_orders * 0.7),
        "Added to Cart": int(total_orders * 0.3),
        "Purchased": int(total_orders * 0.2)
    }

    return {
        "total_orders": int(total_orders),
        "avg_order_value": float(round(avg_order_value, 2)) if pd.notna(avg_order_value) else 0.0,
        "retention_rate": float(round(retention_rate, 2)),
        "avg_rating": float(avg_rating),

        "hourly": {int(k): int(v) for k, v in hourly.to_dict().items()},
        "category": {str(k): float(v) for k, v in category.to_dict().items()},
        "segments": {str(k): float(v) for k, v in segments.to_dict().items()},

        "buyers": buyers,
        "journey": {k: int(v) for k, v in journey.items()}
    }