"""
config/settings.py — ทุน 1,500 บาท
เทรด 2 ครั้ง/วัน | Conf 78%+ | ทบทุนทุกเดือน
"""
import os
from dotenv import load_dotenv
load_dotenv()

API_KEY    = os.getenv("BINANCE_API_KEY", "")
API_SECRET = os.getenv("BINANCE_API_SECRET", "")

SYMBOL   = "XAUTUSDT"
INTERVAL = "5m"

# ── ทุน 1,500 บาท (~42 USDT) ──
ORDER_USDT  = 8.0      # 19% ของทุน — ปลอดภัย

EMA_FAST     = 9
EMA_SLOW     = 21
RSI_PERIOD   = 14
RSI_OB       = 65      # เข้มงวดขึ้น
RSI_OS       = 35
ATR_PERIOD   = 14

MIN_CONFIDENCE    = 78  # ต้อง 78%+ ถึงเทรด
ANALYSIS_INTERVAL = 600 # ทุก 10 นาที
CANDLE_LOOKBACK   = 100

STOP_LOSS_PCT     = 0.8
TAKE_PROFIT_PCT   = 1.8  # R:R = 1:2.25
MAX_EXPOSURE_PCT  = 20.0
MAX_DRAWDOWN_PCT  = 5.0

DASHBOARD_HOST = "0.0.0.0"
DASHBOARD_PORT = int(os.getenv("PORT", 5000))

NOTIFY_LINE       = True
LINE_CHANNEL_TOKEN  = os.getenv("LINE_CHANNEL_TOKEN", "")
LINE_USER_ID        = os.getenv("LINE_USER_ID", "")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET", "")
NOTIFY_TELEGRAM  = False
TELEGRAM_TOKEN   = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

LOG_LEVEL   = "INFO"
LOG_TO_FILE = True
LOG_DIR     = "logs"
