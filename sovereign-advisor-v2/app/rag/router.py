def classify_intent(message: str) -> str:
    text = message.strip().lower()

    advisor_terms = {
        "vault",
        "vault enterprise",
        "hcp vault",
        "hcp vault dedicated",
        "hashicorp",
        "sovereignty",
        "residency",
        "compliance",
        "fips",
        "hsm",
        "air gap",
        "air-gap",
        "seal wrap",
        "boundary",
        "deployment model",
        "deployment tradeoffs",
        "tradeoff",
        "tradeoffs",
        "managed",
        "self-managed",
        "self managed",
        "customer-controlled hsm",
        "control boundary",
        "data sovereignty",
        "compare",
        "comparison",
        "difference",
        "differences",
        "vs",
        "versus",
        "which one",
        "recommend",
        "should i choose",
    }

    if any(term in text for term in advisor_terms):
        return "advisor"

    return "chat"


def route_query(message: str) -> list[str]:
    intent = classify_intent(message)
    if intent != "advisor":
        return []

    return [
        "vault_enterprise_docs",
        "hcp_vault_dedicated_docs",
        "sovereignty_guidelines",
    ]
