# 📘 คู่มือใช้งานกับ Claude Code & Claude Design

---

## ขั้นตอนที่ 1 — เปิด Claude Code

```bash
# ติดตั้ง Claude Code (ถ้ายังไม่มี)
npm install -g @anthropic-ai/claude-code

# เข้าโฟลเดอร์โปรเจกต์
cd nexus-gold-bot

# เปิด Claude Code
claude
```

---

## ขั้นตอนที่ 2 — คำสั่งที่ใช้กับ Claude Code

### เริ่มต้นโปรเจกต์
```
"อ่านไฟล์ README.md และ bot.py แล้วอธิบายโครงสร้างระบบ"
```

### ต่อ Binance API จริง
```
"แก้ไข executor/binance_client.py ให้ต่อ WebSocket จริงกับ Binance
 เพื่อรับราคา XAUUSDT แบบ real-time"
```

### เพิ่ม Dashboard
```
"สร้าง dashboard/app.py เป็น Flask server
 ที่ส่งข้อมูล real-time ผ่าน WebSocket ไปยัง dashboard"
```

### ทดสอบ Backtest
```
"สร้าง strategy/backtest.py ที่ทดสอบกลยุทธ์
 กับข้อมูลย้อนหลัง 3 เดือนของ XAUUSDT"
```

### เพิ่มแจ้งเตือน LINE
```
"แก้ไข utils/notifier.py ให้ส่งแจ้งเตือน LINE Notify
 เมื่อมี Order BUY/SELL"
```

### Deploy บน VPS
```
"สร้าง systemd service file เพื่อให้ bot.py
 รันอัตโนมัติเมื่อ VPS เปิด"
```

---

## ขั้นตอนที่ 3 — ใช้ Claude Design สำหรับ Dashboard

เปิด Claude.ai แล้วบอกว่า:

```
"ทำ Dashboard Trading สวยงามสำหรับ NEXUS GOLD Bot
 ที่แสดง:
 - ราคา XAUUSDT real-time
 - Signal BUY/SELL/HOLD ขนาดใหญ่
 - กราฟแท่งเทียน 5 นาที
 - รายการ Orders ล่าสุด
 - สถานะ AI Agents 5 ตัว
 - P&L วันนี้
 ใช้สีเข้ม พื้นหลังดำ ตัวเลขสีทอง
 รองรับ WebSocket สำหรับข้อมูล real-time"
```

---

## ไฟล์ที่ต้องแก้ไขก่อนรัน

### 1. สร้างไฟล์ .env
```bash
cp .env.example .env
# แก้ไข .env ใส่ API Key จริง
```

### 2. ติดตั้ง Library
```bash
pip install -r requirements.txt
```

### 3. ทดสอบ Connection
```bash
python -c "from executor.binance_client import BinanceClient; c = BinanceClient(); print(c.get_price())"
```

### 4. รัน Bot
```bash
python bot.py
```

---

## โครงสร้าง Flow การทำงาน

```
bot.py (ทุก 60 วินาที)
    │
    ├── BinanceClient.get_price()      ← ดึงราคาจริง
    ├── BinanceClient.get_candles()    ← ดึง Candle
    │
    ├── OrderManager.check_position()  ← ตรวจ SL/TP
    │
    ├── generate_signal()              ← วิเคราะห์
    │       ├── add_indicators()       ← EMA, RSI, ATR
    │       └── ตัดสิน BUY/SELL/HOLD
    │
    ├── OrderManager.execute()         ← ส่ง Order
    │       ├── place_market_order()   ← ส่งจริง
    │       └── บันทึก SL/TP
    │
    └── notify()                       ← แจ้งเตือน LINE/Telegram
```

---

## คำสั่ง Claude Code ที่มีประโยชน์

| ต้องการ | คำสั่ง |
|--------|--------|
| อ่านโค้ดทั้งหมด | `"อธิบายโค้ดทั้งหมดในโฟลเดอร์นี้"` |
| แก้ bug | `"bot.py มี error: [วางข้อความ error]"` |
| เพิ่มฟีเจอร์ | `"เพิ่มระบบ trailing stop loss ใน order_manager.py"` |
| ทดสอบ | `"เขียน unit test สำหรับ strategy/signals.py"` |
| Deploy | `"สร้างไฟล์ Dockerfile สำหรับ deploy บน VPS"` |
