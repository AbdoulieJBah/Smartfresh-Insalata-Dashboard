import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier


def prepare_ml_data(df):
    data = df.copy()
    data.columns = data.columns.str.strip().str.lower()

    numeric_cols = [
        "quantity_produced",
        "quantity_sold",
        "stock_remaining",
        "waste_quantity",
        "defect_count",
        "temperature",
        "delivery_delay_days",
        "revenue"
    ]

    for col in numeric_cols:
        if col not in data.columns:
            data[col] = 0

    data["delivery_delayed"] = (
        data.get("delivery_status", "")
        .astype(str)
        .str.lower()
        .eq("delayed")
        .astype(int)
        if "delivery_status" in data.columns
        else 0
    )

    data["risk_label"] = (
        (data["waste_quantity"] > data["waste_quantity"].mean()) |
        (data["defect_count"] > data["defect_count"].mean()) |
        (data["temperature"] > 6) |
        (data["delivery_delayed"] == 1)
    ).astype(int)

    features = numeric_cols + ["delivery_delayed"]

    X = data[features].fillna(0)
    y = data["risk_label"]

    return X, y, features


def train_risk_model(df):
    X, y, features = prepare_ml_data(df)

    if y.nunique() < 2:
        return None, features

    model = RandomForestClassifier(
        n_estimators=100,
        random_state=42,
        class_weight="balanced"
    )

    model.fit(X, y)

    return model, features


def predict_ml_risk(model, features, row):
    if model is None:
        return {
            "ml_risk_probability": 0,
            "ml_risk_level": "Unavailable"
        }

    row_data = {}

    for col in features:
        if col == "delivery_delayed":
            row_data[col] = 1 if str(row.get("delivery_status", "")).lower() == "delayed" else 0
        else:
            row_data[col] = float(row.get(col, 0))

    X_row = pd.DataFrame([row_data])

    probability = model.predict_proba(X_row)[0][1] * 100

    if probability >= 70:
        level = "High"
    elif probability >= 40:
        level = "Medium"
    else:
        level = "Low"

    return {
        "ml_risk_probability": round(probability, 2),
        "ml_risk_level": level
    }
