# ⚡ NEXUS GOLD — Quick Start Checklist
### เปิดไฟล์นี้ก่อน เช็คทีละข้อ

---

## ✅ บนคอมพิวเตอร์ (ทำก่อน)

- [ ] ติดตั้ง Python 3.11+ จาก python.org
- [ ] ติดตั้ง VS Code จาก code.visualstudio.com
- [ ] แตกไฟล์ nexus-gold-bot.zip
- [ ] เปิด Terminal → `cd nexus-gold-bot`
- [ ] รัน `pip install -r requirements.txt`
- [ ] คัดลอก `.env.example` → `.env`
- [ ] สร้าง API Key จาก Binance TH
- [ ] ใส่ API Key ใน `.env`
- [ ] ทดสอบ `python INVESTMENT_PLAN.py`
- [ ] ทดสอบ connection `python -c "from executor.binance_client import BinanceClient; print(BinanceClient().get_price())"`

---

## ✅ ใช้ Claude Code (ทำต่อ)

- [ ] ติดตั้ง Claude Code: `npm install -g @anthropic-ai/claude-code`
- [ ] เปิดใน Terminal: `claude`
- [ ] บอก Claude Code: "อ่าน README.md แล้วช่วย complete โค้ด"
- [ ] เพิ่ม WebSocket real-time
- [ ] เพิ่ม Flask Dashboard
- [ ] ทดสอบรัน `python bot.py`
- [ ] เปิด http://localhost:5000

---

## ✅ อนาคต — VPS (ทำเมื่อพร้อม)

- [ ] สมัคร Oracle Cloud Free (cloud.oracle.com/free)
- [ ] สร้าง VM Ubuntu 22.04
- [ ] อัปโหลดไฟล์: `scp -r nexus-gold-bot/ ubuntu@IP:~/`
- [ ] รัน deploy: `bash deploy_vps.sh`
- [ ] เปิด Dashboard จากมือถือ: `http://VPS_IP:5000`
- [ ] เปิด LINE Notify ใน `.env`

---

## 📁 ไฟล์สำคัญ

| ไฟล์ | หน้าที่ |
|------|--------|
| `bot.py` | **รันที่นี่** — ไฟล์หลัก |
| `config/settings.py` | ตั้งค่าทุกอย่าง |
| `.env` | API Key (ห้ามแชร์!) |
| `INVESTMENT_PLAN.py` | ดูแผนทบทุน |
| `SETUP_GUIDE.md` | คู่มือละเอียด |
| `CLAUDE_CODE_GUIDE.md` | คำสั่ง Claude Code |
| `deploy_vps.sh` | Deploy VPS อัตโนมัติ |
| `dashboard/static/index.html` | Zoo Dashboard |
| `dashboard/static/dashboard.html` | Trading Dashboard |

---

## 💰 สรุปแผนทุน 1,500 บาท

```
Order Size    : 8 USDT/order
Confidence    : 78%+ เท่านั้น
รอบ/วัน       : ~2 ครั้ง (เฉลี่ย)
กำไรคาด/เดือน : ~120 บาท
ค่า Fee/เดือน : ~34 บาท
กำไรสุทธิ     : ~86 บาท/เดือน
```

> ⚠️ ไม่รับประกันผลตอบแทน | ไม่ใช่คำแนะนำทางการเงิน
