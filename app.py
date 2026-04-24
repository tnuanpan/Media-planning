import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
import random

st.set_page_config(page_title="Media Planning — Saccadhiko", page_icon="📊", layout="wide")

# Mock data
CHANNEL_DATA = {
    "YouTube": {"subscribers": 12500, "views_month": 85000, "engagement": 4.2},
    "Instagram": {"subscribers": 26900, "views_month": 142000, "engagement": 6.8},
    "Facebook": {"subscribers": 34000, "views_month": 98000, "engagement": 3.1},
}

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

page = pages[selected]

# ── Dashboard ──────────────────────────────────────────────
if page == "dashboard":
    st.title("🏠 ภาพรวมทุกช่อง")
    st.caption("ข้อมูล Mock — เชื่อม API จริงในขั้นถัดไป")

    col1, col2, col3 = st.columns(3)
    col1.metric("YouTube", "12,500", "+320 เดือนนี้", help="Subscribers")
    col2.metric("Instagram", "26,900", "+1,200 เดือนนี้", help="Followers")
    col3.metric("Facebook", "34,000", "+450 เดือนนี้", help="Followers")

    st.divider()

    # Views chart
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

    # Engagement
    eng_df = pd.DataFrame({
        "ช่อง": ["YouTube", "Instagram", "Facebook"],
        "Engagement %": [4.2, 6.8, 3.1],
    })
    fig2 = px.bar(eng_df, x="ช่อง", y="Engagement %", color="ช่อง", title="Engagement Rate (%)")
    st.plotly_chart(fig2, use_container_width=True)

# ── Followers ──────────────────────────────────────────────
elif page == "followers":
    st.title("👥 วิเคราะห์ผู้ติดตาม")
    st.info("ข้อมูล Mock — รอเชื่อม Meta API + YouTube Analytics")

    col1, col2 = st.columns(2)
    with col1:
        age_df = pd.DataFrame({
            "กลุ่มอายุ": ["18-24", "25-34", "35-44", "45-54", "55+"],
            "สัดส่วน": [18, 35, 28, 12, 7],
        })
        fig = px.pie(age_df, names="กลุ่มอายุ", values="สัดส่วน", title="อายุผู้ติดตาม")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        gender_df = pd.DataFrame({
            "เพศ": ["ชาย", "หญิง"],
            "สัดส่วน": [42, 58],
        })
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
    st.title("📈 เทรนและกระแส")
    st.info("ข้อมูล Mock — รอเชื่อม Google Trends + YouTube Trending API")

    keywords = ["สมาธิ", "ธรรมะ", "พัฒนาตัวเอง", "mindfulness", "ความสุข"]
    trend_df = pd.DataFrame({
        "คำค้นหา": keywords,
        "ความนิยม": [random.randint(40, 100) for _ in keywords],
    })
    fig = px.bar(trend_df, x="คำค้นหา", y="ความนิยม", title="Google Trends (เดือนนี้)", color="คำค้นหา")
    st.plotly_chart(fig, use_container_width=True)

# ── Competitors ─────────────────────────────────────────────
elif page == "competitors":
    st.title("🔍 วิเคราะห์คู่แข่ง")
    st.info("ข้อมูล Mock — รอเชื่อม YouTube Data API v3")

    comp_df = pd.DataFrame({
        "ช่อง": ["Saccadhiko", "Mission to the Moon", "Lifeenricher"],
        "Subscribers": [12500, 1200000, 890000],
        "Views/เดือน": [85000, 8500000, 6200000],
        "Engagement %": [4.2, 3.1, 3.8],
    })
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
    st.info("ฟีเจอร์ Export PDF / Google Sheets — อยู่ในแผน Phase 4")

    st.subheader("สรุปเดือนนี้")
    st.write("- YouTube: +320 subscribers, views 85,000")
    st.write("- Instagram: +1,200 followers, engagement 6.8%")
    st.write("- Facebook: +450 followers, views 98,000")

    st.divider()
    st.button("📥 Export PDF (เร็วๆ นี้)", disabled=True)
    st.button("📊 ส่ง Google Sheets (เร็วๆ นี้)", disabled=True)
