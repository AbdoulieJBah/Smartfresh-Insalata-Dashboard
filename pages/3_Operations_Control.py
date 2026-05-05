import streamlit as st
import pandas as pd
import plotly.express as px

from data_utils import load_data
from auth_utils import require_role, get_current_user
from ai_utils import generate_ai_response_cached

from utils import (
    setup_page,
    metric_card,
    insight_card,
    section_title,
    style_plotly,
    set_copilot_context,
    render_global_copilot,
)

require_role(["Admin", "Manager", "Operations", "Logistics"])

setup_page("Operations Control", icon="🥬")


# -----------------------------
# PAGE CSS
# -----------------------------
def inject_page_css():
    st.markdown("""
    <style>
    .ops-hero {
        padding: 28px;
        border-radius: 24px;
        background:
            linear-gradient(135deg, rgba(15,23,42,0.96), rgba(6,78,59,0.76)),
            radial-gradient(circle at top right, rgba(34,197,94,0.22), transparent 35%);
        border: 1px solid rgba(34,197,94,0.35);
        box-shadow: 0 18px 48px rgba(0,0,0,0.35);
        margin-bottom: 24px;
    }

    .ops-hero h1 {
        font-size: 2.2rem;
        font-weight: 950;
        color: #ffffff;
        margin-bottom: 8px;
    }

    .ops-hero p {
        color: #d1d5db;
        font-size: 1rem;
        line-height: 1.65;
        margin: 0;
    }
    </style>
    """, unsafe_allow_html=True)


inject_page_css()

# -----------------------------
# USER CONTEXT
# -----------------------------
user = get_current_user()
role = user.get("role", "User")

# -----------------------------
# LOAD DATA
# -----------------------------
df = load_data()
df.columns = df.columns.str.strip().str.lower()

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

numeric_cols = ["stock_remaining", "delivery_delay_days", "order_quantity"]

for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

# -----------------------------
# FILTERS
# -----------------------------
near_expiry = df[df["days_to_expiry"] <= 2]
expired = df[df["days_to_expiry"] < 0]
delayed_df = df[df["delivery_status"] == "Delayed"]

# -----------------------------
# COPILOT CONTEXT
# -----------------------------
set_copilot_context(f"""
Page: Operations Control

Role: {role}

Operations KPIs:
- Total Stock: {df['stock_remaining'].sum():,.0f}
- Near Expiry Records: {len(near_expiry)}
- Expired Records: {len(expired)}
- Delayed Deliveries: {len(delayed_df)}

This page focuses on:
- Inventory monitoring
- Expiry risk
- Dispatch delays
- Client delivery impact
- Stock by product
- Operational recommendations

Rules:
- Expired stock requires immediate review.
- Products with <= 2 days to expiry should be prioritized for dispatch or quality checks.
- Delayed deliveries require logistics coordination.
""")

# -----------------------------
# HEADER
# -----------------------------
st.markdown(f"""
<div class="ops-hero">
    <h1>🥬 Operations Control</h1>
    <p>
        Welcome <b>{user.get('name', 'User')}</b>. You are viewing this module as <b>{role}</b>.
        Monitor inventory, expiry exposure, dispatch issues, and operational bottlenecks in real time.
    </p>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# ROLE VIEW
# -----------------------------
section_title("🧭 Role-Based Operations View")

if role == "Operations":
    insight_card(
        "Operations view: focused on production readiness, stock, expiry, and bottlenecks.",
        level="good"
    )
elif role == "Logistics":
    insight_card(
        "Logistics view: focused on delayed deliveries, dispatch issues, and client impact.",
        level="good"
    )
elif role == "Quality":
    insight_card(
        "Quality view: focused on expiry risk, stock condition, and supplier/product issues.",
        level="good"
    )
elif role == "Manager":
    insight_card(
        "Manager view: summarized view of stock, expiry risk, and delivery performance.",
        level="good"
    )
else:
    insight_card(
        "Admin view: full operations, inventory, expiry, and delivery monitoring.",
        level="good"
    )

# -----------------------------
# KPIs
# -----------------------------
section_title("📌 Operations KPIs")

c1, c2, c3, c4 = st.columns(4)

with c1:
    metric_card(
        "Total Stock",
        f"{df['stock_remaining'].sum():,.0f}",
        "Current available inventory"
    )

with c2:
    metric_card(
        "Near Expiry",
        f"{len(near_expiry)}",
        "≤ 2 days to expiry"
    )

with c3:
    metric_card(
        "Expired Records",
        f"{len(expired)}",
        "Immediate action required"
    )

with c4:
    metric_card(
        "Delayed Deliveries",
        f"{len(delayed_df)}",
        "Logistics exceptions"
    )

# -----------------------------
# PRIORITY ALERTS
# -----------------------------
section_title("🚨 Operations Priority Alerts")

a1, a2, a3 = st.columns(3)

with a1:
    if len(expired) > 0:
        insight_card(
            f"🔴 {len(expired)} expired records detected. Immediate review required.",
            level="critical"
        )
    else:
        insight_card(
            "✅ No expired stock records detected.",
            level="good"
        )

with a2:
    if len(near_expiry) > 0:
        insight_card(
            f"🟡 {len(near_expiry)} products are near expiry.",
            level="risk"
        )
    else:
        insight_card(
            "✅ No near-expiry pressure detected.",
            level="good"
        )

with a3:
    if len(delayed_df) > 0:
        insight_card(
            f"🚚 {len(delayed_df)} delayed deliveries detected.",
            level="risk"
        )
    else:
        insight_card(
            "✅ No delayed deliveries detected.",
            level="good"
        )

# -----------------------------
# INVENTORY & EXPIRY
# -----------------------------
section_title("📦 Inventory & Expiry Monitoring")

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

section_title("⚠️ Products Near Expiry")

if len(near_expiry) > 0:
    st.dataframe(
        near_expiry[inventory_cols].sort_values("days_to_expiry"),
        use_container_width=True
    )
else:
    insight_card(
        "✅ No products near expiry.",
        level="good"
    )

# -----------------------------
# DELIVERY MONITORING
# -----------------------------
section_title("🚚 Delivery Monitoring")

delivery_counts = df["delivery_status"].value_counts().reset_index()
delivery_counts.columns = ["Delivery Status", "Count"]

dc1, dc2 = st.columns(2)

with dc1:
    fig_delivery = px.pie(
        delivery_counts,
        names="Delivery Status",
        values="Count",
        title="Delivery Status Distribution",
        hole=0.45
    )

    st.plotly_chart(
        style_plotly(fig_delivery),
        use_container_width=True
    )

with dc2:
    if len(delayed_df) > 0:
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

        st.plotly_chart(
            style_plotly(fig_delay_client),
            use_container_width=True
        )
    else:
        insight_card(
            "✅ No delayed deliveries found.",
            level="good"
        )

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

section_title("Delayed Deliveries")

if len(delayed_df) > 0:
    st.dataframe(
        delayed_df[delivery_cols],
        use_container_width=True
    )
else:
    insight_card(
        "✅ No delayed deliveries found.",
        level="good"
    )

# -----------------------------
# STOCK BY PRODUCT
# -----------------------------
section_title("📊 Stock by Product")

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

st.plotly_chart(
    style_plotly(fig_stock),
    use_container_width=True
)

# -----------------------------
# AI QUICK ACTIONS
# -----------------------------
section_title("🤖 Operations AI Quick Actions")

qa1, qa2, qa3 = st.columns(3)

with qa1:
    if st.button(
        "📦 Explain Inventory Risk",
        use_container_width=True
    ):
        st.session_state.global_copilot_history.append(
            (
                "user",
                "Explain the inventory, expiry, and stock risks from this Operations Control page."
            )
        )
        st.rerun()

with qa2:
    if st.button(
        "🚚 Analyze Delivery Delays",
        use_container_width=True
    ):
        st.session_state.global_copilot_history.append(
            (
                "user",
                "Analyze the delayed deliveries and recommend logistics actions."
            )
        )
        st.rerun()

with qa3:
    if st.button(
        "🎯 Recommend Ops Actions",
        use_container_width=True
    ):
        st.session_state.global_copilot_history.append(
            (
                "user",
                "Recommend the top operational actions based on inventory, expiry, and delivery risks."
            )
        )
        st.rerun()

# -----------------------------
# ROLE-BASED RECOMMENDATIONS
# -----------------------------
section_title("🎯 Recommended Actions")

recommendations = []

if role in ["Admin", "Operations", "Quality"] and len(near_expiry) > 0:
    recommendations.append(
        "Review near-expiry products and prioritize dispatch or quality checks."
    )

if role in ["Admin", "Operations", "Logistics"] and len(delayed_df) > 0:
    recommendations.append(
        "Coordinate with logistics to resolve delayed deliveries and notify affected clients."
    )

if role in ["Admin", "Manager"] and len(expired) > 0:
    recommendations.append(
        "Escalate expired stock issue to operations management."
    )

if not recommendations:
    recommendations.append(
        "Continue monitoring. No urgent operational actions required."
    )

for rec in recommendations:
    insight_card(
        f"✅ {rec}",
        level="good"
    )

# -----------------------------
# GLOBAL AI COPILOT
# -----------------------------
render_global_copilot(generate_ai_response_cached)
