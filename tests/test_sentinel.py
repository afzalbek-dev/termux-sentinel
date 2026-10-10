"""Unit tests for Termux Sentinel."""
import os
import tempfile
import pytest
from termux_sentinel.collector import SystemCollector
from termux_sentinel.storage import MetricStorage
from termux_sentinel.alerts import AlertEngine

def test_system_collector_metrics():
    collector = SystemCollector()
    data = collector.snapshot()
    
    assert "timestamp" in data
    assert "memory" in data
    assert "cpu" in data
    assert "disk" in data
    assert "battery" in data
    assert data["memory"]["total_mb"] > 0
    assert data["cpu"]["cores"] >= 1
    assert data["disk"]["total_gb"] >= 0

def test_alert_engine_evaluations():
    engine = AlertEngine(cpu_threshold_pct=80.0, mem_threshold_pct=85.0, disk_threshold_pct=90.0, battery_low_pct=20)
    
    # Normal metrics snapshot
    normal_data = {
        "cpu": {"load_percent": 25.0},
        "memory": {"percent": 45.0},
        "disk": {"percent": 50.0},
        "battery": {"capacity": 80, "is_charging": False}
    }
    assert len(engine.evaluate(normal_data)) == 0
    
    # Overloaded snapshot
    critical_data = {
        "cpu": {"load_percent": 95.0},
        "memory": {"percent": 92.0},
        "disk": {"percent": 94.0},
        "battery": {"capacity": 10, "is_charging": False}
    }
    alerts = engine.evaluate(critical_data)
    assert len(alerts) == 4
    metrics = [a["metric"] for a in alerts]
    assert "cpu" in metrics
    assert "memory" in metrics
    assert "disk" in metrics
    assert "battery" in metrics

def test_metric_storage_crud():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tf:
        db_path = tf.name
    
    try:
        storage = MetricStorage(db_path=db_path)
        snapshot = {
            "timestamp": 1700000000,
            "cpu": {"load_percent": 35.5},
            "memory": {"percent": 60.2},
            "disk": {"percent": 45.1},
            "battery": {"capacity": 95}
        }
        row_id = storage.record_snapshot(snapshot)
        assert row_id == 1
        
        recent = storage.get_recent_snapshots(5)
        assert len(recent) == 1
        assert recent[0]["cpu_percent"] == 35.5
        
        alert_id = storage.record_alert("cpu", "WARNING", "High CPU load detected")
        assert alert_id == 1
        alerts = storage.get_recent_alerts(5)
        assert len(alerts) == 1
        assert alerts[0]["metric_name"] == "cpu"
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)
