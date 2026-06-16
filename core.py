"""
core.py — Data models, constants, and persistence layer.
Single source of truth for all game data and business logic.
"""

from __future__ import annotations
import json
from datetime import date
from pathlib import Path
from typing import Any

# ── FILE PATH ─────────────────────────────────────────────────────────────────
DATA_FILE = Path("data.json")

# ── HABIT DEFINITIONS ─────────────────────────────────────────────────────────
# Struktur: id, name, cat, hp_reward, exp_reward, hp_penalty, exp_penalty
# Semua reward/penalty dihitung SAAT RESET, bukan real-time

DEFAULT_HABITS: list[dict] = [
    # ── Faith (urutan pertama, tanpa penalti) ─────────────────────────────────
    {"id":"subuh",    "name":"Subuh",    "cat":"Faith", "hp":3, "exp":5, "hp_pen":0, "exp_pen":0},
    {"id":"dzuhur",   "name":"Dzuhur",   "cat":"Faith", "hp":3, "exp":5, "hp_pen":0, "exp_pen":0},
    {"id":"asyar",    "name":"Asyar",    "cat":"Faith", "hp":3, "exp":5, "hp_pen":0, "exp_pen":0},
    {"id":"magrib",   "name":"Magrib",   "cat":"Faith", "hp":3, "exp":5, "hp_pen":0, "exp_pen":0},
    {"id":"isya",     "name":"Isya",     "cat":"Faith", "hp":3, "exp":5, "hp_pen":0, "exp_pen":0},
    {"id":"duha",     "name":"Duha",     "cat":"Faith", "hp":3, "exp":5, "hp_pen":0, "exp_pen":0},
    {"id":"ngaji",    "name":"Ngaji",    "cat":"Faith", "hp":3, "exp":5, "hp_pen":0, "exp_pen":0},
    {"id":"dzikir",   "name":"Dzikir",   "cat":"Faith", "hp":3, "exp":5, "hp_pen":0, "exp_pen":0},

    # ── Fisik Harian ──────────────────────────────────────────────────────────
    {"id":"tidur",       "name":"Tidur 7 Jam",    "cat":"Fisik", "hp":5,  "exp":0, "hp_pen":3, "exp_pen":0},
    {"id":"stretching",  "name":"Stretching",     "cat":"Fisik", "hp":5,  "exp":0, "hp_pen":3, "exp_pen":0},
    {"id":"pushup_awal", "name":"Push Up Awal",   "cat":"Fisik", "hp":10, "exp":0, "hp_pen":3, "exp_pen":0},
    {"id":"pullup_awal", "name":"Pull Up Awal",   "cat":"Fisik", "hp":10, "exp":0, "hp_pen":3, "exp_pen":0},
    {"id":"skincare_awal","name":"Skincare Awal", "cat":"Fisik", "hp":5,  "exp":0, "hp_pen":3, "exp_pen":0},
    {"id":"pushup_akhir","name":"Push Up Akhir",  "cat":"Fisik", "hp":10, "exp":0, "hp_pen":3, "exp_pen":0},
    {"id":"pullup_akhir","name":"Pull Up Akhir",  "cat":"Fisik", "hp":10, "exp":0, "hp_pen":3, "exp_pen":0},
    {"id":"plank",       "name":"Plank",          "cat":"Fisik", "hp":10, "exp":0, "hp_pen":3, "exp_pen":0},
    {"id":"skincare_akhir","name":"Skincare Akhir","cat":"Fisik","hp":5,  "exp":0, "hp_pen":3, "exp_pen":0},
    {"id":"minum",       "name":"Minum 2 Liter",  "cat":"Fisik", "hp":5,  "exp":0, "hp_pen":3, "exp_pen":0},
    {"id":"makan",       "name":"Makan Bergizi",  "cat":"Fisik", "hp":5,  "exp":0, "hp_pen":3, "exp_pen":0},

    # ── Skill & Knowledge ─────────────────────────────────────────────────────
    {"id":"kuliah",  "name":"Kuliah 1 Jam",       "cat":"Skill", "hp":0, "exp":10, "hp_pen":0, "exp_pen":3},
    {"id":"projek",  "name":"Projek 1 Jam",       "cat":"Skill", "hp":0, "exp":10, "hp_pen":0, "exp_pen":3},
    {"id":"video",   "name":"1 Video Ilmu",        "cat":"Skill", "hp":0, "exp":10, "hp_pen":0, "exp_pen":3},

    # ── Finance ───────────────────────────────────────────────────────────────
    {"id":"pengeluaran_sesuai","name":"Pengeluaran Sesuai Budget","cat":"Finance","hp":0,"exp":5,"hp_pen":0,"exp_pen":1},
    {"id":"catat_pengeluaran", "name":"Catat Pengeluaran",        "cat":"Finance","hp":0,"exp":5,"hp_pen":0,"exp_pen":1},

    # ── Evaluasi ──────────────────────────────────────────────────────────────
    {"id":"input_data","name":"Input Data",  "cat":"Evaluasi","hp":0,"exp":5,"hp_pen":0,"exp_pen":1},
    {"id":"evaluasi",  "name":"Evaluasi",    "cat":"Evaluasi","hp":0,"exp":5,"hp_pen":0,"exp_pen":1},
    {"id":"metime",    "name":"Me Time",     "cat":"Evaluasi","hp":0,"exp":5,"hp_pen":0,"exp_pen":1},
]

# Urutan render kategori di tab harian
HABIT_CATEGORY_ORDER = ["Faith", "Fisik", "Skill", "Finance", "Evaluasi", "Custom"]

# ── WEEKLY MISSIONS ───────────────────────────────────────────────────────────
# Misi: reward +50 HP +20 kupon jika terceklis
DEFAULT_MISSIONS: list[dict] = [
    {"id":"tahlil",    "name":"Tahlil",        "hp":50, "exp":0, "kupon":20, "type":"misi"},
    {"id":"puasa",     "name":"Puasa Sunah",    "hp":50, "exp":0, "kupon":20, "type":"misi"},
    {"id":"lari",      "name":"Lari 3 km",      "hp":50, "exp":0, "kupon":20, "type":"misi"},
    {"id":"gym",       "name":"Gym / Berat",    "hp":50, "exp":0, "kupon":20, "type":"misi"},
    {"id":"yoga",      "name":"Yoga",           "hp":50, "exp":0, "kupon":20, "type":"misi"},
    {"id":"detox",     "name":"Detox Tubuh",    "hp":50, "exp":0, "kupon":20, "type":"misi"},
    {"id":"bodycare",  "name":"Bodycare",       "hp":50, "exp":0, "kupon":20, "type":"misi"},
]

# Kewajiban: penalti -30 HP -20 kupon jika TIDAK terceklis saat reset
DEFAULT_OBLIGATIONS: list[dict] = [
    {"id":"ob_5r",       "name":"5R Kamar",          "pen_hp":30, "pen_kupon":20},
    {"id":"ob_nyuci",    "name":"Nyuci Baju",         "pen_hp":30, "pen_kupon":20},
    {"id":"ob_motor",    "name":"Maintenance Motor",  "pen_hp":30, "pen_kupon":20},
    {"id":"ob_input",    "name":"Input Mingguan",     "pen_hp":30, "pen_kupon":20},
    {"id":"ob_efisik",   "name":"Evaluasi Fisik",     "pen_hp":30, "pen_kupon":20},
    {"id":"ob_elajar",   "name":"Evaluasi Belajar",   "pen_hp":30, "pen_kupon":20},
    {"id":"ob_ekeuangan","name":"Evaluasi Keuangan",  "pen_hp":30, "pen_kupon":20},
    {"id":"ob_eprojek",  "name":"Evaluasi Projek",    "pen_hp":30, "pen_kupon":20},
]

# ── COUPONS ───────────────────────────────────────────────────────────────────
COUPONS: list[dict] = [
    {"id":"makan",   "name":"Makan Enak",   "pts":50,  "value":"Rp50.000"},
    {"id":"hiburan", "name":"Hiburan/Game", "pts":100, "value":"Rp100.000"},
    {"id":"beli",    "name":"Beli Sesuatu", "pts":200, "value":"Rp200.000"},
    {"id":"trip",    "name":"Mini Trip",    "pts":400, "value":"Rp400.000"},
]

# ── LEVELS ────────────────────────────────────────────────────────────────────
LEVELS: list[dict] = [
    {"level":1, "name":"Pemula",   "threshold":0,    "avatar":"👶"},
    {"level":2, "name":"Pejuang",  "threshold":500,  "avatar":"⚔️"},
    {"level":3, "name":"Ksatria",  "threshold":1200, "avatar":"🛡️"},
    {"level":4, "name":"Pahlawan", "threshold":2500, "avatar":"🦸"},
    {"level":5, "name":"Legenda",  "threshold":5000, "avatar":"👑"},
]

# ── BUDGET ────────────────────────────────────────────────────────────────────
BUDGET: dict[str, int] = {
    "Kebutuhan Pokok":  350000,
    "Kost":             600000,
    "Kas Kantor":       100000,
    "Cadangan & Bebas": 400000,
    "Dana Darurat":     200000,
    "UKT Kuliah":       300000,
}

EXPENSE_CATS: list[str] = [
    "Kebutuhan Pokok","Kost","Kas Kantor",
    "Cadangan & Bebas","Dana Darurat","UKT Kuliah",
    "Tabungan Utama","Lainnya"
]

# ── ACHIEVEMENTS ──────────────────────────────────────────────────────────────
ACHIEVEMENTS: list[dict] = [
    {"id":"streak3",  "name":"On Fire",          "desc":"Streak 3 hari",           "icon":"🔥"},
    {"id":"streak7",  "name":"Week Warrior",     "desc":"Streak 7 hari",           "icon":"⚡"},
    {"id":"streak30", "name":"Iron Will",        "desc":"Streak 30 hari",          "icon":"💎"},
    {"id":"faith7",   "name":"Istiqomah",        "desc":"Sholat 5 waktu 7 hari",   "icon":"🕌"},
    {"id":"level2",   "name":"Pejuang Sejati",   "desc":"Mencapai Level 2",        "icon":"⚔️"},
    {"id":"level3",   "name":"Ksatria Muda",     "desc":"Mencapai Level 3",        "icon":"🛡️"},
    {"id":"level4",   "name":"Sang Pahlawan",    "desc":"Mencapai Level 4",        "icon":"🦸"},
    {"id":"level5",   "name":"Sang Legenda",     "desc":"Mencapai Level 5",        "icon":"👑"},
    {"id":"gold1000", "name":"Hemat Pangkal Kaya","desc":"Kumpulkan 1000 Gold",    "icon":"💰"},
    {"id":"kupon5",   "name":"Reward Hunter",    "desc":"Tukar kupon 5 kali",      "icon":"🎟️"},
    {"id":"habit100", "name":"Konsisten",        "desc":"Total 100 habit selesai", "icon":"✅"},
]

# ── DEFAULT STATE ─────────────────────────────────────────────────────────────
def default_state() -> dict[str, Any]:
    return {
        "hp": 50,
        "exp": 0,
        "gold": 0,
        "kupon": 0,
        "shift": "Pagi",
        # {date_str: {habit_id: bool}} — checklist harian
        "habits": {},
        # {week_start: {mission_id: bool}} — misi mingguan
        "missions": {},
        # {week_start: {obligation_id: bool}} — kewajiban mingguan
        "obligations": {},
        "transactions": [],
        "redeem_log": [],
        "streak": 0,
        "best_streak": 0,
        "faith_streak": 0,      # streak sholat 5 waktu lengkap (subuh-isya)
        # {date_str: "done"|"partial"|"miss"} — untuk heatmap
        "week_days": {},
        # [{level, name, date}] — riwayat level up
        "level_history": [],
        # {habit_id: total_count} — total keseluruhan
        "habit_history": {},
        "achievements": [],
        "total_redeems": 0,
        "total_habits_done": 0,
        # habit/misi tambahan dari user
        "custom_habits": [],
        "custom_missions": [],
        # {month_str: {target_id: {label, target, current}}}
        "monthly_targets": {},
        "last_date": str(date.today()),
    }

# ── PERSISTENCE ───────────────────────────────────────────────────────────────
def load() -> dict[str, Any]:
    """Load dari JSON, merge dengan default untuk key baru (backward-compat)."""
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
            base = default_state()
            for k, v in base.items():
                if k not in saved:
                    saved[k] = v
            return saved
        except Exception:
            pass
    return default_state()

def save(data: dict[str, Any]) -> None:
    """Atomic write: tulis ke .tmp dulu, lalu rename — hindari korupsi file."""
    try:
        tmp = DATA_FILE.with_suffix(".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        tmp.replace(DATA_FILE)
    except Exception as e:
        raise RuntimeError(f"Gagal menyimpan data: {e}")

def import_data(json_str: str) -> dict[str, Any]:
    """Parse JSON string, merge dengan default_state untuk key yang hilang."""
    imported = json.loads(json_str)
    base = default_state()
    for k, v in base.items():
        if k not in imported:
            imported[k] = v
    return imported

# ── GAME LOGIC ────────────────────────────────────────────────────────────────
def get_level(hp: int, exp: int) -> tuple[dict, dict | None, int]:
    """Return (current_level_dict, next_level_dict|None, total_stat)."""
    total = hp + exp
    cur, nxt = LEVELS[0], None
    for i, lv in enumerate(LEVELS):
        if total >= lv["threshold"]:
            cur = lv
            nxt = LEVELS[i + 1] if i + 1 < len(LEVELS) else None
    return cur, nxt, total

def get_all_habits(data: dict) -> list[dict]:
    """Gabungkan habit default + custom user."""
    return DEFAULT_HABITS + data.get("custom_habits", [])

def get_all_missions(data: dict) -> list[dict]:
    """Gabungkan misi default + custom user."""
    return DEFAULT_MISSIONS + data.get("custom_missions", [])

def get_today_habits(data: dict) -> dict[str, bool]:
    """Ambil status checklist untuk hari ini."""
    return data["habits"].get(str(date.today()), {})

def set_today_habit(data: dict, habit_id: str, value: bool) -> None:
    """Set satu habit untuk hari ini."""
    today = str(date.today())
    data["habits"].setdefault(today, {})[habit_id] = value

def get_week_key() -> str:
    """Senin minggu ini sebagai key week."""
    today = date.today()
    return str(today - __import__("datetime").timedelta(days=today.weekday()))

def process_daily_reset(data: dict) -> dict[str, Any]:
    """
    Hitung reward dan penalti saat reset hari baru.
    Semua perubahan stat dilakukan di sini — TIDAK real-time.
    Returns: dict ringkasan perubahan untuk ditampilkan ke user.
    """
    today_key   = str(date.today())
    today_h     = get_today_habits(data)
    all_habits  = get_all_habits(data)
    summary     = {"hp_delta": 0, "exp_delta": 0, "kupon_delta": 0,
                   "streak": 0, "messages": []}

    hp_delta  = 0
    exp_delta = 0

    # ── Hitung reward/penalti per habit ──────────────────────────────────────
    for h in all_habits:
        done = today_h.get(h["id"], False)
        if done:
            hp_delta  += h.get("hp",  h.get("hp_reward", 0))
            exp_delta += h.get("exp", h.get("exp_reward", 0))
            data["habit_history"][h["id"]] = data["habit_history"].get(h["id"], 0) + 1
            data["total_habits_done"] = data.get("total_habits_done", 0) + 1
        else:
            # Kurangi penalti (gunakan key baru hp_pen/exp_pen)
            hp_delta  -= h.get("hp_pen",  0)
            exp_delta -= h.get("exp_pen", 0)

    # ── Faith streak tracking (subuh s.d. isya) ───────────────────────────────
    faith_core_ids = ["subuh","dzuhur","asyar","magrib","isya"]
    faith_complete = all(today_h.get(fid, False) for fid in faith_core_ids)
    if faith_complete:
        data["faith_streak"] = data.get("faith_streak", 0) + 1
        if data["faith_streak"] == 7:
            data["kupon"] += 50
            summary["kupon_delta"] += 50
            summary["messages"].append("🕌 Faith Streak 7 hari! +50 kupon")
    else:
        data["faith_streak"] = 0

    # ── Streak harian (semua habit non-Faith harus selesai untuk "done") ─────
    # Tentukan "done" berdasarkan habit Fisik, Skill, Finance, Evaluasi
    non_faith = [h for h in all_habits if h["cat"] != "Faith"]
    core_done_count = sum(1 for h in non_faith if today_h.get(h["id"], False))
    all_non_faith_done = core_done_count == len(non_faith)

    if all_non_faith_done:
        data["streak"] += 1
        if data["streak"] > data["best_streak"]:
            data["best_streak"] = data["streak"]
        data["week_days"][today_key] = "done"

        # Streak rewards
        streak_rewards = {3: 30, 7: 75, 30: 300}
        if data["streak"] in streak_rewards:
            bonus = streak_rewards[data["streak"]]
            data["kupon"] += bonus
            summary["kupon_delta"] += bonus
            summary["messages"].append(f"🔥 Streak {data['streak']} hari! +{bonus} kupon")
    elif core_done_count >= len(non_faith) // 2:
        data["week_days"][today_key] = "partial"
        data["streak"] = 0
    else:
        data["week_days"][today_key] = "miss"
        data["streak"] = 0

    # ── Terapkan perubahan stat ───────────────────────────────────────────────
    data["hp"]  = max(0, data["hp"] + hp_delta)
    data["exp"] = max(0, data["exp"] + exp_delta)

    summary["hp_delta"]  = hp_delta
    summary["exp_delta"] = exp_delta
    summary["streak"]    = data["streak"]

    # ── Reset checklist hari ini ──────────────────────────────────────────────
    data["habits"][today_key] = {}

    return summary

def process_weekly_reset(data: dict) -> dict[str, Any]:
    """
    Hitung penalti kewajiban yang tidak terceklis saat reset minggu baru.
    Returns: ringkasan penalti.
    """
    week_key    = get_week_key()
    obligations = data.get("obligations", {}).get(week_key, {})
    summary     = {"hp_delta": 0, "kupon_delta": 0, "messages": []}

    hp_pen    = 0
    kupon_pen = 0

    for ob in DEFAULT_OBLIGATIONS:
        if not obligations.get(ob["id"], False):
            hp_pen    += ob["pen_hp"]
            kupon_pen += ob["pen_kupon"]
            summary["messages"].append(f"⚠️ {ob['name']} tidak selesai: -{ob['pen_hp']} HP -{ob['pen_kupon']} kupon")

    data["hp"]    = max(0, data["hp"] - hp_pen)
    data["kupon"] = max(0, data["kupon"] - kupon_pen)

    summary["hp_delta"]    = -hp_pen
    summary["kupon_delta"] = -kupon_pen

    # Reset obligations untuk minggu ini
    if week_key in data.get("obligations", {}):
        data["obligations"][week_key] = {}

    return summary

def check_achievements(data: dict) -> list[str]:
    """Cek dan unlock achievement baru. Returns list ID yang baru unlock."""
    newly  = []
    has    = set(data.get("achievements", []))
    lv_now = get_level(data["hp"], data["exp"])[0]["level"]

    checks = {
        "streak3":  data["streak"] >= 3,
        "streak7":  data["streak"] >= 7,
        "streak30": data["streak"] >= 30,
        "faith7":   data.get("faith_streak", 0) >= 7,
        "level2":   lv_now >= 2,
        "level3":   lv_now >= 3,
        "level4":   lv_now >= 4,
        "level5":   lv_now >= 5,
        "gold1000": data["gold"] >= 1000,
        "kupon5":   data.get("total_redeems", 0) >= 5,
        "habit100": data.get("total_habits_done", 0) >= 100,
    }

    for aid, cond in checks.items():
        if cond and aid not in has:
            data["achievements"].append(aid)
            newly.append(aid)

    return newly

def fmt_rp(n: int | float) -> str:
    return "Rp{:,}".format(int(n)).replace(",", ".")
