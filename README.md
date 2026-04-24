# โปรแกรมวางแผนการผลิตสื่อ — ช่อง Saccadhiko

## ภาพรวมช่อง
- **YouTube**: 12,500 subscribers
- **Instagram**: 26,900 followers
- **Facebook**: 34,000 followers

---

## Phase 1: เชื่อมข้อมูล
- [ ] YouTube Analytics API (ข้อมูลช่องตัวเอง)
- [ ] Meta Graph API (Instagram + Facebook ตัวเอง)
- [ ] YouTube Data API v3 (ข้อมูลคู่แข่ง — public)
- [ ] Google Trends (ผ่าน pytrends)

## Phase 2: วิเคราะห์
- [ ] ภาพรวมช่อง (views, followers, engagement)
- [ ] วิเคราะห์ผู้ติดตาม → แบ่ง 3 กลุ่ม target
- [ ] วิเคราะห์เทรน (Google Trends + YouTube Trending)
- [ ] วิเคราะห์คู่แข่ง (Mission to the Moon, Lifeenricher)

## Phase 3: วางแผน
- [ ] แนะนำแนวคอนเทนต์จากข้อมูล
- [ ] ตาราง content calendar
- [ ] แคมเปญ A — กลุ่ม target 1
- [ ] แคมเปญ B — กลุ่ม target 2
- [ ] แคมเปญ C — กลุ่ม target 3

## Phase 4: รายงาน
- [ ] สรุป report สำหรับทีม
- [ ] Export PDF / Google Sheets

---

## หน้าใน App (Streamlit)

| หน้า | เนื้อหา |
|---|---|
| 🏠 Dashboard | ภาพรวมตัวเลขทุกช่อง |
| 👥 ผู้ติดตาม | demographics, แบ่ง 3 กลุ่ม |
| 📈 เทรน | Google Trends + YouTube Trending |
| 🔍 คู่แข่ง | เปรียบเทียบกับ MTTM, Lifeenricher |
| 📅 วางแผน | content calendar + คำแนะนำ |
| 🎯 แคมเปญ | 3 แคมเปญสำหรับ 3 target |
| 📋 รายงาน | Export สรุปให้ทีม |

---

## ลำดับการสร้าง

- [ ] Step 1: Setup project + ติดตั้ง Streamlit
- [ ] Step 2: เชื่อม YouTube API → แสดงข้อมูลพื้นฐาน
- [ ] Step 3: เชื่อม Meta API (IG + FB)
- [ ] Step 4: เพิ่ม Google Trends
- [ ] Step 5: เพิ่มหน้าคู่แข่ง
- [ ] Step 6: วิเคราะห์ + แนะนำคอนเทนต์
- [ ] Step 7: สร้างหน้าแคมเปญ 3 กลุ่ม
- [ ] Step 8: ระบบ Export รายงาน

---

## เทคโนโลยีที่ใช้
- **Streamlit** ✅ — web app (Python)
- **GitHub** — เก็บโค้ด + deploy
- **Streamlit Cloud** — ให้ทีมเข้าใช้งานผ่านเว็บ
- **Claude** — ช่วยเขียนโค้ด

## API ที่ต้องขอ Key
- [ ] YouTube API Key (Google Cloud Console) — ฟรี
- [ ] Meta Developer Account (Facebook for Developers) — ฟรี
