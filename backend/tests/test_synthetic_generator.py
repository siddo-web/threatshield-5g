import pandas as pd

from backend.ml.synthetic_data import generate_traffic


def test_synthetic_generator():
    df = generate_traffic(n_samples=100, random_state=42)
    assert list(df.columns) == [
        "duration",
        "protocol",
        "src_bytes",
        "dst_bytes",
        "packets",
        "src_port",
        "dst_port",
        "packet_rate",
        "byte_rate",
        "flow_duration",
        "tcp_flags",
        "ttl",
        "connection_count",
        "failed_connections",
        "payload_size",
        "label",
    ]
    assert set(df["label"].unique()) <= {"Benign", "DDoS", "Port Scan", "Spoofing", "Malware", "Brute Force"}
