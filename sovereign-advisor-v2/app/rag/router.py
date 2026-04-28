def route_query(message: str) -> list[str]:
    text = message.strip().lower()

    greeting_terms = {
        "hi",
        "hello",
        "hey",
        "yo",
        "hii",
        "hello there",
        "good morning",
        "good afternoon",
        "good evening",
        "how are you",
        "how are you?",
        "how are you doing",
        "thanks",
        "thank you",
        "bye",
        "goodbye",
        "what can you do",
        "help",
        "who are you",
    }

    advisor_terms = {
        "compare",
        "recommend",
        "recommendation",
        "choose",
        "should i",
        "which one",
        "sovereignty",
        "residency",
        "compliance",
        "fips",
        "hsm",
        "air gap",
        "air-gap",
        "seal wrap",
        "vault enterprise",
        "hcp vault dedicated",
        "hard air-gap",
        "customer-controlled hsm",
        "deployment model",
        "data sovereignty",
    }

    if text in greeting_terms:
        return []

    if any(term in text for term in advisor_terms):
        return [
            "vault_enterprise_docs",
            "hcp_vault_dedicated_docs",
            "sovereignty_guidelines",
        ]

    return []
