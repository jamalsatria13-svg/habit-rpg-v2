"""
app.py — Habit RPG main Streamlit application.
Entry point: streamlit run app.py
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import json
from datetime import date, datetime, timedelta
from collections import defaultdict
import sys, os

# Ensure core.py is importable from same directory
sys.path.insert(0, os.path.dirname(__file__))
from core import (
    load, save, default_state,
    get_level, get_all_habits, get_all_missions,
    get_today_habits, set_today_habit, check_achievements,
    fmt_rp, COUPONS, LEVELS, BUDGET, EXPENSE_CATS,
    ACHIEVEMENTS, DEFAULT_HABITS, DEFAULT_MISSIONS,
)

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Habit RPG",
    page_icon="⚔️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ── DARK MODE CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Global dark theme ── */
html, body, [data-testid="stAppViewContainer"],
[data-testid="stMain"], .main {
    background-color: #0f0f1a !important;
    color: #e0e0f0 !important;
}
[data-testid="stSidebar"] { background-color: #13131f !important; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: #1a1a2e;
    border-radius: 12px;
    padding: 4px;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: #888 !important;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 500;
}
.stTabs [aria-selected="true"] {
    background: #252540 !important;
    color: #a78bfa !important;
}

/* ── Metric cards ── */
[data-testid="stMetric"] {
    background: #1a1a2e;
    border: 1px solid #2a2a45;
    border-radius: 12px;
    padding: 12px 10px !important;
}
[data-testid="stMetricLabel"] { color: #888 !important; font-size: 12px !important; }
[data-testid="stMetricValue"] { color: #e0e0f0 !important; font-size: 22px !important; }

/* ── Buttons ── */
.stButton > button {
    background: #1a1a2e;
    color: #a78bfa;
    border: 1px solid #3a3a5c;
    border-radius: 8px;
    font-weight: 500;
    transition: all .15s;
}
.stButton > button:hover {
    background: #252540;
    border-color: #a78bfa;
    color: #fff;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #7c3aed, #a78bfa);
    color: #fff;
    border: none;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #6d28d9, #9061f9);
}

/* ── Inputs ── */
.stTextInput input, .stNumberInput input, .stSelectbox select,
[data-baseweb="select"] {
    background: #1a1a2e !important;
    color: #e0e0f0 !important;
    border-color: #2a2a45 !important;
    border-radius: 8px !important;
}

/* ── Checkboxes ── */
.stCheckbox label { color: #c0c0d8 !important; font-size: 14px; }

/* ── Divider ── */
hr { border-color: #2a2a45 !important; }

/* ── Progress bar ── */
.stProgress > div > div > div {
    background: linear-gradient(90deg, #7c3aed, #a78bfa) !important;
    border-radius: 4px;
}

/* ── Success / warning / error ── */
[data-testid="stAlert"] { border-radius: 10px !important; }

/* ── Custom components ── */
.char-card {
    background: linear-gradient(135deg, #1a1a2e 0%, #252540 100%);
    border: 1px solid #3a3a5c;
    border-radius: 16px;
    padding: 20px;
    text-align: center;
    margin-bottom: 1rem;
    position: relative;
    overflow: hidden;
}
.char-card::before {
    content: '';
    position: absolute;
    top: -50%; left: -50%;
    width: 200%; height: 200%;
    background: radial-gradient(circle, rgba(167,139,250,0.05) 0%, transparent 60%);
}
.avatar-ring {
    width: 80px; height: 80px;
    border-radius: 50%;
    background: linear-gradient(135deg, #7c3aed, #a78bfa);
    display: flex; align-items: center; justify-content: center;
    margin: 0 auto 12px;
    font-size: 36px;
    box-shadow: 0 0 20px rgba(167,139,250,0.4);
}
.level-badge {
    display: inline-block;
    background: linear-gradient(135deg, #7c3aed, #a78bfa);
    color: #fff;
    padding: 3px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    margin-bottom: 8px;
}
.stat-bar-wrap {
    background: #252540;
    border-radius: 6px;
    height: 8px;
    overflow: hidden;
    margin-top: 4px;
}
.stat-bar-fill {
    height: 100%;
    border-radius: 6px;
    transition: width .4s ease;
}
.habit-cat-title {
    font-size: 11px;
    font-weight: 700;
    color: #7c7ca8;
    text-transform: uppercase;
    letter-spacing: .08em;
    margin: 1rem 0 .4rem;
}
.ach-card {
    background: #1a1a2e;
    border: 1px solid #2a2a45;
    border-radius: 10px;
    padding: 10px 12px;
    margin-bottom: 6px;
    display: flex;
    gap: 10px;
    align-items: center;
}
.ach-card.unlocked { border-color: #7c3aed; background: #1e1535; }
.coupon-card {
    background: #1a1a2e;
    border: 1px solid #2a2a45;
    border-radius: 12px;
    padding: 14px;
    margin-bottom: 8px;
    text-align: center;
}
.coupon-card.can-redeem {
    border-color: #7c3aed;
    background: linear-gradient(135deg, #1a1535, #1e1a3a);
}
.tx-row {
    display: flex;
    justify-content: space-between;
    padding: 6px 0;
    border-bottom: 1px solid #1e1e35;
    font-size: 13px;
}
.section-title {
    font-size: 11px;
    font-weight: 700;
    color: #7c7ca8;
    text-transform: uppercase;
    letter-spacing: .08em;
    margin: 1.2rem 0 .6rem;
}
.levelup-banner {
    background: linear-gradient(135deg, #7c3aed, #a78bfa);
    border-radius: 12px;
    padding: 16px;
    text-align: center;
    color: #fff;
    font-weight: 700;
    font-size: 18px;
    margin: 1rem 0;
    animation: pulse 1s ease-in-out;
}
@keyframes pulse {
    0%   { transform: scale(0.95); opacity: .7; }
    50%  { transform: scale(1.02); opacity: 1;  }
    100% { transform: scale(1);    opacity: 1;  }
}
.heatmap-cell {
    display: inline-block;
    width: 12px; height: 12px;
    border-radius: 2px;
    margin: 1px;
}
</style>
""", unsafe_allow_html=True)

# ── SESSION STATE INIT ────────────────────────────────────────────────────────
if "D" not in st.session_state:
    st.session_state.D = load()
if "notifications" not in st.session_state:
    st.session_state.notifications = []

D = st.session_state.D  # shorthand — dict is mutable, changes reflect in session

# ── AUTO DATE CHANGE DETECTION ────────────────────────────────────────────────
# Deteksi ganti hari dan autosave log
if D.get("last_date") != str(date.today()):
    D["last_date"] = str(date.today())
    save(D)

# ── HELPER FUNCTIONS ──────────────────────────────────────────────────────────
def persist():
    """Save current state and sync session."""
    save(st.session_state.D)

def notify(msg: str):
    st.session_state.notifications.append(msg)

def show_notifications():
    for msg in st.session_state.notifications:
        st.toast(msg)
    st.session_state.notifications = []

def render_stat_bar(value: int, max_val: int, color: str) -> str:
    pct = min(100, int((value / max_val) * 100)) if max_val else 0
    return f"""
    <div class="stat-bar-wrap">
        <div class="stat-bar-fill" style="width:{pct}%;background:{color}"></div>
    </div>"""

def get_habit_history_month(habit_id: str) -> int:
    """Count how many times a habit was done this month."""
    month = date.today().strftime("%Y-%m")
    count = 0
    for day_str, day_habits in D.get("habits", {}).items():
        if day_str.startswith(month) and day_habits.get(habit_id, False):
            count += 1
    return count

def build_heatmap_data() -> dict[str, str]:
    """Build {date_str: color} for last 12 weeks."""
    result = {}
    for i in range(84):  # 12 minggu ke belakang
        d = date.today() - timedelta(days=83 - i)
        status = D["week_days"].get(str(d), "none")
        if status == "done":    result[str(d)] = "#7c3aed"
        elif status == "partial": result[str(d)] = "#4a2a7a"
        elif status == "miss":  result[str(d)] = "#3a1a1a"
        else:                   result[str(d)] = "#1a1a2e"
    return result

show_notifications()

# ── TABS ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "⚔️ Harian", "💰 Keuangan", "📅 Mingguan", "📊 Statistik", "🏆 Review"
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — HARIAN
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    # ── Shift toggle ──
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🌅 Shift Pagi",
                     type="primary" if D["shift"] == "Pagi" else "secondary",
                     use_container_width=True):
            D["shift"] = "Pagi"; persist(); st.rerun()
    with col2:
        if st.button("🌙 Shift Malam",
                     type="primary" if D["shift"] == "Malam" else "secondary",
                     use_container_width=True):
            D["shift"] = "Malam"; persist(); st.rerun()

    st.caption(f"**{D['shift']}** | {date.today().strftime('%A, %d %B %Y')}")

    # ── Character card ──
    cur_lv, nxt_lv, total_stat = get_level(D["hp"], D["exp"])
    pct_lv = 0.0
    if nxt_lv:
        pct_lv = min(1.0, (total_stat - cur_lv["threshold"]) / (nxt_lv["threshold"] - cur_lv["threshold"]))

    st.markdown(f"""
    <div class="char-card">
        <div class="avatar-ring">{cur_lv['avatar']}</div>
        <div class="level-badge">Level {cur_lv['level']} — {cur_lv['name']}</div>
        <div style="font-size:13px;color:#888;margin-bottom:12px">
            {'Total: ' + str(total_stat) + ' / ' + str(nxt_lv['threshold']) + ' → Level ' + str(nxt_lv['level']) if nxt_lv else '✨ Level Maksimal!'}
        </div>
    </div>
    """, unsafe_allow_html=True)

    if nxt_lv:
        st.progress(pct_lv)

    # ── Stat cards ──
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("❤️ HP",      f"{D['hp']}/100")
    c2.metric("🧠 EXP",     D["exp"])
    c3.metric("💰 Gold",    D["gold"])
    c4.metric("🎟️ Kupon",  D["kupon"])

    # HP visual bar
    st.markdown(
        render_stat_bar(D["hp"], 100, "#ef4444") +
        render_stat_bar(D["exp"] % 500 if D["exp"] < 5000 else 500, 500, "#8b5cf6") +
        render_stat_bar(min(D["gold"], 9000), 9000, "#f59e0b"),
        unsafe_allow_html=True
    )

    st.divider()

    # ── Habit sections ──
    today_habits = get_today_habits(D)
    all_habits   = get_all_habits(D)

    for cat in ["Fisik Core", "Fisik Bonus", "Belajar", "Ibadah", "Custom"]:
        cat_habits = [h for h in all_habits if h["cat"] == cat]
        if not cat_habits:
            continue
        st.markdown(f'<div class="habit-cat-title">{cat}</div>', unsafe_allow_html=True)

        for h in cat_habits:
            done_now = today_habits.get(h["id"], False)
            pts_parts = []
            if h.get("hp"):  pts_parts.append(f"+{h['hp']} HP")
            if h.get("exp"): pts_parts.append(f"+{h['exp']} EXP")
            month_count = get_habit_history_month(h["id"])
            label = f"{h['name']}   `{'  '.join(pts_parts)}`  ·  *{month_count}x bulan ini*"

            new_val = st.checkbox(label, value=done_now, key=f"cb_{h['id']}")
            if new_val != done_now:
                set_today_habit(D, h["id"], new_val)
                if new_val:
                    if h.get("hp"):  D["hp"]  = min(100, D["hp"] + h["hp"])
                    if h.get("exp"): D["exp"] += h["exp"]
                    D["total_habits_done"] = D.get("total_habits_done", 0) + 1
                    # Update habit history
                    D["habit_history"][h["id"]] = D["habit_history"].get(h["id"], 0) + 1
                else:
                    if h.get("hp"):  D["hp"]  = max(0, D["hp"] - h["hp"])
                    if h.get("exp"): D["exp"] = max(0, D["exp"] - h["exp"])
                    D["total_habits_done"] = max(0, D.get("total_habits_done", 0) - 1)
                    D["habit_history"][h["id"]] = max(0, D["habit_history"].get(h["id"], 0) - 1)

                # Check achievements after each habit change
                new_ach = check_achievements(D)
                for ach_id in new_ach:
                    ach = next((a for a in ACHIEVEMENTS if a["id"] == ach_id), None)
                    if ach:
                        notify(f"{ach['icon']} Achievement unlocked: {ach['name']}!")

                persist()
                st.rerun()

    # ── Custom habit manager ──
    with st.expander("➕ Tambah / Hapus Habit Custom"):
        st.markdown("**Tambah habit baru:**")
        nc1, nc2, nc3 = st.columns([2, 1, 1])
        new_name = nc1.text_input("Nama habit", key="new_habit_name", label_visibility="collapsed", placeholder="Nama habit baru")
        new_hp   = nc2.number_input("HP", min_value=0, max_value=50, value=5, key="new_habit_hp", label_visibility="collapsed")
        new_exp  = nc3.number_input("EXP", min_value=0, max_value=50, value=0, key="new_habit_exp", label_visibility="collapsed")
        new_core = st.checkbox("Habit wajib (core — kena penalti jika skip)", key="new_habit_core")

        if st.button("Tambah Habit", key="btn_add_habit"):
            if new_name.strip():
                # Generate unique id
                new_id = f"custom_{new_name.lower().replace(' ','_')}_{len(D['custom_habits'])}"
                D["custom_habits"].append({
                    "id":   new_id,
                    "name": new_name.strip(),
                    "cat":  "Custom",
                    "hp":   new_hp,
                    "exp":  new_exp,
                    "core": new_core
                })
                persist()
                st.success(f"Habit '{new_name}' ditambahkan!")
                st.rerun()
            else:
                st.error("Nama habit tidak boleh kosong.")

        if D.get("custom_habits"):
            st.markdown("**Hapus habit custom:**")
            for i, ch in enumerate(D["custom_habits"]):
                col_h, col_del = st.columns([4, 1])
                col_h.markdown(f"`{ch['name']}` — +{ch['hp']} HP +{ch['exp']} EXP")
                if col_del.button("🗑️", key=f"del_habit_{i}"):
                    D["custom_habits"].pop(i)
                    persist()
                    st.rerun()

    st.divider()

    # ── Reset hari baru ──
    if st.button("🔄 Reset Hari Baru", use_container_width=True, type="primary"):
        all_h    = get_all_habits(D)
        core_ids = [h["id"] for h in all_h if h.get("core")]
        today_h  = get_today_habits(D)
        all_core_done = all(today_h.get(hid, False) for hid in core_ids)
        today_key = str(date.today())

        # Track sholat streak
        if today_h.get("sholat", False):
            D["sholat_streak"] = D.get("sholat_streak", 0) + 1
        else:
            D["sholat_streak"] = 0

        if all_core_done:
            prev_level = get_level(D["hp"], D["exp"])[0]["level"]
            D["streak"] += 1
            if D["streak"] > D["best_streak"]:
                D["best_streak"] = D["streak"]
            D["week_days"][today_key] = "done"

            # Streak rewards
            if D["streak"] == 3:
                D["kupon"] += 30
                notify("🔥 Streak 3 hari! +30 kupon")
            elif D["streak"] == 7:
                D["kupon"] += 75
                notify("⚡ Streak 7 hari! +75 kupon")
            elif D["streak"] == 30:
                D["kupon"] += 300
                notify("💎 Streak 30 hari! +300 kupon")
            if D.get("sholat_streak", 0) == 7:
                D["kupon"] += 50
                notify("🕌 Sholat streak 7 hari! +50 kupon")

            # Level up detection
            new_level = get_level(D["hp"], D["exp"])[0]["level"]
            if new_level > prev_level:
                D["level_history"].append({
                    "level": new_level,
                    "date": today_key,
                    "name": get_level(D["hp"], D["exp"])[0]["name"]
                })
                st.session_state["levelup_banner"] = new_level
                notify(f"🎉 LEVEL UP! Kamu sekarang Level {new_level}!")

            st.success(f"✅ Hari sempurna! Streak: {D['streak']} hari")
        else:
            done_count = sum(1 for hid in core_ids if today_h.get(hid, False))
            D["week_days"][today_key] = "partial" if done_count >= len(core_ids) // 2 else "miss"
            D["streak"] = 0

            # Penalti habit fisik core yang skip
            for h in all_h:
                if h["cat"] == "Fisik Core" and not today_h.get(h["id"], False):
                    D["hp"] = max(0, D["hp"] - round(h.get("hp", 0) * 0.5))
            if not today_h.get("belajar", False):
                D["exp"] = max(0, D["exp"] - 10)

            st.warning("⚠️ Streak terputus. Penalti diterapkan.")

        # Check achievements
        new_ach = check_achievements(D)
        for ach_id in new_ach:
            ach = next((a for a in ACHIEVEMENTS if a["id"] == ach_id), None)
            if ach:
                notify(f"{ach['icon']} Achievement: {ach['name']}!")

        persist()
        st.rerun()

    # Level up banner (shown once after level up)
    if st.session_state.get("levelup_banner"):
        lv = st.session_state.levelup_banner
        lv_info = next((l for l in LEVELS if l["level"] == lv), None)
        if lv_info:
            st.markdown(f"""
            <div class="levelup-banner">
                {lv_info['avatar']} LEVEL UP! Selamat, kamu sekarang Level {lv} — {lv_info['name']}! {lv_info['avatar']}
            </div>""", unsafe_allow_html=True)
        del st.session_state["levelup_banner"]

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — KEUANGAN
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.metric("💰 Saldo Gold", f"{D['gold']} Gold", f"= {fmt_rp(D['gold'] * 1000)}")
    st.caption("1 Gold = Rp1.000")
    st.divider()

    # Pemasukan
    st.markdown('<div class="section-title">Catat Pendapatan</div>', unsafe_allow_html=True)
    ca, cb = st.columns([2, 1])
    inc_amt  = ca.number_input("inc_amt", min_value=0, step=1000,
                               label_visibility="collapsed", placeholder="Nominal (Rp)", key="inc_amt")
    inc_desc = cb.text_input("inc_desc", label_visibility="collapsed",
                              placeholder="Keterangan", key="inc_desc")
    if st.button("✅ Catat Pemasukan", use_container_width=True):
        if inc_amt > 0:
            g = round(inc_amt / 1000)
            st.session_state.D["gold"] += g
            st.session_state.D["transactions"].insert(0, {
                "type": "in", "desc": inc_desc or "Pendapatan",
                "amt": int(inc_amt), "gold": g,
                "date": str(date.today()),
                "time": datetime.now().strftime("%H:%M"),
                "cat": "Pendapatan"
            })
            new_ach = check_achievements(st.session_state.D)
            for ach_id in new_ach:
                ach = next((a for a in ACHIEVEMENTS if a["id"] == ach_id), None)
                if ach: notify(f"{ach['icon']} Achievement: {ach['name']}!")
            persist()
            notify(f"+{g} Gold — {inc_desc or 'Pendapatan'}")
            st.rerun()
        else:
            st.error("Nominal harus lebih dari 0.")

    st.divider()

    # Pengeluaran
    st.markdown('<div class="section-title">Catat Pengeluaran</div>', unsafe_allow_html=True)
    cc, cd = st.columns([2, 1])
    exp_amt = cc.number_input("exp_amt", min_value=0, step=1000,
                               label_visibility="collapsed", placeholder="Nominal (Rp)", key="exp_amt")
    exp_cat = cd.selectbox("exp_cat", EXPENSE_CATS,
                            label_visibility="collapsed", key="exp_cat")
    if st.button("❌ Catat Pengeluaran", use_container_width=True):
        if exp_amt > 0:
            g = round(exp_amt / 1000)
            st.session_state.D["gold"] = max(0, st.session_state.D["gold"] - g)
            st.session_state.D["transactions"].insert(0, {
                "type": "out", "desc": exp_cat,
                "amt": int(exp_amt), "gold": g,
                "date": str(date.today()),
                "time": datetime.now().strftime("%H:%M"),
                "cat": exp_cat
            })
            persist()
            notify(f"-{g} Gold — {exp_cat}")
            st.rerun()
        else:
            st.error("Nominal harus lebih dari 0.")

    st.divider()

    # Budget monitor
    st.markdown('<div class="section-title">Monitor Budget Bulan Ini</div>', unsafe_allow_html=True)
    this_month = date.today().strftime("%Y-%m")
    for cat, budget in BUDGET.items():
        spent = sum(
            t["amt"] for t in D["transactions"]
            if t["type"] == "out" and t.get("desc") == cat and t["date"].startswith(this_month)
        )
        pct = min(1.0, spent / budget) if budget > 0 else 0.0
        icon = "🔴" if spent > budget else "🟢"
        col_b1, col_b2 = st.columns([3, 1])
        col_b1.markdown(f"{icon} **{cat}**")
        col_b2.markdown(f"<div style='text-align:right;font-size:13px'>{fmt_rp(spent)} / {fmt_rp(budget)}</div>", unsafe_allow_html=True)
        st.progress(pct)

    # Pie chart pengeluaran bulan ini
    st.divider()
    st.markdown('<div class="section-title">Grafik Pengeluaran Bulan Ini</div>', unsafe_allow_html=True)
    cat_totals = defaultdict(int)
    for t in D["transactions"]:
        if t["type"] == "out" and t["date"].startswith(this_month):
            cat_totals[t.get("desc", "Lainnya")] += t["amt"]

    if cat_totals:
        fig_pie = go.Figure(go.Pie(
            labels=list(cat_totals.keys()),
            values=list(cat_totals.values()),
            hole=0.45,
            marker=dict(colors=px.colors.sequential.Purples[-len(cat_totals):]),
            textinfo="label+percent",
            textfont=dict(color="#e0e0f0", size=12),
        ))
        fig_pie.update_layout(
            paper_bgcolor="#0f0f1a", plot_bgcolor="#0f0f1a",
            font=dict(color="#e0e0f0"),
            showlegend=False, margin=dict(t=20, b=20, l=20, r=20),
            height=280
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.caption("Belum ada data pengeluaran bulan ini.")

    # Riwayat transaksi
    st.divider()
    st.markdown('<div class="section-title">Riwayat Transaksi</div>', unsafe_allow_html=True)
    if not D["transactions"]:
        st.caption("Belum ada transaksi.")
    else:
        for t in D["transactions"][:25]:
            sign  = "+" if t["type"] == "in" else "-"
            color = "#34d399" if t["type"] == "in" else "#f87171"
            st.markdown(
                f'<div class="tx-row">'
                f'<span style="color:#888">{t["date"]} {t.get("time","")} · {t["desc"]}</span>'
                f'<span style="color:{color};font-weight:600">{sign}{t["gold"]} Gold</span>'
                f'</div>',
                unsafe_allow_html=True
            )

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — MINGGUAN
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    # Heatmap GitHub-style (12 minggu terakhir)
    st.markdown('<div class="section-title">Heatmap Konsistensi (12 Minggu)</div>', unsafe_allow_html=True)
    heatmap_data = build_heatmap_data()

    # Render heatmap sebagai HTML grid
    weeks: list[list] = []
    current_week: list = []
    for i in range(84):
        d_obj = date.today() - timedelta(days=83 - i)
        if d_obj.weekday() == 0 and current_week:
            weeks.append(current_week)
            current_week = []
        current_week.append((d_obj, heatmap_data.get(str(d_obj), "#1a1a2e")))
    if current_week:
        weeks.append(current_week)

    html_grid = '<div style="display:flex;gap:3px;flex-wrap:nowrap;overflow-x:auto;padding:4px 0">'
    for week in weeks:
        html_grid += '<div style="display:flex;flex-direction:column;gap:3px">'
        for d_obj, color in week:
            html_grid += f'<div title="{d_obj}" style="width:12px;height:12px;border-radius:2px;background:{color}"></div>'
        html_grid += '</div>'
    html_grid += '</div>'
    html_grid += '<div style="font-size:11px;color:#555;margin-top:6px">⬜ Kosong &nbsp; 🟣 Sebagian &nbsp; 🟣 Penuh</div>'
    st.markdown(html_grid, unsafe_allow_html=True)

    st.divider()

    # Streak info
    col_s1, col_s2, col_s3 = st.columns(3)
    col_s1.metric("🔥 Streak", f"{D['streak']} hari")
    col_s2.metric("🏆 Terbaik", f"{D['best_streak']} hari")
    col_s3.metric("🕌 Sholat", f"{D.get('sholat_streak', 0)} hari")

    st.caption("Reward: 3 hari +30 | 7 hari +75 | 30 hari +300 | Sholat 7 hari +50 poin kupon")

    st.divider()

    # Misi mingguan
    st.markdown('<div class="section-title">Misi Bonus Mingguan</div>', unsafe_allow_html=True)
    week_start = str(date.today() - timedelta(days=date.today().weekday()))
    all_missions = get_all_missions(D)

    for m in all_missions:
        mk       = f"{week_start}_{m['id']}"
        done_now = D["missions"].get(mk, False)
        pts_parts = []
        if m.get("hp"):    pts_parts.append(f"+{m['hp']} HP")
        if m.get("exp"):   pts_parts.append(f"+{m['exp']} EXP")
        pts_parts.append(f"+{m['kupon']} kupon")

        new_val = st.checkbox(
            f"{m['name']}   `{'  '.join(pts_parts)}`",
            value=done_now, key=f"mis_{mk}"
        )
        if new_val != done_now:
            D["missions"][mk] = new_val
            if new_val:
                if m.get("hp"):  D["hp"]    = min(100, D["hp"] + m["hp"])
                if m.get("exp"): D["exp"]  += m["exp"]
                D["kupon"] += m["kupon"]
                notify(f"Misi {m['name']} selesai! +{m['kupon']} kupon")
            else:
                if m.get("hp"):  D["hp"]   = max(0, D["hp"] - m["hp"])
                if m.get("exp"): D["exp"]  = max(0, D["exp"] - m["exp"])
                D["kupon"] = max(0, D["kupon"] - m["kupon"])
            persist()
            st.rerun()

    # Custom mission manager
    with st.expander("➕ Tambah / Hapus Misi Custom"):
        nm1, nm2, nm3, nm4 = st.columns([2, 1, 1, 1])
        m_name  = nm1.text_input("m_name",  label_visibility="collapsed", placeholder="Nama misi", key="new_m_name")
        m_hp    = nm2.number_input("m_hp",   min_value=0, max_value=100, value=20, label_visibility="collapsed", key="new_m_hp")
        m_exp   = nm3.number_input("m_exp",  min_value=0, max_value=100, value=0,  label_visibility="collapsed", key="new_m_exp")
        m_kupon = nm4.number_input("m_kupon",min_value=0, max_value=200, value=20, label_visibility="collapsed", key="new_m_kupon")

        if st.button("Tambah Misi", key="btn_add_mission"):
            if m_name.strip():
                new_mid = f"custom_m_{m_name.lower().replace(' ','_')}_{len(D.get('custom_missions',[]))}"
                D.setdefault("custom_missions", []).append({
                    "id": new_mid, "name": m_name.strip(),
                    "hp": int(m_hp), "exp": int(m_exp), "kupon": int(m_kupon),
                    "penalty_hp": 0, "penalty_exp": 0
                })
                persist()
                st.success(f"Misi '{m_name}' ditambahkan!")
                st.rerun()
            else:
                st.error("Nama misi tidak boleh kosong.")

        if D.get("custom_missions"):
            st.markdown("**Hapus misi custom:**")
            for i, cm in enumerate(D["custom_missions"]):
                cmc, cmd = st.columns([4, 1])
                cmc.markdown(f"`{cm['name']}` — +{cm['hp']} HP +{cm['exp']} EXP +{cm['kupon']} kupon")
                if cmd.button("🗑️", key=f"del_m_{i}"):
                    D["custom_missions"].pop(i)
                    persist()
                    st.rerun()

    # Monthly targets
    st.divider()
    st.markdown('<div class="section-title">Target Bulanan</div>', unsafe_allow_html=True)
    month_key = date.today().strftime("%Y-%m")
    D.setdefault("monthly_targets", {}).setdefault(month_key, {
        "belajar":    {"label": "Hari belajar", "target": 20, "current": 0},
        "olahraga":   {"label": "Hari olahraga", "target": 16, "current": 0},
        "sholat":     {"label": "Hari sholat penuh", "target": 30, "current": 0},
    })

    # Auto-update target dari data habit
    mt = D["monthly_targets"][month_key]
    mt["belajar"]["current"]  = sum(1 for ds, dh in D["habits"].items() if ds.startswith(month_key) and dh.get("belajar", False))
    mt["olahraga"]["current"] = sum(1 for ds, dh in D["habits"].items() if ds.startswith(month_key) and any(dh.get(h, False) for h in ["pushup","pullup","plank","stretching"]))
    mt["sholat"]["current"]   = sum(1 for ds, dh in D["habits"].items() if ds.startswith(month_key) and dh.get("sholat", False))

    for tid, t in mt.items():
        pct_t = min(1.0, t["current"] / t["target"]) if t["target"] > 0 else 0
        tc1, tc2 = st.columns([3, 1])
        tc1.markdown(f"**{t['label']}**")
        tc2.markdown(f"<div style='text-align:right;font-size:13px;color:#a78bfa'>{t['current']} / {t['target']}</div>", unsafe_allow_html=True)
        st.progress(pct_t)

    persist()  # save auto-updated targets

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — STATISTIK
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-title">Konsistensi Habit per Minggu (8 Minggu)</div>', unsafe_allow_html=True)

    # Build weekly habit count data
    weekly_labels = []
    weekly_done   = []
    all_h_count   = len(get_all_habits(D))

    for w in range(7, -1, -1):
        week_s = date.today() - timedelta(days=date.today().weekday() + w * 7)
        week_e = week_s + timedelta(days=6)
        label  = week_s.strftime("%d/%m")
        count  = sum(1 for ds, dh in D["habits"].items()
                     if week_s <= date.fromisoformat(ds) <= week_e
                     and sum(dh.values()) > 0)
        weekly_labels.append(label)
        weekly_done.append(count)

    fig_bar = go.Figure(go.Bar(
        x=weekly_labels, y=weekly_done,
        marker=dict(
            color=weekly_done,
            colorscale=[[0, "#2a1a4a"], [1, "#a78bfa"]],
            line=dict(width=0)
        ),
        text=weekly_done, textposition="outside",
        textfont=dict(color="#a78bfa")
    ))
    fig_bar.update_layout(
        paper_bgcolor="#0f0f1a", plot_bgcolor="#0f0f1a",
        font=dict(color="#e0e0f0"),
        xaxis=dict(gridcolor="#1a1a2e", color="#888"),
        yaxis=dict(gridcolor="#1e1e35", color="#888", title="Hari aktif"),
        margin=dict(t=30, b=20, l=20, r=20), height=260,
        showlegend=False
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    # Habit frequency chart (top habits bulan ini)
    st.divider()
    st.markdown('<div class="section-title">Riwayat Habit Bulan Ini</div>', unsafe_allow_html=True)

    month_key2 = date.today().strftime("%Y-%m")
    habit_counts = {}
    all_h2 = get_all_habits(D)
    for h in all_h2:
        cnt = sum(1 for ds, dh in D["habits"].items()
                  if ds.startswith(month_key2) and dh.get(h["id"], False))
        if cnt > 0:
            habit_counts[h["name"]] = cnt

    if habit_counts:
        sorted_habits = sorted(habit_counts.items(), key=lambda x: x[1], reverse=True)
        names  = [x[0] for x in sorted_habits]
        counts = [x[1] for x in sorted_habits]

        fig_h = go.Figure(go.Bar(
            x=counts, y=names, orientation="h",
            marker=dict(
                color=counts,
                colorscale=[[0, "#2a1a4a"], [1, "#7c3aed"]],
                line=dict(width=0)
            ),
            text=counts, textposition="outside",
            textfont=dict(color="#a78bfa")
        ))
        fig_h.update_layout(
            paper_bgcolor="#0f0f1a", plot_bgcolor="#0f0f1a",
            font=dict(color="#e0e0f0"),
            xaxis=dict(gridcolor="#1e1e35", color="#888"),
            yaxis=dict(gridcolor="#0f0f1a", color="#c0c0d8", autorange="reversed"),
            margin=dict(t=10, b=20, l=10, r=40),
            height=max(200, len(names) * 28)
        )
        st.plotly_chart(fig_h, use_container_width=True)
    else:
        st.caption("Belum ada data habit bulan ini.")

    # Gold trend (30 hari terakhir)
    st.divider()
    st.markdown('<div class="section-title">Tren Gold (30 Hari Terakhir)</div>', unsafe_allow_html=True)

    gold_by_day: dict[str, int] = defaultdict(int)
    running = 0
    for t in reversed(D["transactions"]):
        day = t["date"]
        if t["type"] == "in":
            gold_by_day[day] += t["gold"]
        else:
            gold_by_day[day] -= t["gold"]

    last30 = [(date.today() - timedelta(days=29 - i)) for i in range(30)]
    gold_running = []
    cumulative   = 0
    for d_obj in last30:
        cumulative += gold_by_day.get(str(d_obj), 0)
        gold_running.append(cumulative)

    fig_gold = go.Figure(go.Scatter(
        x=[str(d) for d in last30],
        y=gold_running,
        fill="tozeroy",
        fillcolor="rgba(124,58,237,0.15)",
        line=dict(color="#a78bfa", width=2),
        mode="lines"
    ))
    fig_gold.update_layout(
        paper_bgcolor="#0f0f1a", plot_bgcolor="#0f0f1a",
        font=dict(color="#e0e0f0"),
        xaxis=dict(gridcolor="#1e1e35", color="#888", showticklabels=False),
        yaxis=dict(gridcolor="#1e1e35", color="#888", title="Gold"),
        margin=dict(t=10, b=20, l=20, r=20), height=200
    )
    st.plotly_chart(fig_gold, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — REVIEW
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    # Stat summary
    cur_lv3, nxt_lv3, total3 = get_level(D["hp"], D["exp"])
    st.markdown(f"""
    <div class="char-card">
        <div class="avatar-ring">{cur_lv3['avatar']}</div>
        <div class="level-badge">Level {cur_lv3['level']} — {cur_lv3['name']}</div>
        <div style="color:#888;font-size:13px">Total stat: {total3}</div>
    </div>
    """, unsafe_allow_html=True)

    r1, r2, r3, r4 = st.columns(4)
    r1.metric("❤️ HP",      D["hp"])
    r2.metric("🧠 EXP",     D["exp"])
    r3.metric("💰 Gold",    D["gold"])
    r4.metric("🎟️ Kupon",  D["kupon"])

    # Level history
    if D.get("level_history"):
        st.divider()
        st.markdown('<div class="section-title">Riwayat Level Up</div>', unsafe_allow_html=True)
        for lh in reversed(D["level_history"]):
            lv_info = next((l for l in LEVELS if l["level"] == lh["level"]), None)
            icon = lv_info["avatar"] if lv_info else "⭐"
            st.markdown(f"{icon} **Level {lh['level']} — {lh.get('name','')}** · `{lh['date']}`")

    st.divider()

    # Achievements
    st.markdown('<div class="section-title">Achievements</div>', unsafe_allow_html=True)
    unlocked_ids = set(D.get("achievements", []))
    unlocked_count = len(unlocked_ids)
    st.caption(f"{unlocked_count} / {len(ACHIEVEMENTS)} unlocked")

    for a in ACHIEVEMENTS:
        is_unlocked = a["id"] in unlocked_ids
        border_class = "ach-card unlocked" if is_unlocked else "ach-card"
        opacity = "1" if is_unlocked else "0.35"
        st.markdown(f"""
        <div class="{border_class}" style="opacity:{opacity}">
            <span style="font-size:22px">{a['icon']}</span>
            <div>
                <div style="font-weight:600;font-size:14px;color:{'#a78bfa' if is_unlocked else '#888'}">{a['name']}</div>
                <div style="font-size:12px;color:#666">{a['desc']}</div>
            </div>
            {'<span style="margin-left:auto;font-size:11px;color:#7c3aed;font-weight:600">UNLOCKED</span>' if is_unlocked else ''}
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # Tukar kupon — THE FIX: always read/write through st.session_state.D
    st.markdown('<div class="section-title">Tukar Kupon Reward</div>', unsafe_allow_html=True)

    ck1, ck2 = st.columns(2)
    for i, c in enumerate(COUPONS):
        col = ck1 if i % 2 == 0 else ck2
        with col:
            # Read fresh from session state every render
            kupon_now = st.session_state.D["kupon"]
            can_redeem = kupon_now >= c["pts"]

            st.markdown(f"""
            <div class="coupon-card {'can-redeem' if can_redeem else ''}">
                <div style="font-size:20px">{'🎟️' if can_redeem else '🔒'}</div>
                <div style="font-weight:600;color:{'#a78bfa' if can_redeem else '#555'};margin:4px 0">{c['name']}</div>
                <div style="font-size:12px;color:#888">{c['pts']} poin</div>
                <div style="font-size:13px;color:#34d399;font-weight:600">{c['value']}</div>
            </div>
            """, unsafe_allow_html=True)

            btn_label = f"Tukar {c['name']}" if can_redeem else f"{c['pts'] - kupon_now} poin lagi"
            if st.button(btn_label, key=f"rd_{c['id']}", disabled=not can_redeem, use_container_width=True):
                # Directly mutate session state dict and save
                st.session_state.D["kupon"] -= c["pts"]
                st.session_state.D["total_redeems"] = st.session_state.D.get("total_redeems", 0) + 1
                st.session_state.D["redeem_log"].insert(0, {
                    "name": c["name"], "pts": c["pts"],
                    "value": c["value"], "date": str(date.today())
                })
                new_ach = check_achievements(st.session_state.D)
                for ach_id in new_ach:
                    ach = next((a for a in ACHIEVEMENTS if a["id"] == ach_id), None)
                    if ach: notify(f"{ach['icon']} Achievement: {ach['name']}!")
                save(st.session_state.D)  # explicit save
                st.success(f"✅ Kupon '{c['name']}' berhasil ditukar! Sisa: {st.session_state.D['kupon']} poin")
                st.rerun()

    # Riwayat penukaran
    st.divider()
    st.markdown('<div class="section-title">Riwayat Penukaran</div>', unsafe_allow_html=True)
    rl = st.session_state.D.get("redeem_log", [])
    if not rl:
        st.caption("Belum ada penukaran.")
    else:
        for r in rl[:10]:
            st.markdown(
                f'<div class="tx-row">'
                f'<span style="color:#888">{r["date"]} · {r["name"]}</span>'
                f'<span style="color:#f87171;font-weight:600">-{r["pts"]} poin ({r["value"]})</span>'
                f'</div>',
                unsafe_allow_html=True
            )

    st.divider()

    # Data management
    st.markdown('<div class="section-title">Data</div>', unsafe_allow_html=True)
    st.download_button(
        "💾 Export Backup (JSON)",
        data=json.dumps(st.session_state.D, indent=2, ensure_ascii=False),
        file_name=f"habitrpg_backup_{date.today()}.json",
        mime="application/json",
        use_container_width=True
    )

    with st.expander("⚠️ Reset Data"):
        st.warning("Semua data akan dihapus permanen.")
        if st.button("Konfirmasi Reset Semua Data", type="secondary"):
            st.session_state.D = default_state()
            save(st.session_state.D)
            st.success("Data direset.")
            st.rerun()
