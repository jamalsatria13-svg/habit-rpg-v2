"""
app.py — Habit RPG Streamlit application (v3).
Entry point: python -m streamlit run app.py
"""

import json
import sys
import os
import uuid
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import date, datetime, timedelta
from collections import defaultdict

# Pastikan core.py di direktori yang sama dapat diimport
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from core import (
    load, save, import_data, default_state,
    get_level, get_all_habits, get_all_missions,
    get_today_habits, set_today_habit, get_week_key,
    process_daily_reset, process_weekly_reset,
    check_achievements, fmt_rp,
    COUPONS, LEVELS, BUDGET, EXPENSE_CATS,
    ACHIEVEMENTS, DEFAULT_HABITS, DEFAULT_MISSIONS, DEFAULT_OBLIGATIONS,
    HABIT_CATEGORY_ORDER,
)

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Habit RPG",
    page_icon="sword",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ── DARK MODE CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"], .main {
    background-color: #0f0f1a !important; color: #e0e0f0 !important;
}
[data-testid="stSidebar"] { background-color: #13131f !important; }
.stTabs [data-baseweb="tab-list"] {
    background:#1a1a2e; border-radius:12px; padding:4px; gap:4px;
}
.stTabs [data-baseweb="tab"] {
    background:transparent; color:#888 !important;
    border-radius:8px; font-size:13px; font-weight:500;
}
.stTabs [aria-selected="true"] { background:#252540 !important; color:#a78bfa !important; }
[data-testid="stMetric"] {
    background:#1a1a2e; border:1px solid #2a2a45;
    border-radius:12px; padding:12px 10px !important;
}
[data-testid="stMetricLabel"] { color:#888 !important; font-size:12px !important; }
[data-testid="stMetricValue"] { color:#e0e0f0 !important; font-size:22px !important; }
.stButton > button {
    background:#1a1a2e; color:#a78bfa; border:1px solid #3a3a5c;
    border-radius:8px; font-weight:500; transition:all .15s;
}
.stButton > button:hover { background:#252540; border-color:#a78bfa; color:#fff; }
.stButton > button[kind="primary"] {
    background:linear-gradient(135deg,#7c3aed,#a78bfa); color:#fff; border:none;
}
.stButton > button[kind="primary"]:hover {
    background:linear-gradient(135deg,#6d28d9,#9061f9);
}
.stTextInput input, .stNumberInput input, [data-baseweb="select"] {
    background:#1a1a2e !important; color:#e0e0f0 !important;
    border-color:#2a2a45 !important; border-radius:8px !important;
}
.stCheckbox label { color:#c0c0d8 !important; font-size:14px; }
hr { border-color:#2a2a45 !important; }
.stProgress > div > div > div {
    background:linear-gradient(90deg,#7c3aed,#a78bfa) !important; border-radius:4px;
}
[data-testid="stAlert"] { border-radius:10px !important; }

/* ── Custom components ── */
.char-card {
    background:linear-gradient(135deg,#1a1a2e 0%,#252540 100%);
    border:1px solid #3a3a5c; border-radius:16px; padding:20px;
    text-align:center; margin-bottom:1rem; position:relative; overflow:hidden;
}
.char-card::before {
    content:''; position:absolute; top:-50%; left:-50%;
    width:200%; height:200%;
    background:radial-gradient(circle,rgba(167,139,250,0.05) 0%,transparent 60%);
}
.avatar-ring {
    width:80px; height:80px; border-radius:50%;
    background:linear-gradient(135deg,#7c3aed,#a78bfa);
    display:flex; align-items:center; justify-content:center;
    margin:0 auto 12px; font-size:36px;
    box-shadow:0 0 20px rgba(167,139,250,0.4);
}
.level-badge {
    display:inline-block;
    background:linear-gradient(135deg,#7c3aed,#a78bfa);
    color:#fff; padding:3px 12px; border-radius:20px;
    font-size:12px; font-weight:600; margin-bottom:8px;
}
.stat-bar-wrap { background:#252540; border-radius:6px; height:8px; overflow:hidden; margin-top:4px; }
.stat-bar-fill { height:100%; border-radius:6px; transition:width .4s ease; }
.cat-title {
    font-size:11px; font-weight:700; color:#7c7ca8;
    text-transform:uppercase; letter-spacing:.08em; margin:1rem 0 .4rem;
}
.ach-card {
    background:#1a1a2e; border:1px solid #2a2a45; border-radius:10px;
    padding:10px 12px; margin-bottom:6px; display:flex; gap:10px; align-items:center;
}
.ach-card.unlocked { border-color:#7c3aed; background:#1e1535; }
.coupon-card {
    background:#1a1a2e; border:1px solid #2a2a45;
    border-radius:12px; padding:14px; margin-bottom:8px; text-align:center;
}
.coupon-card.can-redeem {
    border-color:#7c3aed;
    background:linear-gradient(135deg,#1a1535,#1e1a3a);
}
.tx-row {
    display:flex; justify-content:space-between;
    padding:6px 0; border-bottom:1px solid #1e1e35; font-size:13px;
}
.sec { font-size:11px; font-weight:700; color:#7c7ca8;
    text-transform:uppercase; letter-spacing:.08em; margin:1.2rem 0 .6rem; }
.levelup-banner {
    background:linear-gradient(135deg,#7c3aed,#a78bfa);
    border-radius:12px; padding:16px; text-align:center;
    color:#fff; font-weight:700; font-size:18px; margin:1rem 0;
    animation:pulse 1s ease-in-out;
}
@keyframes pulse {
    0%{transform:scale(0.95);opacity:.7}
    50%{transform:scale(1.02);opacity:1}
    100%{transform:scale(1);opacity:1}
}
</style>
""", unsafe_allow_html=True)

# ── SESSION STATE INIT ────────────────────────────────────────────────────────
if "D" not in st.session_state:
    st.session_state.D = load()
if "notifications" not in st.session_state:
    st.session_state.notifications = []

D = st.session_state.D

# ── HELPERS ───────────────────────────────────────────────────────────────────
def persist() -> None:
    save(st.session_state.D)

def notify(msg: str) -> None:
    st.session_state.notifications.append(msg)

def show_notifications() -> None:
    for msg in st.session_state.notifications:
        st.toast(msg)
    st.session_state.notifications = []

def render_stat_bar(value: int, ref: int, color: str) -> str:
    """Render HTML progress bar. ref = nilai referensi untuk % tampilan."""
    pct = max(0, min(100, int((value / ref) * 100))) if ref > 0 else 0
    return (f'<div class="stat-bar-wrap">'
            f'<div class="stat-bar-fill" style="width:{pct}%;background:{color}"></div>'
            f'</div>')

def habit_month_count(habit_id: str) -> int:
    m = date.today().strftime("%Y-%m")
    return sum(
        1 for ds, dh in D.get("habits", {}).items()
        if ds.startswith(m) and dh.get(habit_id, False)
    )

def build_heatmap() -> list[tuple[date, str]]:
    COLOR = {"done":"#7c3aed","partial":"#4a2a7a","miss":"#3a1a1a","none":"#1a1a2e"}
    result = []
    for i in range(84):
        d = date.today() - timedelta(days=83 - i)
        result.append((d, COLOR.get(D["week_days"].get(str(d), "none"), "#1a1a2e")))
    return result

# ── AUTO DATE CHANGE & MISSED DAY AUTO-RESET ──────────────────────────────────
today_str = str(date.today())
last_d = D.get("last_date")

if last_d and last_d != today_str:
    # Auto-evaluasi & penalti jika user terlewat login di hari sebelumnya
    if D.get("last_reset") != last_d:
        auto_summary = process_daily_reset(D, target_date=last_d)
        notify(f"Auto-reset missed day ({last_d}): HP {auto_summary['hp_delta']}, EXP {auto_summary['exp_delta']}")
    
    D["last_date"] = today_str
    save(D)

show_notifications()

# ── TABS ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Harian", "Keuangan", "Mingguan", "Statistik", "Review"
])

# =============================================================================
# TAB 1 — HARIAN
# =============================================================================
with tab1:
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Shift Pagi", type="primary" if D["shift"]=="Pagi" else "secondary", use_container_width=True):
            D["shift"] = "Pagi"; persist(); st.rerun()
    with c2:
        if st.button("Shift Malam", type="primary" if D["shift"]=="Malam" else "secondary", use_container_width=True):
            D["shift"] = "Malam"; persist(); st.rerun()

    st.caption(f"**{D['shift']}** | {date.today().strftime('%A, %d %B %Y')}")

    # Character card
    cur_lv, nxt_lv, total_stat = get_level(D["hp"], D["exp"])
    pct_lv = 0.0
    if nxt_lv:
        pct_lv = max(0.0, min(1.0, (total_stat - cur_lv["threshold"]) / (nxt_lv["threshold"] - cur_lv["threshold"])))

    nxt_label = (f"Total: {total_stat} / {nxt_lv['threshold']} → Level {nxt_lv['level']}"
                 if nxt_lv else "Level Maksimal!")
    st.markdown(f"""
    <div class="char-card">
        <div class="avatar-ring">{cur_lv['avatar']}</div>
        <div class="level-badge">Level {cur_lv['level']} — {cur_lv['name']}</div>
        <div style="font-size:13px;color:#888;margin-bottom:12px">{nxt_label}</div>
    </div>""", unsafe_allow_html=True)
    if nxt_lv:
        st.progress(pct_lv)

    # Stat cards
    s1, s2, s3, s4 = st.columns(4)
    s1.metric("HP",    D["hp"])
    s2.metric("EXP",   D["exp"])
    s3.metric("Gold",  D["gold"])
    s4.metric("Kupon", D["kupon"])

    st.markdown(
        render_stat_bar(D["hp"],  max(D["hp"], 200),  "#ef4444") +
        render_stat_bar(D["exp"] % 500 or 1, 500,     "#8b5cf6") +
        render_stat_bar(min(D["gold"], 9000), 9000,   "#f59e0b"),
        unsafe_allow_html=True
    )

    st.divider()

    # Habit checklist
    today_habits = get_today_habits(D)
    all_habits   = get_all_habits(D)

    for cat in HABIT_CATEGORY_ORDER:
        cat_habits = [h for h in all_habits if h["cat"] == cat]
        if not cat_habits:
            continue
        st.markdown(f'<div class="cat-title">{cat}</div>', unsafe_allow_html=True)

        for h in cat_habits:
            done_now  = today_habits.get(h["id"], False)
            hp_r  = h.get("hp",  h.get("hp_reward",  0))
            exp_r = h.get("exp", h.get("exp_reward", 0))
            hp_p  = h.get("hp_pen",  0)
            exp_p = h.get("exp_pen", 0)
            pts   = []
            if hp_r:  pts.append(f"+{hp_r} HP")
            if exp_r: pts.append(f"+{exp_r} EXP")
            if hp_p:  pts.append(f"-{hp_p} HP jika skip")
            if exp_p: pts.append(f"-{exp_p} EXP jika skip")
            mc    = habit_month_count(h["id"])
            label = f"{h['name']}  `{'  |  '.join(pts)}`  · *{mc}x bulan ini*"

            new_val = st.checkbox(label, value=done_now, key=f"cb_{h['id']}")
            if new_val != done_now:
                set_today_habit(D, h["id"], new_val)
                persist()
                st.rerun()

    # Custom habit manager
    with st.expander("Tambah / Hapus Habit Custom"):
        nc1, nc2, nc3 = st.columns([2, 1, 1])
        new_name = nc1.text_input("Nama", key="nh_name", label_visibility="collapsed", placeholder="Nama habit")
        new_hp   = nc2.number_input("HP",  min_value=0, max_value=50, value=5, key="nh_hp",  label_visibility="collapsed")
        new_exp  = nc3.number_input("EXP", min_value=0, max_value=50, value=0, key="nh_exp", label_visibility="collapsed")
        new_hp_pen  = nc2.number_input("Pen HP",  min_value=0, max_value=20, value=3, key="nh_hpen", label_visibility="collapsed")
        new_exp_pen = nc3.number_input("Pen EXP", min_value=0, max_value=20, value=1, key="nh_epen", label_visibility="collapsed")

        if st.button("Tambah Habit", key="btn_add_habit"):
            name = new_name.strip()
            if name:
                hid = f"custom_{uuid.uuid4().hex[:8]}"
                D.setdefault("custom_habits", []).append({
                    "id": hid, "name": name, "cat": "Custom",
                    "hp": int(new_hp),  "exp": int(new_exp),
                    "hp_pen": int(new_hp_pen), "exp_pen": int(new_exp_pen),
                })
                # Clear session state keys
                for k in ["nh_name", "nh_hp", "nh_exp", "nh_hpen", "nh_epen"]:
                    st.session_state.pop(k, None)
                    
                persist()
                st.success(f"Habit '{name}' ditambahkan!")
                st.rerun()
            else:
                st.error("Nama tidak boleh kosong.")

        for i, ch in enumerate(D.get("custom_habits", [])):
            ch_c, ch_d = st.columns([4, 1])
            ch_c.markdown(f"`{ch['name']}` +{ch.get('hp',0)} HP +{ch.get('exp',0)} EXP")
            if ch_d.button("Hapus", key=f"del_h_{ch['id']}"):
                D["custom_habits"].pop(i)
                persist()
                st.rerun()

    st.divider()

    # Tombol Reset Hari Baru
    if st.button("Reset Hari Baru", use_container_width=True, type="primary"):
        prev_lv = get_level(D["hp"], D["exp"])[0]["level"]
        summary = process_daily_reset(st.session_state.D)

        if "sudah direset" in "".join(summary.get("messages", [])):
            st.info(summary["messages"][0])
        else:
            new_lv = get_level(st.session_state.D["hp"], st.session_state.D["exp"])[0]
            if new_lv["level"] > prev_lv:
                st.session_state.D["level_history"].append({
                    "level": new_lv["level"], "name": new_lv["name"], "date": str(date.today())
                })
                st.session_state["levelup_banner"] = new_lv["level"]

            for aid in check_achievements(st.session_state.D):
                ach = next((a for a in ACHIEVEMENTS if a["id"] == aid), None)
                if ach: notify(f"{ach['icon']} Achievement: {ach['name']}!")

            for msg in summary.get("messages", []):
                notify(msg)

            persist()
            delta_hp  = summary["hp_delta"]
            delta_exp = summary["exp_delta"]
            sign_hp   = "+" if delta_hp  >= 0 else ""
            sign_exp  = "+" if delta_exp >= 0 else ""
            st.success(f"Hari direset! HP {sign_hp}{delta_hp} | EXP {sign_exp}{delta_exp} | Streak: {st.session_state.D['streak']} hari")
            st.rerun()

    if st.session_state.get("levelup_banner"):
        lv = st.session_state.levelup_banner
        lv_info = next((l for l in LEVELS if l["level"] == lv), None)
        if lv_info:
            st.markdown(
                f'<div class="levelup-banner">'
                f'{lv_info["avatar"]} LEVEL UP! Level {lv} — {lv_info["name"]}!'
                f'</div>', unsafe_allow_html=True
            )
        del st.session_state["levelup_banner"]

# =============================================================================
# TAB 2 — KEUANGAN
# =============================================================================
with tab2:
    st.metric("Gold Saat Ini", f"{D['gold']} Gold", f"= {fmt_rp(D['gold'] * 1000)}")
    st.caption("1 Gold = Rp1.000")
    st.divider()

    # Pemasukan
    st.markdown('<div class="sec">Catat Pendapatan</div>', unsafe_allow_html=True)
    ca, cb = st.columns([2, 1])
    inc_amt  = ca.number_input("inc_amt", min_value=0, step=1000, label_visibility="collapsed", placeholder="Nominal (Rp)", key="inc_amt")
    inc_desc = cb.text_input("inc_desc", label_visibility="collapsed", placeholder="Keterangan", key="inc_desc")
    
    if st.button("Catat Pemasukan", use_container_width=True):
        if inc_amt > 0:
            g = round(inc_amt / 1000)
            st.session_state.D["gold"] += g
            st.session_state.D["transactions"].insert(0, {
                "type":"in", "desc": inc_desc or "Pendapatan",
                "amt": int(inc_amt), "gold": g, "date": str(date.today()), "time": datetime.now().strftime("%H:%M"),
            })
            for aid in check_achievements(st.session_state.D):
                ach = next((a for a in ACHIEVEMENTS if a["id"] == aid), None)
                if ach: notify(f"{ach['icon']} Achievement: {ach['name']}!")
            
            st.session_state.pop("inc_amt", None)
            st.session_state.pop("inc_desc", None)
            persist()
            notify(f"+{g} Gold masuk!")
            st.rerun()
        else:
            st.error("Nominal harus lebih dari 0.")

    st.divider()

    # Pengeluaran
    st.markdown('<div class="sec">Catat Pengeluaran</div>', unsafe_allow_html=True)
    cc, cd = st.columns([2, 1])
    exp_amt = cc.number_input("exp_amt", min_value=0, step=1000, label_visibility="collapsed", placeholder="Nominal (Rp)", key="exp_amt")
    exp_cat = cd.selectbox("exp_cat", EXPENSE_CATS, label_visibility="collapsed", key="exp_cat")
    
    if st.button("Catat Pengeluaran", use_container_width=True):
        if exp_amt > 0:
            g = round(exp_amt / 1000)
            st.session_state.D["gold"] = max(0, st.session_state.D["gold"] - g)
            st.session_state.D["transactions"].insert(0, {
                "type":"out", "desc": exp_cat,
                "amt": int(exp_amt), "gold": g, "date": str(date.today()), "time": datetime.now().strftime("%H:%M"),
            })
            
            st.session_state.pop("exp_amt", None)
            st.session_state.pop("exp_cat", None)
            persist()
            notify(f"-{g} Gold ({exp_cat})")
            st.rerun()
        else:
            st.error("Nominal harus lebih dari 0.")

    st.divider()

    # Budget monitor
    st.markdown('<div class="sec">Monitor Budget Bulan Ini</div>', unsafe_allow_html=True)
    this_month = date.today().strftime("%Y-%m")
    for cat, budget in BUDGET.items():
        spent = sum(t["amt"] for t in D["transactions"] if t["type"]=="out" and t.get("desc")==cat and t["date"].startswith(this_month))
        pct   = max(0.0, min(1.0, spent / budget)) if budget > 0 else 0.0
        icon  = "🔴" if spent > budget else "🟢"
        bc1, bc2 = st.columns([3, 1])
        bc1.markdown(f"{icon} **{cat}**")
        bc2.markdown(f"<div style='text-align:right;font-size:13px'>{fmt_rp(spent)} / {fmt_rp(budget)}</div>", unsafe_allow_html=True)
        st.progress(pct)

    st.divider()
    st.markdown('<div class="sec">Grafik Pengeluaran Bulan Ini</div>', unsafe_allow_html=True)
    cat_totals: dict[str, int] = defaultdict(int)
    for t in D["transactions"]:
        if t["type"]=="out" and t["date"].startswith(this_month):
            cat_totals[t.get("desc","Lainnya")] += t["amt"]

    if cat_totals:
        n_colors = max(len(cat_totals), 1)
        colors   = px.colors.sequential.Purples[-n_colors:] if n_colors <= 9 else px.colors.sequential.Purples
        fig_pie = go.Figure(go.Pie(
            labels=list(cat_totals.keys()), values=list(cat_totals.values()), hole=0.45,
            marker=dict(colors=colors), textinfo="label+percent", textfont=dict(color="#e0e0f0", size=12),
        ))
        fig_pie.update_layout(
            paper_bgcolor="#0f0f1a", plot_bgcolor="#0f0f1a", font=dict(color="#e0e0f0"), showlegend=False,
            margin=dict(t=20, b=20, l=20, r=20), height=280
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.caption("Belum ada data pengeluaran bulan ini.")

    st.divider()
    st.markdown('<div class="sec">Riwayat Transaksi</div>', unsafe_allow_html=True)
    if not D["transactions"]:
        st.caption("Belum ada transaksi.")
    else:
        for t in D["transactions"][:25]:
            sign  = "+" if t["type"]=="in" else "-"
            color = "#34d399" if t["type"]=="in" else "#f87171"
            st.markdown(
                f'<div class="tx-row">'
                f'<span style="color:#888">{t["date"]} {t.get("time","")} · {t["desc"]}</span>'
                f'<span style="color:{color};font-weight:600">{sign}{t["gold"]} Gold</span>'
                f'</div>', unsafe_allow_html=True
            )

# =============================================================================
# TAB 3 — MINGGUAN
# =============================================================================
with tab3:
    st.markdown('<div class="sec">Heatmap Konsistensi (12 Minggu)</div>', unsafe_allow_html=True)
    hmap = build_heatmap()
    weeks: list[list] = []
    cur_week: list    = []
    for d_obj, color in hmap:
        if d_obj.weekday() == 0 and cur_week:
            weeks.append(cur_week)
            cur_week = []
        cur_week.append((d_obj, color))
    if cur_week:
        weeks.append(cur_week)

    grid = '<div style="display:flex;gap:3px;overflow-x:auto;padding:4px 0">'
    for wk in weeks:
        grid += '<div style="display:flex;flex-direction:column;gap:3px">'
        for d_obj, color in wk:
            grid += f'<div title="{d_obj}" style="width:12px;height:12px;border-radius:2px;background:{color}"></div>'
        grid += '</div>'
    grid += '</div><div style="font-size:11px;color:#555;margin-top:4px">Ungu tua = penuh | Ungu muda = sebagian | Merah = miss</div>'
    st.markdown(grid, unsafe_allow_html=True)

    st.divider()

    sc1, sc2, sc3 = st.columns(3)
    sc1.metric("Streak Harian",  f"{D.get('streak', 0)} hari")
    sc2.metric("Streak Terbaik", f"{D.get('best_streak', 0)} hari")
    sc3.metric("Faith Streak",   f"{D.get('faith_streak', 0)} hari")
    st.caption("Reward: 3 hari +30 | 7 hari +75 | 30 hari +300 | Faith 7 hari +50 kupon")

    st.divider()

    st.markdown('<div class="sec">Misi Mingguan (+50 HP +20 kupon)</div>', unsafe_allow_html=True)
    week_key     = get_week_key()
    all_missions = get_all_missions(D)

    for m in all_missions:
        mk       = f"{week_key}_{m['id']}"
        done_now = D["missions"].get(mk, False)
        hp_r     = m.get("hp", 50)
        k_r      = m.get("kupon", 20)

        new_val = st.checkbox(f"{m['name']}   `+{hp_r} HP  +{k_r} kupon`", value=done_now, key=f"mis_{mk}")
        if new_val != done_now:
            D["missions"][mk] = new_val
            if new_val:
                D["hp"]    += hp_r
                D["kupon"] += k_r
                notify(f"Misi {m['name']} selesai! +{hp_r} HP +{k_r} kupon")
            else:
                D["hp"]    = max(0, D["hp"] - hp_r)
                D["kupon"] = max(0, D["kupon"] - k_r)
            persist()
            st.rerun()

    with st.expander("Tambah / Hapus Misi Custom"):
        nm1, nm2, nm3 = st.columns([2, 1, 1])
        m_name  = nm1.text_input("m_name", label_visibility="collapsed", placeholder="Nama misi", key="new_m_name")
        m_hp    = nm2.number_input("m_hp", min_value=0, max_value=200, value=50, label_visibility="collapsed", key="new_m_hp")
        m_kupon = nm3.number_input("m_kupon", min_value=0, max_value=200, value=20, label_visibility="collapsed", key="new_m_kupon")
        
        if st.button("Tambah Misi", key="btn_add_m"):
            name = m_name.strip()
            if name:
                mid = f"custom_m_{uuid.uuid4().hex[:8]}"
                D.setdefault("custom_missions", []).append({
                    "id": mid, "name": name, "hp": int(m_hp), "exp": 0, "kupon": int(m_kupon), "type": "misi"
                })
                st.session_state.pop("new_m_name", None)
                st.session_state.pop("new_m_hp", None)
                st.session_state.pop("new_m_kupon", None)
                persist()
                st.success(f"Misi '{name}' ditambahkan!")
                st.rerun()
            else:
                st.error("Nama tidak boleh kosong.")

        for i, cm in enumerate(D.get("custom_missions", [])):
            cmc, cmd = st.columns([4, 1])
            cmc.markdown(f"`{cm['name']}` +{cm['hp']} HP +{cm['kupon']} kupon")
            if cmd.button("Hapus", key=f"del_m_{cm['id']}"):
                D["custom_missions"].pop(i)
                persist()
                st.rerun()

    st.divider()

    st.markdown('<div class="sec">Kewajiban Mingguan (-30 HP -20 kupon jika tidak selesai)</div>', unsafe_allow_html=True)
    D.setdefault("obligations", {}).setdefault(week_key, {})

    for ob in DEFAULT_OBLIGATIONS:
        ob_done = D["obligations"][week_key].get(ob["id"], False)
        new_ob  = st.checkbox(f"{ob['name']}   `Penalti: -{ob['pen_hp']} HP  -{ob['pen_kupon']} kupon`", value=ob_done, key=f"ob_{week_key}_{ob['id']}")
        if new_ob != ob_done:
            D["obligations"][week_key][ob["id"]] = new_ob
            persist()
            st.rerun()

    st.divider()

    st.markdown('<div class="sec">Target Bulanan</div>', unsafe_allow_html=True)
    month_key = date.today().strftime("%Y-%m")
    D.setdefault("monthly_targets", {}).setdefault(month_key, {
        "kuliah":  {"label":"Hari kuliah",        "target":20, "current":0},
        "fisik":   {"label":"Hari fisik lengkap",  "target":20, "current":0},
        "faith":   {"label":"Hari sholat 5 waktu", "target":30, "current":0},
    })
    mt = D["monthly_targets"][month_key]
    faith_ids = ["subuh","dzuhur","asyar","magrib","isya"]
    mt["kuliah"]["current"] = sum(1 for ds, dh in D["habits"].items() if ds.startswith(month_key) and dh.get("kuliah", False))
    mt["fisik"]["current"]  = sum(1 for ds, dh in D["habits"].items() if ds.startswith(month_key) and all(dh.get(fid, False) for fid in ["pushup_awal","pullup_awal","plank"]))
    mt["faith"]["current"]  = sum(1 for ds, dh in D["habits"].items() if ds.startswith(month_key) and all(dh.get(fid, False) for fid in faith_ids))
    
    for tid, t in mt.items():
        pct_t = max(0.0, min(1.0, t["current"] / t["target"])) if t["target"] > 0 else 0.0
        tc1, tc2 = st.columns([3, 1])
        tc1.markdown(f"**{t['label']}**")
        tc2.markdown(f"<div style='text-align:right;font-size:13px;color:#a78bfa'>{t['current']} / {t['target']}</div>", unsafe_allow_html=True)
        st.progress(pct_t)
    persist()

    st.divider()

    if st.button("Reset Minggu Baru", use_container_width=True, type="primary"):
        summary_w = process_weekly_reset(st.session_state.D)
        persist()
        
        if "sudah direset" in "".join(summary_w.get("messages", [])):
            st.info(summary_w["messages"][0])
        else:
            if summary_w["messages"]:
                for msg in summary_w["messages"]:
                    notify(msg)
                st.warning(f"Minggu direset. Total penalti: {summary_w['hp_delta']} HP, {summary_w['kupon_delta']} kupon")
            else:
                st.success("Semua kewajiban selesai! Tidak ada penalti minggu ini.")
        st.rerun()

# =============================================================================
# TAB 4 — STATISTIK
# =============================================================================
with tab4:
    st.markdown('<div class="sec">Konsistensi Harian (8 Minggu)</div>', unsafe_allow_html=True)
    w_labels, w_counts = [], []
    for w in range(7, -1, -1):
        ws = date.today() - timedelta(days=date.today().weekday() + w * 7)
        we = ws + timedelta(days=6)
        w_labels.append(ws.strftime("%d/%m"))
        w_counts.append(sum(
            1 for ds, dh in D["habits"].items()
            if ws <= date.fromisoformat(ds) <= we and any(dh.values())
        ))

    fig_bar = go.Figure(go.Bar(
        x=w_labels, y=w_counts,
        marker=dict(color=w_counts, colorscale=[[0,"#2a1a4a"],[1,"#a78bfa"]], line=dict(width=0)),
        text=w_counts, textposition="outside", textfont=dict(color="#a78bfa")
    ))
    fig_bar.update_layout(
        paper_bgcolor="#0f0f1a", plot_bgcolor="#0f0f1a", font=dict(color="#e0e0f0"),
        xaxis=dict(gridcolor="#1a1a2e", color="#888"),
        yaxis=dict(gridcolor="#1e1e35", color="#888", title="Hari aktif"),
        margin=dict(t=30,b=20,l=20,r=20), height=260, showlegend=False
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    st.divider()
    st.markdown('<div class="sec">Frekuensi Habit Bulan Ini</div>', unsafe_allow_html=True)
    month_now = date.today().strftime("%Y-%m")
    h_counts  = {
        h["name"]: sum(1 for ds, dh in D["habits"].items() if ds.startswith(month_now) and dh.get(h["id"], False))
        for h in get_all_habits(D)
    }
    h_counts = {k: v for k, v in h_counts.items() if v > 0}

    if h_counts:
        sorted_h = sorted(h_counts.items(), key=lambda x: x[1], reverse=True)
        fig_h = go.Figure(go.Bar(
            x=[x[1] for x in sorted_h], y=[x[0] for x in sorted_h], orientation="h",
            marker=dict(color=[x[1] for x in sorted_h], colorscale=[[0,"#2a1a4a"],[1,"#7c3aed"]], line=dict(width=0)),
            text=[x[1] for x in sorted_h], textposition="outside", textfont=dict(color="#a78bfa")
        ))
        fig_h.update_layout(
            paper_bgcolor="#0f0f1a", plot_bgcolor="#0f0f1a", font=dict(color="#e0e0f0"),
            xaxis=dict(gridcolor="#1e1e35", color="#888"), yaxis=dict(color="#c0c0d8", autorange="reversed"),
            margin=dict(t=10,b=20,l=10,r=40), height=max(200, len(sorted_h) * 28)
        )
        st.plotly_chart(fig_h, use_container_width=True)
    else:
        st.caption("Belum ada data habit bulan ini.")

    st.divider()
    st.markdown('<div class="sec">Tren Gold (30 Hari Terakhir)</div>', unsafe_allow_html=True)
    gold_by_day: dict[str, int] = defaultdict(int)
    for t in D["transactions"]:
        gold_by_day[t["date"]] += t["gold"] if t["type"]=="in" else -t["gold"]

    last30 = [date.today() - timedelta(days=29-i) for i in range(30)]
    cumulative, gold_series = 0, []
    for d_obj in last30:
        cumulative += gold_by_day.get(str(d_obj), 0)
        gold_series.append(cumulative)

    fig_gold = go.Figure(go.Scatter(
        x=[str(d) for d in last30], y=gold_series, fill="tozeroy", fillcolor="rgba(124,58,237,0.15)",
        line=dict(color="#a78bfa", width=2), mode="lines"
    ))
    fig_gold.update_layout(
        paper_bgcolor="#0f0f1a", plot_bgcolor="#0f0f1a", font=dict(color="#e0e0f0"),
        xaxis=dict(gridcolor="#1e1e35", color="#888", showticklabels=False),
        yaxis=dict(gridcolor="#1e1e35", color="#888", title="Gold"),
        margin=dict(t=10,b=20,l=20,r=20), height=200
    )
    st.plotly_chart(fig_gold, use_container_width=True)

# =============================================================================
# TAB 5 — REVIEW
# =============================================================================
with tab5:
    cur_lv3, nxt_lv3, total3 = get_level(D["hp"], D["exp"])
    st.markdown(f"""
    <div class="char-card">
        <div class="avatar-ring">{cur_lv3['avatar']}</div>
        <div class="level-badge">Level {cur_lv3['level']} — {cur_lv3['name']}</div>
        <div style="color:#888;font-size:13px">Total stat: {total3}</div>
    </div>""", unsafe_allow_html=True)

    r1, r2, r3, r4 = st.columns(4)
    r1.metric("HP",    D["hp"])
    r2.metric("EXP",   D["exp"])
    r3.metric("Gold",  D["gold"])
    r4.metric("Kupon", D["kupon"])

    if D.get("level_history"):
        st.divider()
        st.markdown('<div class="sec">Riwayat Level Up</div>', unsafe_allow_html=True)
        for lh in reversed(D["level_history"]):
            lv_i = next((l for l in LEVELS if l["level"] == lh["level"]), None)
            icon = lv_i["avatar"] if lv_i else "⭐"
            st.markdown(f"{icon} **Level {lh['level']} — {lh.get('name','')}** · `{lh['date']}`")

    st.divider()
    st.markdown('<div class="sec">Achievements</div>', unsafe_allow_html=True)
    unlocked = set(D.get("achievements", []))
    st.caption(f"{len(unlocked)} / {len(ACHIEVEMENTS)} unlocked")
    for a in ACHIEVEMENTS:
        is_u   = a["id"] in unlocked
        cls    = "ach-card unlocked" if is_u else "ach-card"
        op     = "1" if is_u else "0.35"
        badge  = '<span style="margin-left:auto;font-size:11px;color:#7c3aed;font-weight:600">UNLOCKED</span>' if is_u else ""
        name_c = "#a78bfa" if is_u else "#888"
        st.markdown(f"""
        <div class="{cls}" style="opacity:{op}">
            <span style="font-size:22px">{a['icon']}</span>
            <div>
                <div style="font-weight:600;font-size:14px;color:{name_c}">{a['name']}</div>
                <div style="font-size:12px;color:#666">{a['desc']}</div>
            </div>{badge}
        </div>""", unsafe_allow_html=True)

    st.divider()
    st.markdown('<div class="sec">Tukar Kupon Reward</div>', unsafe_allow_html=True)
    ck1, ck2 = st.columns(2)
    for i, c in enumerate(COUPONS):
        col = ck1 if i % 2 == 0 else ck2
        with col:
            kupon_now  = st.session_state.D["kupon"]
            can_redeem = kupon_now >= c["pts"]
            st.markdown(
                f'<div class="coupon-card {"can-redeem" if can_redeem else ""}">'
                f'<div style="font-size:20px">{"🎟️" if can_redeem else "🔒"}</div>'
                f'<div style="font-weight:600;color:{"#a78bfa" if can_redeem else "#555"};margin:4px 0">{c["name"]}</div>'
                f'<div style="font-size:12px;color:#888">{c["pts"]} poin</div>'
                f'<div style="font-size:13px;color:#34d399;font-weight:600">{c["value"]}</div>'
                f'</div>', unsafe_allow_html=True
            )
            btn_lbl = f"Tukar {c['name']}" if can_redeem else f"{c['pts'] - kupon_now} poin lagi"
            if st.button(btn_lbl, key=f"rd_{c['id']}", disabled=not can_redeem, use_container_width=True):
                st.session_state.D["kupon"] -= c["pts"]
                st.session_state.D["total_redeems"] = st.session_state.D.get("total_redeems", 0) + 1
                st.session_state.D["redeem_log"].insert(0, {
                    "name": c["name"], "pts": c["pts"],
                    "value": c["value"], "date": str(date.today())
                })
                for aid in check_achievements(st.session_state.D):
                    ach = next((a for a in ACHIEVEMENTS if a["id"] == aid), None)
                    if ach: notify(f"{ach['icon']} Achievement: {ach['name']}!")
                save(st.session_state.D)
                st.success(f"Kupon '{c['name']}' ditukar! Sisa: {st.session_state.D['kupon']} poin")
                st.rerun()

    st.divider()
    st.markdown('<div class="sec">Riwayat Penukaran</div>', unsafe_allow_html=True)
    rl = st.session_state.D.get("redeem_log", [])
    if not rl:
        st.caption("Belum ada penukaran.")
    else:
        for r in rl[:10]:
            st.markdown(
                f'<div class="tx-row">'
                f'<span style="color:#888">{r["date"]} · {r["name"]}</span>'
                f'<span style="color:#f87171;font-weight:600">-{r["pts"]} poin ({r["value"]})</span>'
                f'</div>', unsafe_allow_html=True
            )

    st.divider()
    st.markdown('<div class="sec">Data</div>', unsafe_allow_html=True)

    st.download_button(
        "Export Backup (JSON)",
        data=json.dumps(st.session_state.D, indent=2, ensure_ascii=False),
        file_name=f"habitrpg_backup_{date.today()}.json",
        mime="application/json",
        use_container_width=True
    )

    st.markdown("**Import / Restore Data dari File JSON:**")
    uploaded = st.file_uploader("Pilih file backup .json", type=["json"], key="import_file")
    if uploaded is not None:
        if st.button("Konfirmasi Import Data", type="secondary", use_container_width=True):
            try:
                raw = uploaded.read().decode("utf-8")
                restored = import_data(raw)
                st.session_state.D = restored
                save(st.session_state.D)
                st.success("Data berhasil diimport!")
                st.rerun()
            except json.JSONDecodeError:
                st.error("File tidak valid. Pastikan file adalah backup JSON yang benar.")
            except Exception as e:
                st.error(f"Gagal import: {e}")

    with st.expander("Reset Semua Data"):
        st.warning("Semua data akan dihapus permanen dan tidak bisa dikembalikan.")
        if st.button("Konfirmasi Reset", type="secondary", use_container_width=True):
            st.session_state.D = default_state()
            save(st.session_state.D)
            st.success("Data direset.")
            st.rerun()
