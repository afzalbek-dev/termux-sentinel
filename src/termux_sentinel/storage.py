"""SQLite metrics storage engine for Termux Sentinel."""
import sqlite3
import json
from typing import List, Dict, Any, Optional

class MetricStorage:
    def __init__(self, db_path: str = "sentinel_metrics.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS metric_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp INTEGER NOT NULL,
                    cpu_percent REAL NOT NULL,
                    mem_percent REAL NOT NULL,
                    disk_percent REAL NOT NULL,
                    battery_capacity INTEGER,
                    raw_data TEXT NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS alert_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp INTEGER NOT NULL,
                    metric_name TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    message TEXT NOT NULL
                )
            """)
            conn.commit()

    def record_snapshot(self, snapshot: Dict[str, Any]) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO metric_snapshots (timestamp, cpu_percent, mem_percent, disk_percent, battery_capacity, raw_data)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                snapshot["timestamp"],
                snapshot["cpu"]["load_percent"],
                snapshot["memory"]["percent"],
                snapshot["disk"]["percent"],
                snapshot["battery"]["capacity"],
                json.dumps(snapshot)
            ))
            conn.commit()
            return cursor.lastrowid

    def get_recent_snapshots(self, limit: int = 10) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, timestamp, cpu_percent, mem_percent, disk_percent, battery_capacity, raw_data
                FROM metric_snapshots ORDER BY id DESC LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    def record_alert(self, metric: str, severity: str, message: str) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO alert_events (timestamp, metric_name, severity, message)
                VALUES (strftime('%s', 'now'), ?, ?, ?)
            """, (metric, severity, message))
            conn.commit()
            return cursor.lastrowid

    def get_recent_alerts(self, limit: int = 10) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, timestamp, metric_name, severity, message
                FROM alert_events ORDER BY id DESC LIMIT ?
            """, (limit,))
            return [dict(r) for r in cursor.fetchall()]
