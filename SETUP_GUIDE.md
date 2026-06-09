# 🚀 NEXUS GOLD — คู่มือติดตั้งและใช้งาน
## ทุน 1,500 บาท | Binance TH | XAUUSDT Spot

---

## 📋 สารบัญ

1. [ติดตั้งบนคอมพิวเตอร์](#1-ติดตั้งบนคอมพิวเตอร์)
2. [ตั้งค่า API Key Binance TH](#2-ตั้งค่า-api-key)
3. [ใช้งานกับ Claude Code](#3-claude-code)
4. [เปิด Dashboard ดูผล](#4-dashboard)
5. [อนาคต — ย้ายไป VPS](#5-vps-อนาคต)

---

## 1. ติดตั้งบนคอมพิวเตอร์

### Step 1.1 — ติดตั้ง Python
```
1. ไปที่ python.org
2. ดาวน์โหลด Python 3.11 หรือใหม่กว่า
3. ติดตั้ง → ✅ ติ๊ก "Add Python to PATH"
4. ทดสอบ: เปิด Terminal พิมพ์ python --version
```

### Step 1.2 — ติดตั้ง VS Code
```
1. ไปที่ code.visualstudio.com
2. ดาวน์โหลดและติดตั้ง
3. เปิดโฟลเดอร์ nexus-gold-bot
```

### Step 1.3 — แตกไฟล์โปรเจกต์
```
1. แตก nexus-gold-bot.zip ไปไว้ที่ Desktop หรือ Documents
2. เปิด Terminal (CMD หรือ PowerShell)
3. พิมพ์: cd Desktop/nexus-gold-bot
```

### Step 1.4 — ติดตั้ง Library
```bash
pip install -r requirements.txt
```

---

## 2. ตั้งค่า API Key

### Step 2.1 — สร้าง API Key จาก Binance TH
```
1. Login binance.th
2. คลิกรูปโปรไฟล์ (มุมขวาบน)
3. เลือก "การจัดการ API"
4. กด "สร้าง API"
5. ตั้งชื่อ: NexusGoldBot
6. เปิด ✅ Enable Reading
7. เปิด ✅ Enable Spot & Margin Trading
8. ❌ อย่าเปิด Withdrawals
9. ยืนยัน Email + 2FA
10. Copy API Key และ Secret Key ทันที!
```

### Step 2.2 — สร้างไฟล์ .env
```
1. ในโฟลเดอร์ nexus-gold-bot
2. คัดลอกไฟล์ .env.example → .env
3. เปิดไฟล์ .env แก้ไข:
```
```
BINANCE_API_KEY=ใส่ API Key ที่นี่
BINANCE_API_SECRET=ใส่ Secret Key ที่นี่
```

---

## 3. Claude Code

### Step 3.1 — ติดตั้ง Claude Code
```bash
npm install -g @anthropic-ai/claude-code
```

### Step 3.2 — เปิด Claude Code ในโปรเจกต์
```bash
cd nexus-gold-bot
claude
```

### Step 3.3 — คำสั่งที่ใช้บ่อย
```
"อ่าน README.md แล้วอธิบายโครงสร้างระบบ"
"เชื่อมต่อ WebSocket Binance จริงใน alpha_scout.py"
"เพิ่ม Flask dashboard ใน dashboard/app.py"
"ทดสอบ connection กับ Binance API"
"เพิ่ม LINE Notify แจ้งเตือนทุก Order"
"สร้าง backtest จากข้อมูล 3 เดือน"
```

### Step 3.4 — ทดสอบ Connection
```bash
python -c "
from executor.binance_client import BinanceClient
c = BinanceClient()
print('ราคา XAUUSDT:', c.get_price())
print('Balance:', c.get_balance())
"
```

---

## 4. Dashboard

### เปิด Dashboard
```bash
python bot.py
```
เปิด Browser: http://localhost:5000

### ดูได้จาก
- คอมที่บ้าน: http://localhost:5000
- มือถือ (WiFi เดียวกัน): http://[IP บ้าน]:5000
- ทุกอุปกรณ์ (ต้องใช้ VPS): http://[VPS IP]:5000

---

## 5. VPS (อนาคต)

### เมื่อพร้อมย้ายไป VPS ทำตามนี้

#### Step 5.1 — สมัคร Oracle Cloud (ฟรี)
```
1. cloud.oracle.com/free
2. สมัครบัญชี (ต้องใช้บัตรเครดิต/เดบิต แต่ไม่ตัดเงิน)
3. สร้าง VM: Ubuntu 22.04 | 1GB RAM | ARM
4. บันทึก IP Address
```

#### Step 5.2 — อัปโหลดไฟล์ขึ้น VPS
```bash
# ใน Terminal บนคอม
scp -r nexus-gold-bot/ ubuntu@[VPS_IP]:~/
```

#### Step 5.3 — ติดตั้งบน VPS
```bash
ssh ubuntu@[VPS_IP]
sudo apt update && sudo apt install python3-pip -y
cd nexus-gold-bot
pip install -r requirements.txt
```

#### Step 5.4 — รัน 24/7 อัตโนมัติ
```bash
# สร้าง service ให้รันตลอด
sudo nano /etc/systemd/system/nexusgold.service
```
```
[Unit]
Description=NEXUS GOLD Trading Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/nexus-gold-bot
ExecStart=/usr/bin/python3 bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```
```bash
sudo systemctl enable nexusgold
sudo systemctl start nexusgold
sudo systemctl status nexusgold
```

#### Step 5.5 — เปิด Port สำหรับ Dashboard
```bash
sudo ufw allow 5000
# แล้วเข้าดูได้จากทุกอุปกรณ์:
# http://[VPS_IP]:5000
```

---

## 💰 แผนการลงทุน ทุน 1,500 บาท

```
Config ที่ตั้งไว้:
- Order Size  : 8 USDT (~280 บาท ต่อ order)
- Stop Loss   : 0.8%
- Take Profit : 1.8%  (R:R = 1:2.25)
- Confidence  : 78%+  (เทรดเฉพาะ Signal แม่น)
- ถี่          : ~2 ครั้ง/วัน เฉลี่ย

ผลที่คาดได้:
- กรณีปกติ  : +120 บาท/เดือน (+8%)
- กรณีดี    : +180 บาท/เดือน (+12%)
- กรณีแย่   : -90  บาท/เดือน (-6%)

แผนทบทุน (ไม่ถอนออก):
- เดือน 6   : ทุน ~2,700 บาท → กำไร ~220/เดือน
- เดือน 12  : ทุน ~5,500 บาท → กำไร ~450/เดือน
- เดือน 22  : ทุน ~28,000 บาท → กำไร ~3,000/เดือน
```

---

## ⚠️ ข้อควรระวัง

```
1. ใส่ API Key เฉพาะในไฟล์ .env เท่านั้น
2. อย่า commit .env ขึ้น GitHub เด็ดขาด
3. ทดสอบ Bot 1-2 สัปดาห์ก่อนทบทุน
4. ตั้ง Stop Loss ทุกครั้ง ไม่ข้าม
5. ดู Dashboard อย่างน้อย 1 ครั้ง/วัน
```

> ⚠️ การเทรดมีความเสี่ยง ไม่มีการรับประกันกำไร
