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


def _get_supabase_client() -> Client:
    """Client 'polos' (belum ada sesi login). Dipakai untuk sign_up/sign_in,
    dan sebagai basis client yang nanti sesinya di-attach setelah login."""
    url = st.secrets.get("SUPABASE_URL") or os.environ.get("SUPABASE_URL")
    key = st.secrets.get("SUPABASE_KEY") or os.environ.get("SUPABASE_KEY")
    if not url or not key:
        raise RuntimeError(
            "SUPABASE_URL / SUPABASE_KEY belum diset. "
            "Tambahkan di .streamlit/secrets.toml atau environment variable."
        )
    return create_client(url, key)


# --- Auth ---
def sign_up(email: str, password: str) -> Client:
    """Daftar user baru. Mengembalikan client yang sudah membawa sesi
    (kalau project mengharuskan konfirmasi email, session bisa None —
    caller perlu menangani kasus itu di app.py)."""
    client = _get_supabase_client()
    client.auth.sign_up({"email": email, "password": password})
    return client


def sign_in(email: str, password: str) -> Client:
    """Login. Mengembalikan client yang sesi auth-nya sudah aktif, sehingga
    setiap request .table(...) berikutnya lewat client ini otomatis membawa
    JWT user tsb dan auth.uid() di RLS akan terisi dengan benar."""
    client = _get_supabase_client()
    client.auth.sign_in_with_password({"email": email, "password": password})
    return client


def sign_out(client: Client) -> None:
    try:
        client.auth.sign_out()
    except Exception:
        pass  # sesi mungkin sudah invalid/expired, aman diabaikan saat logout


def get_current_user_id(client: Client) -> str | None:
    """Ambil user_id (uuid) dari sesi aktif client, atau None kalau belum login."""
    try:
        user = client.auth.get_user()
        return user.user.id if user and user.user else None
    except Exception:
        return None


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
    {"id": "dzuhur", "name": "Dzuhur", "cat": "Faith", "hp": 3, "exp": 5, "hp_pen": 3, "exp_pen": 5, "unlock_level": 2},
    {"id": "asyar", "name": "Asyar", "cat": "Faith", "hp": 3, "exp": 5, "hp_pen": 3, "exp_pen": 5, "unlock_level": 2},
    {"id": "magrib", "name": "Magrib", "cat": "Faith", "hp": 3, "exp": 5, "hp_pen": 3, "exp_pen": 5, "unlock_level": 1},
    {"id": "isya", "name": "Isya", "cat": "Faith", "hp": 3, "exp": 5, "hp_pen": 3, "exp_pen": 5, "unlock_level": 1},
    {"id": "dzikir", "name": "Dzikir", "cat": "Faith", "hp": 3, "exp": 5, "hp_pen": 3, "exp_pen": 5, "unlock_level": 3},
    {"id": "ngaji", "name": "Ngaji", "cat": "Faith", "hp": 3, "exp": 5, "hp_pen": 3, "exp_pen": 5, "unlock_level": 4},
    {"id": "duha", "name": "Duha", "cat": "Faith", "hp": 3, "exp": 5, "hp_pen": 3, "exp_pen": 5, "unlock_level": 5},
    {"id": "jaga_sikap", "name": "Jaga Sikap", "cat": "Faith", "hp": 3, "exp": 3, "hp_pen": 2, "exp_pen": 2, "unlock_level": 5},

    {"id": "tidur", "name": "Tidur 7 Jam", "cat": "Fisik Harian", "hp": 5, "exp": 0, "hp_pen": 3, "exp_pen": 0, "unlock_level": 1},
    {"id": "stretching", "name": "Stretching", "cat": "Fisik Harian", "hp": 5, "exp": 0, "hp_pen": 3, "exp_pen": 0, "unlock_level": 1},
    {"id": "pushup_akhir", "name": "Push Up Akhir", "cat": "Fisik Harian", "hp": 10, "exp": 0, "hp_pen": 3, "exp_pen": 0, "unlock_level": 1},
    {"id": "skincare_akhir", "name": "Skincare Akhir", "cat": "Fisik Harian", "hp": 5, "exp": 0, "hp_pen": 3, "exp_pen": 0, "unlock_level": 1},
    {"id": "minum", "name": "Minum 2 Liter", "cat": "Fisik Harian", "hp": 5, "exp": 0, "hp_pen": 3, "exp_pen": 0, "unlock_level": 2},
    {"id": "pullup_akhir", "name": "Pull Up Akhir", "cat": "Fisik Harian", "hp": 10, "exp": 0, "hp_pen": 3, "exp_pen": 0, "unlock_level": 2},
    {"id": "rokok", "name": "Merokok 3 Batang", "name_by_level": {4: "Merokok 2 Batang"}, "cat": "Fisik Harian", "hp": 10, "exp": 0, "hp_pen": 3, "exp_pen": 0, "unlock_level": 3},
    {"id": "plank", "name": "Plank", "cat": "Fisik Harian", "hp": 10, "exp": 0, "hp_pen": 3, "exp_pen": 0, "unlock_level": 4},
    {"id": "makan", "name": "Makan Bergizi", "cat": "Fisik Harian", "hp": 5, "exp": 0, "hp_pen": 3, "exp_pen": 0, "unlock_level": 3},
    {"id": "pushup_awal", "name": "Push Up Awal", "cat": "Fisik Harian", "hp": 10, "exp": 0, "hp_pen": 3, "exp_pen": 0, "unlock_level": 5},
    {"id": "pullup_awal", "name": "Pull Up Awal", "cat": "Fisik Harian", "hp": 10, "exp": 0, "hp_pen": 3, "exp_pen": 0, "unlock_level": 4},
    {"id": "skincare_awal", "name": "Skincare Awal", "cat": "Fisik Harian", "hp": 5, "exp": 0, "hp_pen": 3, "exp_pen": 0, "unlock_level": 2},

    {"id": "kuliah", "name": "Kuliah 1 Jam", "cat": "Skill & Knowledge", "hp": 0, "exp": 10, "hp_pen": 0, "exp_pen": 3, "unlock_level": 1},
    {"id": "video", "name": "1 Video Ilmu", "cat": "Skill & Knowledge", "hp": 0, "exp": 10, "hp_pen": 0, "exp_pen": 3, "unlock_level": 2},
    {"id": "projek", "name": "Projek 1 Jam", "cat": "Skill & Knowledge", "hp": 0, "exp": 10, "hp_pen": 0, "exp_pen": 3, "unlock_level": 3},

    {"id": "evaluasi", "name": "Evaluasi", "cat": "Evaluasi", "hp": 0, "exp": 5, "hp_pen": 0, "exp_pen": 1, "unlock_level": 1},
]

HABIT_CATEGORY_ORDER = ["Faith", "Fisik Harian", "Skill & Knowledge", "Evaluasi", "Custom"]

# Urutan tampilan misi harian di tab Harian, khusus per kombinasi shift + level.
# Habit yang unlock di level tsb tapi TIDAK ada di list ini (misalnya habit
# custom yang ditambahkan lewat data lama) tetap akan ditampilkan sebagai
# fallback di app.py, cuma dikelompokkan di bagian akhir, bukan hilang.
DAILY_MISSION_ORDER: dict[str, dict[int, list[str]]] = {
    "Pagi": {
        1: ["tidur", "stretching", "subuh", "magrib", "kuliah", "pushup_akhir", "skincare_akhir", "isya", "evaluasi"],
        2: ["tidur", "stretching", "subuh", "skincare_awal", "dzuhur", "asyar", "magrib", "video", "kuliah", "pushup_akhir", "pullup_akhir", "skincare_akhir", "isya", "minum", "evaluasi"],
        3: ["tidur", "stretching", "subuh", "skincare_awal", "dzuhur", "makan", "asyar", "magrib", "video", "kuliah", "projek", "pushup_akhir", "pullup_akhir", "skincare_akhir", "isya", "dzikir", "minum", "rokok", "evaluasi"],
        4: ["tidur", "stretching", "pullup_awal", "subuh", "ngaji", "skincare_awal", "dzuhur", "makan", "asyar", "magrib", "video", "kuliah", "projek", "pushup_akhir", "pullup_akhir", "plank", "skincare_akhir", "isya", "dzikir", "minum", "rokok", "evaluasi"],
        5: ["tidur", "stretching", "pullup_awal", "subuh", "pushup_awal", "ngaji", "skincare_awal", "duha", "dzuhur", "makan", "asyar", "magrib", "video", "kuliah", "projek", "pushup_akhir", "pullup_akhir", "plank", "skincare_akhir", "isya", "dzikir", "minum", "rokok", "jaga_sikap", "evaluasi"],
    },
    "Malam": {
        1: ["tidur", "stretching", "magrib", "isya", "subuh", "kuliah", "pushup_akhir", "skincare_akhir", "evaluasi"],
        2: ["tidur", "stretching", "asyar", "magrib", "skincare_awal", "isya", "subuh", "video", "kuliah", "pushup_akhir", "pullup_akhir", "skincare_akhir", "minum", "evaluasi", "dzuhur"],
        3: ["tidur", "stretching", "asyar", "magrib", "dzikir", "video", "skincare_awal", "isya", "makan", "subuh", "kuliah", "projek", "pushup_akhir", "pullup_akhir", "skincare_akhir", "rokok", "minum", "evaluasi", "dzuhur"],
        4: ["tidur", "stretching", "pullup_awal", "asyar", "magrib", "dzikir", "ngaji", "video", "skincare_awal", "isya", "makan", "subuh", "kuliah", "projek", "pushup_akhir", "pullup_akhir", "plank", "skincare_akhir", "rokok", "minum", "evaluasi", "dzuhur"],
        5: ["tidur", "stretching", "pullup_awal", "asyar", "pushup_awal", "magrib", "dzikir", "ngaji", "video", "skincare_awal", "isya", "makan", "subuh", "kuliah", "projek", "pushup_akhir", "pullup_akhir", "plank", "duha", "skincare_akhir", "rokok", "minum", "jaga_sikap", "evaluasi", "dzuhur"],
    },
}


def get_ordered_daily_habits(data: dict[str, Any]) -> list[dict[str, Any]]:
    """Habit yang unlock, diurutkan sesuai shift+level dari DAILY_MISSION_ORDER.
    Habit unlock yang tidak terdaftar di urutan (misal habit custom lama)
    tetap ikut, ditaruh di akhir supaya tidak ada yang hilang dari checklist."""
    level = get_level(data["hp"], data["exp"])[0]["level"]
    active = get_unlocked_habits(data)
    by_id = {h["id"]: h for h in active}
    order = DAILY_MISSION_ORDER.get(data.get("shift", "Pagi"), {}).get(level, [])
    ordered = [by_id[hid] for hid in order if hid in by_id]
    leftover_ids = set(by_id.keys()) - set(order)
    leftover = [h for h in active if h["id"] in leftover_ids]
    return ordered + leftover

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
    {"level": 2, "name": "POLOS", "threshold": 2000, "avatar": "Lv2"},
    {"level": 3, "name": "PEJUANG", "threshold": 5000, "avatar": "Lv3"},
    {"level": 4, "name": "PENDEKAR", "threshold": 12000, "avatar": "Lv4"},
    {"level": 5, "name": "JAMAL", "threshold": 25000, "avatar": "Lv5"},
]

ACHIEVEMENTS: list[dict[str, Any]] = [
    {"id": "streak3", "name": "On Fire", "desc": "Streak 3 hari", "icon": "*", "reward_hp": 10, "reward_exp": 10},
    {"id": "streak7", "name": "Week Warrior", "desc": "Streak 7 hari", "icon": "*", "reward_hp": 15, "reward_exp": 15},
    {"id": "streak14", "name": "Iron Will", "desc": "Streak 14 hari", "icon": "*", "reward_hp": 20, "reward_exp": 20},
    {"id": "streak30", "name": "Unbreakable", "desc": "Streak 30 hari", "icon": "*", "reward_hp": 25, "reward_exp": 25},
    {"id": "level2", "name": LEVELS[1]["name"], "desc": "Mencapai Level 2", "icon": "*", "reward_kupon": 200},
    {"id": "level3", "name": LEVELS[2]["name"], "desc": "Mencapai Level 3", "icon": "*", "reward_kupon": 200},
    {"id": "level4", "name": LEVELS[3]["name"], "desc": "Mencapai Level 4", "icon": "*", "reward_kupon": 200},
    {"id": "level5", "name": LEVELS[4]["name"], "desc": "Mencapai Level 5", "icon": "*", "reward_kupon": 200},
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
        "daily_stats": {},
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


def load(client: Client, user_id: str) -> dict[str, Any]:
    """Load state milik user_id dari Supabase, lewat client yang sudah login
    (supaya RLS auth.uid() = user_id terpenuhi). Falls back ke default_state()
    in-memory kalau Supabase unreachable — dalam kasus itu tidak akan
    tersimpan sampai koneksi pulih."""
    try:
        resp = (
            client.table(SUPABASE_TABLE)
            .select("data")
            .eq("user_id", user_id)
            .execute()
        )
        if resp.data:
            return migrate_state(resp.data[0]["data"])
        # User baru, belum punya row: seed dengan default_state().
        state = default_state()
        client.table(SUPABASE_TABLE).insert(
            {"user_id": user_id, "data": state}
        ).execute()
        return state
    except Exception as e:
        st.error(f"⚠️ Gagal terhubung ke Supabase, memakai data sementara: {e}")
        return default_state()


def save(client: Client, data: dict[str, Any], user_id: str) -> None:
    try:
        client.table(SUPABASE_TABLE).upsert(
            {"user_id": user_id, "data": data},
            on_conflict="user_id",
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
    gain_total = 0
    penalty_total = 0

    for habit in active_habits:
        done = bool(day_habits.get(habit["id"], False))
        if done:
            hp_delta += int(habit.get("hp", 0))
            exp_delta += int(habit.get("exp", 0))
            gain_total += int(habit.get("hp", 0)) + int(habit.get("exp", 0))
            data["habit_history"][habit["id"]] = data["habit_history"].get(habit["id"], 0) + 1
            data["total_habits_done"] = data.get("total_habits_done", 0) + 1
        else:
            hp_delta -= int(habit.get("hp_pen", 0))
            exp_delta -= int(habit.get("exp_pen", 0))
            penalty_total += int(habit.get("hp_pen", 0)) + int(habit.get("exp_pen", 0))

    data.setdefault("daily_stats", {})[day_key] = {"gain": gain_total, "penalty": penalty_total}

    # Streak now covers ALL unlocked habits (Faith included), not just non-Faith.
    done_count = sum(1 for h in active_habits if day_habits.get(h["id"], False))
    net_delta = hp_delta + exp_delta

    if active_habits and done_count == len(active_habits):
        # 100% misi harian selesai -> putih
        data["streak"] = data.get("streak", 0) + 1
        data["best_streak"] = max(data.get("best_streak", 0), data["streak"])
        data["week_days"][day_key] = "full"
        streak_rewards = {3: 20, 7: 50, 30: 100}
        if data["streak"] in streak_rewards:
            bonus = streak_rewards[data["streak"]]
            data["kupon"] += bonus
            summary["kupon_delta"] += bonus
            summary["messages"].append(f"Streak {data['streak']} hari: +{bonus} kupon")
    elif done_count == 0:
        # Semua misi harian terlewatkan -> merah
        data["week_days"][day_key] = "miss"
        data["streak"] = 0
    elif net_delta > 0:
        # Sebagian terlewat tapi stat bersih naik -> biru
        data["week_days"][day_key] = "gain"
        data["streak"] = 0
    else:
        # Sebagian dikerjakan tapi stat bersih turun/tetap -> ungu
        data["week_days"][day_key] = "loss"
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
        "streak14": data.get("streak", 0) >= 14,
        "streak30": data.get("streak", 0) >= 30,
        "level2": lv_now >= 2,
        "level3": lv_now >= 3,
        "level4": lv_now >= 4,
        "level5": lv_now >= 5,
        "habit100": data.get("total_habits_done", 0) >= 100,
    }
    for ach_id, condition in checks.items():
        if condition and ach_id not in unlocked:
            data["achievements"].append(ach_id)
            newly.append(ach_id)
            ach_def = next((a for a in ACHIEVEMENTS if a["id"] == ach_id), None)
            if ach_def:
                data["hp"] = data.get("hp", 0) + int(ach_def.get("reward_hp", 0))
                data["exp"] = data.get("exp", 0) + int(ach_def.get("reward_exp", 0))
                data["kupon"] = data.get("kupon", 0) + int(ach_def.get("reward_kupon", 0))
    return newly


def fmt_rp(n: int | float) -> str:
    return "Rp{:,}".format(int(n)).replace(",", ".")
