import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Supplier Feedback Sentiment", layout="wide")

st.title("💬 Supplier Feedback Sentiment Analysis")

st.write(
    "Analyze supplier/customer feedback to detect quality concerns, delivery complaints, "
    "freshness issues, and supplier reputation trends."
)

# -----------------------------
# SAMPLE FEEDBACK DATA
# -----------------------------
def generate_feedback_data():
    return pd.DataFrame({
        "date": [
            "2026-04-01", "2026-04-02", "2026-04-03", "2026-04-04",
            "2026-04-05", "2026-04-06", "2026-04-07", "2026-04-08"
        ],
        "supplier": [
            "Farm A", "Farm B", "Farm C", "Farm A",
            "Farm C", "Farm D", "Farm B", "Farm C"
        ],
        "product_name": [
            "Spinach", "Rucola", "Mixed Salad", "Lettuce",
            "Baby Leaf", "Carrots", "Radicchio", "Spinach"
        ],
        "feedback_text": [
            "Fresh product and good packaging",
            "Delivery was late but product quality was acceptable",
            "Poor freshness and damaged packaging",
            "Excellent quality and fast delivery",
            "Spoiled leaves and bad smell reported",
            "Clean product and satisfied customer",
            "Packaging was damaged during transport",
            "Late delivery and poor product freshness"
        ],
        "rating": [5, 3, 1, 5, 1, 4, 2, 1]
    })


uploaded_file = st.file_uploader(
    "Upload supplier feedback CSV/Excel file",
    type=["csv", "xlsx"]
)

if uploaded_file is not None:
    if uploaded_file.name.endswith(".csv"):
        feedback_df = pd.read_csv(uploaded_file)
    else:
        feedback_df = pd.read_excel(uploaded_file)

    st.success("✅ Feedback dataset uploaded successfully")
else:
    feedback_df = generate_feedback_data()
    st.info("ℹ️ Using sample supplier feedback dataset")


# -----------------------------
# SENTIMENT FUNCTION
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
    else:
        return "Neutral"


def sentiment_score(sentiment):
    if sentiment == "Positive":
        return 1
    elif sentiment == "Negative":
        return -1
    return 0


# -----------------------------
# VALIDATION
# -----------------------------
required_cols = ["date", "supplier", "product_name", "feedback_text", "rating"]
missing_cols = [c for c in required_cols if c not in feedback_df.columns]

if missing_cols:
    st.error(f"Missing required columns: {', '.join(missing_cols)}")
    st.stop()


feedback_df["date"] = pd.to_datetime(feedback_df["date"], errors="coerce")
feedback_df["Sentiment"] = feedback_df["feedback_text"].apply(analyze_sentiment)
feedback_df["Sentiment Score"] = feedback_df["Sentiment"].apply(sentiment_score)


# -----------------------------
# KPIs
# -----------------------------
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


# -----------------------------
# CHARTS
# -----------------------------
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


# -----------------------------
# NEGATIVE FEEDBACK PANEL
# -----------------------------
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


# -----------------------------
# RAW DATA
# -----------------------------
with st.expander("📄 View Full Feedback Dataset"):
    st.dataframe(feedback_df, use_container_width=True)


# -----------------------------
# DOWNLOAD
# -----------------------------
st.download_button(
    "Download Sentiment Analysis Report",
    feedback_df.to_csv(index=False),
    "supplier_feedback_sentiment_report.csv",
    "text/csv"
)
