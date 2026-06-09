"""
strategy/indicators.py
======================
คำนวณ Technical Indicators ทั้งหมด
"""

import pandas as pd
import numpy as np
from config.settings import EMA_FAST, EMA_SLOW, RSI_PERIOD, ATR_PERIOD


def calc_ema(series: pd.Series, period: int) -> pd.Series:
    """คำนวณ Exponential Moving Average"""
    return series.ewm(span=period, adjust=False).mean()


def calc_rsi(series: pd.Series, period: int = RSI_PERIOD) -> pd.Series:
    """คำนวณ Relative Strength Index"""
    delta = series.diff()
    gain  = delta.clip(lower=0)
    loss  = -delta.clip(upper=0)
    avg_gain = gain.ewm(com=period-1, adjust=False).mean()
    avg_loss = loss.ewm(com=period-1, adjust=False).mean()
    rs  = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(50)


def calc_atr(df: pd.DataFrame, period: int = ATR_PERIOD) -> pd.Series:
    """คำนวณ Average True Range"""
    high, low, close = df['high'], df['low'], df['close']
    tr = pd.concat([
        high - low,
        (high - close.shift()).abs(),
        (low  - close.shift()).abs()
    ], axis=1).max(axis=1)
    return tr.ewm(span=period, adjust=False).mean()


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """เพิ่ม Indicators ทั้งหมดลงใน DataFrame"""
    df = df.copy()
    df['ema_fast'] = calc_ema(df['close'], EMA_FAST)
    df['ema_slow'] = calc_ema(df['close'], EMA_SLOW)
    df['rsi']      = calc_rsi(df['close'], RSI_PERIOD)
    df['atr']      = calc_atr(df, ATR_PERIOD)
    df['trend']    = (df['ema_fast'] > df['ema_slow']).map({True: 'UP', False: 'DOWN'})
    return df
