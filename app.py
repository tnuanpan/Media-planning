import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
import random

st.set_page_config(page_title="Media Planning — Saccadhiko", page_icon="📊", layout="wide")

# ── API Keys (ใส่ key จริงตรงนี้) ─────────────────────────
YOUTUBE_API_KEY = ""   # ← ใส่ YouTube Data API v3 key
META_ACCESS_TOKEN = "" # ← ใส่ Meta Graph API token
IG_USER_ID = ""        # ← ใส่ Instagram Business Account ID
FB_PAGE_ID = ""        # ← ใส่ Facebook Page ID

# ── YouTube Data API ───────────────────────────────────────
def get_youtube_channel_stats(channel_id, api_key):
    try:
        from googleapiclient.discovery import build
        youtube = build("youtube", "v3", developerKey=api_key)
        res = youtube.channels().list(part="statistics,snippet", id=channel_id).execute()
        item = res["items"][0]
        stats = item["statistics"]
        return {
            "name": item["snippet"]["title"],
            "subscribers": int(stats.get("subscriberCount", 0)),
            "views": int(stats.get("viewCount", 0)),
            "videos": int(stats.get("videoCount", 0)),
        }
    except Exception as e:
        return None

def get_youtube_top_videos(channel_id, api_key, max_results=5):
    try:
        from googleapiclient.discovery import build
        youtube = build("youtube", "v3", developerKey=api_key)
        search = youtube.search().list(
            part="snippet", channelId=channel_id,
            order="viewCount", maxResults=max_results, type="video"
        ).execute()
        videos = []
        for item in search.get("items", []):
            videos.append({
                "title": item["snippet"]["title"],
                "published": item["snippet"]["publishedAt"][:10],
                "video_id": item["id"]["videoId"],
            })
        return videos
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
        if df.empty:
            return None
        return df.drop(columns=["isPartial"], errors="ignore")
    except Exception:
        return None

# ── Meta Graph API ─────────────────────────────────────────
def get_meta_page_stats(page_id, token):
    try:
        import urllib.request, json
        url = f"https://graph.facebook.com/v19.0/{page_id}?fields=fan_count,name&access_token={token}"
        with urllib.request.urlopen(url) as r:
            data = json.loads(r.read())
        return {"name": data.get("name"), "fans": data.get("fan_count")}
    except Exception:
        return None

def get_ig_stats(ig_user_id, token):
    try:
        import urllib.request, json
        url = f"https://graph.facebook.com/v19.0/{ig_user_id}?fields=followers_count,media_count,username&access_token={token}"
        with urllib.request.urlopen(url) as r:
            data = json.loads(r.read())
        return {"username": data.get("username"), "followers": data.get("followers_count"), "media": data.get("media_count")}
    except Exception:
        return None

# ── Mock Fallback ──────────────────────────────────────────
MOCK = {
    "youtube": {"subscribers": 12500, "views": 85000, "videos": 320},
    "instagram": {"followers": 26900, "media": 410},
    "facebook": {"fans": 34000},
    "competitors": [
        {"ช่อง": "Saccadhiko", "Subscribers": 12500, "Engagement %": 4.2},
        {"ช่อง": "Mission to the Moon", "Subscribers": 1200000, "Engagement %": 3.1},
        {"ช่อง": "Lifeenricher", "Subscribers": 890000, "Engagement %": 3.8},
    ],
}

# ── Channel IDs คู่แข่ง (public) ──────────────────────────
COMPETITOR_CHANNELS = {
    "Mission to the Moon": "UCd0pUnH7i5CM-Y8xRe7cZVg",
    "Lifeenricher": "UCuLBFd4xXR_VkBBMrCQFNig",
}

# ── Sidebar ────────────────────────────────────────────────
pages = {
    "🏠 Dashboard": "dashboard",
    "👥 ผู้ติดตาม": "followers",
    "📈 เทรน": "trends",
    "🔍 คู่แข่ง": "competitors",
    "📅 วางแผน": "planning",
    "🎯 แคมเปญ": "campaigns",
    "📋 รายงาน": "report",
}

with st.sidebar:
    st.title("Saccadhiko")
    st.caption("Media Planning Tool")
    st.divider()
    selected = st.radio("เมนู", list(pages.keys()), label_visibility="collapsed")
    st.divider()
    has_yt_key = bool(YOUTUBE_API_KEY)
    has_meta = bool(META_ACCESS_TOKEN)
    st.caption("🔑 API Status")
    st.caption(f"{'🟢' if has_yt_key else '🔴'} YouTube API")
    st.caption(f"{'🟢' if has_meta else '🔴'} Meta API")
    st.caption("🟢 Google Trends")

page = pages[selected]

# ── Dashboard ──────────────────────────────────────────────
if page == "dashboard":
    st.title("🏠 ภาพรวมทุกช่อง")

    yt = MOCK["youtube"]
    ig = MOCK["instagram"]
    fb = MOCK["facebook"]

    if YOUTUBE_API_KEY:
        live = get_youtube_channel_stats("UCxxxxxx", YOUTUBE_API_KEY)  # ใส่ channel ID จริง
        if live:
            yt = live

    if META_ACCESS_TOKEN and FB_PAGE_ID:
        fb_live = get_meta_page_stats(FB_PAGE_ID, META_ACCESS_TOKEN)
        if fb_live:
            fb = {"fans": fb_live["fans"]}

    if META_ACCESS_TOKEN and IG_USER_ID:
        ig_live = get_ig_stats(IG_USER_ID, META_ACCESS_TOKEN)
        if ig_live:
            ig = {"followers": ig_live["followers"], "media": ig_live["media"]}

    col1, col2, col3 = st.columns(3)
    col1.metric("YouTube", f"{yt['subscribers']:,}", "Subscribers")
    col2.metric("Instagram", f"{ig['followers']:,}", "Followers")
    col3.metric("Facebook", f"{fb['fans']:,}", "Fans")

    if not (YOUTUBE_API_KEY and META_ACCESS_TOKEN):
        st.info("💡 ใส่ API Key ใน app.py เพื่อดูข้อมูลจริง — ตอนนี้แสดง Mock data")

    months = [(datetime.now() - timedelta(days=30*i)).strftime("%b %Y") for i in range(5, -1, -1)]
    df = pd.DataFrame({
        "เดือน": months * 3,
        "Views": [random.randint(60000, 100000) for _ in months] +
                 [random.randint(100000, 180000) for _ in months] +
                 [random.randint(70000, 120000) for _ in months],
        "ช่อง": ["YouTube"] * 6 + ["Instagram"] * 6 + ["Facebook"] * 6,
    })
    fig = px.line(df, x="เดือน", y="Views", color="ช่อง", markers=True, title="Views รายเดือน")
    st.plotly_chart(fig, use_container_width=True)

# ── Followers ──────────────────────────────────────────────
elif page == "followers":
    st.title("👥 วิเคราะห์ผู้ติดตาม")
    if not META_ACCESS_TOKEN:
        st.warning("🔴 ยังไม่ได้เชื่อม Meta API — แสดง Mock data")

    col1, col2 = st.columns(2)
    with col1:
        age_df = pd.DataFrame({"กลุ่มอายุ": ["18-24", "25-34", "35-44", "45-54", "55+"], "สัดส่วน": [18, 35, 28, 12, 7]})
        fig = px.pie(age_df, names="กลุ่มอายุ", values="สัดส่วน", title="อายุผู้ติดตาม")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        gender_df = pd.DataFrame({"เพศ": ["ชาย", "หญิง"], "สัดส่วน": [42, 58]})
        fig2 = px.pie(gender_df, names="เพศ", values="สัดส่วน", title="เพศผู้ติดตาม")
        st.plotly_chart(fig2, use_container_width=True)

    st.divider()
    st.subheader("3 กลุ่ม Target")
    c1, c2, c3 = st.columns(3)
    c1.info("**กลุ่ม A** — 25-34 ปี\nสนใจพัฒนาตัวเอง\nอยากเปลี่ยนแปลงชีวิต")
    c2.info("**กลุ่ม B** — 35-44 ปี\nมีครอบครัว\nหาความสมดุล")
    c3.info("**กลุ่ม C** — 18-24 ปี\nนักศึกษา/เริ่มทำงาน\nหาแรงบันดาลใจ")

# ── Trends ─────────────────────────────────────────────────
elif page == "trends":
    st.title("📈 Google Trends")
    st.success("🟢 ข้อมูลจริงจาก Google Trends")

    keywords_input = st.text_input("คำค้นหา (คั่นด้วยจุลภาค)", "สมาธิ,ธรรมะ,mindfulness,พัฒนาตัวเอง,ความสุข")
    timeframe = st.selectbox("ช่วงเวลา", ["today 1-m", "today 3-m", "today 12-m"], index=1)

    keywords = [k.strip() for k in keywords_input.split(",") if k.strip()][:5]

    with st.spinner("กำลังดึงข้อมูลจาก Google Trends..."):
        df = get_trends(keywords, timeframe=timeframe)

    if df is not None:
        fig = px.line(df.reset_index(), x="date", y=keywords, title="ความนิยมตามช่วงเวลา (Google Trends)")
        st.plotly_chart(fig, use_container_width=True)

        avg = df.mean().sort_values(ascending=False)
        fig2 = px.bar(x=avg.index, y=avg.values, labels={"x": "คำค้นหา", "y": "ค่าเฉลี่ย"}, title="ความนิยมเฉลี่ย")
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.error("ดึงข้อมูลไม่ได้ — ลองใหม่อีกครั้ง")

# ── Competitors ─────────────────────────────────────────────
elif page == "competitors":
    st.title("🔍 วิเคราะห์คู่แข่ง")

    competitors = list(MOCK["competitors"])

    if YOUTUBE_API_KEY:
        st.success("🟢 ดึงข้อมูลจาก YouTube API จริง")
        for name, cid in COMPETITOR_CHANNELS.items():
            data = get_youtube_channel_stats(cid, YOUTUBE_API_KEY)
            if data:
                for c in competitors:
                    if c["ช่อง"] == name:
                        c["Subscribers"] = data["subscribers"]
    else:
        st.warning("🔴 ยังไม่ได้ใส่ YouTube API Key — แสดง Mock data")

    comp_df = pd.DataFrame(competitors)
    st.dataframe(comp_df, use_container_width=True, hide_index=True)
    fig = px.bar(comp_df, x="ช่อง", y="Subscribers", color="ช่อง", title="Subscribers เปรียบเทียบ")
    st.plotly_chart(fig, use_container_width=True)

# ── Planning ────────────────────────────────────────────────
elif page == "planning":
    st.title("📅 Content Calendar")
    weeks = ["สัปดาห์ 1", "สัปดาห์ 2", "สัปดาห์ 3", "สัปดาห์ 4"]
    cal_df = pd.DataFrame({
        "สัปดาห์": weeks,
        "YouTube": ["สมาธิเบื้องต้น", "ทำไมต้องภาวนา", "ชีวิตที่สมดุล", "Q&A ธรรมะ"],
        "Instagram": ["Quote ธรรมะ", "Reel สั้น", "Story Poll", "Carousel tips"],
        "Facebook": ["Live ธรรมะ", "Post บทความ", "แชร์คลิป YT", "Community post"],
    })
    st.dataframe(cal_df, use_container_width=True, hide_index=True)

# ── Campaigns ───────────────────────────────────────────────
elif page == "campaigns":
    st.title("🎯 3 แคมเปญ สำหรับ 3 กลุ่ม Target")
    tab1, tab2, tab3 = st.tabs(["แคมเปญ A — 25-34 ปี", "แคมเปญ B — 35-44 ปี", "แคมเปญ C — 18-24 ปี"])
    with tab1:
        st.subheader("เปลี่ยนชีวิตด้วยสติ")
        st.write("- คอนเทนต์: เทคนิคสมาธิที่ใช้ได้จริงในชีวิตประจำวัน")
        st.write("- ช่องทาง: YouTube (long-form) + Instagram Reels")
        st.write("- ความถี่: 2 คลิป/สัปดาห์")
    with tab2:
        st.subheader("สมดุลชีวิตครอบครัว")
        st.write("- คอนเทนต์: ธรรมะสำหรับพ่อแม่ + การเลี้ยงลูก")
        st.write("- ช่องทาง: Facebook Live + YouTube")
        st.write("- ความถี่: Live 1 ครั้ง/สัปดาห์")
    with tab3:
        st.subheader("เริ่มต้นด้วยธรรมะ")
        st.write("- คอนเทนต์: ธรรมะสำหรับคนรุ่นใหม่ สั้น กระชับ")
        st.write("- ช่องทาง: Instagram + TikTok-style Reels")
        st.write("- ความถี่: ทุกวัน (short-form)")

# ── Report ──────────────────────────────────────────────────
elif page == "report":
    st.title("📋 รายงานสรุปทีม")
    st.subheader("สรุปเดือนนี้")
    st.write("- YouTube: +320 subscribers, views 85,000")
    st.write("- Instagram: +1,200 followers, engagement 6.8%")
    st.write("- Facebook: +450 followers, views 98,000")
    st.divider()
    st.button("📥 Export PDF (เร็วๆ นี้)", disabled=True)
    st.button("📊 ส่ง Google Sheets (เร็วๆ นี้)", disabled=True)
