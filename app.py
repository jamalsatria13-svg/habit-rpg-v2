"""
app.py - Habit RPG Streamlit application with Enhanced RPG Icons and Expanded Heatmap.
Run with: python -m streamlit run app.py
"""

from __future__ import annotations

import json
import os
import sys
from datetime import date, timedelta

import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from core import (
    ACHIEVEMENTS,
    COUPONS,
    DEFAULT_OBLIGATIONS,
    LEVELS,
    check_achievements,
    date_key,
    default_state,
    get_all_habits,
    get_all_missions,
    get_level,
    get_ordered_daily_habits,
    get_today_habits,
    get_unlocked_habits,
    get_week_key,
    load,
    now_wib,
    run_due_resets,
    save,
    set_today_habit,
    today_wib,
    fmt_rp,
)

st.set_page_config(
    page_title="Habit RPG ⚔️",
    page_icon="⚔️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Custom CSS styling tailored for the RPG theme
st.markdown(
    """
<style>
html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"], .main {
    background:#0f0f1a !important;
    color:#e0e0f0 !important;
}
[data-testid="stSidebar"] { background:#13131f !important; }
.stTabs [data-baseweb="tab-list"] {
    background:linear-gradient(135deg,#17172a,#22223c);
    border:1px solid #2d2d4d;
    border-radius:14px;
    padding:5px;
    gap:6px;
    box-shadow:0 10px 28px rgba(0,0,0,.22);
}
.stTabs [data-baseweb="tab"] {
    min-height:42px;
    padding:8px 14px;
    background:transparent;
    color:#9b9bb8 !important;
    border-radius:10px;
    font-weight:700;
    font-size:13px;
    letter-spacing:0;
}
.stTabs [data-baseweb="tab"]:hover {
    background:#252540;
    color:#f4f0ff !important;
}
.stTabs [aria-selected="true"] {
    background:linear-gradient(135deg,#7c3aed,#a78bfa) !important;
    color:#fff !important;
    box-shadow:0 8px 18px rgba(124,58,237,.28);
}
[data-testid="stMetric"] {
    background:#1a1a2e;
    border:1px solid #2a2a45;
    border-radius:8px;
    padding:8px 6px !important;
}
[data-testid="stMetricLabel"] { color:#888 !important; font-size:10px !important; }
[data-testid="stMetricValue"] { color:#e0e0f0 !important; font-size:16px !important; }
.st-key-stat_row_harian [data-testid="stHorizontalBlock"],
.st-key-stat_row_review [data-testid="stHorizontalBlock"],
.st-key-shift_row [data-testid="stHorizontalBlock"],
.st-key-streak_row [data-testid="stHorizontalBlock"] {
    flex-wrap:nowrap !important;
    gap:6px !important;
}
.st-key-stat_row_harian [data-testid="stColumn"],
.st-key-stat_row_review [data-testid="stColumn"],
.st-key-shift_row [data-testid="stColumn"],
.st-key-streak_row [data-testid="stColumn"] {
    min-width:0 !important;
    width:auto !important;
    flex:1 1 0 !important;
}
.stButton > button {
    background:#1a1a2e;
    color:#c4b5fd;
    border:1px solid #3a3a5c;
    border-radius:8px;
    font-weight:700;
}
.stButton > button:hover {
    background:#252540;
    border-color:#a78bfa;
    color:#fff;
}
.stButton > button[kind="primary"] {
    background:linear-gradient(135deg,#7c3aed,#a78bfa);
    color:#fff;
    border:none;
}
.stTextInput input, .stNumberInput input, [data-baseweb="select"] {
    background:#1a1a2e !important;
    color:#e0e0f0 !important;
    border-color:#2a2a45 !important;
    border-radius:8px !important;
}
.stCheckbox label {
    color:#d6d3ea !important;
    font-size:15px;
}
hr { border-color:#2a2a45 !important; }
.stProgress > div > div > div {
    background:linear-gradient(90deg,#7c3aed,#a78bfa) !important;
}
[data-testid="stAlert"] { border-radius:10px !important; }
.char-card {
    background:linear-gradient(135deg,#1a1a2e 0%,#252540 100%);
    border:1px solid #3a3a5c;
    border-radius:14px;
    padding:18px;
    text-align:center;
    margin-bottom:1rem;
}
.avatar-ring {
    width:72px;
    height:72px;
    border-radius:50%;
    background:linear-gradient(135deg,#7c3aed,#a78bfa);
    display:flex;
    align-items:center;
    justify-content:center;
    margin:0 auto 12px;
    color:#fff;
    font-size:20px;
    font-weight:900;
    box-shadow:0 0 20px rgba(167,139,250,.35);
}
.level-badge {
    display:inline-block;
    background:#272747;
    color:#c4b5fd;
    padding:4px 12px;
    border-radius:20px;
    font-size:12px;
    font-weight:800;
    margin-bottom:8px;
}
.cat-title, .sec {
    font-size:11px;
    font-weight:800;
    color:#8b8bb2;
    text-transform:uppercase;
    letter-spacing:.08em;
    margin:1.15rem 0 .45rem;
}
.coupon-card, .ach-card {
    background:#1a1a2e;
    border:1px solid #2a2a45;
    border-radius:10px;
    padding:12px;
    margin-bottom:8px;
}
.coupon-card.can-redeem {
    border-color:#7c3aed;
    background:linear-gradient(135deg,#1a1535,#1e1a3a);
}
.ach-card {
    display:flex;
    gap:10px;
    align-items:center;
}
.ach-card.unlocked {
    border-color:#7c3aed;
    background:#1e1535;
}
.tx-row {
    display:flex;
    justify-content:space-between;
    gap:12px;
    padding:7px 0;
    border-bottom:1px solid #1e1e35;
    font-size:13px;
}
</style>
""",
    unsafe_allow_html=True,
)

if "D" not in st.session_state:
    st.session_state.D = load()
if "notifications" not in st.session_state:
    st.session_state.notifications = []

D = st.session_state.D

def persist() -> None:
    save(st.session_state.D)

def notify(message: str) -> None:
    st.session_state.notifications.append(message)

def show_notifications() -> None:
    for message in st.session_state.notifications:
        st.toast(message)
    st.session_state.notifications = []

def render_character(data: dict) -> None:
    current, next_level, total = get_level(data["hp"], data["exp"])
    
    # Logika pemetaan manual teks bawaan core ke emoji baru
    avatar_mapping = {
        "Lv1": "👶",
        "Lv2": "⚔️",
        "Lv3": "🛡️",
        "Lv4": "🔱",
        "Lv5": "👑"
    }
    display_avatar = avatar_mapping.get(current['avatar'], current['avatar'])

    if next_level:
        next_text = f"⚔️ Total Stat (HP+EXP): {total} / {next_level['threshold']} &rarr; Level {next_level['level']}"
        pct = min(1.0, (total - current["threshold"]) / (next_level["threshold"] - current["threshold"]))
    else:
        next_text = f"👑 Total Stat (HP+EXP): {total} | Level Maksimal"
        pct = 1.0

    level_quotes = {
        1: "Kamu adalah sampah. Bahkan tanggung jawab paling dasar pun kamu tinggalkan. Lantas untuk apa kamu berharap.",
        2: "Inilah awal dari perjalananmu. Memang berat tapi yakinlah bahwa ini jalan yang benar untuk tumbuh.",
        3: "Sekarang kamu adalah seorang pejuang. Rasa lelahmu tak seberapa dibanding rasa malu ketika sepelekan.",
        4: "Aku yakin sekarang tubuhmu sudah kuat, mentalmu sudah terbentuk. Namun seorang pendekar akan selalu mengasah kemampuannya untuk bersiap di medan perang.",
        5: "Kamu sekarang adalah JAMAL. Dan jamal sekarang tidak sepele, mampu bertanggung jawab, dan seseorang yang telah mengasah pedangnya. Jangan khianati pedangmu sendiri.",
    }
    quote_text = level_quotes.get(current["level"], "")

    st.markdown(
        f"""
        <div class="char-card" style="text-align:left;">
            <div style="display:flex; align-items:center; gap:14px; margin-bottom:10px;">
                <div class="avatar-ring" style="font-size: 32px; margin:0; flex-shrink:0;">{display_avatar}</div>
                <div style="font-size:16px;color:#c4b5fd;font-style:italic;line-height:1.4;">"{quote_text}"</div>
            </div>
            <div class="level-badge">🏆 Level {current['level']} - {current['name']}</div>
            <div style="font-size:13px;color:#9b9bb8;margin-bottom:8px;">{next_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.progress(pct)
    st.markdown(
        f"<div style='text-align:right;font-size:11px;color:#8b8bb2;margin-top:-6px;'>{pct * 100:.0f}%</div>",
        unsafe_allow_html=True,
    )

def build_heatmap() -> list[tuple[date, str]]:
    color = {
        "full": "#f5f5fa",   # putih: 100% misi harian selesai
        "gain": "#3b82f6",   # biru: ada yang terlewat, tapi stat bersih naik
        "loss": "#7c3aed",   # ungu: ada yang dikerjakan, tapi stat bersih turun
        "miss": "#ef4444",   # merah: semua misi harian terlewat
        "none": "#1a1a2e",   # belum ada data hari itu
    }
    today = today_wib()
    monday_this_week = today - timedelta(days=today.weekday())  # Senin minggu ini
    start_date = monday_this_week - timedelta(weeks=11)  # mundur 12 minggu kalender penuh
    result = []
    for i in range(84):
        day = start_date + timedelta(days=i)
        result.append((day, color.get(D.get("week_days", {}).get(day.isoformat(), "none"), "#1a1a2e")))
    return result

def maybe_record_level_up(previous_level: int) -> None:
    current = get_level(D["hp"], D["exp"])[0]
    if current["level"] > previous_level:
        D.setdefault("level_history", []).append({
            "level": current["level"],
            "name": current["name"],
            "date": date_key(),
        })
        notify(f"⚔️ Level up: Level {current['level']} - {current['name']}")

# Check and execute due resets
previous_level = get_level(D["hp"], D["exp"])[0]["level"]
reset_summaries = run_due_resets(D)
if reset_summaries:
    maybe_record_level_up(previous_level)
    for summary in reset_summaries:
        if summary["type"] == "daily":
            notify(f"🌅 Reset harian {summary['date']}: ❤️ HP {summary['hp_delta']:+}, ✨ EXP {summary['exp_delta']:+}")
        if summary["type"] == "weekly":
            notify(f"📅 Reset mingguan {summary['week']}: ❤️ HP {summary['hp_delta']:+}, 🪙 Kupon {summary['kupon_delta']:+}")
        for msg in summary.get("messages", []):
            notify(msg)
    for aid in check_achievements(D):
        ach = next((a for a in ACHIEVEMENTS if a["id"] == aid), None)
        if ach:
            notify(f"🏆 Achievement Unlocked: {ach['name']}")
    persist()

show_notifications()

tab_harian, tab_mingguan, tab_progres, tab_profil = st.tabs(["📅 Harian", "⚔️ Mingguan", "📊 Progres", "🏆 Profil"])

# ==================== TAB HARIAN ====================
with tab_harian:
    with st.container(key="shift_row"):
        col_shift_1, col_shift_2 = st.columns(2)
        with col_shift_1:
            # Added Sun emoji to Morning Shift
            if st.button("☀️ Shift Pagi", type="primary" if D["shift"] == "Pagi" else "secondary", width='stretch'):
                D["shift"] = "Pagi"
                persist()
                st.rerun()
        with col_shift_2:
            # Added Moon emoji to Night Shift
            if st.button("🌙 Shift Malam", type="primary" if D["shift"] == "Malam" else "secondary", width='stretch'):
                D["shift"] = "Malam"
                persist()
                st.rerun()

    st.caption(f"⚙️ {D['shift']} | 🕒 {now_wib().strftime('%A, %d %B %Y %H:%M')} WIB")
    st.divider()

    today_habits = get_today_habits(D)
    ordered_habits = get_ordered_daily_habits(D)

    for habit in ordered_habits:
        current_value = bool(today_habits.get(habit["id"], False))

        lvl_info = ""
        if "unlock_level" in habit and habit["unlock_level"] > 1:
            lvl_info = f" *(Lv. {habit['unlock_level']})*"

        label_text = f"{habit['name']}{lvl_info}"

        new_value = st.checkbox(label_text, value=current_value, key=f"cb_{date_key()}_{habit['id']}")
        if new_value != current_value:
            set_today_habit(D, habit["id"], new_value)
            persist()
            st.rerun()

# ==================== TAB MINGGUAN ====================
with tab_mingguan:
    week_key = get_week_key()
    D.setdefault("missions", {})
    if not isinstance(D["missions"].get(week_key), dict):
        D["missions"][week_key] = {}
    weekly_missions = D["missions"].setdefault(week_key, {})

    st.divider()
    st.markdown('<div class="sec" style="color:#34d399;">⭐ Misi Mingguan (Bonus Rewards)</div>', unsafe_allow_html=True)
    for mission in get_all_missions(D):
        old_flat_key = f"{week_key}_{mission['id']}"
        if old_flat_key in D["missions"]:
            weekly_missions[mission["id"]] = bool(D["missions"].pop(old_flat_key))
        done = bool(weekly_missions.get(mission["id"], False))
        
        hp_reward = int(mission.get("hp", 0))
        exp_reward = int(mission.get("exp", 0))
        kupon_reward = int(mission.get("kupon", 0))
        
        reward_desc = f" (❤️ +{hp_reward}, ✨ +{exp_reward}, 🪙 +{kupon_reward})"
        new_done = st.checkbox(f"{mission['name']}{reward_desc}", value=done, key=f"mission_{week_key}_{mission['id']}")
        
        if new_done != done:
            weekly_missions[mission["id"]] = new_done
            if new_done:
                D["hp"] += hp_reward
                D["exp"] += exp_reward
                D["kupon"] += kupon_reward
                notify(f"🔥 Misi selesai: {mission['name']}")
            else:
                D["hp"] = max(0, D["hp"] - hp_reward)
                D["exp"] = max(0, D["exp"] - exp_reward)
                D["kupon"] = max(0, D["kupon"] - kupon_reward)
            persist()
            st.rerun()

    with st.expander("➕ Tambah / Hapus Misi Custom"):
        with st.form("form_custom_mission", clear_on_submit=True):
            mc1, mc2, mc3, mc4 = st.columns([2, 1, 1, 1])
            mission_name = mc1.text_input("Nama Misi", placeholder="Nama misi baru")
            mission_hp = mc2.number_input("❤️ HP", min_value=0, max_value=200, value=50)
            mission_exp = mc3.number_input("✨ EXP", min_value=0, max_value=200, value=20)
            mission_kupon = mc4.number_input("🪙 Kupon", min_value=0, max_value=200, value=20)
            
            submit_mission = st.form_submit_button("🚀 Tambah Misi", width='stretch')
            if submit_mission:
                name = mission_name.strip()
                if name:
                    mid = f"custom_m_{name.lower().replace(' ', '_')}_{len(D.get('custom_missions', []))}"
                    D.setdefault("custom_missions", []).append({
                        "id": mid, 
                        "name": name, 
                        "hp": int(mission_hp), 
                        "exp": int(mission_exp), 
                        "kupon": int(mission_kupon)
                    })
                    persist()
                    st.rerun()
                    
        st.write("---")
        for i, mission in enumerate(D.get("custom_missions", [])):
            row_name, row_action = st.columns([4, 1])
            row_name.markdown(f"**{mission['name']}** <span style='color:#777; font-size:12px;'>(❤️ +{mission.get('hp',0)}, ✨ +{mission.get('exp',0)}, 🪙 +{mission.get('kupon',0)})</span>", unsafe_allow_html=True)
            if row_action.button("🗑️ Hapus", key=f"delete_custom_mission_{mission['id']}"):
                D["custom_missions"].pop(i)
                persist()
                st.rerun()

    st.divider()
    st.markdown('<div class="sec" style="color:#f59e0b;">⚠️ Kewajiban Mingguan (Penalti Berbahaya)</div>', unsafe_allow_html=True)
    obligations = D.setdefault("obligations", {}).setdefault(week_key, {})
    for obligation in DEFAULT_OBLIGATIONS:
        done = bool(obligations.get(obligation["id"], False))
        penalty_desc = f" *(Gagal: 💔 -{obligation['pen_hp']} HP, 🪙 -{obligation['pen_kupon']} Kupon)*"
        new_done = st.checkbox(f"{obligation['name']}{penalty_desc}", value=done, key=f"obligation_{week_key}_{obligation['id']}")
        if new_done != done:
            obligations[obligation["id"]] = new_done
            persist()
            st.rerun()

# ==================== TAB PROGRES ====================
with tab_progres:
    st.markdown('<div class="sec">🔥 Streak</div>', unsafe_allow_html=True)
    with st.container(key="streak_row"):
        streak_1, streak_2 = st.columns(2)
        streak_1.metric("🔥 Streak Harian", f"{D.get('streak', 0)} hari")
        streak_2.metric("👑 Streak Terbaik", f"{D.get('best_streak', 0)} hari")

    st.divider()
    st.markdown('<div class="sec">🟩 Heatmap Konsistensi</div>', unsafe_allow_html=True)
    heatmap_days = build_heatmap()  # 84 hari = 12 kolom x 7 baris
    columns_12x7: list[list[tuple[date, str]]] = [
        heatmap_days[i:i + 7] for i in range(0, len(heatmap_days), 7)
    ]

    # --- HEATMAP GRID 12x7 ---
    grid = '<div style="display:flex;gap:5px;overflow-x:auto;padding:6px 0">'
    for col in columns_12x7:
        grid += '<div style="display:flex;flex-direction:column;gap:5px">'
        for day, color in col:
            grid += f'<div title="{day.isoformat()}" style="width:18px;height:18px;border-radius:3px;background:{color}"></div>'
        grid += "</div>"
    grid += "</div>"
    st.markdown(grid, unsafe_allow_html=True)

    st.divider()
    st.markdown('<div class="sec">📈 Perolehan Stat per Hari</div>', unsafe_allow_html=True)
    daily_stats = D.get("daily_stats", {})
    today_key = date_key()
    today_is_live = today_key not in daily_stats  # hari ini belum "ditutup" oleh reset harian

    live_gain, live_penalty = 0, 0
    if today_is_live:
        today_habits_now = D["habits"].get(today_key, {})
        unlocked_now = get_unlocked_habits(D)
        live_gain = sum(
            int(h.get("hp", 0)) + int(h.get("exp", 0))
            for h in unlocked_now if today_habits_now.get(h["id"], False)
        )
        live_penalty = sum(
            int(h.get("hp_pen", 0)) + int(h.get("exp_pen", 0))
            for h in unlocked_now if not today_habits_now.get(h["id"], False)
        )

    display_days = sorted(set(daily_stats.keys()) | ({today_key} if today_is_live else set()))[-30:]

    chart_labels, gain_values, penalty_values = [], [], []
    for ds in display_days:
        is_today_live_point = today_is_live and ds == today_key
        entry = daily_stats.get(ds, {})
        gain_values.append(live_gain if is_today_live_point else int(entry.get("gain", 0)))
        penalty_values.append(live_penalty if is_today_live_point else int(entry.get("penalty", 0)))
        label = date.fromisoformat(ds).strftime("%d/%m")
        chart_labels.append(f"{label}*" if is_today_live_point else label)

    if today_is_live:
        st.caption("* Hari ini masih berjalan — angka final baru terkunci setelah reset harian berikutnya.")

    if gain_values:
        fig_gain = go.Figure(go.Scatter(
            x=chart_labels,
            y=gain_values,
            mode="lines+markers",
            line=dict(color="#a78bfa", width=2),
            marker=dict(color="#7c3aed", size=6),
            fill="tozeroy",
            fillcolor="rgba(124,58,237,0.15)",
        ))
        fig_gain.update_layout(
            paper_bgcolor="#0f0f1a",
            plot_bgcolor="#0f0f1a",
            font=dict(color="#e0e0f0"),
            xaxis=dict(gridcolor="#1a1a2e", color="#888"),
            yaxis=dict(gridcolor="#1e1e35", color="#888", title="HP+EXP diperoleh"),
            margin=dict(t=20, b=20, l=20, r=20),
            height=260,
            showlegend=False,
        )
        st.plotly_chart(fig_gain, width='stretch')
    else:
        st.caption("Belum ada data harian untuk ditampilkan.")

    st.divider()
    st.markdown('<div class="sec">📉 Penalti Stat per Hari</div>', unsafe_allow_html=True)
    if penalty_values:
        fig_penalty = go.Figure(go.Scatter(
            x=chart_labels,
            y=penalty_values,
            mode="lines+markers",
            line=dict(color="#ef4444", width=2),
            marker=dict(color="#ef4444", size=6),
            fill="tozeroy",
            fillcolor="rgba(239,68,68,0.15)",
        ))
        fig_penalty.update_layout(
            paper_bgcolor="#0f0f1a",
            plot_bgcolor="#0f0f1a",
            font=dict(color="#e0e0f0"),
            xaxis=dict(gridcolor="#1a1a2e", color="#888"),
            yaxis=dict(gridcolor="#1e1e35", color="#888", title="HP+EXP hilang"),
            margin=dict(t=20, b=20, l=20, r=20),
            height=260,
            showlegend=False,
        )
        st.plotly_chart(fig_penalty, width='stretch')
    else:
        st.caption("Belum ada data harian untuk ditampilkan.")

    st.divider()
    st.markdown('<div class="sec">📊 Konsistensi Harian 8 Minggu</div>', unsafe_allow_html=True)
    labels, counts = [], []
    for offset in range(7, -1, -1):
        start = today_wib() - timedelta(days=today_wib().weekday() + offset * 7)
        end = start + timedelta(days=6)
        labels.append(start.strftime("%d/%m"))
        counts.append(sum(1 for ds, dh in D["habits"].items() if start <= date.fromisoformat(ds) <= end and any(dh.values())))
    fig_week = go.Figure(go.Bar(
        x=labels,
        y=counts,
        marker=dict(color=counts, colorscale=[[0, "#2a1a4a"], [1, "#a78bfa"]]),
        text=counts,
        textposition="outside",
        textfont=dict(color="#a78bfa"),
    ))
    fig_week.update_layout(
        paper_bgcolor="#0f0f1a",
        plot_bgcolor="#0f0f1a",
        font=dict(color="#e0e0f0"),
        xaxis=dict(gridcolor="#1a1a2e", color="#888"),
        yaxis=dict(gridcolor="#1e1e35", color="#888", title="Hari aktif"),
        margin=dict(t=30, b=20, l=20, r=20),
        height=260,
        showlegend=False,
    )
    st.plotly_chart(fig_week, width='stretch')

    st.divider()
    st.markdown('<div class="sec">🔥 Frekuensi Habit Bulan Ini</div>', unsafe_allow_html=True)
    month = today_wib().strftime("%Y-%m")
    habit_counts = {
        habit["name"]: sum(1 for ds, dh in D["habits"].items() if ds.startswith(month) and dh.get(habit["id"], False))
        for habit in get_all_habits(D)
    }
    habit_counts = {name: count for name, count in habit_counts.items() if count > 0}
    if habit_counts:
        sorted_counts = sorted(habit_counts.items(), key=lambda item: item[1], reverse=True)
        fig_habits = go.Figure(go.Bar(
            x=[count for _, count in sorted_counts],
            y=[name for name, _ in sorted_counts],
            orientation="h",
            marker=dict(color=[count for _, count in sorted_counts], colorscale=[[0, "#2a1a4a"], [1, "#7c3aed"]]),
            text=[count for _, count in sorted_counts],
            textposition="outside",
            textfont=dict(color="#a78bfa"),
        ))
        fig_habits.update_layout(
            paper_bgcolor="#0f0f1a",
            plot_bgcolor="#0f0f1a",
            font=dict(color="#e0e0f0"),
            xaxis=dict(gridcolor="#1e1e35", color="#888"),
            yaxis=dict(color="#c0c0d8", autorange="reversed"),
            margin=dict(t=10, b=20, l=10, r=40),
            height=max(220, len(sorted_counts) * 30),
        )
        st.plotly_chart(fig_habits, width='stretch')
    else:
        st.caption("Belum ada data habit bulan ini.")

    st.divider()
    st.markdown('<div class="sec">📈 Target Bulanan</div>', unsafe_allow_html=True)
    month_key = today_wib().strftime("%Y-%m")
    targets = D.setdefault("monthly_targets", {}).setdefault(month_key, {})
    defaults = {
        "kuliah": {"label": "Hari kuliah", "target": 20, "current": 0},
        "fisik": {"label": "Hari fisik lengkap (Kumulatif)", "target": 20, "current": 0},
        "faith": {"label": "Hari sholat 5 waktu", "target": 30, "current": 0},
    }
    for key, value in defaults.items():
        targets.setdefault(key, value.copy())

    faith_ids = ["subuh", "dzuhur", "asyar", "magrib", "isya"]
    targets["kuliah"]["current"] = sum(1 for ds, dh in D["habits"].items() if ds.startswith(month_key) and dh.get("kuliah", False))

    total_physical_days = 0
    all_habits_pool = get_all_habits(D)
    physical_ids = [h["id"] for h in all_habits_pool if h.get("cat") == "Fisik Harian"]

    for ds, dh in D["habits"].items():
        if ds.startswith(month_key) and physical_ids:
            if any(dh.get(pid, False) for pid in physical_ids):
                total_physical_days += 1

    targets["fisik"]["current"] = total_physical_days
    targets["faith"]["current"] = sum(1 for ds, dh in D["habits"].items() if ds.startswith(month_key) and all(dh.get(fid, False) for fid in faith_ids))

    for target in targets.values():
        pct = min(1.0, target["current"] / target["target"]) if target["target"] else 0
        label_col, count_col = st.columns([3, 1])
        label_col.markdown(f"**{target['label']}**")
        count_col.markdown(f"<div style='text-align:right;color:#a78bfa'>{target['current']} / {target['target']}</div>", unsafe_allow_html=True)
        st.progress(pct)
    # NOTE: previously this called persist() unconditionally on every
    # render of this tab, which meant an extra Supabase write on every
    # single rerun even with no changes. monthly_targets are recomputed
    # every render anyway, so only persist if they actually changed.
    if D.get("monthly_targets") != st.session_state.get("_last_monthly_targets"):
        persist()
        st.session_state["_last_monthly_targets"] = json.loads(json.dumps(D.get("monthly_targets")))

# ==================== TAB PROFIL ====================
with tab_profil:
    render_character(D)
    with st.container(key="stat_row_review"):
        rv1, rv2, rv3 = st.columns(3)
        rv1.metric("❤️ HP", D["hp"])
        rv2.metric("✨ EXP", D["exp"])
        rv3.metric("🪙 Kupon", D["kupon"])

    if D.get("level_history"):
        st.divider()
        st.markdown('<div class="sec">📈 Riwayat Level Up</div>', unsafe_allow_html=True)
        for item in reversed(D["level_history"][-10:]):
            st.markdown(f"📈 **Level {item['level']} - {item.get('name', '')}** · `{item['date']}`")

    st.divider()
    st.markdown('<div class="sec">🏆 Achievements</div>', unsafe_allow_html=True)
    unlocked = set(D.get("achievements", []))
    st.caption(f"{len(unlocked)} / {len(ACHIEVEMENTS)} unlocked")
    for achievement in ACHIEVEMENTS:
        is_unlocked = achievement["id"] in unlocked
        css_class = "ach-card unlocked" if is_unlocked else "ach-card"
        opacity = "1" if is_unlocked else ".38"
        badge = '<span style="margin-left:auto;font-size:11px;color:#a78bfa;font-weight:800">UNLOCKED</span>' if is_unlocked else ""
        st.markdown(
            f"""
            <div class="{css_class}" style="opacity:{opacity}">
                <span style="font-size:18px">{achievement['icon']}</span>
                <div>
                    <div style="font-weight:800;color:#c4b5fd">{achievement['name']}</div>
                    <div style="font-size:12px;color:#777">{achievement['desc']}</div>
                </div>
                {badge}
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.divider()
    st.markdown('<div class="sec">🎟️ Ambil Reward</div>', unsafe_allow_html=True)
    reward_col_1, reward_col_2 = st.columns(2)
    for index, coupon in enumerate(COUPONS):
        column = reward_col_1 if index % 2 == 0 else reward_col_2
        with column:
            cost = int(coupon.get("cost", coupon.get("pts", 0)))
            can_redeem = D["kupon"] >= cost
            
            coupon_val = coupon['value']
            if isinstance(coupon_val, (int, float)):
                coupon_formatted_val = fmt_rp(coupon_val)
            else:
                coupon_formatted_val = str(coupon_val)

            # Added Icons inside HTML Coupon Card layout
            st.markdown(
                f"""
                <div class="coupon-card {'can-redeem' if can_redeem else ''}">
                    <div style="font-weight:800;color:{'#c4b5fd' if can_redeem else '#777'}">🎟️ {coupon['name']}</div>
                    <div style="font-size:12px;color:#888">🪙 {cost} kupon</div>
                    <div style="font-size:13px;color:#34d399;font-weight:800">💵 {coupon_formatted_val}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            button_label = f"🛒 Ambil {coupon['name']}" if can_redeem else f"🔒 Butuh {cost - D['kupon']} kupon"
            if st.button(button_label, key=f"redeem_{coupon['id']}", disabled=not can_redeem, width='stretch'):
                D["kupon"] -= cost
                D["total_redeems"] = D.get("total_redeems", 0) + 1
                D.setdefault("redeem_log", []).insert(0, {
                    "name": coupon["name"],
                    "cost": cost,
                    "value": coupon_formatted_val,
                    "date": date_key(),
                })
                for aid in check_achievements(D):
                    ach = next((a for a in ACHIEVEMENTS if a["id"] == aid), None)
                    if ach:
                        notify(f"🏆 Achievement Unlocked: {ach['name']}")
                persist()
                st.rerun()

    st.divider()
    st.markdown('<div class="sec">🧾 Riwayat Reward</div>', unsafe_allow_html=True)
    redeem_log = D.get("redeem_log", [])
    if redeem_log:
        for item in redeem_log[:10]:
            cost = item.get("cost", item.get("pts", 0))
            # Added dynamic transactional history row with currency and point logs
            st.markdown(
                f'<div class="tx-row"><span style="color:#888">🧾 {item["date"]} · {item["name"]}</span>'
                f'<span style="color:#f87171;font-weight:800">🪙 -{cost} kupon ({item["value"]})</span></div>',
                unsafe_allow_html=True,
            )
    else:
        st.caption("Belum ada reward yang diambil.")

    st.divider()
    with st.expander("🚨 Reset Semua Data"):
        st.warning("Semua data akan dihapus permanen.")
        if st.button("💥 Konfirmasi Reset", width='stretch'):
            st.session_state.D = default_state()
            save(st.session_state.D)
            st.rerun()
