"""
bot.py
======
NEXUS GOLD — ไฟล์หลัก
รันคำสั่ง: python bot.py
"""

import time
import threading
from datetime import datetime

from config.settings import ANALYSIS_INTERVAL, SYMBOL, DASHBOARD_HOST, DASHBOARD_PORT
from executor.binance_client import BinanceClient
from executor.order_manager import OrderManager
from strategy.signals import generate_signal
from utils.logger import get_logger
from utils.notifier import notify, order_message
from dashboard.app import run_dashboard, update_state

log = get_logger("NEXUS-BOT")

PRICE_FEED_INTERVAL = 5  # push ราคาใหม่ทุก 5 วินาที


class NexusBot:

    def __init__(self):
        log.info("=" * 50)
        log.info("⚡ NEXUS GOLD BOT เริ่มต้น")
        log.info(f"   Symbol: {SYMBOL}")
        log.info(f"   วิเคราะห์ทุก {ANALYSIS_INTERVAL} วินาที")
        log.info(f"   Dashboard: http://localhost:{DASHBOARD_PORT}")
        log.info("=" * 50)

        self.client   = BinanceClient()
        self.manager  = OrderManager(self.client)
        self.running  = False
        self.cycle    = 0
        self.start_ts = time.time()
        self._last_signal_data = {}

    def _price_feed(self):
        """Push ราคาใหม่ทุก 5 วินาที โดยไม่รัน analysis"""
        while self.running:
            try:
                price = self.client.get_price()
                data = dict(self._last_signal_data)
                data["price"] = price
                data["uptime_sec"] = int(time.time() - self.start_ts)
                data["open_position"] = self.manager.open_position
                update_state(**data)
            except Exception:
                pass
            time.sleep(PRICE_FEED_INTERVAL)

    def run(self):
        self.running = True

        # เริ่ม price feed thread
        feed_thread = threading.Thread(target=self._price_feed, daemon=True)
        feed_thread.start()

        while self.running:
            try:
                self.cycle += 1
                now = datetime.now().strftime('%H:%M:%S')
                log.info(f"── Cycle #{self.cycle} ── {now} ──")

                # 1. ดึงราคาและ Candles
                price   = self.client.get_price()
                candles = self.client.get_candles(limit=100)
                log.info(f"ราคา XAUTUSDT: {price:.2f} USDT")

                # 2. ตรวจ SL/TP
                self.manager.check_position(price)

                # 3. วิเคราะห์ Signal
                signal = generate_signal(candles)
                log.info(
                    f"Signal: {signal.action} | "
                    f"Conf: {signal.confidence}% | "
                    f"RSI: {signal.rsi:.1f} | "
                    f"Trend: {signal.trend}"
                )
                log.info(f"เหตุผล: {signal.reason}")

                # 4. ดึง Balance
                bal = self.client.get_balance()

                # 5. คำนวณ SL/TP แสดงบน dashboard
                sl = self.manager.calc_sl(signal.action if signal.action != "HOLD" else "BUY", price)
                tp = self.manager.calc_tp(signal.action if signal.action != "HOLD" else "BUY", price)

                # 6. Push ไป dashboard + เก็บไว้ให้ price feed ใช้
                self._last_signal_data = dict(
                    signal=signal.action,
                    confidence=signal.confidence,
                    reason=signal.reason,
                    rsi=signal.rsi,
                    ema_fast=signal.ema_fast,
                    ema_slow=signal.ema_slow,
                    atr=signal.atr,
                    trend=signal.trend,
                    sl=sl,
                    tp=tp,
                    balance_usdt=bal["usdt"],
                    balance_xaut=bal["xaut"],
                    balance_thb=bal.get("thb", 0.0),
                    orders=self.manager.orders[-30:],
                    cycle=self.cycle,
                )
                update_state(
                    price=price,
                    uptime_sec=int(time.time() - self.start_ts),
                    open_position=self.manager.open_position,
                    **self._last_signal_data,
                )

                # 7. ส่ง Order ถ้ามี Signal
                if signal.action != "HOLD":
                    executed = self.manager.execute(signal)
                    if executed:
                        pos = self.manager.open_position
                        msg = order_message(
                            pos['side'], pos['entry'],
                            pos['quantity'], pos['sl'],
                            pos['tp'], pos['confidence']
                        )
                        notify(msg)

                log.info(f"รอ {ANALYSIS_INTERVAL} วินาที...")
                time.sleep(ANALYSIS_INTERVAL)

            except KeyboardInterrupt:
                log.info("หยุด Bot (Ctrl+C)")
                self.running = False

            except Exception as e:
                log.error(f"เกิดข้อผิดพลาด: {e}")
                log.info("รอ 30 วินาทีแล้วลองใหม่...")
                time.sleep(30)

    def stop(self):
        self.running = False
        log.info("🛑 Bot หยุดทำงาน")


if __name__ == "__main__":
    bot = NexusBot()

    # เริ่ม Dashboard ใน background thread
    dash_thread = threading.Thread(
        target=run_dashboard,
        kwargs={"host": DASHBOARD_HOST, "port": DASHBOARD_PORT},
        daemon=True
    )
    dash_thread.start()
    log.info(f"🌐 Dashboard เปิดที่ http://localhost:{DASHBOARD_PORT}")

    bot.run()
