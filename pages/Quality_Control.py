import streamlit as st
import plotly.express as px
from data_utils import load_data

st.title("✅ Quality Control")

df = load_data()

total_defects = df["defect_count"].sum()
total_production = df["quantity_produced"].sum()
defect_rate = (total_defects / total_production) * 100

c1, c2 = st.columns(2)
c1.metric("Total Defects", total_defects)
c2.metric("Defect Rate", f"{defect_rate:.2f}%")

supplier_quality = df.groupby("supplier")[["defect_count", "waste_quantity"]].sum().reset_index()

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
