import math
from datetime import datetime, timedelta


def calculate_from_colli(colli, buste_per_collo, grams_per_busta, kg_per_case, colli_per_pallet, waste_percent=0):
    total_buste = colli * buste_per_collo
    net_kg = (total_buste * grams_per_busta) / 1000
    production_kg = net_kg * (1 + waste_percent / 100)

    cases_needed = math.ceil(production_kg / kg_per_case)
    pallets_needed = math.ceil(colli / colli_per_pallet)

    return {
        "mode": "From colli",
        "colli": colli,
        "total_buste": total_buste,
        "net_kg": round(net_kg, 2),
        "production_kg": round(production_kg, 2),
        "cases_needed": cases_needed,
        "pallets_needed": pallets_needed
    }


def calculate_from_cases(incoming_cases, kg_per_case, buste_per_collo, grams_per_busta, colli_per_pallet, waste_percent=0):
    available_kg = incoming_cases * kg_per_case
    usable_kg = available_kg / (1 + waste_percent / 100)

    total_buste = math.floor((usable_kg * 1000) / grams_per_busta)
    colli_possible = math.floor(total_buste / buste_per_collo)
    pallets_needed = math.ceil(colli_possible / colli_per_pallet)

    return {
        "mode": "From incoming cases",
        "incoming_cases": incoming_cases,
        "available_kg": round(available_kg, 2),
        "usable_kg_after_waste": round(usable_kg, 2),
        "total_buste_possible": total_buste,
        "colli_possible": colli_possible,
        "pallets_needed": pallets_needed
    }


def calculate_from_kg(available_kg, buste_per_collo, grams_per_busta, kg_per_case, colli_per_pallet, waste_percent=0):
    usable_kg = available_kg / (1 + waste_percent / 100)

    total_buste = math.floor((usable_kg * 1000) / grams_per_busta)
    colli_possible = math.floor(total_buste / buste_per_collo)
    cases_equivalent = math.ceil(available_kg / kg_per_case)
    pallets_needed = math.ceil(colli_possible / colli_per_pallet)

    return {
        "mode": "From available kg",
        "available_kg": round(available_kg, 2),
        "usable_kg_after_waste": round(usable_kg, 2),
        "total_buste_possible": total_buste,
        "colli_possible": colli_possible,
        "cases_equivalent": cases_equivalent,
        "pallets_needed": pallets_needed
    }


def estimate_machine_schedule(total_buste, machine_speed_buste_per_hour, setup_minutes, departure_datetime):
    production_minutes = math.ceil((total_buste / machine_speed_buste_per_hour) * 60)
    total_minutes = production_minutes + setup_minutes

    departure_datetime = datetime.fromisoformat(departure_datetime)
    recommended_start = departure_datetime - timedelta(minutes=total_minutes)

    return {
        "total_buste": total_buste,
        "production_minutes": production_minutes,
        "setup_minutes": setup_minutes,
        "total_required_minutes": total_minutes,
        "recommended_start_time": recommended_start.strftime("%Y-%m-%d %H:%M"),
        "departure_time": departure_datetime.strftime("%Y-%m-%d %H:%M")
    }
