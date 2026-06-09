"""
run_once.py
===========
GitHub Actions version — รันครั้งเดียวแล้วจบ
State เก็บใน state.json | Trade history ใน trades.json
"""

import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

from executor.binance_client import BinanceClient
from strategy.signals import generate_signal
from utils.notifier import notify
from utils.stats import (
    record_open, record_close, load_trades,
    format_daily_report, format_trade_open, format_trade_close,
    calc_stats, get_daily_trades
)
from utils.logger import get_logger
from config.settings import MIN_CONFIDENCE, ORDER_USDT, STOP_LOSS_PCT, TAKE_PROFIT_PCT

log      = get_logger("NEXUS-ACTION")
STATE_F  = Path(__file__).parent / "state.json"
TH_TZ    = timezone(timedelta(hours=7))


# ── State helpers ─────────────────────────────────────────────────────

def load_state() -> dict:
    if STATE_F.exists():
        return json.loads(STATE_F.read_text())
    return {"position": None, "cycle": 0, "last_daily": ""}


def save_state(s: dict):
    STATE_F.write_text(json.dumps(s, indent=2, default=str))


# ── Main ──────────────────────────────────────────────────────────────

def run():
    now_th  = datetime.now(TH_TZ)
    now_str = now_th.strftime("%Y-%m-%d %H:%M ICT")
    today   = now_th.strftime("%Y-%m-%d")

    log.info("=" * 50)
    log.info(f"NEXUS GOLD — GitHub Actions @ {now_str}")
    log.info("=" * 50)

    state = load_state()
    state["cycle"] = state.get("cycle", 0) + 1

    client  = BinanceClient()
    price   = client.get_price()
    bal     = client.get_balance()
    candles = client.get_candles(limit=100)
    signal  = generate_signal(candles)

    log.info(f"Price  : {price:.2f} | USDT: {bal['usdt']:.4f} | XAUT: {bal['xaut']:.6f}")
    log.info(f"Signal : {signal.action} ({signal.confidence}%) | RSI:{signal.rsi:.1f} | {signal.trend}")
    log.info(f"Cycle  : #{state['cycle']}")

    # ── 1. ตรวจ SL/TP ────────────────────────────────────────────────
    pos = state.get("position")
    if pos:
        entry    = pos["entry"]
        side     = pos["side"]
        trade_id = pos.get("trade_id", 0)

        hit_tp = (side == "BUY"  and price >= pos["tp"]) or \
                 (side == "SELL" and price <= pos["tp"])
        hit_sl = (side == "BUY"  and price <= pos["sl"]) or \
                 (side == "SELL" and price >= pos["sl"])

        if hit_tp or hit_sl:
            reason     = "TP" if hit_tp else "SL"
            close_side = "SELL" if side == "BUY" else "BUY"
            result     = client.place_market_order(close_side, pos["quantity"])

            if result["success"]:
                record_close(trade_id, price, reason)
                trades    = load_trades()
                closed_t  = next((t for t in trades if t["id"] == trade_id), None)
                if closed_t:
                    notify(format_trade_close(closed_t))
                state["position"] = None
                log.info(f"{reason} hit @ {price:.2f} | trade #{trade_id} closed")
            save_state(state)
            _check_daily_summary(state, today, now_th)
            return

    # ── 2. เปิด Order ใหม่ ───────────────────────────────────────────
    if signal.action != "HOLD" \
       and signal.confidence >= MIN_CONFIDENCE \
       and not state.get("position"):

        qty = round(ORDER_USDT / price, 4)
        sl  = round(price * (1 - STOP_LOSS_PCT / 100),  2) if signal.action == "BUY" \
              else round(price * (1 + STOP_LOSS_PCT / 100),  2)
        tp  = round(price * (1 + TAKE_PROFIT_PCT / 100), 2) if signal.action == "BUY" \
              else round(price * (1 - TAKE_PROFIT_PCT / 100), 2)

        result = client.place_market_order(signal.action, qty)
        if result["success"]:
            pos_data = {
                "side": signal.action, "entry": price,
                "quantity": qty, "sl": sl, "tp": tp,
                "confidence": signal.confidence, "reason": signal.reason,
            }
            trade = record_open(pos_data, {
                "rsi": signal.rsi, "trend": signal.trend,
                "ema_fast": signal.ema_fast, "ema_slow": signal.ema_slow,
            })
            pos_data["trade_id"] = trade["id"]
            state["position"] = pos_data
            notify(format_trade_open(trade))
            log.info(f"Order #{trade['id']} opened: {signal.action} {qty} @ {price:.2f}")

    # ── 3. Hourly status (ทุก 6 รอบ = 1 ชั่วโมง) ────────────────────
    if state["cycle"] % 6 == 0:
        _send_hourly(price, bal, signal, state)

    # ── 4. Daily summary ──────────────────────────────────────────────
    _check_daily_summary(state, today, now_th)

    save_state(state)
    log.info("Done.")


def _send_hourly(price, bal, signal, state):
    se  = "🟢" if signal.action=="BUY" else "🔴" if signal.action=="SELL" else "🟡"
    pos = state.get("position")
    pos_text = "ไม่มี"
    if pos:
        pnl = (price - pos["entry"]) * pos["quantity"] \
              if pos["side"] == "BUY" else (pos["entry"] - price) * pos["quantity"]
        pos_text = f'{pos["side"]} @{pos["entry"]:.2f} (P&L:{pnl:+.4f})'

    stats = calc_stats(load_trades())
    wr_text = f"{stats['win_rate']}% ({stats['wins']}W/{stats['losses']}L)" \
              if stats.get("total", 0) > 0 else "ยังไม่มีข้อมูล"

    notify(
        f"⚡ NEXUS GOLD — Hourly\n"
        f"{'─'*24}\n"
        f"💰 {price:.2f} USDT\n"
        f"{se} {signal.action} ({signal.confidence}%) RSI:{signal.rsi:.1f}\n"
        f"💵 USDT: {bal['usdt']:.4f}\n"
        f"📋 Position: {pos_text}\n"
        f"🎯 Win Rate: {wr_text}\n"
        f"🔄 Cycle #{state['cycle']}"
    )


def _check_daily_summary(state, today, now_th):
    """ส่ง Daily Summary เวลา 23:00-23:10 ไทย (ทุกคืน)"""
    hour   = now_th.hour
    last   = state.get("last_daily", "")
    if hour == 23 and last != today:
        report = format_daily_report(today)
        notify(report)
        state["last_daily"] = today
        log.info("Daily summary sent")


if __name__ == "__main__":
    run()
