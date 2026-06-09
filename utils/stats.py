"""
utils/stats.py
==============
เก็บสถิติการเทรดทุกตัว
วิเคราะห์ Win Rate, P&L, Drawdown
"""

import json
from pathlib import Path
from datetime import datetime, timezone, timedelta

TRADES_FILE = Path(__file__).parent.parent / "trades.json"
TH_TZ = timezone(timedelta(hours=7))


# ── Load / Save ──────────────────────────────────────────────────────

def load_trades() -> list:
    if TRADES_FILE.exists():
        data = json.loads(TRADES_FILE.read_text())
        return data.get("trades", [])
    return []


def save_trades(trades: list):
    TRADES_FILE.write_text(json.dumps({"trades": trades}, indent=2, default=str))


# ── Record trade ─────────────────────────────────────────────────────

def record_open(position: dict, signal_data: dict) -> dict:
    """บันทึกเมื่อเปิด trade"""
    trades = load_trades()
    trade_id = len(trades) + 1
    now = datetime.now(TH_TZ).strftime("%Y-%m-%d %H:%M")

    trade = {
        "id":           trade_id,
        "side":         position["side"],
        "entry":        position["entry"],
        "entry_time":   now,
        "exit":         None,
        "exit_time":    None,
        "quantity":     position["quantity"],
        "order_usdt":   round(position["entry"] * position["quantity"], 4),
        "sl":           position["sl"],
        "tp":           position["tp"],
        "confidence":   position["confidence"],
        "rsi":          round(signal_data.get("rsi", 0), 1),
        "trend":        signal_data.get("trend", "--"),
        "ema_fast":     round(signal_data.get("ema_fast", 0), 2),
        "ema_slow":     round(signal_data.get("ema_slow", 0), 2),
        "reason":       position.get("reason", "--"),
        "result":       "OPEN",
        "pnl":          0.0,
        "pnl_pct":      0.0,
        "hold_min":     0,
    }
    trades.append(trade)
    save_trades(trades)
    return trade


def record_close(trade_id: int, exit_price: float, result: str):
    """บันทึกเมื่อปิด trade"""
    trades = load_trades()
    now = datetime.now(TH_TZ).strftime("%Y-%m-%d %H:%M")

    for t in trades:
        if t["id"] == trade_id:
            entry_dt = datetime.strptime(t["entry_time"], "%Y-%m-%d %H:%M")
            exit_dt  = datetime.strptime(now, "%Y-%m-%d %H:%M")
            hold_min = int((exit_dt - entry_dt).total_seconds() / 60)

            pnl = (exit_price - t["entry"]) * t["quantity"] \
                  if t["side"] == "BUY" else \
                  (t["entry"] - exit_price) * t["quantity"]
            pnl_pct = (pnl / t["order_usdt"]) * 100 if t["order_usdt"] else 0

            t["exit"]      = exit_price
            t["exit_time"] = now
            t["result"]    = result
            t["pnl"]       = round(pnl, 4)
            t["pnl_pct"]   = round(pnl_pct, 2)
            t["hold_min"]  = hold_min
            break

    save_trades(trades)


# ── Statistics ───────────────────────────────────────────────────────

def calc_stats(trades: list) -> dict:
    """คำนวณสถิติรวม"""
    closed = [t for t in trades if t["result"] in ("TP", "SL")]
    if not closed:
        return {"total": 0}

    wins   = [t for t in closed if t["result"] == "TP"]
    losses = [t for t in closed if t["result"] == "SL"]
    buys   = [t for t in closed if t["side"] == "BUY"]
    sells  = [t for t in closed if t["side"] == "SELL"]

    total_pnl  = sum(t["pnl"] for t in closed)
    win_pnl    = sum(t["pnl"] for t in wins)
    loss_pnl   = sum(t["pnl"] for t in losses)
    win_rate   = len(wins) / len(closed) * 100 if closed else 0

    # Max Drawdown
    cumulative = 0
    peak = 0
    max_dd = 0
    for t in closed:
        cumulative += t["pnl"]
        if cumulative > peak:
            peak = cumulative
        dd = peak - cumulative
        if dd > max_dd:
            max_dd = dd

    # Avg hold time
    avg_hold = sum(t["hold_min"] for t in closed) / len(closed) if closed else 0

    # Profit Factor
    gross_win  = abs(win_pnl)
    gross_loss = abs(loss_pnl)
    pf = gross_win / gross_loss if gross_loss > 0 else float('inf')

    # Best/Worst trade
    best  = max(closed, key=lambda x: x["pnl"])
    worst = min(closed, key=lambda x: x["pnl"])

    return {
        "total":      len(closed),
        "wins":       len(wins),
        "losses":     len(losses),
        "open":       len([t for t in trades if t["result"] == "OPEN"]),
        "win_rate":   round(win_rate, 1),
        "total_pnl":  round(total_pnl, 4),
        "win_pnl":    round(win_pnl, 4),
        "loss_pnl":   round(loss_pnl, 4),
        "max_dd":     round(max_dd, 4),
        "avg_hold":   int(avg_hold),
        "profit_factor": round(pf, 2),
        "best_trade": best,
        "worst_trade": worst,
        "buy_count":  len(buys),
        "sell_count": len(sells),
    }


def get_daily_trades(date_str: str = None) -> list:
    """ดึง trades ของวันที่ระบุ (YYYY-MM-DD) หรือวันนี้"""
    if not date_str:
        date_str = datetime.now(TH_TZ).strftime("%Y-%m-%d")
    return [t for t in load_trades() if t.get("entry_time", "").startswith(date_str)]


# ── Format Reports ───────────────────────────────────────────────────

def format_daily_report(date_str: str = None) -> str:
    """สร้าง LINE message รายวัน"""
    if not date_str:
        date_str = datetime.now(TH_TZ).strftime("%Y-%m-%d")

    all_trades  = load_trades()
    day_trades  = get_daily_trades(date_str)
    all_stats   = calc_stats(all_trades)
    day_closed  = [t for t in day_trades if t["result"] in ("TP", "SL")]
    day_pnl     = sum(t["pnl"] for t in day_closed)
    day_wins    = [t for t in day_closed if t["result"] == "TP"]
    day_losses  = [t for t in day_closed if t["result"] == "SL"]

    # format date Thai style
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d")
        date_th = d.strftime("%d/%m/%Y")
    except:
        date_th = date_str

    pnl_emoji = "📈" if day_pnl >= 0 else "📉"
    lines = [
        "📋 NEXUS GOLD — Daily Report",
        "═" * 26,
        f"📅 {date_th}",
        "",
        f"━━ วันนี้ ━━",
        f"🔢 เทรดทั้งหมด : {len(day_trades)} ครั้ง",
        f"✅ ชนะ (TP)   : {len(day_wins)} ครั้ง",
        f"❌ แพ้ (SL)   : {len(day_losses)} ครั้ง",
        f"{pnl_emoji} P&L วันนี้  : {day_pnl:+.4f} USDT",
        f"             ({day_pnl * 36:.1f} บาท)",
    ]

    # รายการเทรดวันนี้
    if day_closed:
        lines.append("")
        lines.append("━━ รายการวันนี้ ━━")
        for t in day_closed:
            r_emoji = "✅" if t["result"] == "TP" else "❌"
            lines.append(
                f"{r_emoji} {t['side']} @{t['entry']:.1f}"
                f" → {t['exit']:.1f}"
                f" ({t['pnl']:+.4f}) [{t['hold_min']}m]"
            )

    # สถิติรวมทั้งหมด
    if all_stats.get("total", 0) > 0:
        lines += [
            "",
            "━━ สถิติสะสม ━━",
            f"📊 เทรดรวม   : {all_stats['total']} ครั้ง",
            f"🎯 Win Rate  : {all_stats['win_rate']}%",
            f"💰 P&L รวม  : {all_stats['total_pnl']:+.4f} USDT",
            f"           ({all_stats['total_pnl'] * 36:.1f} บาท)",
            f"⚡ Profit F. : {all_stats['profit_factor']}x",
            f"📉 Max DD    : -{all_stats['max_dd']:.4f} USDT",
            f"⏱ ถือเฉลี่ย : {all_stats['avg_hold']} นาที",
        ]
        if all_stats.get("best_trade"):
            b = all_stats["best_trade"]
            lines.append(f"🏆 Best Trade: {b['side']} +{b['pnl']:.4f}")
        if all_stats.get("worst_trade"):
            w = all_stats["worst_trade"]
            lines.append(f"💔 Worst     : {w['side']} {w['pnl']:.4f}")
    else:
        lines += ["", "ยังไม่มีเทรดที่ปิดแล้ว"]

    lines += ["", "━" * 26, "⚡ NEXUS GOLD Bot — Auto Report"]
    return "\n".join(lines)


def format_trade_open(trade: dict) -> str:
    """ข้อความแจ้งเปิด trade"""
    se = "🟢" if trade["side"] == "BUY" else "🔴"
    return (
        f"{se} เปิด {trade['side']} #{trade['id']}\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"💰 ราคาเข้า : {trade['entry']:.2f} USDT\n"
        f"📦 จำนวน   : {trade['quantity']} XAUT\n"
        f"🛡 SL       : {trade['sl']:.2f}\n"
        f"🎯 TP       : {trade['tp']:.2f}\n"
        f"📊 Conf.   : {trade['confidence']}%\n"
        f"📈 RSI     : {trade['rsi']}\n"
        f"🧭 Trend   : {trade['trend']}\n"
        f"💡 {trade['reason']}"
    )


def format_trade_close(trade: dict) -> str:
    """ข้อความแจ้งปิด trade"""
    r_emoji = "✅" if trade["result"] == "TP" else "❌"
    pnl_emoji = "📈" if trade["pnl"] >= 0 else "📉"
    return (
        f"{r_emoji} ปิด {trade['side']} #{trade['id']} [{trade['result']}]\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"📍 เข้า    : {trade['entry']:.2f} USDT\n"
        f"📍 ออก    : {trade['exit']:.2f} USDT\n"
        f"{pnl_emoji} P&L     : {trade['pnl']:+.4f} USDT\n"
        f"         ({trade['pnl'] * 36:+.1f} บาท)\n"
        f"⏱ ถือ    : {trade['hold_min']} นาที\n"
        f"📊 P&L%  : {trade['pnl_pct']:+.2f}%"
    )
