import streamlit as st
import plotly.express as px
from data_utils import load_data, calculate_kpis

st.set_page_config(page_title="Business Intelligence", layout="wide")

st.title("📊 Business Intelligence — Strategic, Quality & Supplier Insights")

df = load_data()
df.columns = df.columns.str.strip().str.lower()

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
    elif negative_score > positive_score:
        return "Negative"
    return "Neutral"


def sentiment_score(sentiment):
    if sentiment == "Positive":
        return 1
    if sentiment == "Negative":
        return -1
    return 0


df["sentiment"] = df["feedback_text"].apply(analyze_sentiment)
df["sentiment_score"] = df["sentiment"].apply(sentiment_score)

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

st.subheader("📌 Strategic KPIs")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Revenue", f"€{total_revenue:,.2f}")
c2.metric("Clients", total_clients)
c3.metric("Suppliers", total_suppliers)
c4.metric("Avg Feedback Rating", f"{avg_rating:.2f}")

c5, c6, c7, c8 = st.columns(4)
c5.metric("Total Defects", f"{kpis['total_defects']:,}")
c6.metric("Defect Rate", f"{kpis['defect_rate']:.2f}%")
c7.metric("Waste Rate", f"{kpis['waste_rate']:.2f}%")
c8.metric("Negative Feedback", negative_count)

st.markdown("---")

# -----------------------------
# REVENUE INSIGHTS
# -----------------------------
st.subheader("💰 Revenue Insights")

client_revenue = (
    df.groupby("client")["revenue"]
    .sum()
    .reset_index()
    .sort_values("revenue", ascending=False)
)

fig_client = px.bar(
    client_revenue,
    x="client",
    y="revenue",
    title="Revenue by Client"
)
st.plotly_chart(fig_client, use_container_width=True)

product_revenue = (
    df.groupby("product_name")["revenue"]
    .sum()
    .reset_index()
    .sort_values("revenue", ascending=False)
)

fig_product = px.bar(
    product_revenue,
    x="product_name",
    y="revenue",
    title="Revenue by Product"
)
st.plotly_chart(fig_product, use_container_width=True)

# -----------------------------
# CLIENT DEPENDENCY
# -----------------------------
st.subheader("⚠️ Client Dependency Insight")

client_revenue["revenue_share_%"] = (
    client_revenue["revenue"] / client_revenue["revenue"].sum()
) * 100

top_client = client_revenue.iloc[0]

st.info(
    f"Top client **{top_client['client']}** contributes "
    f"**{top_client['revenue_share_%']:.2f}%** of total revenue."
)

if top_client["revenue_share_%"] > 40:
    st.warning("⚠️ High client concentration risk detected.")
else:
    st.success("✅ Revenue is reasonably distributed across clients.")

st.dataframe(client_revenue, use_container_width=True)

st.markdown("---")

# -----------------------------
# SUPPLIER QUALITY PERFORMANCE
# -----------------------------
st.subheader("🏭 Supplier Quality Performance")

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

st.dataframe(supplier_perf, use_container_width=True)

fig_supplier_risk = px.bar(
    supplier_perf,
    x="supplier",
    y="quality_risk_score",
    title="Supplier Quality Risk Score"
)
st.plotly_chart(fig_supplier_risk, use_container_width=True)

fig_supplier_quality = px.bar(
    supplier_perf,
    x="supplier",
    y=["total_defects", "total_waste"],
    barmode="group",
    title="Supplier Defects and Waste"
)
st.plotly_chart(fig_supplier_quality, use_container_width=True)

# -----------------------------
# TEMPERATURE RISK
# -----------------------------
st.subheader("🌡️ Temperature Risk Records")

temp_issues = df[df["temperature"] > 6]

if len(temp_issues) > 0:
    st.dataframe(
        temp_issues[[
            "batch_id",
            "product_name",
            "supplier",
            "temperature",
            "defect_count",
            "waste_quantity"
        ]],
        use_container_width=True
    )
else:
    st.success("✅ No temperature risk records detected.")

st.markdown("---")

# -----------------------------
# SENTIMENT ANALYSIS
# -----------------------------
st.subheader("💬 Supplier Feedback Sentiment")

sentiment_counts = df["sentiment"].value_counts().reset_index()
sentiment_counts.columns = ["Sentiment", "Count"]

s1, s2, s3 = st.columns(3)
s1.metric("Positive Feedback", positive_count)
s2.metric("Neutral Feedback", neutral_count)
s3.metric("Negative Feedback", negative_count)

fig_sentiment = px.pie(
    sentiment_counts,
    names="Sentiment",
    values="Count",
    title="Feedback Sentiment Distribution",
    hole=0.4,
    color="Sentiment",
    color_discrete_map={
        "Positive": "green",
        "Neutral": "orange",
        "Negative": "red"
    }
)
st.plotly_chart(fig_sentiment, use_container_width=True)

fig_supplier_sentiment = px.bar(
    supplier_perf.sort_values("avg_sentiment_score"),
    x="supplier",
    y="avg_sentiment_score",
    title="Average Sentiment Score by Supplier"
)
st.plotly_chart(fig_supplier_sentiment, use_container_width=True)

st.subheader("⚠️ Negative Feedback Alerts")

negative_df = df[df["sentiment"] == "Negative"]

if len(negative_df) > 0:
    available_cols = [
        "date",
        "supplier",
        "product_name",
        "feedback_text",
        "rating",
        "sentiment"
    ]
    available_cols = [col for col in available_cols if col in negative_df.columns]

    st.dataframe(
        negative_df[available_cols],
        use_container_width=True
    )
else:
    st.success("✅ No negative feedback detected.")

st.markdown("---")

# -----------------------------
# TRENDS
# -----------------------------
st.subheader("📈 Business & Quality Trends Over Time")

date_col = "date" if "date" in df.columns else "order_date"

if date_col in df.columns:
    trend_df = (
        df.groupby(date_col)
        .agg(
            revenue=("revenue", "sum"),
            waste=("waste_quantity", "sum"),
            defects=("defect_count", "sum")
        )
        .reset_index()
        .sort_values(date_col)
    )

    fig_revenue_trend = px.line(
        trend_df,
        x=date_col,
        y="revenue",
        title="Revenue Trend Over Time",
        markers=True
    )
    st.plotly_chart(fig_revenue_trend, use_container_width=True)

    fig_waste_trend = px.line(
        trend_df,
        x=date_col,
        y="waste",
        title="Waste Trend Over Time",
        markers=True
    )
    st.plotly_chart(fig_waste_trend, use_container_width=True)

    fig_defect_trend = px.line(
        trend_df,
        x=date_col,
        y="defects",
        title="Defect Trend Over Time",
        markers=True
    )
    st.plotly_chart(fig_defect_trend, use_container_width=True)

# -----------------------------
# DOWNLOAD
# -----------------------------
st.download_button(
    "Download Business Intelligence Report",
    df.to_csv(index=False),
    "smartfresh_business_intelligence_report.csv",
    "text/csv"
)
