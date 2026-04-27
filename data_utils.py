import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def generate_sample_data():
    np.random.seed(42)

    products = ["Rucola", "Spinach", "Mixed Salad", "Lettuce", "Baby Leaf", "Carrots", "Radicchio"]
    categories = ["Leafy Greens", "Mixed Salad", "Vegetables"]
    suppliers = ["Farm A", "Farm B", "Farm C", "Farm D"]
    customers = ["Supermarket A", "Supermarket B", "Restaurant Group", "Local Market", "Distributor X"]
    statuses = ["Delivered", "Pending", "Delayed"]

    rows = []

    for i in range(250):
        date = datetime.today() - timedelta(days=np.random.randint(0, 90))
        product = np.random.choice(products)
        produced = np.random.randint(200, 2000)
        sold = np.random.randint(100, produced)
        stock = produced - sold
        waste = np.random.randint(0, max(1, int(produced * 0.12)))
        defects = np.random.randint(0, 30)
        expiry = date + timedelta(days=np.random.randint(2, 10))
        delay = np.random.choice([0, 0, 0, 1, 2, 3])
        revenue = sold * np.random.uniform(1.2, 4.5)

        rows.append({
            "date": date.date(),
            "batch_id": f"BATCH-{1000+i}",
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
            "customer": np.random.choice(customers),
            "order_quantity": sold,
            "delivery_status": np.random.choice(statuses, p=[0.75, 0.15, 0.10]),
            "delivery_delay_days": delay,
            "revenue": round(revenue, 2)
        })

    return pd.DataFrame(rows)


def load_data():
    if "smartfresh_df" not in st.session_state:
        st.session_state.smartfresh_df = generate_sample_data()

    df = st.session_state.smartfresh_df.copy()
    df["date"] = pd.to_datetime(df["date"])
    df["expiry_date"] = pd.to_datetime(df["expiry_date"])
    return df


def calculate_kpis(df):
    total_production = df["quantity_produced"].sum()
    total_sales = df["quantity_sold"].sum()
    total_waste = df["waste_quantity"].sum()
    revenue = df["revenue"].sum()
    delayed = (df["delivery_status"] == "Delayed").sum()
    total_defects = df["defect_count"].sum()

    waste_rate = (total_waste / total_production) * 100 if total_production else 0
    defect_rate = (total_defects / total_production) * 100 if total_production else 0

    return {
        "total_production": total_production,
        "total_sales": total_sales,
        "total_waste": total_waste,
        "waste_rate": waste_rate,
        "revenue": revenue,
        "delayed": delayed,
        "total_defects": total_defects,
        "defect_rate": defect_rate,
        "stock_remaining": df["stock_remaining"].sum()
    }
