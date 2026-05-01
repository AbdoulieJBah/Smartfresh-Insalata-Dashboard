import streamlit as st
import pandas as pd
import plotly.express as px
from data_utils import load_data
from auth_utils import require_role, get_current_user

require_role(["Admin", "Manager", "Operations", "Logistics"])

st.set_page_config(page_title="Operations Control", layout="wide")

# -----------------------------
# USER CONTEXT
# -----------------------------
user = get_current_user()
role = user.get("role", "User")

st.title("🥬 Operations Control — Inventory, Expiry & Deliveries")

st.write(
    f"Welcome **{user.get('name', 'User')}**. "
    f"You are viewing this page as **{role}**."
)

# -----------------------------
# LOAD DATA
# -----------------------------
df = load_data()
df.columns = df.columns.str.strip().str.lower()

# -----------------------------
# SAFETY CHECKS / COLUMN FIXES
# -----------------------------
today = pd.Timestamp.today().normalize()

if "date" in df.columns:
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
else:
    df["date"] = today

if "expiry_date" not in df.columns:
    df["expiry_date"] = df["date"] + pd.Timedelta(days=5)
else:
    df["expiry_date"] = pd.to_datetime(df["expiry_date"], errors="coerce")

df["days_to_expiry"] = (df["expiry_date"] - today).dt.days

if "delivery_status" not in df.columns:
    df["delivery_status"] = "Unknown"

df["delivery_status"] = df["delivery_status"].astype(str).str.strip().str.title()

if "stock_remaining" not in df.columns:
    df["stock_remaining"] = 0

if "product_name" not in df.columns:
    df["product_name"] = "Unknown Product"

if "supplier" not in df.columns:
    df["supplier"] = "Unknown Supplier"

if "batch_id" not in df.columns:
    df["batch_id"] = "N/A"

if "client" not in df.columns:
    df["client"] = df["customer"] if "customer" in df.columns else "Unknown Client"

if "delivery_delay_days" not in df.columns:
    df["delivery_delay_days"] = 0

if "order_quantity" not in df.columns:
    df["order_quantity"] = df["quantity_sold"] if "quantity_sold" in df.columns else 0

# -----------------------------
# ROLE-BASED VIEW MESSAGE
# -----------------------------
st.subheader("🧭 Role-Based Operations View")

if role == "Operations":
    st.info("Operations view: focused on production readiness, stock, expiry, and bottlenecks.")
elif role == "Logistics":
    st.info("Logistics view: focused on delayed deliveries, dispatch issues, and client impact.")
elif role == "Quality":
    st.info("Quality view: focused on expiry risk, stock condition, and supplier/product issues.")
elif role == "Manager":
    st.info("Manager view: summarized view of stock, expiry risk, and delivery performance.")
else:
    st.info("Admin view: full operations, inventory, expiry, and delivery monitoring.")

st.markdown("---")

# -----------------------------
# FILTERS
# -----------------------------
near_expiry = df[df["days_to_expiry"] <= 2]
expired = df[df["days_to_expiry"] < 0]
delayed_df = df[df["delivery_status"] == "Delayed"]

# -----------------------------
# KPIs
# -----------------------------
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Stock", f"{df['stock_remaining'].sum():,}")
c2.metric("Near Expiry", len(near_expiry))
c3.metric("Expired Records", len(expired))
c4.metric("Delayed Deliveries", len(delayed_df))

st.markdown("---")

# -----------------------------
# ROLE-BASED PRIORITY ALERTS
# -----------------------------
st.subheader("🚨 Operations Priority Alerts")

if len(expired) > 0:
    st.error(f"🔴 {len(expired)} expired records detected. Immediate review required.")

if len(near_expiry) > 0:
    st.warning(f"🟡 {len(near_expiry)} products are near expiry.")

if len(delayed_df) > 0:
    st.warning(f"🚚 {len(delayed_df)} delayed deliveries detected.")

if len(expired) == 0 and len(near_expiry) == 0 and len(delayed_df) == 0:
    st.success("✅ No major inventory, expiry, or delivery issues detected.")

st.markdown("---")

# -----------------------------
# INVENTORY & EXPIRY
# -----------------------------
if role in ["Admin", "Manager", "Operations", "Quality"]:
    st.subheader("📦 Inventory & Expiry Monitoring")

    inventory_cols = [
        "batch_id",
        "product_name",
        "supplier",
        "stock_remaining",
        "expiry_date",
        "days_to_expiry"
    ]

    inventory_cols = [c for c in inventory_cols if c in df.columns]

    st.dataframe(
        df[inventory_cols].sort_values("days_to_expiry"),
        use_container_width=True
    )

    st.subheader("⚠️ Products Near Expiry")

    if len(near_expiry) > 0:
        st.dataframe(
            near_expiry[inventory_cols].sort_values("days_to_expiry"),
            use_container_width=True
        )
    else:
        st.success("✅ No products near expiry.")

    st.markdown("---")

# -----------------------------
# DELIVERY MONITORING
# -----------------------------
if role in ["Admin", "Manager", "Operations", "Logistics"]:
    st.subheader("🚚 Delivery Monitoring")

    delivery_counts = df["delivery_status"].value_counts().reset_index()
    delivery_counts.columns = ["Delivery Status", "Count"]

    fig_delivery = px.pie(
        delivery_counts,
        names="Delivery Status",
        values="Count",
        title="Delivery Status Distribution",
        hole=0.4
    )

    st.plotly_chart(fig_delivery, use_container_width=True)

    delivery_cols = [
        "date",
        "client",
        "customer",
        "product_name",
        "order_quantity",
        "delivery_status",
        "delivery_delay_days"
    ]

    delivery_cols = [c for c in delivery_cols if c in df.columns]

    st.subheader("Delayed Deliveries")

    if len(delayed_df) > 0:
        st.dataframe(
            delayed_df[delivery_cols],
            use_container_width=True
        )

        delayed_by_client = (
            delayed_df.groupby("client")
            .size()
            .reset_index(name="delayed_count")
            .sort_values("delayed_count", ascending=False)
        )

        fig_delay_client = px.bar(
            delayed_by_client,
            x="client",
            y="delayed_count",
            title="Delayed Deliveries by Client"
        )

        st.plotly_chart(fig_delay_client, use_container_width=True)
    else:
        st.success("✅ No delayed deliveries found.")

    st.markdown("---")

# -----------------------------
# STOCK BY PRODUCT
# -----------------------------
if role in ["Admin", "Manager", "Operations", "Quality"]:
    st.subheader("📊 Stock by Product")

    stock_product = (
        df.groupby("product_name")["stock_remaining"]
        .sum()
        .reset_index()
        .sort_values("stock_remaining", ascending=False)
    )

    fig_stock = px.bar(
        stock_product,
        x="product_name",
        y="stock_remaining",
        title="Stock Remaining by Product"
    )

    st.plotly_chart(fig_stock, use_container_width=True)

# -----------------------------
# ROLE-BASED RECOMMENDATIONS
# -----------------------------
st.markdown("---")
st.subheader("🎯 Recommended Actions")

recommendations = []

if role in ["Admin", "Operations", "Quality"] and len(near_expiry) > 0:
    recommendations.append("Review near-expiry products and prioritize dispatch or quality checks.")

if role in ["Admin", "Operations", "Logistics"] and len(delayed_df) > 0:
    recommendations.append("Coordinate with logistics to resolve delayed deliveries and notify affected clients.")

if role in ["Admin", "Manager"] and len(expired) > 0:
    recommendations.append("Escalate expired stock issue to operations management.")

if not recommendations:
    recommendations.append("Continue monitoring. No urgent operational actions required.")

for rec in recommendations:
    st.write(f"- {rec}")
