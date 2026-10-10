"""Threshold-based alerting engine for Termux Sentinel."""
from typing import Dict, Any, List

class AlertEngine:
    def __init__(self,
                 cpu_threshold_pct: float = 85.0,
                 mem_threshold_pct: float = 90.0,
                 disk_threshold_pct: float = 90.0,
                 battery_low_pct: int = 15):
        self.cpu_threshold = cpu_threshold_pct
        self.mem_threshold = mem_threshold_pct
        self.disk_threshold = disk_threshold_pct
        self.battery_low = battery_low_pct

    def evaluate(self, snapshot: Dict[str, Any]) -> List[Dict[str, str]]:
        alerts = []

        # CPU check
        cpu_pct = snapshot.get("cpu", {}).get("load_percent", 0.0)
        if cpu_pct > self.cpu_threshold:
            alerts.append({
                "metric": "cpu",
                "severity": "WARNING",
                "message": f"CPU load yuqori: {cpu_pct}% (Chegara: {self.cpu_threshold}%)"
            })

        # Memory check
        mem_pct = snapshot.get("memory", {}).get("percent", 0.0)
        if mem_pct > self.mem_threshold:
            alerts.append({
                "metric": "memory",
                "severity": "CRITICAL",
                "message": f"Operativ xotira (RAM) to'lmoqda: {mem_pct}% (Chegara: {self.mem_threshold}%)"
            })

        # Disk check
        disk_pct = snapshot.get("disk", {}).get("percent", 0.0)
        if disk_pct > self.disk_threshold:
            alerts.append({
                "metric": "disk",
                "severity": "CRITICAL",
                "message": f"Disk xotirasi to'lmoqda: {disk_pct}% (Chegara: {self.disk_threshold}%)"
            })

        # Battery check (only if not charging)
        battery = snapshot.get("battery", {})
        capacity = battery.get("capacity")
        is_charging = battery.get("is_charging", False)
        if capacity is not None and capacity <= self.battery_low and not is_charging:
            alerts.append({
                "metric": "battery",
                "severity": "WARNING",
                "message": f"Batareya quvvati past: {capacity}% (Quvvatlashga ulang!)"
            })

        return alerts
