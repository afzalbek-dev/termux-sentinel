# 🛡️ Termux Sentinel — ARM64 System Health & Monitoring Tool

Termux (Android) va Debian ARM64 muhitlari uchun maxsus ishlab chiqilgan, yengil va avtonom tizim ko'rsatkichlarini kuzatish (monitoring) utilitasi.

---

## 🌟 Imkoniyatlari

- **CPU yuklamasi:** 1m, 5m, 15m load average va protsessor yadrolari yuklama foizi.
- **Operativ xotira (RAM):** `/proc/meminfo` orqali aniq xotira hisobi (band, bo'sh, jami).
- **Disk hajmi:** Partition bo'yicha bo'sh joy va foiz ko'rsatkichlari.
- **Batareya holati:** Android/Linux sysfs drayveri orqali quvvat foizi va zaryadlash holati.
- **SQLite Arxivlash:** Barcha o'lchovlar vaqt tamg'asi (timestamp) bilan lokal SQLite bazasiga saqlanadi.
- **Moslashuvchan Ogohlantirishlar (Alerts):** CPU > 85%, RAM > 90%, Disk > 90%, Batareya < 15% holatlarida avtomatik ogohlantirish qaydnomasi.

---

## 🚀 O'rnatish va Ishga Tushirish

### 1. Talablar
- Python 3.9+ (Python 3.13 tavsiya etiladi)
- Linux / Android Termux ARM64

### 2. O'rnatish
```bash
git clone https://github.com/afzalbek-dev/termux-sentinel.git
cd termux-sentinel
pip install -e .
```

### 3. Foydalanish
```bash
# Tizim holatini ko'rish
python3 -m termux_sentinel.cli status

# Joriy holatni bazaga yozish (cron yoki daemon uchun)
python3 -m termux_sentinel.cli collect

# Oxirgi o'lchovlar tarixini chiqarish
python3 -m termux_sentinel.cli history --limit 10

# Chegaradan oshgan ogohlantirishlarni ko'rish
python3 -m termux_sentinel.cli alerts
```

---

## 🧪 Testlarni Ishga Tushirish

```bash
pytest tests/ -v
```

---

## 📄 Litsenziya

MIT License. Muallif: [Afzalbek](https://github.com/afzalbek-dev).
