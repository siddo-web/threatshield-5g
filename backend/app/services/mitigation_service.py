MITIGATION_RULES = {
    "DDoS": "rate-limit",
    "Port Scan": "alert",
    "Scan": "alert",
    "Spoofing": "block",
    "Malware": "block",
    "Brute Force": "alert",
    "Zero-day": "quarantine",
    "Benign": "allow",
}


def get_mitigation_action(attack_type: str) -> str:
    normalized = str(attack_type or "").strip()
    return MITIGATION_RULES.get(normalized, "allow")
