"""Command Line Interface for Termux Sentinel."""
import sys
import argparse
import json
from .collector import SystemCollector
from .storage import MetricStorage
from .alerts import AlertEngine

def main():
    parser = argparse.ArgumentParser(description="Termux Sentinel — ARM64 System Health & Monitoring Tool")
    subparsers = parser.add_subparsers(dest="command", help="Mavjud buyruqlar")

    # snapshot command
    subparsers.add_parser("status", help="Tizimning joriy holati va parametrlarini ko'rsatish")

    # collect command
    subparsers.add_parser("collect", help="Yangi ko'rsatkichlarni o'lchab ma'lumotlar bazasiga yozish")

    # history command
    hist_parser = subparsers.add_parser("history", help="Oxirgi o'lchovlar tarixini ko'rish")
    hist_parser.add_argument("--limit", type=int, default=5, help="Chiqariladigan yozuvlar soni")

    # alerts command
    subparsers.add_parser("alerts", help="Oxirgi favqulodda ogohlantirishlar ro'yxati")

    args = parser.parse_args()
    collector = SystemCollector()
    storage = MetricStorage()
    engine = AlertEngine()

    if args.command == "status" or not args.command:
        data = collector.snapshot()
        print("\n🛡️  TERMUX SENTINEL TIZIM HOLATI")
        print("──────────────────────────────────────────")
        print(f"🖥️  CPU:     {data['cpu']['load_percent']}% yuklama ({data['cpu']['cores']} yadro, 1m: {data['cpu']['load_1m']})")
        print(f"🧠 RAM:     {data['memory']['used_mb']} MB / {data['memory']['total_mb']} MB ({data['memory']['percent']}%)")
        print(f"💾 Disk:    {data['disk']['used_gb']} GB / {data['disk']['total_gb']} GB ({data['disk']['percent']}%)")
        print(f"🔋 Batareya:{data['battery']['capacity']}% [{data['battery']['status']}]")

        alerts = engine.evaluate(data)
        if alerts:
            print("\n⚠️  OGOHLANTIRISHLAR:")
            for a in alerts:
                print(f"  [{a['severity']}] {a['message']}")
        else:
            print("\n✅ Tizim me'yorida ishlamoqda.")
        print()

    elif args.command == "collect":
        data = collector.snapshot()
        row_id = storage.record_snapshot(data)
        alerts = engine.evaluate(data)
        for a in alerts:
            storage.record_alert(a["metric"], a["severity"], a["message"])
        print(f"Snapshot #{row_id} bazaga muvaffaqiyatli saqlandi. Aniqlangan ogohlantirishlar: {len(alerts)}")

    elif args.command == "history":
        rows = storage.get_recent_snapshots(args.limit)
        print(f"\n📊 OXIRGI {len(rows)} TA O'LCHOV:")
        for r in rows:
            print(f"#{r['id']} | CPU: {r['cpu_percent']}% | RAM: {r['mem_percent']}% | Disk: {r['disk_percent']}% | Batareya: {r['battery_capacity']}%")

    elif args.command == "alerts":
        alerts = storage.get_recent_alerts(10)
        print(f"\n🚨 SO'NGGI OGOHLANTIRISHLAR ({len(alerts)} ta):")
        for a in alerts:
            print(f"[{a['severity']}] {a['metric_name']}: {a['message']}")

if __name__ == "__main__":
    main()
