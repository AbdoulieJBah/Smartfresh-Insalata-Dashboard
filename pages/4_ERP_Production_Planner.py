import streamlit as st
import pandas as pd
import numpy as np
import math
from datetime import datetime, timedelta
import plotly.express as px

from utils import inject_css
from data_utils import load_data
from auth_utils import require_role, get_current_user
from utils import setup_page, premium_hero, metric_card, insight_card, section_title, style_plotly

require_role(["Admin", "Manager", "Operations"])

setup_page("ERP Production Planner")

inject_css()

# -----------------------------
# PREMIUM UI HELPERS
# -----------------------------
def inject_page_css():
    st.markdown("""
    <style>
    .erp-hero {
        padding: 28px;
        border-radius: 24px;
        background:
            linear-gradient(135deg, rgba(15,23,42,0.96), rgba(6,78,59,0.76)),
            radial-gradient(circle at top right, rgba(34,197,94,0.22), transparent 35%);
        border: 1px solid rgba(34,197,94,0.35);
        box-shadow: 0 18px 48px rgba(0,0,0,0.35);
        margin-bottom: 24px;
    }

    .erp-hero h1 {
        font-size: 2.2rem;
        font-weight: 950;
        color: #ffffff;
        margin-bottom: 8px;
    }

    .erp-hero p {
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
        padding: 18px;
        border-radius: 18px;
        background: rgba(15,23,42,0.88);
        border: 1px solid rgba(34,197,94,0.24);
        box-shadow: 0 12px 32px rgba(0,0,0,0.28);
        min-height: 115px;
    }

    .metric-label {
        color: #9ca3af;
        font-size: 0.82rem;
        font-weight: 700;
    }

    .metric-value {
        color: #ffffff;
        font-size: 1.65rem;
        font-weight: 900;
        margin-top: 10px;
    }

    .metric-note {
        color: #86efac;
        font-size: 0.8rem;
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

    .insight-good { border-left: 4px solid #22c55e; }
    .insight-risk { border-left: 4px solid #f59e0b; }
    .insight-critical { border-left: 4px solid #ef4444; }
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
# CONFIG
# -----------------------------
machines = {
    "Machine A": {"speed": 4200, "setup_minutes": 30},
    "Machine B": {"speed": 3600, "setup_minutes": 25},
    "Machine C": {"speed": 5000, "setup_minutes": 35},
}

shifts = {
    "Shift 1": {"start": "06:00", "end": "14:00", "min_hours": 6},
    "Shift 2": {"start": "14:00", "end": "22:00", "min_hours": 6},
}

# -----------------------------
# DEFAULT FIELDS
# -----------------------------
if "client" not in df.columns:
    df["client"] = df["customer"] if "customer" in df.columns else "Unknown"

if "product_name" not in df.columns:
    df["product_name"] = "Unknown Product"

if "batch_id" not in df.columns:
    df["batch_id"] = "N/A"

if "order_quantity" not in df.columns:
    if "quantity_sold" in df.columns:
        df["order_quantity"] = df["quantity_sold"]
    else:
        df["order_quantity"] = 0

df["order_quantity"] = pd.to_numeric(df["order_quantity"], errors="coerce").fillna(0)

if "colli_ordered" not in df.columns:
    df["colli_ordered"] = np.ceil(df["order_quantity"] / 4).astype(int)

if "departure_datetime" not in df.columns:
    base = datetime.now().replace(minute=0, second=0, microsecond=0)
    df["departure_datetime"] = [
        base + timedelta(hours=int(np.random.randint(6, 48)))
        for _ in range(len(df))
    ]

df["departure_datetime"] = pd.to_datetime(df["departure_datetime"], errors="coerce")

# -----------------------------
# HEADER
# -----------------------------
st.markdown(f"""
<div class="erp-hero">
    <h1>🏭 ERP Production Planner</h1>
    <p>
        Welcome <b>{user.get('name', 'User')}</b>. You are viewing this page as <b>{role}</b>.
        Optimize packaging, shifts, machines, workload balance, deadlines, incoming cases, and pedane requirements.
    </p>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# ROLE MESSAGE
# -----------------------------
st.markdown('<div class="section-title">🧭 Role-Based Planning View</div>', unsafe_allow_html=True)

if role == "Operations":
    insight_card("Operations view: full access to planning controls, shift balancing, and machine optimization.")
elif role == "Manager":
    insight_card("Manager view: strategic review of production capacity, workload balance, and scheduling risks.")
else:
    insight_card("Admin view: full ERP planning and optimization control.")

# -----------------------------
# SIDEBAR SETTINGS
# -----------------------------
st.sidebar.header("⚙️ ERP Planner Settings")

buste_per_collo = st.sidebar.number_input("Buste per Collo", value=4, disabled=role == "Manager")
grams_per_busta = st.sidebar.number_input("Grams per Busta", value=125, disabled=role == "Manager")
waste_percent = st.sidebar.slider("Waste / Machine Loss %", 0, 20, 5, disabled=role == "Manager")
colli_per_pallet = st.sidebar.number_input("Colli per Pedana", value=192, disabled=role == "Manager")
kg_per_incoming_case = st.sidebar.number_input("Kg per Incoming Case", value=6, disabled=role == "Manager")

orders_to_optimize = st.sidebar.slider("Orders to Optimize", 10, 150, 40)

selected_machines = st.sidebar.multiselect(
    "Available Machines",
    list(machines.keys()),
    default=list(machines.keys()),
    disabled=role == "Manager"
)

balance_weight = st.sidebar.slider(
    "Shift Balance Priority",
    0,
    10,
    5,
    disabled=role == "Manager"
)

if not selected_machines:
    insight_card("Please select at least one machine.", level="critical")
    st.stop()

# -----------------------------
# SHIFT TIME SETUP
# -----------------------------
today = datetime.today().date()


def make_dt(time_str):
    return datetime.combine(today, datetime.strptime(time_str, "%H:%M").time())


shift_windows = {
    shift: {
        "start": make_dt(info["start"]),
        "end": make_dt(info["end"]),
        "min_hours": info["min_hours"]
    }
    for shift, info in shifts.items()
}

availability = {}

for shift_name, shift_info in shift_windows.items():
    for machine in selected_machines:
        availability[(shift_name, machine)] = shift_info["start"]

shift_minutes_assigned = {shift: 0 for shift in shifts.keys()}

orders = df.sort_values("departure_datetime").head(orders_to_optimize).copy()
scheduled = []

# -----------------------------
# OPTIMIZATION LOOP
# -----------------------------
for _, row in orders.iterrows():
    colli = int(row["colli_ordered"])

    total_buste = colli * buste_per_collo
    net_kg = (total_buste * grams_per_busta) / 1000
    production_kg = net_kg * (1 + waste_percent / 100)

    incoming_cases_needed = math.ceil(production_kg / kg_per_incoming_case)
    pedane_needed = math.ceil(colli / colli_per_pallet)

    best_option = None
    best_score = float("inf")

    for shift_name, shift_info in shift_windows.items():
        for machine in selected_machines:
            speed = machines[machine]["speed"]
            setup = machines[machine]["setup_minutes"]

            production_minutes = math.ceil((total_buste / speed) * 60) + setup

            start_time = availability[(shift_name, machine)]
            finish_time = start_time + timedelta(minutes=production_minutes)

            shift_overtime = max(0, (finish_time - shift_info["end"]).total_seconds() / 60)
            departure_time = row["departure_datetime"]
            lateness = max(0, (finish_time - departure_time).total_seconds() / 60)
            slack = (departure_time - finish_time).total_seconds() / 60

            avg_shift_minutes = (
                sum(shift_minutes_assigned.values()) / len(shift_minutes_assigned)
                if shift_minutes_assigned else 0
            )

            balance_penalty = abs(
                (shift_minutes_assigned[shift_name] + production_minutes)
                - avg_shift_minutes
            )

            min_required_minutes = shift_info["min_hours"] * 60
            underfilled_bonus = -120 if shift_minutes_assigned[shift_name] < min_required_minutes else 0

            score = (
                lateness * 10
                + shift_overtime * 6
                + balance_penalty * balance_weight
                + production_minutes * 0.1
                + underfilled_bonus
            )

            if score < best_score:
                best_score = score
                best_option = {
                    "shift": shift_name,
                    "machine": machine,
                    "start_time": start_time,
                    "finish_time": finish_time,
                    "production_minutes": production_minutes,
                    "setup_minutes": setup,
                    "speed": speed,
                    "lateness": lateness,
                    "slack": slack,
                    "shift_overtime": shift_overtime,
                    "score": score
                }

    shift = best_option["shift"]
    machine = best_option["machine"]

    availability[(shift, machine)] = best_option["finish_time"]
    shift_minutes_assigned[shift] += best_option["production_minutes"]

    if best_option["lateness"] > 0:
        status = "Late"
    elif best_option["slack"] <= 60:
        status = "At Risk"
    elif best_option["slack"] <= 180:
        status = "Urgent"
    else:
        status = "On Time"

    scheduled.append({
        "client": row.get("client", "Unknown"),
        "product_name": row.get("product_name", ""),
        "batch_id": row.get("batch_id", ""),
        "colli_ordered": colli,
        "total_buste": total_buste,
        "net_kg": round(net_kg, 2),
        "production_kg": round(production_kg, 2),
        "incoming_cases_needed": incoming_cases_needed,
        "pedane_needed": pedane_needed,
        "shift": shift,
        "machine": machine,
        "machine_speed": best_option["speed"],
        "setup_minutes": best_option["setup_minutes"],
        "production_minutes": best_option["production_minutes"],
        "start_time": best_option["start_time"],
        "finish_time": best_option["finish_time"],
        "departure_datetime": row["departure_datetime"],
        "slack_minutes": round(best_option["slack"], 1),
        "lateness_minutes": round(best_option["lateness"], 1),
        "shift_overtime_minutes": round(best_option["shift_overtime"], 1),
        "status": status,
        "optimization_score": round(best_option["score"], 2)
    })

opt_df = pd.DataFrame(scheduled)

# -----------------------------
# KPIs
# -----------------------------
st.markdown('<div class="section-title">📌 Optimization Summary</div>', unsafe_allow_html=True)

k1, k2, k3, k4, k5, k6 = st.columns(6)

with k1:
    metric_card("Orders Optimized", f"{len(opt_df)}", "Selected workload")
with k2:
    metric_card("Late Orders", f"{(opt_df['status'] == 'Late').sum()}", "Critical risk")
with k3:
    metric_card("At Risk", f"{(opt_df['status'] == 'At Risk').sum()}", "≤ 60 min slack")
with k4:
    metric_card("Urgent", f"{(opt_df['status'] == 'Urgent').sum()}", "≤ 180 min slack")
with k5:
    metric_card("Incoming Cases", f"{opt_df['incoming_cases_needed'].sum():,}", "Raw material need")
with k6:
    metric_card("Pedane Needed", f"{opt_df['pedane_needed'].sum():,}", "Logistics units")

# -----------------------------
# PLANNING INTELLIGENCE
# -----------------------------
st.markdown('<div class="section-title">🧠 Planning Intelligence</div>', unsafe_allow_html=True)

late_orders = (opt_df["status"] == "Late").sum()
risk_orders = (opt_df["status"] == "At Risk").sum()
urgent_orders = (opt_df["status"] == "Urgent").sum()

if late_orders > 0:
    insight_card(f"🔴 {late_orders} orders are late. Immediate replanning required.", level="critical")
elif risk_orders > 0:
    insight_card(f"🟡 {risk_orders} orders are at risk. Consider faster machine allocation.", level="risk")
elif urgent_orders > 0:
    insight_card(f"🟠 {urgent_orders} urgent orders should be monitored closely.", level="risk")
else:
    insight_card("✅ Production plan is currently feasible and on time.")

# -----------------------------
# SHIFT BALANCE
# -----------------------------
st.markdown('<div class="section-title">⚖️ Shift Workload Balance</div>', unsafe_allow_html=True)

shift_summary = (
    opt_df.groupby("shift")
    .agg(
        orders=("client", "count"),
        total_minutes=("production_minutes", "sum"),
        total_kg=("production_kg", "sum"),
        total_buste=("total_buste", "sum")
    )
    .reset_index()
)

shift_summary["hours"] = shift_summary["total_minutes"] / 60

fig_shift = px.bar(
    shift_summary,
    x="shift",
    y="hours",
    text="hours",
    title="Optimized Workload by Shift"
)
fig_shift = style_plotly(fig_shift)
st.plotly_chart(fig_shift, use_container_width=True)

for _, row in shift_summary.iterrows():
    min_hours = shifts[row["shift"]]["min_hours"]

    if row["hours"] < min_hours:
        insight_card(
            f"⚠️ {row['shift']} has only {row['hours']:.2f} hours. Minimum target is {min_hours} hours.",
            level="risk"
        )
    else:
        insight_card(f"✅ {row['shift']} meets minimum workload: {row['hours']:.2f} hours.")

st.dataframe(shift_summary, use_container_width=True)

# -----------------------------
# MACHINE WORKLOAD
# -----------------------------
st.markdown('<div class="section-title">⚙️ Machine Workload Distribution</div>', unsafe_allow_html=True)

machine_summary = (
    opt_df.groupby(["shift", "machine"])
    .agg(
        orders=("client", "count"),
        minutes=("production_minutes", "sum"),
        kg=("production_kg", "sum"),
        buste=("total_buste", "sum")
    )
    .reset_index()
)

machine_summary["hours"] = machine_summary["minutes"] / 60

fig_machine = px.bar(
    machine_summary,
    x="machine",
    y="hours",
    color="shift",
    barmode="group",
    title="Machine Workload by Shift"
)
fig_machine = style_plotly(fig_machine)
st.plotly_chart(fig_machine, use_container_width=True)

st.dataframe(machine_summary, use_container_width=True)

# -----------------------------
# TIMELINE
# -----------------------------
st.markdown('<div class="section-title">🗓️ Optimized Production Timeline</div>', unsafe_allow_html=True)

timeline_df = opt_df.copy()
timeline_df["task"] = (
    timeline_df["client"].astype(str)
    + " | "
    + timeline_df["product_name"].astype(str)
)

fig_timeline = px.timeline(
    timeline_df,
    x_start="start_time",
    x_end="finish_time",
    y="machine",
    color="status",
    facet_row="shift",
    hover_data=[
        "client",
        "product_name",
        "colli_ordered",
        "total_buste",
        "production_kg",
        "incoming_cases_needed",
        "pedane_needed",
        "departure_datetime",
        "slack_minutes",
        "lateness_minutes"
    ],
    title="Automatic Shift + Machine Schedule"
)

fig_timeline.update_yaxes(autorange="reversed")
fig_timeline = style_plotly(fig_timeline)
st.plotly_chart(fig_timeline, use_container_width=True)

# -----------------------------
# TABLE
# -----------------------------
st.markdown('<div class="section-title">📋 Detailed Optimized Production Plan</div>', unsafe_allow_html=True)

display_cols = [
    "client",
    "product_name",
    "colli_ordered",
    "total_buste",
    "production_kg",
    "incoming_cases_needed",
    "pedane_needed",
    "shift",
    "machine",
    "start_time",
    "finish_time",
    "departure_datetime",
    "slack_minutes",
    "status",
]

st.dataframe(
    opt_df[display_cols].sort_values(["departure_datetime", "start_time"]),
    use_container_width=True
)

if role in ["Admin", "Operations"]:
    st.download_button(
        "Download Optimized Production Plan",
        opt_df.to_csv(index=False),
        "smartfresh_optimized_production_plan.csv",
        "text/csv"
    )
else:
    insight_card("Manager view is read-only. Download access is limited to Admin and Operations roles.", level="risk")
