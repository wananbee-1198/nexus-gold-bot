"""
utils/notifier.py
=================
แจ้งเตือนผ่าน LINE Messaging API และ Telegram
"""

import requests
from config.settings import (
    NOTIFY_LINE, LINE_CHANNEL_TOKEN, LINE_USER_ID,
    NOTIFY_TELEGRAM, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
)
from utils.logger import get_logger

log = get_logger("Notifier")


def notify(message: str):
    """ส่งแจ้งเตือนทุกช่องทางที่เปิดใช้งาน"""
    if NOTIFY_LINE:
        _send_line(message)
    if NOTIFY_TELEGRAM:
        _send_telegram(message)


def _send_line(message: str):
    """ส่งแจ้งเตือนผ่าน LINE Messaging API"""
    try:
        r = requests.post(
            "https://api.line.me/v2/bot/message/push",
            headers={
                "Authorization": f"Bearer {LINE_CHANNEL_TOKEN}",
                "Content-Type": "application/json",
            },
            json={
                "to": LINE_USER_ID,
                "messages": [{"type": "text", "text": message}],
            },
            timeout=5,
        )
        if r.status_code == 200:
            log.info("LINE notification sent")
        else:
            log.error(f"LINE error {r.status_code}: {r.text}")
    except Exception as e:
        log.error(f"LINE exception: {e}")


def _send_telegram(message: str):
    """ส่งแจ้งเตือนผ่าน Telegram Bot"""
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            json={"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"},
            timeout=5,
        )
        if r.status_code == 200:
            log.info("Telegram notification sent")
        else:
            log.error(f"Telegram error {r.status_code}: {r.text}")
    except Exception as e:
        log.error(f"Telegram exception: {e}")


def order_message(side: str, price: float, qty: float, sl: float, tp: float, conf: int) -> str:
    emoji = "🟢" if side == "BUY" else "🔴"
    return (
        f"{emoji} NEXUS GOLD — {side}\n"
        f"💰 ราคา: {price:.2f} USDT\n"
        f"📦 จำนวน: {qty} XAUT\n"
        f"🛡 Stop Loss: {sl:.2f}\n"
        f"🎯 Take Profit: {tp:.2f}\n"
        f"📊 Confidence: {conf}%"
    )


def close_message(side: str, entry: float, close: float, pnl: float, reason: str) -> str:
    emoji = "✅" if pnl >= 0 else "❌"
    return (
        f"{emoji} ปิด Position ({reason})\n"
        f"📍 เข้า: {entry:.2f} → ออก: {close:.2f}\n"
        f"💵 P&L: {pnl:+.4f} USDT"
    )
