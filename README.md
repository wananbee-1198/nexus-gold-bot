# ⚡ NEXUS GOLD — AI Trading Bot
### XAUUSDT Spot | Binance TH | Trend Following | Auto 24/7

---

## 📁 โครงสร้างโปรเจกต์

```
nexus-gold-bot/
│
├── config/
│   ├── settings.py          ← API Key, ตั้งค่าการเทรด
│   └── constants.py         ← ค่าคงที่ทั้งระบบ
│
├── agents/
│   ├── alpha_scout.py       ← ดึงราคา real-time (WebSocket)
│   ├── sigma_quant.py       ← วิเคราะห์ EMA, RSI, Signal
│   ├── delta_risk.py        ← จัดการ SL/TP, Exposure
│   ├── omega_exec.py        ← ส่ง Order จริงไป Binance
│   └── gamma_comms.py       ← ประสานงาน Agents ทั้งหมด
│
├── strategy/
│   ├── indicators.py        ← คำนวณ EMA, RSI, ATR
│   ├── signals.py           ← logic BUY/SELL/HOLD
│   └── backtest.py          ← ทดสอบกลยุทธ์ย้อนหลัง
│
├── executor/
│   ├── binance_client.py    ← เชื่อมต่อ Binance API
│   ├── order_manager.py     ← จัดการ Orders
│   └── position_tracker.py ← ติดตาม Position ที่เปิดอยู่
│
├── dashboard/
│   ├── app.py               ← Flask web server
│   ├── websocket_server.py  ← ส่งข้อมูล real-time ไปหน้าจอ
│   └── static/
│       ├── index.html       ← หน้า Dashboard (Claude Design)
│       ├── style.css
│       └── app.js
│
├── utils/
│   ├── logger.py            ← บันทึก Log ทุกการทำงาน
│   ├── notifier.py          ← แจ้งเตือน LINE/Telegram
│   └── helpers.py           ← ฟังก์ชันทั่วไป
│
├── logs/                    ← ไฟล์ Log อัตโนมัติ
├── data/                    ← ข้อมูล Candle ที่บันทึกไว้
│
├── bot.py                   ← ไฟล์หลัก รันที่นี่
├── requirements.txt         ← Library ที่ต้องติดตั้ง
├── .env                     ← API Key (ห้าม commit ขึ้น Git)
├── .gitignore
└── README.md
```

---

## 🚀 วิธีเริ่มต้นใช้งาน

### 1. ติดตั้ง Python
```
python.org → ดาวน์โหลด Python 3.11+
ติดตั้ง → ติ๊ก "Add Python to PATH"
```

### 2. ติดตั้ง Library
```bash
pip install -r requirements.txt
```

### 3. ตั้งค่า API Key
```
แก้ไขไฟล์ .env
ใส่ API_KEY และ API_SECRET จาก Binance TH
```

### 4. รัน Bot
```bash
python bot.py
```

### 5. เปิด Dashboard
```
เปิด Browser → http://localhost:5000
```

---

## ⚙️ การตั้งค่าหลัก

| ค่า | ค่าเริ่มต้น | คำอธิบาย |
|-----|------------|---------|
| SYMBOL | XAUUSDT | คู่เทรด |
| ORDER_USDT | 50 | ขนาด Order (USDT) |
| EMA_FAST | 9 | EMA เร็ว |
| EMA_SLOW | 21 | EMA ช้า |
| RSI_PERIOD | 14 | RSI Period |
| RSI_OB | 68 | RSI Overbought |
| RSI_OS | 32 | RSI Oversold |
| STOP_LOSS_PCT | 0.8 | Stop Loss % |
| TAKE_PROFIT_PCT | 1.6 | Take Profit % |
| MIN_CONFIDENCE | 62 | Confidence ขั้นต่ำ |
| INTERVAL | 5m | Candle Interval |

---

## 🤖 AI Agents

| Agent | หน้าที่ | ทำงานทุก |
|-------|--------|---------|
| Alpha Scout | ดึงราคา WebSocket | Real-time |
| Sigma Quant | วิเคราะห์ Signal | 30 วินาที |
| Delta Risk | ตรวจ Risk | ทุก Order |
| Omega Exec | ส่ง Order | เมื่อมี Signal |
| Gamma Comms | ประสานงาน | ตลอดเวลา |

---

## 📊 กลยุทธ์ Trend Following

```
BUY  → EMA9 ตัด EMA21 ขึ้น + RSI < 68 + Confidence > 62%
SELL → EMA9 ตัด EMA21 ลง  + RSI > 32 + Confidence > 62%
HOLD → รอ Signal ที่ชัดเจน
```

---

## ⚠️ คำเตือน
การเทรด Spot มีความเสี่ยง ใช้เงินที่ยอมรับการสูญเสียได้เท่านั้น
ไม่ใช่คำแนะนำทางการเงิน
