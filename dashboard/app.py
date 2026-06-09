"""
dashboard/app.py
================
Flask + SocketIO server
push ข้อมูล real-time ไปหน้า dashboard
+ LINE Bot webhook
"""

import threading
import hmac
import hashlib
import base64
import requests as req
from flask import Flask, jsonify, send_from_directory, request, abort
from flask_socketio import SocketIO
from flask_cors import CORS

app = Flask(__name__, static_folder="static")
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

# ── Shared state ─────────────────────────────────────────────────────
_state = {
    "price":        0.0,
    "signal":       "HOLD",
    "confidence":   0,
    "reason":       "รอข้อมูล...",
    "rsi":          50.0,
    "ema_fast":     0.0,
    "ema_slow":     0.0,
    "atr":          0.0,
    "trend":        "--",
    "sl":           0.0,
    "tp":           0.0,
    "balance_usdt": 0.0,
    "balance_xaut": 0.0,
    "balance_thb":  0.0,
    "open_position": None,
    "orders":       [],
    "cycle":        0,
    "uptime_sec":   0,
    "price_history": [],
}
_lock = threading.Lock()


def update_state(**kwargs):
    with _lock:
        _state.update(kwargs)
        if "price" in kwargs and kwargs["price"] > 0:
            _state["price_history"].append(kwargs["price"])
            if len(_state["price_history"]) > 200:
                _state["price_history"].pop(0)
    socketio.emit("state", _get_snapshot())


def _get_snapshot():
    with _lock:
        return dict(_state)


# ── Dashboard routes ─────────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory("static", "dashboard.html")

@app.route("/zoo")
def zoo():
    return send_from_directory("static", "zoo.html")

@app.route("/office")
def office():
    return send_from_directory("static", "office.html")

@app.route("/pixel")
def pixel():
    return send_from_directory("static", "pixel.html")

@app.route("/api/state")
def api_state():
    return jsonify(_get_snapshot())


# ── LINE Bot Webhook ─────────────────────────────────────────────────

def _verify_line_signature(body: str, signature: str) -> bool:
    from config.settings import LINE_CHANNEL_SECRET
    if not LINE_CHANNEL_SECRET:
        return True  # ถ้าไม่มี secret ข้ามการ verify
    mac = hmac.new(LINE_CHANNEL_SECRET.encode(), body.encode(), hashlib.sha256).digest()
    return base64.b64encode(mac).decode() == signature


def _line_reply(reply_token: str, text: str):
    from config.settings import LINE_CHANNEL_TOKEN
    req.post(
        "https://api.line.me/v2/bot/message/reply",
        headers={"Authorization": f"Bearer {LINE_CHANNEL_TOKEN}", "Content-Type": "application/json"},
        json={"replyToken": reply_token, "messages": [{"type": "text", "text": text}]},
        timeout=5,
    )


def _handle_command(text: str) -> str:
    s = _get_snapshot()
    cmd = text.strip().lower()

    price = s.get("price", 0)
    sig   = s.get("signal", "HOLD")
    conf  = s.get("confidence", 0)
    rsi   = s.get("rsi", 50)
    trend = s.get("trend", "--")
    usdt  = s.get("balance_usdt", 0)
    xaut  = s.get("balance_xaut", 0)
    thb   = s.get("balance_thb", 0)
    cycle = s.get("cycle", 0)
    pos   = s.get("open_position")
    reason = s.get("reason", "--")
    sl    = s.get("sl", 0)
    tp    = s.get("tp", 0)
    up    = s.get("uptime_sec", 0)
    h, m  = divmod(up // 60, 60)

    sig_emoji = "🟢" if sig == "BUY" else "🔴" if sig == "SELL" else "🟡"

    if cmd in ["สถานะ", "status", "ดู", "stat", "s"]:
        pos_text = "ไม่มี"
        if pos:
            pnl = (price - pos["entry"]) * pos["quantity"] if pos["side"] == "BUY" else (pos["entry"] - price) * pos["quantity"]
            pos_text = f'{pos["side"]} @ {pos["entry"]:.2f} (P&L: {pnl:+.4f})'
        return (
            f"⚡ NEXUS GOLD — Cycle #{cycle}\n"
            f"{'─'*28}\n"
            f"💰 ราคา: {price:.2f} USDT\n"
            f"{sig_emoji} Signal: {sig} ({conf}%)\n"
            f"📈 RSI: {rsi:.1f} | Trend: {trend}\n"
            f"{'─'*28}\n"
            f"💵 USDT: {usdt:.4f}\n"
            f"🥇 XAUT: {xaut:.6f}\n"
            f"🏦 THB: {thb:.2f}\n"
            f"📋 Position: {pos_text}\n"
            f"⏱ Uptime: {h:02d}:{m:02d}"
        )

    elif cmd in ["ราคา", "price", "p"]:
        return f"💰 XAUTUSDT: {price:.2f} USDT"

    elif cmd in ["balance", "เงิน", "bal", "b"]:
        return (
            f"💼 ยอดเงิน\n"
            f"💵 USDT: {usdt:.4f}\n"
            f"🥇 XAUT: {xaut:.6f}\n"
            f"🏦 THB: {thb:.2f}"
        )

    elif cmd in ["signal", "สัญญาณ"]:
        return (
            f"{sig_emoji} Signal: {sig}\n"
            f"📊 Confidence: {conf}%\n"
            f"📈 RSI: {rsi:.1f} | Trend: {trend}\n"
            f"💡 {reason}\n"
            f"🛡 SL: {sl:.2f} | 🎯 TP: {tp:.2f}"
        )

    elif cmd in ["position", "pos", "เปิด"]:
        if not pos:
            return "📋 ไม่มี Position เปิดอยู่"
        pnl = (price - pos["entry"]) * pos["quantity"] if pos["side"] == "BUY" else (pos["entry"] - price) * pos["quantity"]
        emoji = "🟢" if pos["side"] == "BUY" else "🔴"
        return (
            f"{emoji} Position เปิดอยู่\n"
            f"Side: {pos['side']}\n"
            f"เข้าที่: {pos['entry']:.2f} USDT\n"
            f"ปัจจุบัน: {price:.2f} USDT\n"
            f"SL: {pos['sl']:.2f} | TP: {pos['tp']:.2f}\n"
            f"P&L: {pnl:+.4f} USDT"
        )

    elif cmd in ["orders", "ออเดอร์", "o"]:
        orders = s.get("orders", [])
        if not orders:
            return "📋 ยังไม่มี Orders"
        lines = [f"📋 Orders ล่าสุด ({len(orders)} รายการ)"]
        for o in list(reversed(orders))[:5]:
            pnl = o.get("pnl", 0)
            status = "OPEN" if o.get("status") == "OPEN" else f"{pnl:+.4f}"
            lines.append(f"{'🟢' if o['side']=='BUY' else '🔴'} {o['side']} @ {o['entry']:.2f} → {status}")
        return "\n".join(lines)

    elif cmd in ["help", "ช่วย", "คำสั่ง", "?"]:
        return (
            "📋 คำสั่ง NEXUS GOLD Bot\n"
            "─────────────────────\n"
            "สถานะ — ดูสถานะทั้งหมด\n"
            "ราคา — ราคาปัจจุบัน\n"
            "balance — ยอดเงิน\n"
            "signal — signal ล่าสุด\n"
            "position — position เปิดอยู่\n"
            "orders — ออเดอร์ล่าสุด"
        )

    else:
        return "พิมพ์ help เพื่อดูคำสั่งทั้งหมด 📋"


@app.route("/webhook/line", methods=["POST"])
def line_webhook():
    body      = request.get_data(as_text=True)
    signature = request.headers.get("X-Line-Signature", "")

    if not _verify_line_signature(body, signature):
        abort(403)

    data = request.get_json(silent=True) or {}
    for event in data.get("events", []):
        if event.get("type") == "message" and event["message"].get("type") == "text":
            text        = event["message"]["text"]
            reply_token = event["replyToken"]
            reply       = _handle_command(text)
            threading.Thread(target=_line_reply, args=(reply_token, reply), daemon=True).start()

    return "OK", 200


# ── SocketIO ─────────────────────────────────────────────────────────

@socketio.on("connect")
def on_connect():
    socketio.emit("state", _get_snapshot())


# ── Runner ───────────────────────────────────────────────────────────

def run_dashboard(host="0.0.0.0", port=5000):
    socketio.run(app, host=host, port=port, allow_unsafe_werkzeug=True, log_output=False)
