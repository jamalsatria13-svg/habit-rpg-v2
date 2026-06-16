"""
core.py — Data models, constants, and persistence layer.
Single source of truth for all game data.
"""

from __future__ import annotations
import json
from datetime import date, datetime
from pathlib import Path
from typing import Any

# ── FILE PATH ─────────────────────────────────────────────────────────────────
DATA_FILE = Path("data.json")

# ── DEFAULT HABITS (seeded on first run) ─────────────────────────────────────
DEFAULT_HABITS = [
    # id, nama, kategori, hp, exp, core
    {"id":"stretching",  "name":"Stretching",             "cat":"Fisik Core",  "hp":5,  "exp":0,  "core":True},
    {"id":"pushup",      "name":"Push Up 4x15",           "cat":"Fisik Core",  "hp":10, "exp":0,  "core":True},
    {"id":"pullup",      "name":"Pull Up 2x5",            "cat":"Fisik Core",  "hp":10, "exp":0,  "core":True},
    {"id":"plank",       "name":"Plank 1 Menit",          "cat":"Fisik Core",  "hp":5,  "exp":0,  "core":True},
    {"id":"tidur",       "name":"Tidur 7 Jam",            "cat":"Fisik Core",  "hp":10, "exp":0,  "core":True},
    {"id":"skincare",    "name":"Skincare Pagi & Malam",  "cat":"Fisik Core",  "hp":5,  "exp":0,  "core":True},
    {"id":"minum",       "name":"Minum 2L Air",           "cat":"Fisik Core",  "hp":5,  "exp":0,  "core":True},
    {"id":"handgrip",    "name":"Hand Grip 100x",         "cat":"Fisik Bonus", "hp":5,  "exp":0,  "core":False},
    {"id":"nafas",       "name":"Latihan Pernapasan",     "cat":"Fisik Bonus", "hp":5,  "exp":0,  "core":False},
    {"id":"tomat",       "name":"Makan Tomat",            "cat":"Fisik Bonus", "hp":3,  "exp":0,  "core":False},
    {"id":"belajar",     "name":"Belajar & Kuliah",       "cat":"Belajar",     "hp":0,  "exp":20, "core":True},
    {"id":"video",       "name":"1 Video Ilmu",           "cat":"Belajar",     "hp":0,  "exp":5,  "core":False},
    {"id":"sholat",      "name":"Sholat 5 Waktu + Wirid", "cat":"Ibadah",      "hp":5,  "exp":10, "core":True},
    {"id":"ngaji",       "name":"Ngaji 2 Halaman",        "cat":"Ibadah",      "hp":0,  "exp":5,  "core":False},
    {"id":"duha",        "name":"Duha / Sholat Malam",    "cat":"Ibadah",      "hp":0,  "exp":10, "core":False},
    {"id":"almulk",      "name":"Dengerin Al-Mulk",       "cat":"Ibadah",      "hp":0,  "exp":3,  "core":False},
]

DEFAULT_MISSIONS = [
    {"id":"lari",   "name":"Lari",         "hp":50, "exp":0,  "kupon":30, "penalty_hp":25, "penalty_exp":0},
    {"id":"gym",    "name":"Gym",          "hp":50, "exp":0,  "kupon":30, "penalty_hp":25, "penalty_exp":0},
    {"id":"puasa",  "name":"Puasa Sunnah", "hp":30, "exp":20, "kupon":40, "penalty_hp":0,  "penalty_exp":0},
    {"id":"detox",  "name":"Detox Tubuh",  "hp":20, "exp":0,  "kupon":20, "penalty_hp":0,  "penalty_exp":0},
    {"id":"tahlil", "name":"Tahlil",       "hp":0,  "exp":20, "kupon":20, "penalty_hp":0,  "penalty_exp":0},
]

COUPONS = [
    {"id":"makan",   "name":"Makan Enak",   "pts":50,  "value":"Rp50.000"},
    {"id":"hiburan", "name":"Hiburan/Game", "pts":100, "value":"Rp100.000"},
    {"id":"beli",    "name":"Beli Sesuatu", "pts":200, "value":"Rp200.000"},
    {"id":"trip",    "name":"Mini Trip",    "pts":400, "value":"Rp400.000"},
]

LEVELS = [
    {"level":1, "name":"Pemula",   "threshold":0,    "avatar":"👶"},
    {"level":2, "name":"Pejuang",  "threshold":500,  "avatar":"⚔️"},
    {"level":3, "name":"Ksatria",  "threshold":1200, "avatar":"🛡️"},
    {"level":4, "name":"Pahlawan", "threshold":2500, "avatar":"🦸"},
    {"level":5, "name":"Legenda",  "threshold":5000, "avatar":"👑"},
]

BUDGET = {
    "Kebutuhan Pokok":  350000,
    "Kost":             600000,
    "Kas Kantor":       100000,
    "Cadangan & Bebas": 400000,
    "Dana Darurat":     200000,
    "UKT Kuliah":       300000,
}

EXPENSE_CATS = [
    "Kebutuhan Pokok","Kost","Kas Kantor",
    "Cadangan & Bebas","Dana Darurat","UKT Kuliah",
    "Tabungan Utama","Lainnya"
]

ACHIEVEMENTS = [
    {"id":"streak3",     "name":"On Fire",          "desc":"Streak 3 hari berturut-turut",     "icon":"🔥"},
    {"id":"streak7",     "name":"Week Warrior",     "desc":"Streak 7 hari berturut-turut",     "icon":"⚡"},
    {"id":"streak30",    "name":"Iron Will",        "desc":"Streak 30 hari berturut-turut",    "icon":"💎"},
    {"id":"sholat7",     "name":"Istiqomah",        "desc":"Sholat lengkap 7 hari berturut",   "icon":"🕌"},
    {"id":"level2",      "name":"Pejuang Sejati",   "desc":"Mencapai Level 2",                 "icon":"⚔️"},
    {"id":"level3",      "name":"Ksatria Muda",     "desc":"Mencapai Level 3",                 "icon":"🛡️"},
    {"id":"level4",      "name":"Sang Pahlawan",    "desc":"Mencapai Level 4",                 "icon":"🦸"},
    {"id":"level5",      "name":"Sang Legenda",     "desc":"Mencapai Level 5",                 "icon":"👑"},
    {"id":"gold1000",    "name":"Hemat Pangkal Kaya","desc":"Kumpulkan 1000 Gold",             "icon":"💰"},
    {"id":"kupon5",      "name":"Reward Hunter",    "desc":"Tukar kupon 5 kali",               "icon":"🎟️"},
    {"id":"habit100",    "name":"Konsisten",        "desc":"Total 100 habit selesai",          "icon":"✅"},
]

# ── DEFAULT STATE ─────────────────────────────────────────────────────────────
def default_state() -> dict[str, Any]:
    return {
        "hp": 50, "exp": 0, "gold": 0, "kupon": 0,
        "shift": "Pagi",
        # habits: {date_str: {habit_id: bool}}
        "habits": {},
        # missions: {week_start: {mission_id: bool}}
        "missions": {},
        "transactions": [],
        "redeem_log": [],
        "streak": 0,
        "best_streak": 0,
        "sholat_streak": 0,
        # week_days: {date_str: "done"|"partial"|"miss"}
        "week_days": {},
        # level_history: [{level, date}]
        "level_history": [],
        # habit_history: {habit_id: total_count}
        "habit_history": {},
        "achievements": [],
        "total_redeems": 0,
        "total_habits_done": 0,
        # custom habits added by user
        "custom_habits": [],
        # custom missions added by user
        "custom_missions": [],
        # monthly targets: {month_str: {target_id: {target, current}}}
        "monthly_targets": {},
        "last_date": str(date.today()),
    }

# ── PERSISTENCE ───────────────────────────────────────────────────────────────
def load() -> dict[str, Any]:
    """Load data from JSON file, merge with defaults for new keys."""
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
            # Merge: ensure new keys from default_state exist in old saves
            base = default_state()
            for k, v in base.items():
                if k not in saved:
                    saved[k] = v
            return saved
        except Exception:
            pass
    return default_state()

def save(data: dict[str, Any]) -> None:
    """Atomically save data to JSON file."""
    try:
        tmp = DATA_FILE.with_suffix(".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        tmp.replace(DATA_FILE)
    except Exception as e:
        raise RuntimeError(f"Gagal menyimpan data: {e}")

# ── GAME LOGIC ────────────────────────────────────────────────────────────────
def get_level(hp: int, exp: int) -> tuple[dict, dict | None, int]:
    """Return (current_level, next_level, total_stat)."""
    total = hp + exp
    cur = LEVELS[0]
    nxt = None
    for i, lv in enumerate(LEVELS):
        if total >= lv["threshold"]:
            cur = lv
            nxt = LEVELS[i + 1] if i + 1 < len(LEVELS) else None
    return cur, nxt, total

def get_all_habits(data: dict) -> list[dict]:
    """Merge default + custom habits."""
    return DEFAULT_HABITS + data.get("custom_habits", [])

def get_all_missions(data: dict) -> list[dict]:
    """Merge default + custom missions."""
    return DEFAULT_MISSIONS + data.get("custom_missions", [])

def get_today_habits(data: dict) -> dict[str, bool]:
    """Get habit completion dict for today."""
    today = str(date.today())
    return data["habits"].get(today, {})

def set_today_habit(data: dict, habit_id: str, value: bool) -> None:
    """Set a single habit for today."""
    today = str(date.today())
    if today not in data["habits"]:
        data["habits"][today] = {}
    data["habits"][today][habit_id] = value

def check_achievements(data: dict) -> list[str]:
    """Check and unlock new achievements. Returns list of newly unlocked."""
    newly_unlocked = []
    unlocked = set(data.get("achievements", []))

    checks = {
        "streak3":   data["streak"] >= 3,
        "streak7":   data["streak"] >= 7,
        "streak30":  data["streak"] >= 30,
        "sholat7":   data.get("sholat_streak", 0) >= 7,
        "level2":    (get_level(data["hp"], data["exp"])[0]["level"]) >= 2,
        "level3":    (get_level(data["hp"], data["exp"])[0]["level"]) >= 3,
        "level4":    (get_level(data["hp"], data["exp"])[0]["level"]) >= 4,
        "level5":    (get_level(data["hp"], data["exp"])[0]["level"]) >= 5,
        "gold1000":  data["gold"] >= 1000,
        "kupon5":    data.get("total_redeems", 0) >= 5,
        "habit100":  data.get("total_habits_done", 0) >= 100,
    }

    for ach_id, condition in checks.items():
        if condition and ach_id not in unlocked:
            data["achievements"].append(ach_id)
            newly_unlocked.append(ach_id)

    return newly_unlocked

def fmt_rp(n: int | float) -> str:
    return "Rp{:,}".format(int(n)).replace(",", ".")
