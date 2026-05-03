import streamlit as st
import pandas as pd
import plotly.express as px

from utils import inject_css
from data_utils import load_data
from auth_utils import require_role, get_current_user
from utils import setup_page, premium_hero, metric_card, insight_card, section_title, style_plotly

require_role(["Admin", "Manager", "Operations", "Logistics"])

setup_page("Operations Control")

inject_css()

# -----------------------------
# PREMIUM UI HELPERS
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

    .section-title {
        font-size: 1.22rem;
        font-weight: 850;
        color: #ffffff;
        margin: 1.5rem 0 0.8rem 0;
    }

    .metric-card {
        padding: 20px;
        border-radius: 18px;
        background: rgba(15,23,42,0.88);
        border: 1px solid rgba(34,197,94,0.24);
        box-shadow: 0 12px 32px rgba(0,0,0,0.28);
        min-height: 120px;
    }

    .metric-label {
        color: #9ca3af;
        font-size: 0.86rem;
        font-weight: 700;
    }

    .metric-value {
        color: #ffffff;
        font-size: 1.8rem;
        font-weight: 900;
        margin-top: 10px;
    }

    .metric-note {
        color: #86efac;
        font-size: 0.82rem;
        margin-top: 8px;
        font-weight: 650;
    }

    .insight-card {
        padding: 18px 20px;
        border-radius: 16px;
        background: rgba(15,23,42,0.82);
        border: 1px solid rgba(148,163,184,0.18);
        margin-bottom: 10px;
        color: #e5e7eb;
    }

    .insight-good {
        border-left: 4px solid #22c55e;
    }

    .insight-risk {
        border-left: 4px solid #f59e0b;
    }

    .insight-critical {
        border-left: 4px solid #ef4444;
    }
    </style>
    """, unsafe_allow_html=True)


def metric_card(label, value, note=""):
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-note">{note}</div>
    </div>
    """, unsafe_allow_html=True)


def insight_card(message, level="good"):
    css_class = {
        "good": "insight-good",
        "risk": "insight-risk",
        "critical": "insight-critical",
    }.get(level, "insight-good")

    st.markdown(f"""
    <div class="insight-card {css_class}">
        {message}
    </div>
    """, unsafe_allow_html=True)


def style_plotly(fig):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e5e7eb"),
        title_font=dict(size=18, color="#ffffff"),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e5e7eb")
        ),
        margin=dict(l=20, r=20, t=55, b=25),
    )
    fig.update_xaxes(gridcolor="rgba(148,163,184,0.15)")
    fig.update_yaxes(gridcolor="rgba(148,163,184,0.15)")
    return fig


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
# ROLE-BASED VIEW MESSAGE
# -----------------------------
st.markdown('<div class="section-title">🧭 Role-Based Operations View</div>', unsafe_allow_html=True)

if role == "Operations":
    insight_card("Operations view: focused on production readiness, stock, expiry, and bottlenecks.")
elif role == "Logistics":
    insight_card("Logistics view: focused on delayed deliveries, dispatch issues, and client impact.")
elif role == "Quality":
    insight_card("Quality view: focused on expiry risk, stock condition, and supplier/product issues.")
elif role == "Manager":
    insight_card("Manager view: summarized view of stock, expiry risk, and delivery performance.")
else:
    insight_card("Admin view: full operations, inventory, expiry, and delivery monitoring.")

# -----------------------------
# KPIs
# -----------------------------
st.markdown('<div class="section-title">📌 Operations KPIs</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)

with c1:
    metric_card("Total Stock", f"{df['stock_remaining'].sum():,.0f}", "Current available inventory")

with c2:
    metric_card("Near Expiry", f"{len(near_expiry)}", "≤ 2 days to expiry")

with c3:
    metric_card("Expired Records", f"{len(expired)}", "Immediate action required")

with c4:
    metric_card("Delayed Deliveries", f"{len(delayed_df)}", "Logistics exceptions")

# -----------------------------
# PRIORITY ALERTS
# -----------------------------
st.markdown('<div class="section-title">🚨 Operations Priority Alerts</div>', unsafe_allow_html=True)

a1, a2, a3 = st.columns(3)

with a1:
    if len(expired) > 0:
        insight_card(f"🔴 {len(expired)} expired records detected. Immediate review required.", level="critical")
    else:
        insight_card("✅ No expired stock records detected.")

with a2:
    if len(near_expiry) > 0:
        insight_card(f"🟡 {len(near_expiry)} products are near expiry.", level="risk")
    else:
        insight_card("✅ No near-expiry pressure detected.")

with a3:
    if len(delayed_df) > 0:
        insight_card(f"🚚 {len(delayed_df)} delayed deliveries detected.", level="risk")
    else:
        insight_card("✅ No delayed deliveries detected.")

# -----------------------------
# INVENTORY & EXPIRY
# -----------------------------
if role in ["Admin", "Manager", "Operations", "Quality"]:
    st.markdown('<div class="section-title">📦 Inventory & Expiry Monitoring</div>', unsafe_allow_html=True)

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

    st.markdown('<div class="section-title">⚠️ Products Near Expiry</div>', unsafe_allow_html=True)

    if len(near_expiry) > 0:
        st.dataframe(
            near_expiry[inventory_cols].sort_values("days_to_expiry"),
            use_container_width=True
        )
    else:
        insight_card("✅ No products near expiry.")

# -----------------------------
# DELIVERY MONITORING
# -----------------------------
if role in ["Admin", "Manager", "Operations", "Logistics"]:
    st.markdown('<div class="section-title">🚚 Delivery Monitoring</div>', unsafe_allow_html=True)

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
        fig_delivery = style_plotly(fig_delivery)
        st.plotly_chart(fig_delivery, use_container_width=True)

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
            fig_delay_client = style_plotly(fig_delay_client)
            st.plotly_chart(fig_delay_client, use_container_width=True)
        else:
            insight_card("✅ No delayed deliveries found.")

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

    st.markdown('<div class="section-title">Delayed Deliveries</div>', unsafe_allow_html=True)

    if len(delayed_df) > 0:
        st.dataframe(
            delayed_df[delivery_cols],
            use_container_width=True
        )
    else:
        insight_card("✅ No delayed deliveries found.")

# -----------------------------
# STOCK BY PRODUCT
# -----------------------------
if role in ["Admin", "Manager", "Operations", "Quality"]:
    st.markdown('<div class="section-title">📊 Stock by Product</div>', unsafe_allow_html=True)

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
    fig_stock = style_plotly(fig_stock)
    st.plotly_chart(fig_stock, use_container_width=True)

# -----------------------------
# ROLE-BASED RECOMMENDATIONS
# -----------------------------
st.markdown('<div class="section-title">🎯 Recommended Actions</div>', unsafe_allow_html=True)

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
    insight_card(f"✅ {rec}")
