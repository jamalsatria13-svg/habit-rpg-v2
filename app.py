"""
app.py - Habit RPG Streamlit application.
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
    HABIT_CATEGORY_ORDER,
    LEVELS,
    check_achievements,
    date_key,
    default_state,
    get_all_habits,
    get_all_missions,
    get_level,
    get_today_habits,
    get_unlocked_habits,
    get_week_key,
    import_data,
    load,
    now_wib,
    run_due_resets,
    save,
    set_today_habit,
    today_wib,
)


st.set_page_config(
    page_title="Habit RPG",
    page_icon="⚔️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

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
    border-radius:10px;
    padding:12px 10px !important;
}
[data-testid="stMetricLabel"] { color:#888 !important; font-size:12px !important; }
[data-testid="stMetricValue"] { color:#e0e0f0 !important; font-size:22px !important; }
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
    next_text = f"Total: {total} / {next_level['threshold']} -> Level {next_level['level']}" if next_level else "Level Maksimal"
    st.markdown(
        f"""
        <div class="char-card">
            <div class="avatar-ring">{current['avatar']}</div>
            <div class="level-badge">Level {current['level']} - {current['name']}</div>
            <div style="font-size:13px;color:#9b9bb8">{next_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if next_level:
        pct = min(1.0, (total - current["threshold"]) / (next_level["threshold"] - current["threshold"]))
        st.progress(pct)


def month_count(habit_id: str) -> int:
    month = today_wib().strftime("%Y-%m")
    return sum(1 for ds, dh in D.get("habits", {}).items() if ds.startswith(month) and dh.get(habit_id, False))


def build_heatmap() -> list[tuple[date, str]]:
    color = {"done": "#7c3aed", "partial": "#4a2a7a", "miss": "#3a1a1a", "none": "#1a1a2e"}
    result = []
    for i in range(84):
        day = today_wib() - timedelta(days=83 - i)
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
        notify(f"Level up: Level {current['level']} - {current['name']}")


previous_level = get_level(D["hp"], D["exp"])[0]["level"]
reset_summaries = run_due_resets(D)
if reset_summaries:
    maybe_record_level_up(previous_level)
    for summary in reset_summaries:
        if summary["type"] == "daily":
            notify(f"Reset harian {summary['date']}: HP {summary['hp_delta']:+}, EXP {summary['exp_delta']:+}")
        if summary["type"] == "weekly":
            notify(f"Reset mingguan {summary['week']}: HP {summary['hp_delta']:+}, Kupon {summary['kupon_delta']:+}")
        for msg in summary.get("messages", []):
            notify(msg)
    for aid in check_achievements(D):
        ach = next((a for a in ACHIEVEMENTS if a["id"] == aid), None)
        if ach:
            notify(f"Achievement: {ach['name']}")
    persist()

show_notifications()

tab_harian, tab_mingguan, tab_statistik, tab_review = st.tabs(["Harian", "Mingguan", "Statistik", "Review"])


with tab_harian:
    col_shift_1, col_shift_2 = st.columns(2)
    with col_shift_1:
        if st.button("Shift Pagi", type="primary" if D["shift"] == "Pagi" else "secondary", use_container_width=True):
            D["shift"] = "Pagi"
            persist()
            st.rerun()
    with col_shift_2:
        if st.button("Shift Malam", type="primary" if D["shift"] == "Malam" else "secondary", use_container_width=True):
            D["shift"] = "Malam"
            persist()
            st.rerun()

    st.caption(f"{D['shift']} | {now_wib().strftime('%A, %d %B %Y %H:%M')} WIB")
    render_character(D)

    metric_hp, metric_exp, metric_kupon = st.columns(3)
    metric_hp.metric("HP", D["hp"])
    metric_exp.metric("EXP", D["exp"])
    metric_kupon.metric("Kupon", D["kupon"])

    st.divider()

    today_habits = get_today_habits(D)
    active_habits = get_unlocked_habits(D)

    for category in HABIT_CATEGORY_ORDER:
        items = [habit for habit in active_habits if habit["cat"] == category]
        if not items:
            continue
        st.markdown(f'<div class="cat-title">{category}</div>', unsafe_allow_html=True)
        for habit in items:
            current_value = bool(today_habits.get(habit["id"], False))
            new_value = st.checkbox(habit["name"], value=current_value, key=f"cb_{date_key()}_{habit['id']}")
            if new_value != current_value:
                set_today_habit(D, habit["id"], new_value)
                persist()
                st.rerun()

    with st.expander("Tambah / Hapus Habit Custom"):
        hc1, hc2, hc3 = st.columns([2, 1, 1])
        new_name = hc1.text_input("Nama", key="custom_habit_name", label_visibility="collapsed", placeholder="Nama habit")
        new_hp = hc2.number_input("HP", min_value=0, max_value=50, value=5, key="custom_habit_hp", label_visibility="collapsed")
        new_exp = hc3.number_input("EXP", min_value=0, max_value=50, value=0, key="custom_habit_exp", label_visibility="collapsed")
        new_hp_pen = hc2.number_input("Pen HP", min_value=0, max_value=20, value=3, key="custom_habit_hp_pen", label_visibility="collapsed")
        new_exp_pen = hc3.number_input("Pen EXP", min_value=0, max_value=20, value=1, key="custom_habit_exp_pen", label_visibility="collapsed")
        if st.button("Tambah Habit", key="add_custom_habit"):
            name = new_name.strip()
            if name:
                hid = f"custom_{name.lower().replace(' ', '_')}_{len(D.get('custom_habits', []))}"
                D.setdefault("custom_habits", []).append({
                    "id": hid,
                    "name": name,
                    "cat": "Custom",
                    "hp": int(new_hp),
                    "exp": int(new_exp),
                    "hp_pen": int(new_hp_pen),
                    "exp_pen": int(new_exp_pen),
                    "unlock_level": 1,
                })
                persist()
                st.rerun()
        for i, habit in enumerate(D.get("custom_habits", [])):
            row_name, row_action = st.columns([4, 1])
            row_name.markdown(f"**{habit['name']}**")
            if row_action.button("Hapus", key=f"delete_custom_habit_{i}"):
                D["custom_habits"].pop(i)
                persist()
                st.rerun()


with tab_mingguan:
    st.markdown('<div class="sec">Heatmap Konsistensi</div>', unsafe_allow_html=True)
    weeks: list[list[tuple[date, str]]] = []
    current_week: list[tuple[date, str]] = []
    for day, color in build_heatmap():
        if day.weekday() == 0 and current_week:
            weeks.append(current_week)
            current_week = []
        current_week.append((day, color))
    if current_week:
        weeks.append(current_week)

    grid = '<div style="display:flex;gap:3px;overflow-x:auto;padding:4px 0">'
    for week in weeks:
        grid += '<div style="display:flex;flex-direction:column;gap:3px">'
        for day, color in week:
            grid += f'<div title="{day.isoformat()}" style="width:12px;height:12px;border-radius:2px;background:{color}"></div>'
        grid += "</div>"
    grid += "</div>"
    st.markdown(grid, unsafe_allow_html=True)

    st.divider()
    streak_1, streak_2, streak_3 = st.columns(3)
    streak_1.metric("Streak Harian", f"{D.get('streak', 0)} hari")
    streak_2.metric("Streak Terbaik", f"{D.get('best_streak', 0)} hari")
    streak_3.metric("Faith Streak", f"{D.get('faith_streak', 0)} hari")

    week_key = get_week_key()
    D.setdefault("missions", {})
    if not isinstance(D["missions"].get(week_key), dict):
        D["missions"][week_key] = {}
    weekly_missions = D["missions"].setdefault(week_key, {})

    st.divider()
    st.markdown('<div class="sec">Misi Mingguan</div>', unsafe_allow_html=True)
    for mission in get_all_missions(D):
        old_flat_key = f"{week_key}_{mission['id']}"
        if old_flat_key in D["missions"]:
            weekly_missions[mission["id"]] = bool(D["missions"].pop(old_flat_key))
        done = bool(weekly_missions.get(mission["id"], False))
        new_done = st.checkbox(mission["name"], value=done, key=f"mission_{week_key}_{mission['id']}")
        if new_done != done:
            weekly_missions[mission["id"]] = new_done
            hp_reward = int(mission.get("hp", 50))
            kupon_reward = int(mission.get("kupon", 20))
            if new_done:
                D["hp"] += hp_reward
                D["kupon"] += kupon_reward
                notify(f"Misi selesai: {mission['name']}")
            else:
                D["hp"] = max(0, D["hp"] - hp_reward)
                D["kupon"] = max(0, D["kupon"] - kupon_reward)
            persist()
            st.rerun()

    with st.expander("Tambah / Hapus Misi Custom"):
        mc1, mc2, mc3 = st.columns([2, 1, 1])
        mission_name = mc1.text_input("Nama misi", key="custom_mission_name", label_visibility="collapsed", placeholder="Nama misi")
        mission_hp = mc2.number_input("HP", min_value=0, max_value=200, value=50, key="custom_mission_hp", label_visibility="collapsed")
        mission_kupon = mc3.number_input("Kupon", min_value=0, max_value=200, value=20, key="custom_mission_kupon", label_visibility="collapsed")
        if st.button("Tambah Misi", key="add_custom_mission"):
            name = mission_name.strip()
            if name:
                mid = f"custom_m_{name.lower().replace(' ', '_')}_{len(D.get('custom_missions', []))}"
                D.setdefault("custom_missions", []).append({"id": mid, "name": name, "hp": int(mission_hp), "exp": 0, "kupon": int(mission_kupon)})
                persist()
                st.rerun()
        for i, mission in enumerate(D.get("custom_missions", [])):
            row_name, row_action = st.columns([4, 1])
            row_name.markdown(f"**{mission['name']}**")
            if row_action.button("Hapus", key=f"delete_custom_mission_{i}"):
                D["custom_missions"].pop(i)
                persist()
                st.rerun()

    st.divider()
    st.markdown('<div class="sec">Kewajiban Mingguan</div>', unsafe_allow_html=True)
    obligations = D.setdefault("obligations", {}).setdefault(week_key, {})
    for obligation in DEFAULT_OBLIGATIONS:
        done = bool(obligations.get(obligation["id"], False))
        new_done = st.checkbox(obligation["name"], value=done, key=f"obligation_{week_key}_{obligation['id']}")
        if new_done != done:
            obligations[obligation["id"]] = new_done
            persist()
            st.rerun()

    st.divider()
    st.markdown('<div class="sec">Target Bulanan</div>', unsafe_allow_html=True)
    month_key = today_wib().strftime("%Y-%m")
    targets = D.setdefault("monthly_targets", {}).setdefault(month_key, {})
    defaults = {
        "kuliah": {"label": "Hari kuliah", "target": 20, "current": 0},
        "fisik": {"label": "Hari fisik lengkap", "target": 20, "current": 0},
        "faith": {"label": "Hari sholat 5 waktu", "target": 30, "current": 0},
    }
    for key, value in defaults.items():
        targets.setdefault(key, value.copy())
    faith_ids = ["subuh", "dzuhur", "asyar", "magrib", "isya"]
    targets["kuliah"]["current"] = sum(1 for ds, dh in D["habits"].items() if ds.startswith(month_key) and dh.get("kuliah", False))
    targets["fisik"]["current"] = sum(1 for ds, dh in D["habits"].items() if ds.startswith(month_key) and dh.get("pushup_akhir", False))
    targets["faith"]["current"] = sum(1 for ds, dh in D["habits"].items() if ds.startswith(month_key) and all(dh.get(fid, False) for fid in faith_ids))
    for target in targets.values():
        pct = min(1.0, target["current"] / target["target"]) if target["target"] else 0
        label_col, count_col = st.columns([3, 1])
        label_col.markdown(f"**{target['label']}**")
        count_col.markdown(f"<div style='text-align:right;color:#a78bfa'>{target['current']} / {target['target']}</div>", unsafe_allow_html=True)
        st.progress(pct)
    persist()


with tab_statistik:
    st.markdown('<div class="sec">Konsistensi Harian 8 Minggu</div>', unsafe_allow_html=True)
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
    st.plotly_chart(fig_week, use_container_width=True)

    st.divider()
    st.markdown('<div class="sec">Frekuensi Habit Bulan Ini</div>', unsafe_allow_html=True)
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
        st.plotly_chart(fig_habits, use_container_width=True)
    else:
        st.caption("Belum ada data habit bulan ini.")


with tab_review:
    render_character(D)
    rv1, rv2, rv3 = st.columns(3)
    rv1.metric("HP", D["hp"])
    rv2.metric("EXP", D["exp"])
    rv3.metric("Kupon", D["kupon"])

    if D.get("level_history"):
        st.divider()
        st.markdown('<div class="sec">Riwayat Level Up</div>', unsafe_allow_html=True)
        for item in reversed(D["level_history"][-10:]):
            st.markdown(f"**Level {item['level']} - {item.get('name', '')}** · `{item['date']}`")

    st.divider()
    st.markdown('<div class="sec">Achievements</div>', unsafe_allow_html=True)
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
    st.markdown('<div class="sec">Ambil Reward</div>', unsafe_allow_html=True)
    reward_col_1, reward_col_2 = st.columns(2)
    for index, coupon in enumerate(COUPONS):
        column = reward_col_1 if index % 2 == 0 else reward_col_2
        with column:
            cost = int(coupon.get("cost", coupon.get("pts", 0)))
            can_redeem = D["kupon"] >= cost
            st.markdown(
                f"""
                <div class="coupon-card {'can-redeem' if can_redeem else ''}">
                    <div style="font-weight:800;color:{'#c4b5fd' if can_redeem else '#777'}">{coupon['name']}</div>
                    <div style="font-size:12px;color:#888">{cost} kupon</div>
                    <div style="font-size:13px;color:#34d399;font-weight:800">{coupon['value']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            button_label = f"Ambil {coupon['name']}" if can_redeem else f"Butuh {cost - D['kupon']} kupon lagi"
            if st.button(button_label, key=f"redeem_{coupon['id']}", disabled=not can_redeem, use_container_width=True):
                D["kupon"] -= cost
                D["total_redeems"] = D.get("total_redeems", 0) + 1
                D.setdefault("redeem_log", []).insert(0, {
                    "name": coupon["name"],
                    "cost": cost,
                    "value": coupon["value"],
                    "date": date_key(),
                })
                for aid in check_achievements(D):
                    ach = next((a for a in ACHIEVEMENTS if a["id"] == aid), None)
                    if ach:
                        notify(f"Achievement: {ach['name']}")
                persist()
                st.rerun()

    st.divider()
    st.markdown('<div class="sec">Riwayat Reward</div>', unsafe_allow_html=True)
    redeem_log = D.get("redeem_log", [])
    if redeem_log:
        for item in redeem_log[:10]:
            cost = item.get("cost", item.get("pts", 0))
            st.markdown(
                f'<div class="tx-row"><span style="color:#888">{item["date"]} · {item["name"]}</span>'
                f'<span style="color:#f87171;font-weight:800">-{cost} kupon ({item["value"]})</span></div>',
                unsafe_allow_html=True,
            )
    else:
        st.caption("Belum ada reward yang diambil.")

    st.divider()
    st.markdown('<div class="sec">Data</div>', unsafe_allow_html=True)
    st.download_button(
        "Export Backup (JSON)",
        data=json.dumps(D, indent=2, ensure_ascii=False),
        file_name=f"habitrpg_backup_{date_key()}.json",
        mime="application/json",
        use_container_width=True,
    )
    uploaded = st.file_uploader("Pilih file backup .json", type=["json"], key="import_file")
    if uploaded is not None and st.button("Konfirmasi Import Data", use_container_width=True):
        try:
            restored = import_data(uploaded.read().decode("utf-8"))
            st.session_state.D = restored
            save(st.session_state.D)
            st.success("Data berhasil diimport.")
            st.rerun()
        except json.JSONDecodeError:
            st.error("File JSON tidak valid.")
        except Exception as exc:
            st.error(f"Gagal import: {exc}")

    with st.expander("Reset Semua Data"):
        st.warning("Semua data akan dihapus permanen.")
        if st.button("Konfirmasi Reset", use_container_width=True):
            st.session_state.D = default_state()
            save(st.session_state.D)
            st.rerun()
