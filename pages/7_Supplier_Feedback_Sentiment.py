import streamlit as st
import pandas as pd
import plotly.express as px
from data_utils import load_data

st.set_page_config(page_title="Supplier Feedback Sentiment", layout="wide")

st.title("💬 Supplier Feedback Sentiment Analysis")

df = load_data()
df.columns = df.columns.str.strip().str.lower()

# Create rating if missing
if "rating" not in df.columns:
    df["rating"] = 3

required_columns = ["date", "supplier", "product_name", "feedback_text", "rating"]
missing_columns = [col for col in required_columns if col not in df.columns]

if missing_columns:
    st.error(f"Missing required columns: {', '.join(missing_columns)}")
    st.write("Available columns:", list(df.columns))
    st.stop()

feedback_df = df.copy()
feedback_df["date"] = pd.to_datetime(feedback_df["date"], errors="coerce")

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


feedback_df["Sentiment"] = feedback_df["feedback_text"].apply(analyze_sentiment)
feedback_df["Sentiment Score"] = feedback_df["Sentiment"].apply(sentiment_score)

total_feedback = len(feedback_df)
positive_count = (feedback_df["Sentiment"] == "Positive").sum()
neutral_count = (feedback_df["Sentiment"] == "Neutral").sum()
negative_count = (feedback_df["Sentiment"] == "Negative").sum()
avg_rating = feedback_df["rating"].mean()

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Feedback", total_feedback)
c2.metric("Positive", positive_count)
c3.metric("Neutral", neutral_count)
c4.metric("Negative", negative_count)
c5.metric("Avg Rating", f"{avg_rating:.2f}")

st.subheader("📊 Sentiment Overview")

sentiment_counts = feedback_df["Sentiment"].value_counts().reset_index()
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
    feedback_df.groupby("supplier")
    .agg(
        avg_sentiment_score=("Sentiment Score", "mean"),
        avg_rating=("rating", "mean"),
        negative_feedback=("Sentiment", lambda x: (x == "Negative").sum()),
        total_feedback=("Sentiment", "count")
    )
    .reset_index()
    .sort_values("avg_sentiment_score")
)

st.dataframe(supplier_sentiment, use_container_width=True)

fig_supplier = px.bar(
    supplier_sentiment,
    x="supplier",
    y="avg_sentiment_score",
    title="Average Sentiment Score by Supplier"
)

st.plotly_chart(fig_supplier, use_container_width=True)

st.subheader("⚠️ Negative Feedback Alerts")

negative_df = feedback_df[feedback_df["Sentiment"] == "Negative"]

if len(negative_df) > 0:
    st.dataframe(
        negative_df[[
            "date",
            "supplier",
            "product_name",
            "feedback_text",
            "rating",
            "Sentiment"
        ]],
        use_container_width=True
    )
else:
    st.success("No negative feedback detected.")

with st.expander("📄 View Full Feedback Dataset"):
    st.dataframe(feedback_df, use_container_width=True)

st.download_button(
    "Download Sentiment Analysis Report",
    feedback_df.to_csv(index=False),
    "supplier_feedback_sentiment_report.csv",
    "text/csv"
)
