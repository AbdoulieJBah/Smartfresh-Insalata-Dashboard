def planner_agent(alert):
    risk_type = alert.get("risk_type", "")
    priority = alert.get("priority_score", 0)

    if priority >= 80:
        return "Immediate escalation and operational intervention required."

    if risk_type == "High Waste":
        return "Plan supplier quality review and production adjustment."

    if risk_type == "Cold Chain Risk":
        return "Plan cold-chain inspection and possible shipment hold."

    if risk_type == "Delivery Delay":
        return "Plan logistics dispatch review and client notification."

    if risk_type == "Quality Defect":
        return "Plan quality inspection and defect root-cause analysis."

    return "Continue monitoring and review during next operations check."


def executor_agent(alert):
    risk_type = alert.get("risk_type", "")
    priority = alert.get("priority_score", 0)

    decision = {
        "execute": False,
        "execution_action": "Monitor",
        "execution_status": "Pending"
    }

    if priority >= 80:
        decision["execute"] = True
        decision["execution_action"] = "Escalate to management immediately"
        decision["execution_status"] = "Executed"

    elif risk_type == "Cold Chain Risk":
        decision["execute"] = True
        decision["execution_action"] = "Trigger cold-chain inspection"
        decision["execution_status"] = "Executed"

    elif risk_type == "Quality Defect":
        decision["execute"] = True
        decision["execution_action"] = "Trigger quality inspection"
        decision["execution_status"] = "Executed"

    elif risk_type == "Delivery Delay":
        decision["execute"] = True
        decision["execution_action"] = "Notify logistics team"
        decision["execution_status"] = "Executed"

    return decision


def multi_agent_decision(alert):
    plan = planner_agent(alert)
    execution = executor_agent(alert)

    return {
        "planner_recommendation": plan,
        "execute": execution["execute"],
        "execution_action": execution["execution_action"],
        "execution_status": execution["execution_status"]
    }
