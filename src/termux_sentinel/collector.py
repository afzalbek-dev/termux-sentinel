"""System metrics collector for Termux and Linux ARM64 systems."""
import os
import shutil
import time
from typing import Dict, Any, Optional

class SystemCollector:
    """Collects CPU, Memory, Disk, and Battery metrics safely on Linux/Termux."""

    def __init__(self, sysfs_battery_path: str = "/sys/class/power_supply/battery"):
        self.battery_path = sysfs_battery_path

    def get_memory_info(self) -> Dict[str, float]:
        """Parses /proc/meminfo to retrieve total, available and used memory in MB."""
        meminfo: Dict[str, int] = {}
        if os.path.exists("/proc/meminfo"):
            try:
                with open("/proc/meminfo", "r") as f:
                    for line in f:
                        parts = line.split(":")
                        if len(parts) == 2:
                            key = parts[0].strip()
                            val_str = parts[1].strip().split()[0]
                            meminfo[key] = int(val_str)
            except Exception:
                pass

        total_kb = meminfo.get("MemTotal", 1024 * 1024)
        avail_kb = meminfo.get("MemAvailable", meminfo.get("MemFree", 512 * 1024))
        used_kb = max(0, total_kb - avail_kb)

        total_mb = round(total_kb / 1024.0, 2)
        used_mb = round(used_kb / 1024.0, 2)
        pct = round((used_kb / total_kb) * 100.0, 1) if total_kb > 0 else 0.0

        return {
            "total_mb": total_mb,
            "used_mb": used_mb,
            "percent": pct
        }

    def get_cpu_load(self) -> Dict[str, float]:
        """Retrieves system load average from os.getloadavg() or /proc/loadavg."""
        try:
            l1, l5, l15 = os.getloadavg()
        except (AttributeError, OSError):
            l1, l5, l15 = (0.0, 0.0, 0.0)

        cpu_count = os.cpu_count() or 1
        return {
            "load_1m": round(l1, 2),
            "load_5m": round(l5, 2),
            "load_15m": round(l15, 2),
            "cores": cpu_count,
            "load_percent": round(min(100.0, (l1 / cpu_count) * 100.0), 1)
        }

    def get_disk_info(self, path: str = "/") -> Dict[str, Any]:
        """Calculates total, used, free disk space in GB."""
        try:
            usage = shutil.disk_usage(path)
            total_gb = round(usage.total / (1024**3), 2)
            used_gb = round(usage.used / (1024**3), 2)
            free_gb = round(usage.free / (1024**3), 2)
            pct = round((usage.used / usage.total) * 100.0, 1) if usage.total > 0 else 0.0
            return {
                "total_gb": total_gb,
                "used_gb": used_gb,
                "free_gb": free_gb,
                "percent": pct
            }
        except Exception:
            return {"total_gb": 0.0, "used_gb": 0.0, "free_gb": 0.0, "percent": 0.0}

    def get_battery_info(self) -> Dict[str, Any]:
        """Attempts to read battery capacity and status from Linux sysfs."""
        capacity_file = os.path.join(self.battery_path, "capacity")
        status_file = os.path.join(self.battery_path, "status")

        capacity = None
        status = "Unknown"

        if os.path.exists(capacity_file):
            try:
                with open(capacity_file, "r") as f:
                    capacity = int(f.read().strip())
            except Exception:
                pass

        if os.path.exists(status_file):
            try:
                with open(status_file, "r") as f:
                    status = f.read().strip()
            except Exception:
                pass

        return {
            "capacity": capacity if capacity is not None else 100,
            "status": status,
            "is_charging": status.lower() in ("charging", "full")
        }

    def snapshot(self) -> Dict[str, Any]:
        """Captures a complete system metrics snapshot."""
        return {
            "timestamp": int(time.time()),
            "memory": self.get_memory_info(),
            "cpu": self.get_cpu_load(),
            "disk": self.get_disk_info(),
            "battery": self.get_battery_info()
        }
