import streamlit as st
import plotly.express as px
from data_utils import load_data, calculate_kpis

st.set_page_config(page_title="Quality Control", layout="wide")

st.title("✅ Quality Control — Supplier & Defect Analysis")

df = load_data()
kpis = calculate_kpis(df)

c1, c2, c3 = st.columns(3)
c1.metric("Total Defects", kpis["total_defects"])
c2.metric("Defect Rate", f"{kpis['defect_rate']:.2f}%")
c3.metric("Temperature Risk Records", len(df[df["temperature"] > 6]))

supplier_quality = df.groupby("supplier")[[
    "defect_count",
    "waste_quantity"
]].sum().reset_index()

fig = px.bar(
    supplier_quality.sort_values("defect_count", ascending=False),
    x="supplier",
    y="defect_count",
    title="Defects by Supplier"
)

st.plotly_chart(fig, use_container_width=True)

st.subheader("🌡️ Temperature Risk Records")

temp_issues = df[df["temperature"] > 6]

st.dataframe(
    temp_issues[[
        "batch_id",
        "product_name",
        "supplier",
        "temperature",
        "defect_count"
    ]],
    use_container_width=True
)
