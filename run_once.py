"""
run_once.py
===========
GitHub Actions version — รันครั้งเดียวแล้วจบ
State เก็บใน state.json ระหว่าง run
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

from executor.binance_client import BinanceClient
from strategy.signals import generate_signal
from utils.notifier import notify, order_message, close_message
from utils.logger import get_logger
from config.settings import (
    MIN_CONFIDENCE, ORDER_USDT,
    STOP_LOSS_PCT, TAKE_PROFIT_PCT
)

log  = get_logger("NEXUS-ACTION")
STATE_FILE = Path(__file__).parent / "state.json"


# ── State helpers ────────────────────────────────────────────────────

def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"position": None, "orders": [], "cycle": 0}


def save_state(state: dict):
    STATE_FILE.write_text(json.dumps(state, indent=2, default=str))


# ── Main ─────────────────────────────────────────────────────────────

def run():
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    log.info("=" * 50)
    log.info(f"NEXUS GOLD — GitHub Actions Run @ {now}")
    log.info("=" * 50)

    state = load_state()
    state["cycle"] = state.get("cycle", 0) + 1

    client = BinanceClient()
    price  = client.get_price()
    bal    = client.get_balance()
    candles = client.get_candles(limit=100)

    log.info(f"Price : {price:.2f} USDT")
    log.info(f"USDT  : {bal['usdt']:.4f}")
    log.info(f"XAUT  : {bal['xaut']:.6f}")
    log.info(f"Cycle : #{state['cycle']}")

    # 1. ── ตรวจ SL/TP ถ้ามี position เปิดอยู่ ───────────────────────
    pos = state.get("position")
    if pos:
        entry = pos["entry"]
        side  = pos["side"]
        sl    = pos["sl"]
        tp    = pos["tp"]
        qty   = pos["quantity"]

        hit_sl = (side == "BUY"  and price <= sl) or \
                 (side == "SELL" and price >= sl)
        hit_tp = (side == "BUY"  and price >= tp) or \
                 (side == "SELL" and price <= tp)

        if hit_tp or hit_sl:
            reason = "TP" if hit_tp else "SL"
            close_side = "SELL" if side == "BUY" else "BUY"
            pnl = (price - entry) * qty if side == "BUY" else (entry - price) * qty

            log.info(f"{'✅' if hit_tp else '❌'} {reason} hit @ {price:.2f} | P&L: {pnl:+.4f}")
            result = client.place_market_order(close_side, qty)

            if result["success"]:
                # บันทึกลง orders history
                pos["status"]      = "CLOSED"
                pos["close_price"] = price
                pos["close_reason"]= reason
                pos["pnl"]         = round(pnl, 4)
                state.setdefault("orders", []).append(pos)
                state["position"] = None

                msg = close_message(side, entry, price, pnl, reason)
                notify(msg)
                save_state(state)
                log.info("Position closed and notified")
            return

    # 2. ── วิเคราะห์ Signal ─────────────────────────────────────────
    signal = generate_signal(candles)
    log.info(
        f"Signal : {signal.action} | Conf: {signal.confidence}% | "
        f"RSI: {signal.rsi:.1f} | Trend: {signal.trend}"
    )
    log.info(f"Reason : {signal.reason}")

    # 3. ── ส่ง Order ถ้า Signal ผ่านเงื่อนไข ─────────────────────────
    if signal.action != "HOLD" \
       and signal.confidence >= MIN_CONFIDENCE \
       and not state.get("position"):

        qty = round(ORDER_USDT / price, 4)
        sl  = round(price * (1 - STOP_LOSS_PCT / 100), 2)  \
              if signal.action == "BUY" else \
              round(price * (1 + STOP_LOSS_PCT / 100), 2)
        tp  = round(price * (1 + TAKE_PROFIT_PCT / 100), 2) \
              if signal.action == "BUY" else \
              round(price * (1 - TAKE_PROFIT_PCT / 100), 2)

        log.info(f"Executing {signal.action} | qty={qty} | SL={sl} | TP={tp}")
        result = client.place_market_order(signal.action, qty)

        if result["success"]:
            state["position"] = {
                "side":       signal.action,
                "entry":      price,
                "quantity":   qty,
                "sl":         sl,
                "tp":         tp,
                "confidence": signal.confidence,
                "reason":     signal.reason,
                "status":     "OPEN",
                "opened_at":  now,
            }
            msg = order_message(
                signal.action, price, qty, sl, tp, signal.confidence
            )
            notify(msg)
            log.info("Order executed and LINE notified")
        else:
            log.error(f"Order failed: {result.get('error')}")

    save_state(state)
    log.info("State saved. Done.")


if __name__ == "__main__":
    run()
