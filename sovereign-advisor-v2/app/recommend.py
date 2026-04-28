from typing import Dict


def recommend(profile: Dict) -> Dict:
    geo = profile.get("geo", "Unknown")
    compliance = profile.get("compliance", "Medium")
    ownership = profile.get("ownership", "Managed Service")
    data_residency = profile.get("data_residency", "Flexible")
    growth = profile.get("growth", "Unknown")
    workload = profile.get("workload", "General")

    if compliance in ["High", "Very high"] and ownership == "Customer Managed" and data_residency == "Strict":
        recommendation = "IBM HashiCorp Enterprise (Self-Managed)"
        confidence = 0.9
    elif ownership == "Managed Service" and geo == "Europe":
        recommendation = "HCP Europe"
        confidence = 0.86
    elif ownership == "Managed Service":
        recommendation = "HCP"
        confidence = 0.82
    else:
        recommendation = "Hybrid"
        confidence = 0.78

    return {
        "recommendation": recommendation,
        "confidence": confidence,
        "reason": (
            f"Based on geography={geo}, workload={workload}, compliance={compliance}, "
            f"ownership={ownership}, growth={growth}, and data_residency={data_residency}, "
            f"the recommended deployment model is {recommendation}."
        ),
        "profile": profile,
    }
