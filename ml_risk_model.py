import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, balanced_accuracy_score, precision_score, recall_score, f1_score

try:
    from xgboost import XGBClassifier
    XGBOOST_AVAILABLE = True
except Exception:
    from sklearn.ensemble import RandomForestClassifier
    XGBOOST_AVAILABLE = False


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

    for col in numeric_cols:
        data[col] = pd.to_numeric(data[col], errors="coerce").fillna(0)

    if "delivery_status" in data.columns:
        data["delivery_delayed"] = (
            data["delivery_status"]
            .astype(str)
            .str.lower()
            .eq("delayed")
            .astype(int)
        )
    else:
        data["delivery_delayed"] = 0

    data["waste_rate"] = np.where(
        data["quantity_produced"] > 0,
        data["waste_quantity"] / data["quantity_produced"],
        0
    )

    data["defect_rate"] = np.where(
        data["quantity_produced"] > 0,
        data["defect_count"] / data["quantity_produced"],
        0
    )

    data["sell_through_rate"] = np.where(
        data["quantity_produced"] > 0,
        data["quantity_sold"] / data["quantity_produced"],
        0
    )

    data["stock_pressure"] = np.where(
        data["quantity_sold"] > 0,
        data["stock_remaining"] / data["quantity_sold"],
        0
    )

    data["revenue_per_unit"] = np.where(
        data["quantity_sold"] > 0,
        data["revenue"] / data["quantity_sold"],
        0
    )

    data["risk_label"] = (
        (data["waste_rate"] > 0.08) |
        (data["defect_rate"] > 0.015) |
        (data["temperature"] > 6) |
        (data["delivery_delayed"] == 1) |
        (data["delivery_delay_days"] > 1) |
        (data["stock_pressure"] > 1.2)
    ).astype(int)

    features = numeric_cols + [
        "delivery_delayed",
        "waste_rate",
        "defect_rate",
        "sell_through_rate",
        "stock_pressure",
        "revenue_per_unit"
    ]

    X = data[features].replace([np.inf, -np.inf], 0).fillna(0)
    y = data["risk_label"]

    return X, y, features


def train_risk_model(df):
    X, y, features = prepare_ml_data(df)

    metrics = {
        "model_type": "Unavailable",
        "accuracy": None,
        "balanced_accuracy": None,
        "precision": None,
        "recall": None,
        "f1_score": None,
        "training_rows": len(X),
        "features": features
    }

    if len(X) < 20 or y.nunique() < 2:
        return None, features, metrics

    try:
        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=0.25,
            random_state=42,
            stratify=y
        )
    except Exception:
        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=0.25,
            random_state=42
        )

    if XGBOOST_AVAILABLE:
        model = XGBClassifier(
            n_estimators=120,
            max_depth=4,
            learning_rate=0.08,
            subsample=0.9,
            colsample_bytree=0.9,
            eval_metric="logloss",
            random_state=42
        )
        metrics["model_type"] = "XGBoost"
    else:
        model = RandomForestClassifier(
            n_estimators=150,
            random_state=42,
            class_weight="balanced"
        )
        metrics["model_type"] = "RandomForest Fallback"

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    metrics.update({
        "accuracy": round(accuracy_score(y_test, y_pred), 3),
        "balanced_accuracy": round(balanced_accuracy_score(y_test, y_pred), 3),
        "precision": round(precision_score(y_test, y_pred, zero_division=0), 3),
        "recall": round(recall_score(y_test, y_pred, zero_division=0), 3),
        "f1_score": round(f1_score(y_test, y_pred, zero_division=0), 3),
    })

    return model, features, metrics


def predict_ml_risk(model, features, row):
    if model is None:
        return {
            "ml_risk_probability": 0,
            "ml_risk_level": "Unavailable"
        }

    row_data = {}

    quantity_produced = float(row.get("quantity_produced", 0) or 0)
    quantity_sold = float(row.get("quantity_sold", 0) or 0)
    stock_remaining = float(row.get("stock_remaining", 0) or 0)
    waste_quantity = float(row.get("waste_quantity", 0) or 0)
    defect_count = float(row.get("defect_count", 0) or 0)
    revenue = float(row.get("revenue", 0) or 0)

    engineered_values = {
        "delivery_delayed": 1 if str(row.get("delivery_status", "")).lower() == "delayed" else 0,
        "waste_rate": waste_quantity / quantity_produced if quantity_produced else 0,
        "defect_rate": defect_count / quantity_produced if quantity_produced else 0,
        "sell_through_rate": quantity_sold / quantity_produced if quantity_produced else 0,
        "stock_pressure": stock_remaining / quantity_sold if quantity_sold else 0,
        "revenue_per_unit": revenue / quantity_sold if quantity_sold else 0,
    }

    for col in features:
        if col in engineered_values:
            row_data[col] = engineered_values[col]
        else:
            row_data[col] = float(row.get(col, 0) or 0)

    X_row = pd.DataFrame([row_data], columns=features).replace([np.inf, -np.inf], 0).fillna(0)

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


def get_feature_importance(model, features):
    if model is None:
        return pd.DataFrame(columns=["feature", "importance"])

    if hasattr(model, "feature_importances_"):
        return (
            pd.DataFrame({
                "feature": features,
                "importance": model.feature_importances_
            })
            .sort_values("importance", ascending=False)
            .reset_index(drop=True)
        )

    return pd.DataFrame(columns=["feature", "importance"])
