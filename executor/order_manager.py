"""
executor/order_manager.py
=========================
จัดการ Orders ทั้งหมด
คำนวณ SL/TP และ Position Size
"""

from config.settings import (
    ORDER_USDT, STOP_LOSS_PCT, TAKE_PROFIT_PCT, MIN_CONFIDENCE
)
from executor.binance_client import BinanceClient
from strategy.signals import Signal
from utils.logger import get_logger

log = get_logger("OrderManager")


class OrderManager:

    def __init__(self, client: BinanceClient):
        self.client = client
        self.orders = []          # ประวัติ Orders
        self.open_position = None # Position ที่เปิดอยู่

    def calc_quantity(self, price: float) -> float:
        """คำนวณจำนวน XAU จาก USDT"""
        return round(ORDER_USDT / price, 4)

    def calc_sl(self, side: str, entry: float) -> float:
        """คำนวณ Stop Loss"""
        if side == "BUY":
            return round(entry * (1 - STOP_LOSS_PCT / 100), 2)
        return round(entry * (1 + STOP_LOSS_PCT / 100), 2)

    def calc_tp(self, side: str, entry: float) -> float:
        """คำนวณ Take Profit"""
        if side == "BUY":
            return round(entry * (1 + TAKE_PROFIT_PCT / 100), 2)
        return round(entry * (1 - TAKE_PROFIT_PCT / 100), 2)

    def execute(self, signal: Signal) -> bool:
        """
        รับ Signal แล้วตัดสินใจส่ง Order
        คืนค่า True ถ้าส่ง Order สำเร็จ
        """
        if signal.action == "HOLD":
            log.info("Signal HOLD — ไม่ส่ง Order")
            return False

        if signal.confidence < MIN_CONFIDENCE:
            log.info(f"Confidence ต่ำเกินไป ({signal.confidence}%) — ข้าม")
            return False

        # ไม่เปิด Order ซ้อนกัน
        if self.open_position:
            log.info("มี Position เปิดอยู่แล้ว — ข้าม")
            return False

        qty = self.calc_quantity(signal.price)
        sl  = self.calc_sl(signal.action, signal.price)
        tp  = self.calc_tp(signal.action, signal.price)

        log.info(f"ส่ง {signal.action} {qty} XAU @ {signal.price:.2f}")
        log.info(f"SL: {sl} | TP: {tp} | Conf: {signal.confidence}%")

        result = self.client.place_market_order(signal.action, qty)

        if result['success']:
            order_data = {
                'id':         result['order'].get('orderId'),
                'side':       signal.action,
                'entry':      signal.price,
                'quantity':   qty,
                'sl':         sl,
                'tp':         tp,
                'confidence': signal.confidence,
                'reason':     signal.reason,
                'status':     'OPEN',
                'pnl':        0.0,
            }
            self.orders.append(order_data)
            self.open_position = order_data
            log.info(f"✅ Order สำเร็จ #{order_data['id']}")
            return True
        else:
            log.error(f"❌ Order ผิดพลาด: {result['error']}")
            return False

    def check_position(self, current_price: float):
        """ตรวจสอบว่าถึง SL หรือ TP แล้วหรือยัง"""
        if not self.open_position:
            return

        pos   = self.open_position
        side  = pos['side']
        entry = pos['entry']
        sl    = pos['sl']
        tp    = pos['tp']

        hit_sl = (side == "BUY"  and current_price <= sl) or \
                 (side == "SELL" and current_price >= sl)
        hit_tp = (side == "BUY"  and current_price >= tp) or \
                 (side == "SELL" and current_price <= tp)

        if hit_tp:
            self._close_position(current_price, "TP")
        elif hit_sl:
            self._close_position(current_price, "SL")

    def _close_position(self, close_price: float, reason: str):
        """ปิด Position"""
        pos  = self.open_position
        side = "SELL" if pos['side'] == "BUY" else "BUY"
        pnl  = (close_price - pos['entry']) * pos['quantity']
        if pos['side'] == "SELL":
            pnl = -pnl

        self.client.place_market_order(side, pos['quantity'])

        pos['status']      = 'CLOSED'
        pos['close_price'] = close_price
        pos['close_reason']= reason
        pos['pnl']         = round(pnl, 4)

        emoji = "✅" if pnl >= 0 else "❌"
        log.info(f"{emoji} ปิด Position ({reason}) | P&L: {pnl:+.4f} USDT")

        self.open_position = None
