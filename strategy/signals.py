"""
strategy/signals.py
===================
Logic การตัดสิน BUY / SELL / HOLD
"""

import pandas as pd
from dataclasses import dataclass
from config.settings import RSI_OB, RSI_OS, MIN_CONFIDENCE
from strategy.indicators import add_indicators


@dataclass
class Signal:
    action:     str    # BUY | SELL | HOLD
    confidence: int    # 0-100
    reason:     str
    price:      float
    ema_fast:   float
    ema_slow:   float
    rsi:        float
    atr:        float
    trend:      str


def generate_signal(df: pd.DataFrame) -> Signal:
    """
    วิเคราะห์และสร้าง Signal จาก Candle DataFrame
    """
    if len(df) < 35:
        return Signal("HOLD", 0, "ข้อมูลไม่เพียงพอ", 0, 0, 0, 50, 0, "--")

    df = add_indicators(df)
    row  = df.iloc[-1]
    prev = df.iloc[-2]

    price    = float(row['close'])
    ema_fast = float(row['ema_fast'])
    ema_slow = float(row['ema_slow'])
    rsi      = float(row['rsi'])
    atr      = float(row['atr'])
    trend    = str(row['trend'])

    prev_ef  = float(prev['ema_fast'])
    prev_es  = float(prev['ema_slow'])

    cross_up   = prev_ef <= prev_es and ema_fast > ema_slow
    cross_down = prev_ef >= prev_es and ema_fast < ema_slow

    # ── ตัดสิน Signal ────────────────────────────────────────────
    action     = "HOLD"
    confidence = 0
    reason     = ""

    if cross_up and rsi < RSI_OB:
        action     = "BUY"
        confidence = 78 + (10 if rsi < 50 else 0)
        reason     = f"EMA{9}×EMA{21} ตัดขึ้น | RSI {rsi:.1f}"

    elif cross_down and rsi > RSI_OS:
        action     = "SELL"
        confidence = 78 + (10 if rsi > 50 else 0)
        reason     = f"EMA{9}×EMA{21} ตัดลง | RSI {rsi:.1f}"

    elif trend == "UP" and rsi < 38:
        action     = "BUY"
        confidence = 62
        reason     = f"Trend ขาขึ้น + RSI Oversold {rsi:.1f}"

    elif trend == "DOWN" and rsi > 62:
        action     = "SELL"
        confidence = 62
        reason     = f"Trend ขาลง + RSI Overbought {rsi:.1f}"

    else:
        reason = f"Trend: {trend} | RSI: {rsi:.1f} | รอ Signal ที่ชัดขึ้น"

    confidence = min(confidence, 95)

    return Signal(
        action=action,
        confidence=confidence,
        reason=reason,
        price=price,
        ema_fast=ema_fast,
        ema_slow=ema_slow,
        rsi=rsi,
        atr=atr,
        trend=trend,
    )
