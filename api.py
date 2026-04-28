from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="SmartFresh AI Backend API")


class RiskInput(BaseModel):
    product_name: str
    supplier: str
    quantity_produced: float
    quantity_sold: float
    stock_remaining: float
    waste_quantity: float
    defect_count: int
    temperature: float
    delivery_status: str
    delivery_delay_days: int


@app.get("/")
def home():
    return {"message": "SmartFresh AI Backend API is running"}


@app.post("/risk-score")
def risk_score(data: RiskInput):
    score = 0
    reasons = []

    waste_rate = (data.waste_quantity / data.quantity_produced) * 100 if data.quantity_produced else 0
    defect_rate = (data.defect_count / data.quantity_produced) * 100 if data.quantity_produced else 0

    if waste_rate > 8:
        score += 25
        reasons.append("High waste rate detected")

    if defect_rate > 1.5:
        score += 20
        reasons.append("High defect rate detected")

    if data.temperature > 6:
        score += 20
        reasons.append("Temperature above recommended cold-chain level")

    if data.delivery_status.lower() == "delayed":
        score += 20
        reasons.append("Delivery delay detected")

    if data.delivery_delay_days > 1:
        score += 10
        reasons.append("Delivery delay is above acceptable level")

    if data.stock_remaining > data.quantity_sold:
        score += 15
        reasons.append("High remaining stock compared to sales")

    score = min(score, 100)

    if score >= 70:
        category = "High"
    elif score >= 40:
        category = "Medium"
    else:
        category = "Low"

    return {
        "product_name": data.product_name,
        "supplier": data.supplier,
        "risk_score": score,
        "risk_category": category,
        "risk_reasons": reasons if reasons else ["Low operational risk"]
    }
