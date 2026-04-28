import streamlit as st
import plotly.express as px
from data_utils import load_data, calculate_kpis

st.set_page_config(page_title="Quality & Sentiment", layout="wide")

st.title("✅ Quality & Supplier Sentiment — Defects, Waste & Feedback")

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
positive_count = (df["sentiment"] == "Positive").sum()
neutral_count = (df["sentiment"] == "Neutral").sum()
negative_count = (df["sentiment"] == "Negative").sum()

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Defects", f"{kpis['total_defects']:,}")
c2.metric("Defect Rate", f"{kpis['defect_rate']:.2f}%")
c3.metric("Positive Feedback", positive_count)
c4.metric("Neutral Feedback", neutral_count)
c5.metric("Negative Feedback", negative_count)

st.markdown("---")

# -----------------------------
# QUALITY CONTROL
# -----------------------------
st.subheader("🧪 Supplier Quality Analysis")

supplier_quality = (
    df.groupby("supplier")[["defect_count", "waste_quantity"]]
    .sum()
    .reset_index()
    .sort_values("defect_count", ascending=False)
)

fig_quality = px.bar(
    supplier_quality,
    x="supplier",
    y=["defect_count", "waste_quantity"],
    barmode="group",
    title="Defects and Waste by Supplier"
)

st.plotly_chart(fig_quality, use_container_width=True)

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

st.subheader("🏭 Supplier Sentiment Ranking")

supplier_sentiment = (
    df.groupby("supplier")
    .agg(
        avg_sentiment_score=("sentiment_score", "mean"),
        avg_rating=("rating", "mean"),
        negative_feedback=("sentiment", lambda x: (x == "Negative").sum()),
        total_feedback=("sentiment", "count"),
        total_defects=("defect_count", "sum"),
        total_waste=("waste_quantity", "sum")
    )
    .reset_index()
    .sort_values("avg_sentiment_score")
)

st.dataframe(supplier_sentiment, use_container_width=True)

fig_supplier_sentiment = px.bar(
    supplier_sentiment,
    x="supplier",
    y="avg_sentiment_score",
    title="Average Sentiment Score by Supplier"
)

st.plotly_chart(fig_supplier_sentiment, use_container_width=True)

st.subheader("⚠️ Negative Feedback Alerts")

negative_df = df[df["sentiment"] == "Negative"]

if len(negative_df) > 0:
    st.dataframe(
        negative_df[[
            "date",
            "supplier",
            "product_name",
            "feedback_text",
            "rating",
            "sentiment"
        ]],
        use_container_width=True
    )
else:
    st.success("✅ No negative feedback detected.")

st.download_button(
    "Download Quality & Sentiment Report",
    df.to_csv(index=False),
    "smartfresh_quality_sentiment_report.csv",
    "text/csv"
)
