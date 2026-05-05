import random
import pandas as pd
from datetime import datetime, timedelta


# =========================================================
# MACHINE MASTER DATA
# =========================================================
MACHINES = [
    {
        "machine_id": "MES-01",
        "machine_name": "MES Operator Terminal",
        "machine_type": "MES Terminal",
        "line": "LINEA20",
        "product": "Spinacino Bio",
    },
    {
        "machine_id": "TOMRA-01",
        "machine_name": "TOMRA Optical Sorter",
        "machine_type": "Optical Sorter",
        "line": "LINEA20",
        "product": "Spinacino Bio",
    },
    {
        "machine_id": "ISHIDA-01",
        "machine_name": "Ishida Checkweigher",
        "machine_type": "Weigher",
        "line": "LINEA20",
        "product": "200g Sfalciati",
    },
    {
        "machine_id": "MARKEM-01",
        "machine_name": "Markem-Imaje SmartDate X40",
        "machine_type": "Printer / Coder",
        "line": "LINEA20",
        "product": "Spinacino Bio",
    },
    {
        "machine_id": "IDECON-01",
        "machine_name": "Idecon Packaging System",
        "machine_type": "Packaging",
        "line": "LINEA20",
        "product": "200g Sfalciati",
    },
]


# =========================================================
# MES OPERATOR SESSION
# =========================================================
def generate_operator_session():
    ordered_qty = 11520
    produced_qty = random.randint(2500, 7600)
    remaining = max(ordered_qty - produced_qty, 0)
    progress_pct = round((produced_qty / ordered_qty) * 100, 2)

    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "operator": "02",
        "shift": "Turno 2",
        "work_order": "26125492/83",
        "client": "Fruchtimport GmbH",
        "destination": "Germany",
        "product": "Spinacino Bio",
        "phase": "CONF + ETICH",
        "line": "LINEA20",
        "ordered_qty": ordered_qty,
        "produced_qty": produced_qty,
        "to_produce": random.randint(1000, 3000),
        "remaining": remaining,
        "progress_pct": progress_pct,
        "status": random.choices(
            ["Running", "Warning", "Stopped"],
            weights=[75, 18, 7],
            k=1
        )[0],
        "start_time": "04/05/2026 10:00",
        "notes": "Packaging and labeling in progress",
    }


# =========================================================
# MACHINE EVENT GENERATION
# =========================================================
def generate_machine_event(machine):
    status = random.choices(
        ["Running", "Running", "Running", "Warning", "Stopped"],
        weights=[55, 20, 10, 10, 5],
        k=1
    )[0]

    speed = random.randint(35, 115)
    target_speed = random.choice([60, 80, 100])
    temperature = round(random.uniform(2.5, 8.5), 1)
    reject_rate = round(random.uniform(0, 9), 2)
    downtime_minutes = random.randint(0, 35)
    vibration = round(random.uniform(0.1, 4.5), 2)

    target_weight = random.choice([100, 125, 200])
    weight_avg = round(random.uniform(target_weight - 12, target_weight + 12), 1)

    accepted_packs = random.randint(500, 3500)
    rejected_packs = int((reject_rate / 100) * accepted_packs)

    alarm = "None"
    risk_score = 0
    risk_reasons = []

    if status == "Stopped":
        risk_score += 35
        alarm = random.choice([
            "Machine stopped",
            "Emergency stop activated",
            "Material jam",
            "Operator pause",
        ])
        risk_reasons.append("Machine stopped")

    if status == "Warning" and alarm == "None":
        alarm = random.choice([
            "Low speed detected",
            "Weight deviation",
            "High reject rate",
            "Temperature risk",
            "Printer/coder warning",
        ])

    if speed < target_speed * 0.7:
        risk_score += 20
        risk_reasons.append("Production speed below target")

    if temperature > 6:
        risk_score += 25
        risk_reasons.append("Temperature above safe threshold")

    if reject_rate > 5:
        risk_score += 25
        risk_reasons.append("High reject rate")

    if downtime_minutes > 15:
        risk_score += 25
        risk_reasons.append("Downtime risk")

    if vibration > 3.5:
        risk_score += 20
        risk_reasons.append("Possible mechanical instability")

    if abs(weight_avg - target_weight) > 8:
        risk_score += 15
        risk_reasons.append("Weight outside tolerance")

    risk_score = min(risk_score, 100)

    if risk_score >= 70:
        risk_level = "High"
    elif risk_score >= 40:
        risk_level = "Medium"
    elif risk_score > 0:
        risk_level = "Low"
    else:
        risk_level = "Normal"

    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "machine_id": machine["machine_id"],
        "machine": machine["machine_name"],
        "machine_name": machine["machine_name"],
        "machine_type": machine["machine_type"],
        "line": machine["line"],
        "product": machine["product"],
        "status": status,
        "speed": speed,
        "target_speed": target_speed,
        "temperature": temperature,
        "target_weight": target_weight,
        "weight_avg": weight_avg,
        "accepted_packs": accepted_packs,
        "rejected_packs": rejected_packs,
        "reject_rate": reject_rate,
        "defect_rate": reject_rate,
        "downtime_minutes": downtime_minutes,
        "vibration": vibration,
        "alarm": alarm,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "risk_reasons": ", ".join(risk_reasons) if risk_reasons else "No major risk detected",
    }


# =========================================================
# SNAPSHOT + HISTORY
# =========================================================
def generate_machine_snapshot():
    events = [generate_machine_event(machine) for machine in MACHINES]
    return pd.DataFrame(events)


def generate_industry_40_events():
    return generate_machine_snapshot()


def generate_machine_history(cycles=50):
    history = []
    base_time = datetime.now() - timedelta(minutes=cycles)

    for i in range(cycles):
        event_time = base_time + timedelta(minutes=i)

        for machine in MACHINES:
            event = generate_machine_event(machine)
            event["timestamp"] = event_time.strftime("%Y-%m-%d %H:%M:%S")
            history.append(event)

    return pd.DataFrame(history)


# =========================================================
# MACHINE HEALTH SUMMARY
# =========================================================
def summarize_machine_health(df):
    if df.empty:
        return {
            "machines": 0,
            "running": 0,
            "warnings": 0,
            "stopped": 0,
            "high_risk": 0,
            "medium_risk": 0,
            "avg_risk_score": 0,
            "avg_temperature": 0,
            "avg_reject_rate": 0,
        }

    return {
        "machines": df["machine_id"].nunique(),
        "running": int((df["status"] == "Running").sum()),
        "warnings": int((df["status"] == "Warning").sum()),
        "stopped": int((df["status"] == "Stopped").sum()),
        "high_risk": int((df["risk_level"] == "High").sum()),
        "medium_risk": int((df["risk_level"] == "Medium").sum()),
        "avg_risk_score": round(df["risk_score"].mean(), 2),
        "avg_temperature": round(df["temperature"].mean(), 2),
        "avg_reject_rate": round(df["reject_rate"].mean(), 2),
    }


# =========================================================
# AI OPERATOR RECOMMENDATIONS
# =========================================================
def generate_ai_operator_recommendation(row):
    risk_score = row.get("risk_score", 0)
    risk_level = row.get("risk_level", "Normal")
    temperature = row.get("temperature", 0)
    reject_rate = row.get("reject_rate", 0)
    speed = row.get("speed", 0)
    target_speed = row.get("target_speed", 100)
    downtime = row.get("downtime_minutes", 0)
    vibration = row.get("vibration", 0)
    weight_avg = row.get("weight_avg", 0)
    target_weight = row.get("target_weight", 0)
    status = row.get("status", "")

    if risk_level == "High" or risk_score >= 70:
        return "Escalate immediately to operations or maintenance. Inspect the machine before continuing normal production."

    if status == "Stopped":
        return "Check machine stop reason, clear material jam if present, and notify maintenance if downtime continues."

    if temperature > 6:
        return "Check cold-chain conditions and verify product temperature stability."

    if reject_rate > 5:
        return "Inspect product quality, reject flow, and machine calibration settings."

    if speed < target_speed * 0.7:
        return "Review product feeding, operator workflow, and machine speed settings."

    if downtime > 15:
        return "Investigate downtime cause and create maintenance action."

    if vibration > 3.5:
        return "Inspect mechanical components and check for abnormal vibration."

    if target_weight and abs(weight_avg - target_weight) > 8:
        return "Check weighing calibration, tare settings, and product flow stability."

    return "Machine operating within acceptable simulated limits. Continue monitoring."


# =========================================================
# CONTROL ROOM SUMMARY
# =========================================================
def generate_control_room_summary(machine_df, operator_session):
    summary = summarize_machine_health(machine_df)

    highest_risk = None
    if not machine_df.empty:
        highest_risk = machine_df.sort_values("risk_score", ascending=False).iloc[0].to_dict()

    return {
        "line": operator_session.get("line", "N/A"),
        "work_order": operator_session.get("work_order", "N/A"),
        "product": operator_session.get("product", "N/A"),
        "operator": operator_session.get("operator", "N/A"),
        "shift": operator_session.get("shift", "N/A"),
        "progress_pct": operator_session.get("progress_pct", 0),
        "machines": summary["machines"],
        "running": summary["running"],
        "warnings": summary["warnings"],
        "stopped": summary["stopped"],
        "high_risk": summary["high_risk"],
        "avg_risk_score": summary["avg_risk_score"],
        "highest_risk_machine": highest_risk.get("machine", "N/A") if highest_risk else "N/A",
        "highest_risk_score": highest_risk.get("risk_score", 0) if highest_risk else 0,
        "highest_risk_reason": highest_risk.get("risk_reasons", "N/A") if highest_risk else "N/A",
    }
