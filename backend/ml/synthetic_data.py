"""Synthetic traffic generation for the ThreatShield 5G demo mode."""

from __future__ import annotations

import numpy as np
import pandas as pd


def generate_traffic(n_samples: int = 5000, random_state: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(random_state)
    labels = ["Benign", "DDoS", "Port Scan", "Spoofing", "Malware", "Brute Force"]
    weights = np.array([0.55, 0.15, 0.10, 0.08, 0.07, 0.05])
    classes = rng.choice(labels, size=n_samples, p=weights)

    rows = []
    for label in classes:
        if label == "Benign":
            duration = rng.integers(5, 250)
            protocol = rng.choice(["TCP", "UDP", "ICMP"], p=[0.7, 0.2, 0.1])
            src_bytes = rng.normal(1200, 500)
            dst_bytes = rng.normal(980, 400)
            packets = rng.integers(20, 150)
            src_port = rng.integers(1024, 65535)
            dst_port = rng.integers(80, 443)
            packet_rate = rng.normal(12, 4)
            byte_rate = rng.normal(1800, 700)
            flow_duration = rng.integers(50, 500)
            tcp_flags = int(rng.choice([0, 1, 2, 4, 16], p=[0.2, 0.3, 0.2, 0.2, 0.1]))
            ttl = rng.integers(50, 120)
            connection_count = rng.integers(1, 8)
            failed_connections = rng.integers(0, 2)
            payload_size = rng.normal(500, 150)
        elif label == "DDoS":
            duration = rng.integers(1, 25)
            protocol = rng.choice(["TCP", "UDP"], p=[0.5, 0.5])
            src_bytes = rng.normal(25000, 12000)
            dst_bytes = rng.normal(50000, 20000)
            packets = rng.integers(300, 4000)
            src_port = rng.integers(1024, 65535)
            dst_port = 80
            packet_rate = rng.normal(240, 80)
            byte_rate = rng.normal(300000, 100000)
            flow_duration = rng.integers(1, 30)
            tcp_flags = int(rng.choice([0, 2, 4], p=[0.2, 0.5, 0.3]))
            ttl = rng.integers(20, 60)
            connection_count = rng.integers(50, 200)
            failed_connections = rng.integers(10, 80)
            payload_size = rng.normal(200, 100)
        elif label == "Port Scan":
            duration = rng.integers(1, 8)
            protocol = rng.choice(["TCP", "UDP"])
            src_bytes = rng.normal(300, 120)
            dst_bytes = rng.normal(250, 100)
            packets = rng.integers(5, 40)
            src_port = rng.integers(1024, 65535)
            dst_port = rng.integers(1, 65535)
            packet_rate = rng.normal(80, 25)
            byte_rate = rng.normal(5000, 2000)
            flow_duration = rng.integers(1, 10)
            tcp_flags = int(rng.choice([2, 4, 16], p=[0.4, 0.3, 0.3]))
            ttl = rng.integers(30, 80)
            connection_count = rng.integers(10, 60)
            failed_connections = rng.integers(3, 25)
            payload_size = rng.normal(80, 20)
        elif label == "Spoofing":
            duration = rng.integers(2, 70)
            protocol = rng.choice(["TCP", "ICMP"], p=[0.7, 0.3])
            src_bytes = rng.normal(1200, 550)
            dst_bytes = rng.normal(950, 500)
            packets = rng.integers(15, 120)
            src_port = rng.integers(1024, 65535)
            dst_port = rng.integers(80, 443)
            packet_rate = rng.normal(18, 8)
            byte_rate = rng.normal(2800, 1200)
            flow_duration = rng.integers(5, 200)
            tcp_flags = int(rng.choice([0, 1, 2], p=[0.3, 0.5, 0.2]))
            ttl = rng.integers(5, 25)
            connection_count = rng.integers(3, 20)
            failed_connections = rng.integers(0, 10)
            payload_size = rng.normal(300, 120)
        elif label == "Malware":
            duration = rng.integers(3, 90)
            protocol = rng.choice(["TCP", "UDP", "HTTP"], p=[0.5, 0.3, 0.2])
            src_bytes = rng.normal(8000, 2500)
            dst_bytes = rng.normal(5000, 2200)
            packets = rng.integers(40, 240)
            src_port = rng.integers(1024, 65535)
            dst_port = rng.integers(444, 8080)
            packet_rate = rng.normal(35, 15)
            byte_rate = rng.normal(9000, 5000)
            flow_duration = rng.integers(20, 220)
            tcp_flags = int(rng.choice([2, 4, 16], p=[0.4, 0.4, 0.2]))
            ttl = rng.integers(30, 90)
            connection_count = rng.integers(8, 35)
            failed_connections = rng.integers(1, 12)
            payload_size = rng.normal(500, 140)
        else:
            duration = rng.integers(10, 150)
            protocol = rng.choice(["TCP", "UDP"])
            src_bytes = rng.normal(5000, 1500)
            dst_bytes = rng.normal(1800, 800)
            packets = rng.integers(20, 180)
            src_port = rng.integers(1024, 65535)
            dst_port = rng.integers(22, 3389)
            packet_rate = rng.normal(28, 12)
            byte_rate = rng.normal(6000, 2500)
            flow_duration = rng.integers(8, 200)
            tcp_flags = int(rng.choice([1, 2, 4], p=[0.2, 0.5, 0.3]))
            ttl = rng.integers(40, 110)
            connection_count = rng.integers(4, 25)
            failed_connections = rng.integers(2, 18)
            payload_size = rng.normal(260, 90)

        rows.append(
            {
                "duration": float(max(1.0, duration)),
                "protocol": protocol,
                "src_bytes": float(max(0.0, src_bytes)),
                "dst_bytes": float(max(0.0, dst_bytes)),
                "packets": int(max(1, packets)),
                "src_port": int(src_port),
                "dst_port": int(dst_port),
                "packet_rate": float(max(0.1, packet_rate)),
                "byte_rate": float(max(0.1, byte_rate)),
                "flow_duration": float(max(1.0, flow_duration)),
                "tcp_flags": int(tcp_flags),
                "ttl": int(ttl),
                "connection_count": int(connection_count),
                "failed_connections": int(failed_connections),
                "payload_size": float(max(0.0, payload_size)),
                "label": label,
            }
        )

    return pd.DataFrame(rows)
