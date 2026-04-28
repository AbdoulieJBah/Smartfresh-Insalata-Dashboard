import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def generate_sample_data():
    np.random.seed(42)

    products = ["Rucola", "Spinach", "Mixed Salad", "Lettuce", "Baby Leaf", "Carrots", "Radicchio"]
    categories = ["Leafy Greens", "Mixed Salad", "Vegetables"]
    suppliers = ["Farm A", "Farm B", "Farm C", "Farm D"]
    customers = ["Fruva", "Coop", "Conad", "Lidl", "Eurospin", "Distributor X"]
    statuses = ["Delivered", "Pending", "Delayed"]

    feedback_samples = [
        "Fresh product and good packaging",
        "Excellent quality and fast delivery",
        "Delivery was late but product quality was acceptable",
        "Poor freshness and damaged packaging",
        "Spoiled leaves and bad smell reported",
        "Clean product and satisfied customer",
        "Packaging was damaged during transport",
        "Late delivery and poor product freshness",
        "Good quality but delivery delay",
        "Very fresh and reliable supplier"
    ]

    rows = []

    for i in range(500):
        date = datetime.today() - timedelta(days=np.random.randint(0, 120))
        product = np.random.choice(products)
        produced = np.random.randint(200, 3000)
        sold = np.random.randint(100, produced)
        stock = produced - sold
        waste = np.random.randint(0, max(1, int(produced * 0.15)))
        defects = np.random.randint(0, 40)
        expiry = date + timedelta(days=np.random.randint(2, 10))
        delay = np.random.randint(0, 4)
        revenue = sold * np.random.uniform(1.5, 5.0)

        rows.append({
            "date": date.date(),
            "batch_id": f"BATCH-{1000+i}",
            "client": np.random.choice(customers),
            "customer": np.random.choice(customers),
            "product_name": product,
            "product_category": np.random.choice(categories),
            "supplier": np.random.choice(suppliers),
            "quantity_produced": produced,
            "quantity_sold": sold,
            "stock_remaining": stock,
            "expiry_date": expiry.date(),
            "waste_quantity": waste,
            "defect_count": defects,
            "temperature": round(np.random.uniform(2, 8), 1),
            "order_quantity": sold,
            "colli_ordered": np.random.randint(200, 4000),
            "delivery_status": np.random.choice(statuses, p=[0.70, 0.15, 0.15]),
            "delivery_delay_days": delay,
            "revenue": round(revenue, 2),
            "feedback_text": np.random.choice(feedback_samples),
            "rating": np.random.randint(1, 6)
        })

    return pd.DataFrame(rows)


def load_data():
    if "smartfresh_df" not in st.session_state:
        try:
            st.session_state.smartfresh_df = pd.read_csv("smartfresh_full_dataset_500.csv")
        except Exception:
            st.session_state.smartfresh_df = generate_sample_data()

    df = st.session_state.smartfresh_df.copy()
    df.columns = df.columns.str.strip().str.lower()

    if "client" not in df.columns and "customer" in df.columns:
        df["client"] = df["customer"]

    if "order_quantity" not in df.columns and "quantity_sold" in df.columns:
        df["order_quantity"] = df["quantity_sold"]

    if "colli_ordered" not in df.columns:
        if "order_quantity" in df.columns:
            df["colli_ordered"] = np.ceil(df["order_quantity"] / 4).astype(int)
        else:
            df["colli_ordered"] = np.random.randint(200, 4000, size=len(df))

    if "feedback_text" not in df.columns:
        df["feedback_text"] = "No feedback provided"

    if "rating" not in df.columns:
        df["rating"] = 3

    if "delivery_delay_days" not in df.columns:
        df["delivery_delay_days"] = 0

    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")

    if "expiry_date" in df.columns:
        df["expiry_date"] = pd.to_datetime(df["expiry_date"], errors="coerce")

    return df


def calculate_kpis(df):
    total_production = df["quantity_produced"].sum()
    total_sales = df["quantity_sold"].sum()
    total_waste = df["waste_quantity"].sum()
    total_defects = df["defect_count"].sum()
    revenue = df["revenue"].sum()
    delayed = (df["delivery_status"].astype(str).str.title() == "Delayed").sum()

    waste_rate = (total_waste / total_production) * 100 if total_production else 0
    defect_rate = (total_defects / total_production) * 100 if total_production else 0

    return {
        "total_production": total_production,
        "total_sales": total_sales,
        "total_waste": total_waste,
        "waste_rate": waste_rate,
        "total_defects": total_defects,
        "defect_rate": defect_rate,
        "revenue": revenue,
        "delayed": delayed,
        "stock_remaining": df["stock_remaining"].sum()
    }
