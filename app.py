import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
import random

st.set_page_config(page_title="Saccadhiko | Media Planning", page_icon="📊", layout="wide")

# ── Global CSS (design จาก HTML) ───────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;900&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200');

html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }

/* Hide default streamlit header/footer */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem !important; padding-bottom: 2rem !important; }

/* Glass card */
.glass {
    backdrop-filter: blur(20px);
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 16px;
    position: relative;
}
.glass::before {
    content: "";
    position: absolute;
    inset: 0;
    border-radius: 12px;
    border: 1px solid transparent;
    background: linear-gradient(to bottom, rgba(255,255,255,0.12), rgba(255,255,255,0.02)) border-box;
    -webkit-mask: linear-gradient(#fff 0 0) padding-box, linear-gradient(#fff 0 0);
    mask: linear-gradient(#fff 0 0) padding-box, linear-gradient(#fff 0 0);
    -webkit-mask-composite: xor;
    mask-composite: exclude;
    pointer-events: none;
}

/* Metric card */
.metric-card {
    backdrop-filter: blur(20px);
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 12px;
    padding: 20px;
    text-align: left;
}
.metric-label {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #a0908a;
    margin-bottom: 8px;
}
.metric-value {
    font-size: 28px;
    font-weight: 700;
    color: #ffffff;
    letter-spacing: -0.02em;
    margin-bottom: 4px;
}
.metric-delta-pos { font-size: 12px; font-weight: 700; color: #f9b89d; }
.metric-delta-neg { font-size: 12px; font-weight: 700; color: #ffb4ab; }
.metric-sub { font-size: 10px; color: #666; text-transform: uppercase; letter-spacing: 0.05em; }

/* Section title */
.section-title {
    font-size: 24px;
    font-weight: 600;
    color: #ffffff;
    letter-spacing: -0.01em;
    margin-bottom: 4px;
}
.section-sub {
    font-size: 14px;
    color: #a0908a;
    margin-bottom: 24px;
}

/* Status badge */
.badge-live {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(249,184,157,0.1); border-radius: 99px;
    padding: 3px 10px; font-size: 10px; font-weight: 700;
    text-transform: uppercase; color: #f9b89d; letter-spacing: 0.05em;
}
.badge-dot { width: 7px; height: 7px; border-radius: 50%; background: #f9b89d;
    box-shadow: 0 0 8px rgba(249,184,157,0.8); display: inline-block; }
.badge-warn {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(255,180,171,0.1); border-radius: 99px;
    padding: 3px 10px; font-size: 10px; font-weight: 700;
    text-transform: uppercase; color: #ffb4ab; letter-spacing: 0.05em;
}

/* Progress bar */
.progress-wrap { margin-bottom: 18px; }
.progress-label { display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 6px; }
.progress-track { height: 6px; background: rgba(255,255,255,0.06); border-radius: 99px; overflow: hidden; }
.progress-fill { height: 100%; border-radius: 99px; }

/* Tab override */
.stTabs [data-baseweb="tab-list"] { gap: 4px; background: rgba(255,255,255,0.03); border-radius: 8px; padding: 4px; }
.stTabs [data-baseweb="tab"] { border-radius: 6px; color: #a0908a; font-size: 13px; font-weight: 600; }
.stTabs [aria-selected="true"] { background: rgba(255,181,150,0.15) !important; color: #ffb596 !important; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: #0A0A0A !important;
    border-right: 1px solid rgba(255,255,255,0.06);
}
</style>
""", unsafe_allow_html=True)

# ── API Keys ───────────────────────────────────────────────
YOUTUBE_API_KEY = "AIzaSyDL8BtNjTpA1qjVPCI5RpbcQfn61TMiGU0"
META_ACCESS_TOKEN = ""
IG_USER_ID = ""
FB_PAGE_ID = ""

# ── YouTube API ────────────────────────────────────────────
SACCADHIKO_CHANNEL_ID = "UCnYIX3wHxACEHsj5ApkxJ-w"

@st.cache_data(ttl=3600)
def get_youtube_stats(channel_id, api_key):
    try:
        from googleapiclient.discovery import build
        yt = build("youtube", "v3", developerKey=api_key)
        res = yt.channels().list(part="statistics,snippet", id=channel_id).execute()
        s = res["items"][0]["statistics"]
        return {
            "subscribers": int(s.get("subscriberCount", 0)),
            "views": int(s.get("viewCount", 0)),
            "videos": int(s.get("videoCount", 0)),
        }
    except Exception:
        return None

@st.cache_data(ttl=3600)
def get_youtube_top_videos(channel_id, api_key, max_results=5):
    try:
        from googleapiclient.discovery import build
        yt = build("youtube", "v3", developerKey=api_key)
        search = yt.search().list(
            part="snippet", channelId=channel_id,
            order="viewCount", maxResults=max_results, type="video"
        ).execute()
        return [{"title": i["snippet"]["title"][:60], "วันที่": i["snippet"]["publishedAt"][:10]} for i in search["items"]]
    except Exception:
        return []

# ── Google Trends ──────────────────────────────────────────
@st.cache_data(ttl=3600)
def get_trends(keywords, timeframe="today 3-m", geo="TH"):
    try:
        from pytrends.request import TrendReq
        pt = TrendReq(hl="th-TH", tz=420)
        pt.build_payload(keywords, timeframe=timeframe, geo=geo)
        df = pt.interest_over_time()
        return None if df.empty else df.drop(columns=["isPartial"], errors="ignore")
    except Exception:
        return None

# ── Plotly theme ───────────────────────────────────────────
COLORS = ["#ffb596", "#f9b89d", "#7ad2f6", "#c0c1ff", "#4edea3"]
PLOT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", color="#a0908a", size=12),
    xaxis=dict(gridcolor="rgba(255,255,255,0.05)", linecolor="rgba(255,255,255,0.05)"),
    yaxis=dict(gridcolor="rgba(255,255,255,0.05)", linecolor="rgba(255,255,255,0.05)"),
    legend=dict(bgcolor="rgba(0,0,0,0)"),
    margin=dict(l=0, r=0, t=40, b=0),
)

# ── Sidebar ────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding: 8px 4px 24px 4px;">
        <div style="font-size:18px;font-weight:900;color:#fff;letter-spacing:-0.02em;">SACCADHIKO</div>
        <div style="font-size:10px;font-weight:600;color:#555;text-transform:uppercase;letter-spacing:0.1em;margin-top:2px;">Media Planning Tool</div>
    </div>
    """, unsafe_allow_html=True)

    pages = {
        "Dashboard": "🏠",
        "ผู้ติดตาม": "👥",
        "Google Trends": "📈",
        "คู่แข่ง": "🔍",
        "Content Calendar": "📅",
        "แคมเปญ": "🎯",
        "รายงาน": "📋",
    }
    selected = st.radio(
        "nav", [f"{v}  {k}" for k, v in pages.items()],
        label_visibility="collapsed"
    )
    page = selected.split("  ", 1)[1]

    st.markdown("<div style='margin-top:32px;padding-top:16px;border-top:1px solid rgba(255,255,255,0.06)'>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:0.08em;color:#555;margin-bottom:8px;">API Status</div>
    <div style="font-size:12px;color:#777;margin:4px 0;">{'🟢' if YOUTUBE_API_KEY else '🔴'} YouTube API</div>
    <div style="font-size:12px;color:#777;margin:4px 0;">{'🟢' if META_ACCESS_TOKEN else '🔴'} Meta API</div>
    <div style="font-size:12px;color:#777;margin:4px 0;">🟢 Google Trends</div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ── Dashboard ──────────────────────────────────────────────
if page == "Dashboard":
    st.markdown('<div class="section-title">Media Orchestrator</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">ภาพรวมทุกช่องทาง — Saccadhiko</div>', unsafe_allow_html=True)

    # ดึงข้อมูล YouTube จริง
    yt_data = get_youtube_stats(SACCADHIKO_CHANNEL_ID, YOUTUBE_API_KEY) if YOUTUBE_API_KEY else None
    yt_subs = f"{yt_data['subscribers']:,}" if yt_data else "12,500"
    yt_views = f"{yt_data['views']:,}" if yt_data else "—"
    yt_label = "🟢 Live" if yt_data else "Mock"

    c1, c2, c3, c4 = st.columns(4)
    cards = [
        ("YouTube Subscribers", yt_subs, yt_label, True),
        ("Instagram Followers", "26,900", "+1,200", True),
        ("Facebook Fans", "34,000", "+450", True),
        ("YouTube Total Views", yt_views, yt_label, True),
    ]
    for col, (label, val, delta, pos) in zip([c1, c2, c3, c4], cards):
        delta_class = "metric-delta-pos" if pos else "metric-delta-neg"
        col.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{val}</div>
            <span class="{delta_class}">{delta}</span>
            <span class="metric-sub"> vs เดือนที่แล้ว</span>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    col_left, col_right = st.columns([2, 1])
    with col_left:
        months = [(datetime.now() - timedelta(days=30*i)).strftime("%b %Y") for i in range(5, -1, -1)]
        df = pd.DataFrame({
            "เดือน": months * 3,
            "Views": [random.randint(60000, 100000) for _ in months] +
                     [random.randint(100000, 180000) for _ in months] +
                     [random.randint(70000, 120000) for _ in months],
            "ช่อง": ["YouTube"] * 6 + ["Instagram"] * 6 + ["Facebook"] * 6,
        })
        fig = px.line(df, x="เดือน", y="Views", color="ช่อง",
                      markers=True, title="Views รายเดือน",
                      color_discrete_sequence=COLORS)
        fig.update_layout(**PLOT_LAYOUT)
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_right:
        yt_subs_num = yt_data['subscribers'] if yt_data else 12500
        total = max(yt_subs_num, 26900, 34000)
        yt_pct = int(yt_subs_num / total * 100)
        st.markdown(f"""
        <div class="glass">
            <div style="font-size:13px;font-weight:600;color:#fff;margin-bottom:16px;">Followers by Channel</div>
            <div class="progress-wrap">
                <div class="progress-label"><span style="color:#ccc">YouTube</span><span style="color:#fff;font-family:monospace">{yt_subs_num:,}</span></div>
                <div class="progress-track"><div class="progress-fill" style="width:{yt_pct}%;background:#ffb596"></div></div>
            </div>
            <div class="progress-wrap">
                <div class="progress-label"><span style="color:#ccc">Instagram</span><span style="color:#fff;font-family:monospace">26,900</span></div>
                <div class="progress-track"><div class="progress-fill" style="width:79%;background:#f9b89d"></div></div>
            </div>
            <div class="progress-wrap">
                <div class="progress-label"><span style="color:#ccc">Facebook</span><span style="color:#fff;font-family:monospace">34,000</span></div>
                <div class="progress-track"><div class="progress-fill" style="width:100%;background:#7ad2f6"></div></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Top Videos
    if YOUTUBE_API_KEY:
        videos = get_youtube_top_videos(SACCADHIKO_CHANNEL_ID, YOUTUBE_API_KEY)
        if videos:
            st.markdown('<div class="glass">', unsafe_allow_html=True)
            st.markdown('<div style="font-size:13px;font-weight:600;color:#fff;margin-bottom:12px;text-transform:uppercase;letter-spacing:0.05em;">🎬 Top Videos</div>', unsafe_allow_html=True)
            st.dataframe(pd.DataFrame(videos), use_container_width=True, hide_index=True)
            st.markdown('</div>', unsafe_allow_html=True)

# ── Followers ──────────────────────────────────────────────
elif page == "ผู้ติดตาม":
    st.markdown('<div class="section-title">👥 วิเคราะห์ผู้ติดตาม</div>', unsafe_allow_html=True)
    if not META_ACCESS_TOKEN:
        st.markdown('<div class="glass"><span class="badge-warn"><span class="badge-dot" style="background:#ffb4ab;box-shadow:0 0 8px rgba(255,180,171,0.8)"></span>ยังไม่ได้เชื่อม Meta API — แสดง Mock data</span></div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        age_df = pd.DataFrame({"กลุ่มอายุ": ["18-24", "25-34", "35-44", "45-54", "55+"], "สัดส่วน": [18, 35, 28, 12, 7]})
        fig = px.pie(age_df, names="กลุ่มอายุ", values="สัดส่วน", title="อายุผู้ติดตาม", hole=0.5,
                     color_discrete_sequence=COLORS)
        fig.update_layout(**PLOT_LAYOUT)
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        gender_df = pd.DataFrame({"เพศ": ["ชาย", "หญิง"], "สัดส่วน": [42, 58]})
        fig2 = px.pie(gender_df, names="เพศ", values="สัดส่วน", title="เพศผู้ติดตาม", hole=0.5,
                      color_discrete_sequence=COLORS)
        fig2.update_layout(**PLOT_LAYOUT)
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="glass">
        <div style="font-size:13px;font-weight:600;color:#fff;margin-bottom:16px;text-transform:uppercase;letter-spacing:0.05em;">3 กลุ่ม Target</div>
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;">
            <div style="background:rgba(255,181,150,0.07);border:1px solid rgba(255,181,150,0.2);border-radius:10px;padding:16px;">
                <div style="font-size:10px;color:#ffb596;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;">กลุ่ม A</div>
                <div style="font-size:16px;font-weight:700;color:#fff;margin:6px 0;">25–34 ปี</div>
                <div style="font-size:12px;color:#a0908a;">สนใจพัฒนาตัวเอง<br>อยากเปลี่ยนแปลงชีวิต</div>
            </div>
            <div style="background:rgba(122,210,246,0.07);border:1px solid rgba(122,210,246,0.2);border-radius:10px;padding:16px;">
                <div style="font-size:10px;color:#7ad2f6;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;">กลุ่ม B</div>
                <div style="font-size:16px;font-weight:700;color:#fff;margin:6px 0;">35–44 ปี</div>
                <div style="font-size:12px;color:#a0908a;">มีครอบครัว<br>หาความสมดุลในชีวิต</div>
            </div>
            <div style="background:rgba(192,193,255,0.07);border:1px solid rgba(192,193,255,0.2);border-radius:10px;padding:16px;">
                <div style="font-size:10px;color:#c0c1ff;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;">กลุ่ม C</div>
                <div style="font-size:16px;font-weight:700;color:#fff;margin:6px 0;">18–24 ปี</div>
                <div style="font-size:12px;color:#a0908a;">นักศึกษา/เริ่มทำงาน<br>หาแรงบันดาลใจ</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Trends ─────────────────────────────────────────────────
elif page == "Google Trends":
    st.markdown('<div class="section-title">📈 Google Trends</div>', unsafe_allow_html=True)
    st.markdown('<div class="badge-live"><span class="badge-dot"></span>ข้อมูลจริงจาก Google Trends</div>', unsafe_allow_html=True)
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])
    with col1:
        keywords_input = st.text_input("คำค้นหา (คั่นด้วยจุลภาค)", "สมาธิ,ธรรมะ,mindfulness,พัฒนาตัวเอง,ความสุข")
    with col2:
        timeframe = st.selectbox("ช่วงเวลา", ["today 1-m", "today 3-m", "today 12-m"], index=1)

    keywords = [k.strip() for k in keywords_input.split(",") if k.strip()][:5]

    with st.spinner("กำลังดึงข้อมูลจาก Google Trends..."):
        df = get_trends(keywords, timeframe=timeframe)

    if df is not None:
        fig = px.line(df.reset_index(), x="date", y=keywords,
                      title="ความนิยมตามช่วงเวลา", color_discrete_sequence=COLORS)
        fig.update_layout(**PLOT_LAYOUT)
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        avg = df.mean().sort_values(ascending=False)
        fig2 = px.bar(x=avg.index, y=avg.values,
                      labels={"x": "คำค้นหา", "y": "ค่าเฉลี่ย"},
                      title="ความนิยมเฉลี่ย", color=avg.index,
                      color_discrete_sequence=COLORS)
        fig2.update_layout(**PLOT_LAYOUT)
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.error("ดึงข้อมูลไม่ได้ — ลองใหม่อีกครั้ง")

# ── Competitors ─────────────────────────────────────────────
elif page == "คู่แข่ง":
    st.markdown('<div class="section-title">🔍 วิเคราะห์คู่แข่ง</div>', unsafe_allow_html=True)
    if not YOUTUBE_API_KEY:
        st.markdown('<div class="glass"><span class="badge-warn"><span class="badge-dot" style="background:#ffb4ab;box-shadow:0 0 8px rgba(255,180,171,0.8)"></span>ยังไม่ได้ใส่ YouTube API Key — แสดง Mock data</span></div>', unsafe_allow_html=True)

    comp_df = pd.DataFrame([
        {"ช่อง": "Saccadhiko", "Subscribers": 12500, "Views/เดือน": 85000, "Engagement %": 4.2},
        {"ช่อง": "Mission to the Moon", "Subscribers": 1200000, "Views/เดือน": 8500000, "Engagement %": 3.1},
        {"ช่อง": "Lifeenricher", "Subscribers": 890000, "Views/เดือน": 6200000, "Engagement %": 3.8},
    ])

    col1, col2 = st.columns([3, 2])
    with col1:
        fig = px.bar(comp_df, x="ช่อง", y="Subscribers", color="ช่อง",
                     title="Subscribers เปรียบเทียบ", color_discrete_sequence=COLORS)
        fig.update_layout(**PLOT_LAYOUT)
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        fig2 = px.bar(comp_df, x="ช่อง", y="Engagement %", color="ช่อง",
                      title="Engagement Rate", color_discrete_sequence=COLORS)
        fig2.update_layout(**PLOT_LAYOUT)
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.dataframe(comp_df, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── Planning ────────────────────────────────────────────────
elif page == "Content Calendar":
    st.markdown('<div class="section-title">📅 Content Calendar</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">วางแผนคอนเทนต์รายสัปดาห์ทุกช่องทาง</div>', unsafe_allow_html=True)

    weeks = ["สัปดาห์ 1", "สัปดาห์ 2", "สัปดาห์ 3", "สัปดาห์ 4"]
    cal_df = pd.DataFrame({
        "สัปดาห์": weeks,
        "YouTube": ["สมาธิเบื้องต้น", "ทำไมต้องภาวนา", "ชีวิตที่สมดุล", "Q&A ธรรมะ"],
        "Instagram": ["Quote ธรรมะ", "Reel สั้น", "Story Poll", "Carousel tips"],
        "Facebook": ["Live ธรรมะ", "Post บทความ", "แชร์คลิป YT", "Community post"],
    })
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.dataframe(cal_df, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── Campaigns ───────────────────────────────────────────────
elif page == "แคมเปญ":
    st.markdown('<div class="section-title">🎯 Campaign Planning</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">3 แคมเปญ สำหรับ 3 กลุ่ม Target</div>', unsafe_allow_html=True)

    # Stepper
    st.markdown("""
    <div class="glass" style="display:flex;align-items:center;gap:24px;">
        <div style="display:flex;align-items:center;gap:10px;">
            <div style="width:32px;height:32px;border-radius:50%;background:#ffb596;color:#581e00;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:14px;">1</div>
            <span style="font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:0.06em;color:#fff;">Definition</span>
        </div>
        <div style="height:1px;width:40px;background:rgba(255,255,255,0.1)"></div>
        <div style="display:flex;align-items:center;gap:10px;">
            <div style="width:32px;height:32px;border-radius:50%;border:1px solid #ffb596;color:#ffb596;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:14px;">2</div>
            <span style="font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:0.06em;color:#fff;">Allocation</span>
        </div>
        <div style="height:1px;width:40px;background:rgba(255,255,255,0.1)"></div>
        <div style="display:flex;align-items:center;gap:10px;opacity:0.4;">
            <div style="width:32px;height:32px;border-radius:50%;border:1px solid rgba(255,255,255,0.4);color:rgba(255,255,255,0.4);display:flex;align-items:center;justify-content:center;font-weight:700;font-size:14px;">3</div>
            <span style="font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:0.06em;">Targeting</span>
        </div>
        <div style="height:1px;width:40px;background:rgba(255,255,255,0.1)"></div>
        <div style="display:flex;align-items:center;gap:10px;opacity:0.4;">
            <div style="width:32px;height:32px;border-radius:50%;border:1px solid rgba(255,255,255,0.4);color:rgba(255,255,255,0.4);display:flex;align-items:center;justify-content:center;font-weight:700;font-size:14px;">4</div>
            <span style="font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:0.06em;">Launch</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["กลุ่ม A — 25-34 ปี", "กลุ่ม B — 35-44 ปี", "กลุ่ม C — 18-24 ปี"])
    with tab1:
        st.markdown("""
        <div class="glass">
            <div style="font-size:18px;font-weight:700;color:#ffb596;margin-bottom:8px;">เปลี่ยนชีวิตด้วยสติ</div>
            <div style="font-size:13px;color:#ccc;line-height:1.8;">
                🎯 <b>เป้าหมาย:</b> Brand Awareness + Community Building<br>
                📹 <b>คอนเทนต์:</b> เทคนิคสมาธิที่ใช้ได้จริงในชีวิตประจำวัน<br>
                📡 <b>ช่องทาง:</b> YouTube (long-form) + Instagram Reels<br>
                📅 <b>ความถี่:</b> 2 คลิป/สัปดาห์
            </div>
        </div>
        """, unsafe_allow_html=True)
    with tab2:
        st.markdown("""
        <div class="glass">
            <div style="font-size:18px;font-weight:700;color:#7ad2f6;margin-bottom:8px;">สมดุลชีวิตครอบครัว</div>
            <div style="font-size:13px;color:#ccc;line-height:1.8;">
                🎯 <b>เป้าหมาย:</b> Engagement + Loyalty<br>
                📹 <b>คอนเทนต์:</b> ธรรมะสำหรับพ่อแม่ + การเลี้ยงลูก<br>
                📡 <b>ช่องทาง:</b> Facebook Live + YouTube<br>
                📅 <b>ความถี่:</b> Live 1 ครั้ง/สัปดาห์
            </div>
        </div>
        """, unsafe_allow_html=True)
    with tab3:
        st.markdown("""
        <div class="glass">
            <div style="font-size:18px;font-weight:700;color:#c0c1ff;margin-bottom:8px;">เริ่มต้นด้วยธรรมะ</div>
            <div style="font-size:13px;color:#ccc;line-height:1.8;">
                🎯 <b>เป้าหมาย:</b> Reach + Follower Growth<br>
                📹 <b>คอนเทนต์:</b> ธรรมะสำหรับคนรุ่นใหม่ สั้น กระชับ<br>
                📡 <b>ช่องทาง:</b> Instagram Reels + Facebook Short<br>
                📅 <b>ความถี่:</b> ทุกวัน (short-form)
            </div>
        </div>
        """, unsafe_allow_html=True)

# ── Report ──────────────────────────────────────────────────
elif page == "รายงาน":
    st.markdown('<div class="section-title">📋 รายงานสรุปทีม</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="glass">
        <div style="font-size:13px;font-weight:600;color:#fff;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:16px;">สรุปเดือนนี้</div>
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;">
            <div style="background:rgba(255,255,255,0.03);border-radius:8px;padding:14px;">
                <div style="font-size:10px;color:#ffb596;font-weight:700;text-transform:uppercase;letter-spacing:0.06em;">YouTube</div>
                <div style="font-size:20px;font-weight:700;color:#fff;margin:4px 0;">+320</div>
                <div style="font-size:11px;color:#777;">Subscribers · 85,000 views</div>
            </div>
            <div style="background:rgba(255,255,255,0.03);border-radius:8px;padding:14px;">
                <div style="font-size:10px;color:#f9b89d;font-weight:700;text-transform:uppercase;letter-spacing:0.06em;">Instagram</div>
                <div style="font-size:20px;font-weight:700;color:#fff;margin:4px 0;">+1,200</div>
                <div style="font-size:11px;color:#777;">Followers · 6.8% engagement</div>
            </div>
            <div style="background:rgba(255,255,255,0.03);border-radius:8px;padding:14px;">
                <div style="font-size:10px;color:#7ad2f6;font-weight:700;text-transform:uppercase;letter-spacing:0.06em;">Facebook</div>
                <div style="font-size:20px;font-weight:700;color:#fff;margin:4px 0;">+450</div>
                <div style="font-size:11px;color:#777;">Fans · 98,000 views</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.button("📥 Export PDF", disabled=True, use_container_width=True)
    with col2:
        st.button("📊 ส่ง Google Sheets", disabled=True, use_container_width=True)
