from backend.app.services.mitigation_service import get_mitigation_action


def test_mitigation_mapping():
    assert get_mitigation_action("DDoS") == "rate-limit"
    assert get_mitigation_action("Port Scan") == "alert"
    assert get_mitigation_action("Spoofing") == "block"
    assert get_mitigation_action("Benign") == "allow"
