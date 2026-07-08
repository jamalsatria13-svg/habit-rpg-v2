"""
core.py - data, persistence, and Habit RPG game rules.
"""

from __future__ import annotations

import json
import os
from copy import deepcopy
from datetime import date, datetime, timedelta, timezone
from typing import Any

import streamlit as st
from supabase import create_client, Client

try:
    from zoneinfo import ZoneInfo
except Exception:  # pragma: no cover - old Python fallback
    ZoneInfo = None


WIB = ZoneInfo("Asia/Jakarta") if ZoneInfo else timezone(timedelta(hours=7))

# --- Supabase persistence config ---
SUPABASE_TABLE = "habit_state"
SUPABASE_ROW_ID = 1  # single-user: always the same fixed row


def _get_supabase_client() -> Client:
    url = st.secrets.get("SUPABASE_URL") or os.environ.get("SUPABASE_URL")
    key = st.secrets.get("SUPABASE_KEY") or os.environ.get("SUPABASE_KEY")
    if not url or not key:
        raise RuntimeError(
            "SUPABASE_URL / SUPABASE_KEY belum diset. "
            "Tambahkan di .streamlit/secrets.toml atau environment variable."
        )
    return create_client(url, key)


def now_wib() -> datetime:
    return datetime.now(WIB)


def today_wib() -> date:
    return now_wib().date()


def date_key(d: date | None = None) -> str:
    return (d or today_wib()).isoformat()


def parse_date(value: str | None, fallback: date | None = None) -> date:
    try:
        return date.fromisoformat(str(value))
    except Exception:
        return fallback or today_wib()


def get_week_key(d: date | None = None) -> str:
    day = d or today_wib()
    return (day - timedelta(days=day.weekday())).isoformat()


DEFAULT_HABITS: list[dict[str, Any]] = [
    {"id": "subuh", "name": "Subuh", "cat": "Faith", "hp": 3, "exp": 5, "hp_pen": 3, "exp_pen": 5, "unlock_level": 1},
    {"id": "dzuhur", "name": "Dzuhur", "cat": "Faith", "hp": 3, "exp": 5, "hp_pen": 3, "exp_pen": 5, "unlock_level": 1},
    {"id": "asyar", "name": "Asyar", "cat": "Faith", "hp": 3, "exp": 5, "hp_pen": 3, "exp_pen": 5, "unlock_level": 1},
    {"id": "magrib", "name": "Magrib", "cat": "Faith", "hp": 3, "exp": 5, "hp_pen": 3, "exp_pen": 5, "unlock_level": 1},
    {"id": "isya", "name": "Isya", "cat": "Faith", "hp": 3, "exp": 5, "hp_pen": 3, "exp_pen": 5, "unlock_level": 1},
    {"id": "dzikir", "name": "Dzikir", "cat": "Faith", "hp": 3, "exp": 5, "hp_pen": 3, "exp_pen": 5, "unlock_level": 2},
    {"id": "ngaji", "name": "Ngaji", "cat": "Faith", "hp": 3, "exp": 5, "hp_pen": 3, "exp_pen": 5, "unlock_level": 3},
    {"id": "duha", "name": "Duha", "cat": "Faith", "hp": 3, "exp": 5, "hp_pen": 3, "exp_pen": 5, "unlock_level": 4},
    {"id": "jaga_sikap", "name": "Jaga Sikap", "cat": "Faith", "hp": 3, "exp": 3, "hp_pen": 2, "exp_pen": 2, "unlock_level": 5},

    {"id": "tidur", "name": "Tidur 7 Jam", "cat": "Fisik Harian", "hp": 5, "exp": 0, "hp_pen": 3, "exp_pen": 0, "unlock_level": 1},
    {"id": "stretching", "name": "Stretching", "cat": "Fisik Harian", "hp": 5, "exp": 0, "hp_pen": 3, "exp_pen": 0, "unlock_level": 1},
    {"id": "pushup_akhir", "name": "Push Up Akhir", "cat": "Fisik Harian", "hp": 10, "exp": 0, "hp_pen": 3, "exp_pen": 0, "unlock_level": 1},
    {"id": "skincare_akhir", "name": "Skincare Akhir", "cat": "Fisik Harian", "hp": 5, "exp": 0, "hp_pen": 3, "exp_pen": 0, "unlock_level": 1},
    {"id": "minum", "name": "Minum 2 Liter", "cat": "Fisik Harian", "hp": 5, "exp": 0, "hp_pen": 3, "exp_pen": 0, "unlock_level": 1},
    {"id": "pullup_akhir", "name": "Pull Up Akhir", "cat": "Fisik Harian", "hp": 10, "exp": 0, "hp_pen": 3, "exp_pen": 0, "unlock_level": 2},
    {"id": "rokok", "name": "Merokok 3 Batang", "name_by_level": {4: "Merokok 2 Batang"}, "cat": "Fisik Harian", "hp": 10, "exp": 0, "hp_pen": 3, "exp_pen": 0, "unlock_level": 3},
    {"id": "plank", "name": "Plank", "cat": "Fisik Harian", "hp": 10, "exp": 0, "hp_pen": 3, "exp_pen": 0, "unlock_level": 3},
    {"id": "makan", "name": "Makan Bergizi", "cat": "Fisik Harian", "hp": 5, "exp": 0, "hp_pen": 3, "exp_pen": 0, "unlock_level": 3},
    {"id": "pushup_awal", "name": "Push Up Awal", "cat": "Fisik Harian", "hp": 10, "exp": 0, "hp_pen": 3, "exp_pen": 0, "unlock_level": 4},
    {"id": "pullup_awal", "name": "Pull Up Awal", "cat": "Fisik Harian", "hp": 10, "exp": 0, "hp_pen": 3, "exp_pen": 0, "unlock_level": 4},
    {"id": "skincare_awal", "name": "Skincare Awal", "cat": "Fisik Harian", "hp": 5, "exp": 0, "hp_pen": 3, "exp_pen": 0, "unlock_level": 4},

    {"id": "kuliah", "name": "Kuliah 1 Jam", "cat": "Skill & Knowledge", "hp": 0, "exp": 10, "hp_pen": 0, "exp_pen": 3, "unlock_level": 1},
    {"id": "video", "name": "1 Video Ilmu", "cat": "Skill & Knowledge", "hp": 0, "exp": 10, "hp_pen": 0, "exp_pen": 3, "unlock_level": 1},
    {"id": "projek", "name": "Projek 1 Jam", "cat": "Skill & Knowledge", "hp": 0, "exp": 10, "hp_pen": 0, "exp_pen": 3, "unlock_level": 3},

    {"id": "input_data", "name": "Input Data", "cat": "Evaluasi", "hp": 0, "exp": 5, "hp_pen": 0, "exp_pen": 1, "unlock_level": 1},
    {"id": "evaluasi", "name": "Evaluasi", "cat": "Evaluasi", "hp": 0, "exp": 5, "hp_pen": 0, "exp_pen": 1, "unlock_level": 1},
    {"id": "metime", "name": "Me Time", "cat": "Evaluasi", "hp": 0, "exp": 5, "hp_pen": 0, "exp_pen": 1, "unlock_level": 2},
]

HABIT_CATEGORY_ORDER = ["Faith", "Fisik Harian", "Skill & Knowledge", "Evaluasi", "Custom"]

DEFAULT_MISSIONS: list[dict[str, Any]] = [
    {"id": "tahlil", "name": "Tahlil", "hp": 50, "exp": 0, "kupon": 20},
    {"id": "puasa", "name": "Puasa Sunah", "hp": 50, "exp": 0, "kupon": 20},
    {"id": "lari", "name": "Lari 3 km", "hp": 50, "exp": 0, "kupon": 20},
    {"id": "gym", "name": "Gym / Berat", "hp": 50, "exp": 0, "kupon": 20},
    {"id": "yoga", "name": "Yoga", "hp": 50, "exp": 0, "kupon": 20},
    {"id": "detox", "name": "Detox Tubuh", "hp": 50, "exp": 0, "kupon": 20},
    {"id": "bodycare", "name": "Bodycare", "hp": 50, "exp": 0, "kupon": 20},
]

DEFAULT_OBLIGATIONS: list[dict[str, Any]] = [
    {"id": "ob_5r", "name": "5R Kamar", "pen_hp": 30, "pen_kupon": 20},
    {"id": "ob_nyuci", "name": "Nyuci Baju", "pen_hp": 30, "pen_kupon": 20},
    {"id": "ob_motor", "name": "Maintenance Motor", "pen_hp": 30, "pen_kupon": 20},
    {"id": "ob_input", "name": "Input Mingguan", "pen_hp": 30, "pen_kupon": 20},
    {"id": "ob_efisik", "name": "Evaluasi Fisik", "pen_hp": 30, "pen_kupon": 20},
    {"id": "ob_elajar", "name": "Evaluasi Belajar", "pen_hp": 30, "pen_kupon": 20},
    {"id": "ob_ekeuangan", "name": "Evaluasi Keuangan", "pen_hp": 30, "pen_kupon": 20},
    {"id": "ob_eprojek", "name": "Evaluasi Projek", "pen_hp": 30, "pen_kupon": 20},
]

COUPONS: list[dict[str, Any]] = [
    {"id": "makan", "name": "Makan Enak", "cost": 50, "value": "Rp50.000"},
    {"id": "hiburan", "name": "Hiburan/Game", "cost": 100, "value": "Rp100.000"},
    {"id": "beli", "name": "Beli Sesuatu", "cost": 200, "value": "Rp200.000"},
    {"id": "trip", "name": "Mini Trip", "cost": 400, "value": "Rp400.000"},
]

LEVELS: list[dict[str, Any]] = [
    {"level": 1, "name": "PECUNDANG", "threshold": 0, "avatar": "Lv1"},
    {"level": 2, "name": "POLOS", "threshold": 500, "avatar": "Lv2"},
    {"level": 3, "name": "PEJUANG", "threshold": 1200, "avatar": "Lv3"},
    {"level": 4, "name": "PENDEKAR", "threshold": 2500, "avatar": "Lv4"},
    {"level": 5, "name": "JAMAL", "threshold": 5000, "avatar": "Lv5"},
]

ACHIEVEMENTS: list[dict[str, str]] = [
    {"id": "streak3", "name": "On Fire", "desc": "Streak 3 hari", "icon": "*"},
    {"id": "streak7", "name": "Week Warrior", "desc": "Streak 7 hari", "icon": "*"},
    {"id": "streak30", "name": "Iron Will", "desc": "Streak 30 hari", "icon": "*"},
    {"id": "faith7", "name": "Istiqomah", "desc": "Sholat 5 waktu 7 hari", "icon": "*"},
    {"id": "level2", "name": "Pejuang Sejati", "desc": "Mencapai Level 2", "icon": "*"},
    {"id": "level3", "name": "Ksatria Muda", "desc": "Mencapai Level 3", "icon": "*"},
    {"id": "level4", "name": "Sang Pahlawan", "desc": "Mencapai Level 4", "icon": "*"},
    {"id": "level5", "name": "Sang Legenda", "desc": "Mencapai Level 5", "icon": "*"},
    {"id": "kupon5", "name": "Reward Hunter", "desc": "Tukar reward 5 kali", "icon": "*"},
    {"id": "habit100", "name": "Konsisten", "desc": "Total 100 habit selesai", "icon": "*"},
]


def default_state() -> dict[str, Any]:
    today = date_key()
    return {
        "hp": 50,
        "exp": 0,
        "kupon": 0,
        "shift": "Pagi",
        "habits": {},
        "missions": {},
        "obligations": {},
        "redeem_log": [],
        "streak": 0,
        "best_streak": 0,
        "faith_streak": 0,
        "week_days": {},
        "level_history": [],
        "habit_history": {},
        "achievements": [],
        "total_redeems": 0,
        "total_habits_done": 0,
        "custom_habits": [],
        "custom_missions": [],
        "monthly_targets": {},
        "last_date": today,
        "last_week": get_week_key(),
        # Old fields retained in data for backward compatibility, hidden from UI.
        "gold": 0,
        "transactions": [],
    }


def migrate_state(data: dict[str, Any]) -> dict[str, Any]:
    base = default_state()
    for key, value in base.items():
        data.setdefault(key, value)
    if "sholat_streak" in data and "faith_streak" not in data:
        data["faith_streak"] = data.get("sholat_streak", 0)
    data["habits"] = data.get("habits") or {}
    data["missions"] = data.get("missions") or {}
    data["obligations"] = data.get("obligations") or {}
    data["last_date"] = parse_date(data.get("last_date"), today_wib()).isoformat()
    data["last_week"] = get_week_key(parse_date(data.get("last_week"), today_wib()))
    return data


def load() -> dict[str, Any]:
    """Load state from Supabase. Falls back to a fresh default_state()
    in-memory if Supabase is unreachable, so the app doesn't hard-crash —
    but note that in that fallback case nothing will persist until
    connectivity is restored."""
    try:
        client = _get_supabase_client()
        resp = (
            client.table(SUPABASE_TABLE)
            .select("data")
            .eq("id", SUPABASE_ROW_ID)
            .execute()
        )
        if resp.data:
            return migrate_state(resp.data[0]["data"])
        # No row yet: seed it.
        state = default_state()
        client.table(SUPABASE_TABLE).insert(
            {"id": SUPABASE_ROW_ID, "data": state}
        ).execute()
        return state
    except Exception as e:
        st.error(f"⚠️ Gagal terhubung ke Supabase, memakai data sementara: {e}")
        return default_state()


def save(data: dict[str, Any]) -> None:
    try:
        client = _get_supabase_client()
        client.table(SUPABASE_TABLE).upsert(
            {"id": SUPABASE_ROW_ID, "data": data}
        ).execute()
    except Exception as e:
        raise RuntimeError(f"Gagal menyimpan data ke Supabase: {e}")


def import_data(json_str: str) -> dict[str, Any]:
    imported = json.loads(json_str)
    return migrate_state(imported)


def get_level(hp: int, exp: int) -> tuple[dict[str, Any], dict[str, Any] | None, int]:
    total = hp + exp
    cur = LEVELS[0]
    nxt = None
    for i, lv in enumerate(LEVELS):
        if total >= lv["threshold"]:
            cur = lv
            nxt = LEVELS[i + 1] if i + 1 < len(LEVELS) else None
    return cur, nxt, total


def resolve_habit_for_level(habit: dict[str, Any], level: int) -> dict[str, Any]:
    item = deepcopy(habit)
    for min_level, name in sorted(item.get("name_by_level", {}).items()):
        if level >= int(min_level):
            item["name"] = name
    return item


def get_all_habits(data: dict[str, Any]) -> list[dict[str, Any]]:
    return [resolve_habit_for_level(h, get_level(data["hp"], data["exp"])[0]["level"]) for h in DEFAULT_HABITS] + data.get("custom_habits", [])


def get_unlocked_habits(data: dict[str, Any]) -> list[dict[str, Any]]:
    level = get_level(data["hp"], data["exp"])[0]["level"]
    habits = [
        resolve_habit_for_level(h, level)
        for h in DEFAULT_HABITS
        if int(h.get("unlock_level", 1)) <= level
    ]
    for h in data.get("custom_habits", []):
        if int(h.get("unlock_level", 1)) <= level:
            habits.append(h)
    return habits


def get_all_missions(data: dict[str, Any]) -> list[dict[str, Any]]:
    return DEFAULT_MISSIONS + data.get("custom_missions", [])


def get_today_habits(data: dict[str, Any]) -> dict[str, bool]:
    return data["habits"].get(date_key(), {})


def set_today_habit(data: dict[str, Any], habit_id: str, value: bool) -> None:
    data["habits"].setdefault(date_key(), {})[habit_id] = value


def process_daily_reset(data: dict[str, Any], day: date | None = None) -> dict[str, Any]:
    day = day or today_wib()
    day_key = date_key(day)
    day_habits = data["habits"].get(day_key, {})
    active_habits = get_unlocked_habits(data)
    summary = {"date": day_key, "hp_delta": 0, "exp_delta": 0, "kupon_delta": 0, "streak": 0, "messages": []}
    hp_delta = 0
    exp_delta = 0

    for habit in active_habits:
        done = bool(day_habits.get(habit["id"], False))
        if done:
            hp_delta += int(habit.get("hp", 0))
            exp_delta += int(habit.get("exp", 0))
            data["habit_history"][habit["id"]] = data["habit_history"].get(habit["id"], 0) + 1
            data["total_habits_done"] = data.get("total_habits_done", 0) + 1
        else:
            hp_delta -= int(habit.get("hp_pen", 0))
            exp_delta -= int(habit.get("exp_pen", 0))

    faith_core_ids = ["subuh", "dzuhur", "asyar", "magrib", "isya"]
    if all(day_habits.get(fid, False) for fid in faith_core_ids):
        data["faith_streak"] = data.get("faith_streak", 0) + 1
        if data["faith_streak"] == 7:
            data["kupon"] += 50
            summary["kupon_delta"] += 50
            summary["messages"].append("Faith streak 7 hari: +50 kupon")
    else:
        data["faith_streak"] = 0

    non_faith = [h for h in active_habits if h.get("cat") != "Faith"]
    done_count = sum(1 for h in non_faith if day_habits.get(h["id"], False))
    if non_faith and done_count == len(non_faith):
        data["streak"] = data.get("streak", 0) + 1
        data["best_streak"] = max(data.get("best_streak", 0), data["streak"])
        data["week_days"][day_key] = "done"
        streak_rewards = {3: 30, 7: 75, 30: 300}
        if data["streak"] in streak_rewards:
            bonus = streak_rewards[data["streak"]]
            data["kupon"] += bonus
            summary["kupon_delta"] += bonus
            summary["messages"].append(f"Streak {data['streak']} hari: +{bonus} kupon")
    elif non_faith and done_count >= max(1, len(non_faith) // 2):
        data["week_days"][day_key] = "partial"
        data["streak"] = 0
    else:
        data["week_days"][day_key] = "miss"
        data["streak"] = 0

    data["hp"] = max(0, data.get("hp", 0) + hp_delta)
    data["exp"] = max(0, data.get("exp", 0) + exp_delta)

    summary["hp_delta"] = hp_delta
    summary["exp_delta"] = exp_delta
    summary["streak"] = data["streak"]
    return summary


def process_weekly_reset(data: dict[str, Any], week_key: str | None = None) -> dict[str, Any]:
    week_key = week_key or get_week_key()
    obligations = data.get("obligations", {}).get(week_key, {})
    summary = {"week": week_key, "hp_delta": 0, "kupon_delta": 0, "messages": []}
    hp_pen = 0
    kupon_pen = 0
    for ob in DEFAULT_OBLIGATIONS:
        if not obligations.get(ob["id"], False):
            hp_pen += int(ob["pen_hp"])
            kupon_pen += int(ob["pen_kupon"])
            summary["messages"].append(f"{ob['name']} tidak selesai: -{ob['pen_hp']} HP -{ob['pen_kupon']} kupon")

    data["hp"] = max(0, data.get("hp", 0) - hp_pen)
    data["kupon"] = max(0, data.get("kupon", 0) - kupon_pen)
    data.setdefault("obligations", {})[week_key] = {}
    data.setdefault("missions", {})[week_key] = {}
    summary["hp_delta"] = -hp_pen
    summary["kupon_delta"] = -kupon_pen
    return summary


def run_due_resets(data: dict[str, Any]) -> list[dict[str, Any]]:
    summaries: list[dict[str, Any]] = []
    today = today_wib()

    last_day = parse_date(data.get("last_date"), today)
    while last_day < today:
        summaries.append({"type": "daily", **process_daily_reset(data, last_day)})
        last_day += timedelta(days=1)
    data["last_date"] = today.isoformat()

    current_week = get_week_key(today)
    last_week = get_week_key(parse_date(data.get("last_week"), today))
    week_day = parse_date(last_week, today)
    while week_day < parse_date(current_week, today):
        summaries.append({"type": "weekly", **process_weekly_reset(data, week_day.isoformat())})
        week_day += timedelta(days=7)
    data["last_week"] = current_week
    return summaries


def check_achievements(data: dict[str, Any]) -> list[str]:
    newly = []
    unlocked = set(data.get("achievements", []))
    lv_now = get_level(data["hp"], data["exp"])[0]["level"]
    checks = {
        "streak3": data.get("streak", 0) >= 3,
        "streak7": data.get("streak", 0) >= 7,
        "streak30": data.get("streak", 0) >= 30,
        "faith7": data.get("faith_streak", 0) >= 7,
        "level2": lv_now >= 2,
        "level3": lv_now >= 3,
        "level4": lv_now >= 4,
        "level5": lv_now >= 5,
        "kupon5": data.get("total_redeems", 0) >= 5,
        "habit100": data.get("total_habits_done", 0) >= 100,
    }
    for ach_id, condition in checks.items():
        if condition and ach_id not in unlocked:
            data["achievements"].append(ach_id)
            newly.append(ach_id)
    return newly


def fmt_rp(n: int | float) -> str:
    return "Rp{:,}".format(int(n)).replace(",", ".")
