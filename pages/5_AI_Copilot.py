import streamlit as st
import json
from data_utils import load_data, calculate_kpis
from ai_utils import generate_ai_response
from auth_utils import require_role

require_role(["Admin", "Manager", "Operations", "Quality", "Logistics"])
from production_tools import (
    calculate_from_colli,
    calculate_from_cases,
    calculate_from_kg,
    estimate_machine_schedule
)

st.set_page_config(page_title="AI Copilot", layout="wide")

st.title("🤖 SmartFresh AI Copilot — Operations & Production Assistant")

df = load_data()
kpis = calculate_kpis(df)

st.markdown("""
Ask questions about production, inventory, waste, suppliers, deliveries, traceability, and ERP planning.

This copilot can also run real production tools:
- Colli → cases / kg / pedane
- Incoming cases → possible colli
- Available kg → possible colli
- Machine start-time scheduling
""")

if "smartfresh_chat" not in st.session_state:
    st.session_state.smartfresh_chat = []


def run_tool(tool_name, args):
    if tool_name == "calculate_from_colli":
        return calculate_from_colli(**args)
    if tool_name == "calculate_from_cases":
        return calculate_from_cases(**args)
    if tool_name == "calculate_from_kg":
        return calculate_from_kg(**args)
    if tool_name == "estimate_machine_schedule":
        return estimate_machine_schedule(**args)

    return {"error": "Unknown tool"}


def detect_tool_request(question):
    q = question.lower()

    if "incoming cases" in q or ("cases" in q and "produce" in q):
        return "calculate_from_cases"

    if "available kg" in q or ("kg" in q and "make" in q):
        return "calculate_from_kg"

    if "colli" in q and ("cases" in q or "pedane" in q or "pallet" in q):
        return "calculate_from_colli"

    if "machine" in q or "departure" in q or "start time" in q:
        return "estimate_machine_schedule"

    return None


for msg in st.session_state.smartfresh_chat:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

question = st.chat_input("Ask SmartFresh AI...")

if question:
    st.session_state.smartfresh_chat.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.markdown(question)

    tool_name = detect_tool_request(question)

    with st.chat_message("assistant"):
        if tool_name:
            st.info(f"🔧 Suggested tool: `{tool_name}`")
            st.warning("Enter the values below so the tool can calculate accurately.")

            with st.form("tool_form"):
                if tool_name == "calculate_from_colli":
                    colli = st.number_input("Colli ordered", value=3456)
                    buste_per_collo = st.number_input("Buste per collo", value=4)
                    grams_per_busta = st.number_input("Grams per busta", value=125)
                    kg_per_case = st.number_input("Kg per incoming case", value=6)
                    colli_per_pallet = st.number_input("Colli per pallet / pedana", value=192)
                    waste_percent = st.number_input("Waste %", value=5)

                    submitted = st.form_submit_button("Run Tool")

                    if submitted:
                        result = run_tool(
                            "calculate_from_colli",
                            {
                                "colli": colli,
                                "buste_per_collo": buste_per_collo,
                                "grams_per_busta": grams_per_busta,
                                "kg_per_case": kg_per_case,
                                "colli_per_pallet": colli_per_pallet,
                                "waste_percent": waste_percent
                            }
                        )

                        st.json(result)

                        prompt = f"""
You are a production planning expert for a fresh produce packaging company.

User question:
{question}

Tool result:
{json.dumps(result, indent=2)}

Explain the result clearly:
- total buste
- total kg
- incoming cases needed
- pedane needed
- operational recommendation
- highlight risks with ⚠️ if needed
"""

                        answer = generate_ai_response(prompt)
                        st.markdown(answer)

                        st.session_state.smartfresh_chat.append({
                            "role": "assistant",
                            "content": answer
                        })

                elif tool_name == "calculate_from_cases":
                    incoming_cases = st.number_input("Incoming cases", value=288)
                    kg_per_case = st.number_input("Kg per incoming case", value=6)
                    buste_per_collo = st.number_input("Buste per collo", value=4)
                    grams_per_busta = st.number_input("Grams per busta", value=125)
                    colli_per_pallet = st.number_input("Colli per pallet / pedana", value=192)
                    waste_percent = st.number_input("Waste %", value=0)

                    submitted = st.form_submit_button("Run Tool")

                    if submitted:
                        result = run_tool(
                            "calculate_from_cases",
                            {
                                "incoming_cases": incoming_cases,
                                "kg_per_case": kg_per_case,
                                "buste_per_collo": buste_per_collo,
                                "grams_per_busta": grams_per_busta,
                                "colli_per_pallet": colli_per_pallet,
                                "waste_percent": waste_percent
                            }
                        )

                        st.json(result)

                        prompt = f"""
You are a production planning expert.

User question:
{question}

Tool result:
{json.dumps(result, indent=2)}

Explain:
- available kg
- usable kg after waste
- possible buste
- possible colli
- pedane needed
- whether this could satisfy a production order
"""

                        answer = generate_ai_response(prompt)
                        st.markdown(answer)

                        st.session_state.smartfresh_chat.append({
                            "role": "assistant",
                            "content": answer
                        })

                elif tool_name == "calculate_from_kg":
                    available_kg = st.number_input("Available kg", value=1728)
                    buste_per_collo = st.number_input("Buste per collo", value=4)
                    grams_per_busta = st.number_input("Grams per busta", value=125)
                    kg_per_case = st.number_input("Kg per incoming case", value=6)
                    colli_per_pallet = st.number_input("Colli per pallet / pedana", value=192)
                    waste_percent = st.number_input("Waste %", value=0)

                    submitted = st.form_submit_button("Run Tool")

                    if submitted:
                        result = run_tool(
                            "calculate_from_kg",
                            {
                                "available_kg": available_kg,
                                "buste_per_collo": buste_per_collo,
                                "grams_per_busta": grams_per_busta,
                                "kg_per_case": kg_per_case,
                                "colli_per_pallet": colli_per_pallet,
                                "waste_percent": waste_percent
                            }
                        )

                        st.json(result)

                        prompt = f"""
You are a production planning expert.

User question:
{question}

Tool result:
{json.dumps(result, indent=2)}

Explain clearly:
- how many buste can be produced
- how many colli can be produced
- equivalent cases
- pedane needed
- recommendation
"""

                        answer = generate_ai_response(prompt)
                        st.markdown(answer)

                        st.session_state.smartfresh_chat.append({
                            "role": "assistant",
                            "content": answer
                        })

                elif tool_name == "estimate_machine_schedule":
                    total_buste = st.number_input("Total buste", value=13824)
                    machine_speed_buste_per_hour = st.number_input("Machine speed buste/hour", value=4000)
                    setup_minutes = st.number_input("Setup minutes", value=30)
                    departure_datetime = st.text_input("Departure datetime", value="2026-04-30 18:00")

                    submitted = st.form_submit_button("Run Tool")

                    if submitted:
                        result = run_tool(
                            "estimate_machine_schedule",
                            {
                                "total_buste": total_buste,
                                "machine_speed_buste_per_hour": machine_speed_buste_per_hour,
                                "setup_minutes": setup_minutes,
                                "departure_datetime": departure_datetime
                            }
                        )

                        st.json(result)

                        prompt = f"""
You are a production scheduling expert.

User question:
{question}

Tool result:
{json.dumps(result, indent=2)}

Explain:
- production duration
- setup time
- recommended start time
- departure risk
- practical recommendation
"""

                        answer = generate_ai_response(prompt)
                        st.markdown(answer)

                        st.session_state.smartfresh_chat.append({
                            "role": "assistant",
                            "content": answer
                        })

        else:
            sample_data = df.sample(min(25, len(df))).to_dict(orient="records")

            prompt = f"""
You are SmartFresh AI, an operations intelligence assistant for a fresh produce company.

Key KPIs:
- Total production: {kpis["total_production"]}
- Total sales: {kpis["total_sales"]}
- Waste rate: {kpis["waste_rate"]:.2f}%
- Defect rate: {kpis["defect_rate"]:.2f}%
- Delayed deliveries: {kpis["delayed"]}
- Total revenue: €{kpis["revenue"]:.2f}

Dataset sample:
{sample_data}

User question:
{question}

Answer like a professional operations analyst:
- concise bullet points
- clear calculations if needed
- highlight risks with ⚠️
- give practical recommendations
"""

            with st.spinner("SmartFresh AI is analyzing..."):
                answer = generate_ai_response(prompt)
                st.markdown(answer)

            st.session_state.smartfresh_chat.append({
                "role": "assistant",
                "content": answer
            })
