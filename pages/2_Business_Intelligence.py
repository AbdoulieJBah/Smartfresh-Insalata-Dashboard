import streamlit as st
import plotly.express as px
import pandas as pd

from data_utils import load_data, calculate_kpis
from auth_utils import require_role, get_current_user

require_role(["Admin", "Manager", "Quality"])

st.set_page_config(page_title="Business Intelligence", layout="wide")

# -----------------------------
# PREMIUM UI HELPERS
# -----------------------------
def inject_page_css():
    st.markdown("""
    <style>
    .bi-hero {
        padding: 28px;
        border-radius: 24px;
        background:
            linear-gradient(135deg, rgba(15,23,42,0.96), rgba(6,78,59,0.76)),
            radial-gradient(circle at top right, rgba(34,197,94,0.22), transparent 35%);
        border: 1px solid rgba(34,197,94,0.35);
        box-shadow: 0 18px 48px rgba(0,0,0,0.35);
        margin-bottom: 24px;
    }

    .bi-hero h1 {
        font-size: 2.2rem;
        font-weight: 950;
        color: #ffffff;
        margin-bottom: 8px;
    }

    .bi-hero p {
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

    .premium-panel {
        padding: 20px;
        border-radius: 18px;
        background: rgba(15,23,42,0.78);
        border: 1px solid rgba(34,197,94,0.18);
        box-shadow: 0 10px 26px rgba(0,0,0,0.24);
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


def insight_card(message, risk=False):
    css_class = "insight-risk" if risk else "insight-good"
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


def safe_numeric(data, cols):
    for col in cols:
        if col not in data.columns:
            data[col] = 0
        data[col] = pd.to_numeric(data[col], errors="coerce").fillna(0)
    return data


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

required_numeric_cols = [
    "revenue",
    "waste_quantity",
    "defect_count",
    "temperature",
    "rating",
    "quantity_sold",
    "quantity_produced",
]

df = safe_numeric(df, required_numeric_cols)

if "client" not in df.columns:
    df["client"] = df["customer"] if "customer" in df.columns else "Unknown"

if "supplier" not in df.columns:
    df["supplier"] = "Unknown"

if "product_name" not in df.columns:
    df["product_name"] = "Unknown Product"

if "delivery_status" not in df.columns:
    df["delivery_status"] = "Unknown"

if "batch_id" not in df.columns:
    df["batch_id"] = "N/A"

date_col = "date" if "date" in df.columns else "order_date"

kpis = calculate_kpis(df)

# -----------------------------
# SENTIMENT FUNCTIONS
# -----------------------------
positive_words = [
    "good", "fresh", "excellent", "clean", "fast", "satisfied",
    "great", "quality", "acceptable", "reliable"
]

negative_words = [
    "bad", "late", "damaged", "poor", "spoiled", "dirty",
    "complaint", "smell", "defect", "delay", "problem"
]


def analyze_sentiment(text):
    text = str(text).lower()
    positive_score = sum(word in text for word in positive_words)
    negative_score = sum(word in text for word in negative_words)

    if positive_score > negative_score:
        return "Positive"
    if negative_score > positive_score:
        return "Negative"
    return "Neutral"


def sentiment_score(sentiment):
    if sentiment == "Positive":
        return 1
    if sentiment == "Negative":
        return -1
    return 0


if "feedback_text" in df.columns:
    df["sentiment"] = df["feedback_text"].apply(analyze_sentiment)
else:
    df["feedback_text"] = ""
    df["sentiment"] = "Neutral"

df["sentiment_score"] = df["sentiment"].apply(sentiment_score)

# -----------------------------
# HEADER
# -----------------------------
st.markdown(f"""
<div class="bi-hero">
    <h1>📊 Business Intelligence</h1>
    <p>
        Welcome <b>{user.get('name', 'User')}</b>. You are viewing this page as <b>{role}</b>.
        This module combines revenue intelligence, supplier quality, feedback sentiment,
        operational risk, and trend analytics.
    </p>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# ROLE VIEW
# -----------------------------
st.markdown('<div class="section-title">🧭 Role-Based Intelligence View</div>', unsafe_allow_html=True)

if role == "Manager":
    insight_card("Manager view: focused on revenue, clients, business performance, and strategic risks.")
elif role == "Operations":
    insight_card("Operations view: focused on production, waste, delays, temperature, and operational bottlenecks.")
elif role == "Quality":
    insight_card("Quality view: focused on defects, waste, supplier quality, sentiment, and temperature risks.")
elif role == "Logistics":
    insight_card("Logistics view: focused on delivery delays, dispatch risks, and client impact.")
else:
    insight_card("Admin view: full business, quality, operations, and logistics intelligence.")

# -----------------------------
# KPIs
# -----------------------------
total_revenue = df["revenue"].sum()
total_clients = df["client"].nunique()
total_suppliers = df["supplier"].nunique()
avg_rating = df["rating"].mean() if "rating" in df.columns else 0

positive_count = (df["sentiment"] == "Positive").sum()
neutral_count = (df["sentiment"] == "Neutral").sum()
negative_count = (df["sentiment"] == "Negative").sum()

st.markdown('<div class="section-title">📌 Strategic KPIs</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
with c1:
    metric_card("Total Revenue", f"€{total_revenue:,.2f}", "Business performance")
with c2:
    metric_card("Clients", f"{total_clients}", "Unique customer base")
with c3:
    metric_card("Suppliers", f"{total_suppliers}", "Supplier network")
with c4:
    metric_card("Avg Rating", f"{avg_rating:.2f}", "Feedback quality")

c5, c6, c7, c8 = st.columns(4)
with c5:
    metric_card("Total Defects", f"{kpis['total_defects']:,}", "Quality exceptions")
with c6:
    metric_card("Defect Rate", f"{kpis['defect_rate']:.2f}%", "Target threshold: 2%")
with c7:
    metric_card("Waste Rate", f"{kpis['waste_rate']:.2f}%", "Target threshold: 8%")
with c8:
    metric_card("Negative Feedback", f"{negative_count}", "Sentiment risk")

# -----------------------------
# REVENUE DROP INTELLIGENCE
# -----------------------------
if role in ["Admin", "Manager", "Operations"]:
    st.markdown('<div class="section-title">📉 Revenue Drop Intelligence</div>', unsafe_allow_html=True)

    if date_col in df.columns and "revenue" in df.columns:
        rev_df = df.copy()
        rev_df[date_col] = pd.to_datetime(rev_df[date_col], errors="coerce")
        rev_df = rev_df.dropna(subset=[date_col])

        daily_revenue = (
            rev_df.groupby(date_col)
            .agg(
                revenue=("revenue", "sum"),
                orders=("batch_id", "count"),
                quantity_sold=("quantity_sold", "sum"),
                waste=("waste_quantity", "sum"),
                defects=("defect_count", "sum"),
                delayed_deliveries=("delivery_status", lambda x: (x.astype(str).str.lower() == "delayed").sum())
            )
            .reset_index()
            .sort_values(date_col)
        )

        if len(daily_revenue) >= 2:
            latest = daily_revenue.iloc[-1]
            previous = daily_revenue.iloc[-2]

            previous_revenue = previous["revenue"]
            latest_revenue = latest["revenue"]

            revenue_change = latest_revenue - previous_revenue
            revenue_change_pct = (revenue_change / previous_revenue) * 100 if previous_revenue else 0

            r1, r2, r3, r4 = st.columns(4)
            with r1:
                metric_card("Previous Revenue", f"€{previous_revenue:,.2f}", "Previous period")
            with r2:
                metric_card("Latest Revenue", f"€{latest_revenue:,.2f}", "Latest period")
            with r3:
                metric_card("Revenue Change", f"€{revenue_change:,.2f}", f"{revenue_change_pct:.2f}%")
            with r4:
                metric_card("Latest Orders", f"{int(latest['orders'])}", "Order count")

            if revenue_change < 0:
                insight_card(
                    f"⚠️ Revenue decreased by <b>{abs(revenue_change_pct):.2f}%</b> compared with the previous period.",
                    risk=True
                )

                possible_causes = []

                if latest["orders"] < previous["orders"]:
                    possible_causes.append("Lower order volume")
                if latest["quantity_sold"] < previous["quantity_sold"]:
                    possible_causes.append("Lower quantity sold")
                if latest["waste"] > previous["waste"]:
                    possible_causes.append("Higher waste level")
                if latest["defects"] > previous["defects"]:
                    possible_causes.append("Higher defect count")
                if latest["delayed_deliveries"] > previous["delayed_deliveries"]:
                    possible_causes.append("More delayed deliveries")

                if possible_causes:
                    for cause in possible_causes:
                        insight_card(f"⚠️ Likely cause: {cause}", risk=True)
                else:
                    insight_card("Revenue dropped, but no obvious operational cause was detected.", risk=True)

                insight_card("Recommended actions: review client contribution, product revenue drops, supplier quality, and delivery performance.")
            else:
                insight_card(f"✅ Revenue increased by <b>{revenue_change_pct:.2f}%</b> compared with the previous period.")

            fig_revenue_drop = px.line(
                daily_revenue,
                x=date_col,
                y="revenue",
                title="Daily Revenue Trend",
                markers=True
            )
            fig_revenue_drop = style_plotly(fig_revenue_drop)
            st.plotly_chart(fig_revenue_drop, use_container_width=True)

        else:
            insight_card("Not enough date periods available to compare revenue changes.", risk=True)
    else:
        insight_card("Revenue Drop Intelligence requires date/order_date and revenue columns.", risk=True)

# -----------------------------
# REVENUE INSIGHTS
# -----------------------------
if role in ["Admin", "Manager"]:
    st.markdown('<div class="section-title">💰 Revenue Insights</div>', unsafe_allow_html=True)

    client_revenue = (
        df.groupby("client")["revenue"]
        .sum()
        .reset_index()
        .sort_values("revenue", ascending=False)
    )

    product_revenue = (
        df.groupby("product_name")["revenue"]
        .sum()
        .reset_index()
        .sort_values("revenue", ascending=False)
    )

    rc1, rc2 = st.columns(2)

    with rc1:
        fig_client = px.bar(
            client_revenue,
            x="client",
            y="revenue",
            title="Revenue by Client"
        )
        fig_client = style_plotly(fig_client)
        st.plotly_chart(fig_client, use_container_width=True)

    with rc2:
        fig_product = px.bar(
            product_revenue,
            x="product_name",
            y="revenue",
            title="Revenue by Product"
        )
        fig_product = style_plotly(fig_product)
        st.plotly_chart(fig_product, use_container_width=True)

    st.markdown('<div class="section-title">⚠️ Client Dependency Insight</div>', unsafe_allow_html=True)

    if client_revenue["revenue"].sum() > 0:
        client_revenue["revenue_share_%"] = (
            client_revenue["revenue"] / client_revenue["revenue"].sum()
        ) * 100

        top_client = client_revenue.iloc[0]

        insight_card(
            f"Top client <b>{top_client['client']}</b> contributes "
            f"<b>{top_client['revenue_share_%']:.2f}%</b> of total revenue.",
            risk=top_client["revenue_share_%"] > 40
        )

        if top_client["revenue_share_%"] > 40:
            insight_card("⚠️ High client concentration risk detected.", risk=True)
        else:
            insight_card("✅ Revenue is reasonably distributed across clients.")

        st.dataframe(client_revenue, use_container_width=True)
    else:
        insight_card("No revenue available for client dependency analysis.", risk=True)

# -----------------------------
# SUPPLIER QUALITY PERFORMANCE
# -----------------------------
supplier_perf = pd.DataFrame()

if role in ["Admin", "Manager", "Operations", "Quality"]:
    st.markdown('<div class="section-title">🏭 Supplier Quality Performance</div>', unsafe_allow_html=True)

    supplier_perf = (
        df.groupby("supplier")
        .agg(
            total_waste=("waste_quantity", "sum"),
            total_defects=("defect_count", "sum"),
            avg_temperature=("temperature", "mean"),
            avg_rating=("rating", "mean"),
            total_revenue=("revenue", "sum"),
            avg_sentiment_score=("sentiment_score", "mean"),
            negative_feedback=("sentiment", lambda x: (x == "Negative").sum()),
            total_feedback=("sentiment", "count")
        )
        .reset_index()
    )

    supplier_perf["quality_risk_score"] = (
        supplier_perf["total_waste"] * 0.4
        + supplier_perf["total_defects"] * 0.4
        + supplier_perf["avg_temperature"] * 10
        + supplier_perf["negative_feedback"] * 20
    )

    supplier_perf = supplier_perf.sort_values("quality_risk_score", ascending=False)

    sc1, sc2 = st.columns(2)

    with sc1:
        fig_supplier_risk = px.bar(
            supplier_perf,
            x="supplier",
            y="quality_risk_score",
            title="Supplier Quality Risk Score"
        )
        fig_supplier_risk = style_plotly(fig_supplier_risk)
        st.plotly_chart(fig_supplier_risk, use_container_width=True)

    with sc2:
        fig_supplier_quality = px.bar(
            supplier_perf,
            x="supplier",
            y=["total_defects", "total_waste"],
            barmode="group",
            title="Supplier Defects and Waste"
        )
        fig_supplier_quality = style_plotly(fig_supplier_quality)
        st.plotly_chart(fig_supplier_quality, use_container_width=True)

    st.dataframe(supplier_perf, use_container_width=True)

# -----------------------------
# TEMPERATURE RISK
# -----------------------------
if role in ["Admin", "Operations", "Quality"]:
    st.markdown('<div class="section-title">🌡️ Temperature Risk Records</div>', unsafe_allow_html=True)

    temp_issues = df[df["temperature"] > 6]

    if len(temp_issues) > 0:
        insight_card(f"⚠️ {len(temp_issues)} temperature risk records detected.", risk=True)

        available_cols = [
            "batch_id",
            "product_name",
            "supplier",
            "temperature",
            "defect_count",
            "waste_quantity"
        ]
        available_cols = [col for col in available_cols if col in temp_issues.columns]

        st.dataframe(temp_issues[available_cols], use_container_width=True)
    else:
        insight_card("✅ No temperature risk records detected.")

# -----------------------------
# SENTIMENT ANALYSIS
# -----------------------------
if role in ["Admin", "Manager", "Quality"]:
    st.markdown('<div class="section-title">💬 Supplier Feedback Sentiment</div>', unsafe_allow_html=True)

    sentiment_counts = df["sentiment"].value_counts().reset_index()
    sentiment_counts.columns = ["Sentiment", "Count"]

    s1, s2, s3 = st.columns(3)
    with s1:
        metric_card("Positive Feedback", f"{positive_count}", "Customer/supplier signals")
    with s2:
        metric_card("Neutral Feedback", f"{neutral_count}", "Neutral records")
    with s3:
        metric_card("Negative Feedback", f"{negative_count}", "Potential quality risk")

    sent1, sent2 = st.columns(2)

    with sent1:
        fig_sentiment = px.pie(
            sentiment_counts,
            names="Sentiment",
            values="Count",
            title="Feedback Sentiment Distribution",
            hole=0.45
        )
        fig_sentiment = style_plotly(fig_sentiment)
        st.plotly_chart(fig_sentiment, use_container_width=True)

    with sent2:
        if not supplier_perf.empty:
            fig_supplier_sentiment = px.bar(
                supplier_perf.sort_values("avg_sentiment_score"),
                x="supplier",
                y="avg_sentiment_score",
                title="Average Sentiment Score by Supplier"
            )
            fig_supplier_sentiment = style_plotly(fig_supplier_sentiment)
            st.plotly_chart(fig_supplier_sentiment, use_container_width=True)
        else:
            insight_card("Supplier sentiment requires supplier performance data.", risk=True)

    st.markdown('<div class="section-title">⚠️ Negative Feedback Alerts</div>', unsafe_allow_html=True)

    negative_df = df[df["sentiment"] == "Negative"]

    if len(negative_df) > 0:
        available_cols = [
            "date",
            "order_date",
            "supplier",
            "product_name",
            "feedback_text",
            "rating",
            "sentiment"
        ]
        available_cols = [col for col in available_cols if col in negative_df.columns]

        st.dataframe(negative_df[available_cols], use_container_width=True)
    else:
        insight_card("✅ No negative feedback detected.")

# -----------------------------
# BUSINESS & QUALITY TRENDS
# -----------------------------
st.markdown('<div class="section-title">📈 Business & Quality Trends Over Time</div>', unsafe_allow_html=True)

if date_col in df.columns:
    trend_df = df.copy()
    trend_df[date_col] = pd.to_datetime(trend_df[date_col], errors="coerce")

    trend_df = (
        trend_df.dropna(subset=[date_col])
        .groupby(date_col)
        .agg(
            revenue=("revenue", "sum"),
            waste=("waste_quantity", "sum"),
            defects=("defect_count", "sum")
        )
        .reset_index()
        .sort_values(date_col)
    )

    t1, t2 = st.columns(2)

    if role in ["Admin", "Manager"]:
        with t1:
            fig_revenue_trend = px.line(
                trend_df,
                x=date_col,
                y="revenue",
                title="Revenue Trend Over Time",
                markers=True
            )
            fig_revenue_trend = style_plotly(fig_revenue_trend)
            st.plotly_chart(fig_revenue_trend, use_container_width=True)

    if role in ["Admin", "Manager", "Operations", "Quality"]:
        with t2:
            fig_waste_trend = px.line(
                trend_df,
                x=date_col,
                y="waste",
                title="Waste Trend Over Time",
                markers=True
            )
            fig_waste_trend = style_plotly(fig_waste_trend)
            st.plotly_chart(fig_waste_trend, use_container_width=True)

        fig_defect_trend = px.line(
            trend_df,
            x=date_col,
            y="defects",
            title="Defect Trend Over Time",
            markers=True
        )
        fig_defect_trend = style_plotly(fig_defect_trend)
        st.plotly_chart(fig_defect_trend, use_container_width=True)
else:
    insight_card("Trend analysis requires date or order_date column.", risk=True)

# -----------------------------
# DOWNLOAD
# -----------------------------
if role in ["Admin", "Manager"]:
    st.download_button(
        "Download Business Intelligence Report",
        df.to_csv(index=False),
        "smartfresh_business_intelligence_report.csv",
        "text/csv"
    )
