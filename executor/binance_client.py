"""
executor/binance_client.py
==========================
เชื่อมต่อ Binance TH API (api.binance.th)
ดึงราคา + ส่ง Order
"""

import time
import hmac
import hashlib
import pandas as pd
import requests
from config.settings import API_KEY, API_SECRET, SYMBOL, INTERVAL

BASE_URL = "https://api.binance.th"
RECV_WINDOW = 60000


class BinanceClient:

    def __init__(self):
        self.key = API_KEY
        self.secret = API_SECRET
        self.symbol = SYMBOL
        self._time_offset = 0
        self._sync_time()

    def _sync_time(self):
        st = requests.get(f"{BASE_URL}/api/v1/time", timeout=5).json()["serverTime"]
        self._time_offset = st - int(time.time() * 1000)

    def _timestamp(self):
        return int(time.time() * 1000) + self._time_offset

    def _sign(self, query: str) -> str:
        return hmac.new(self.secret.encode(), query.encode(), hashlib.sha256).hexdigest()

    def _get(self, path: str, params: dict = None, signed: bool = False):
        p = params or {}
        if signed:
            p["timestamp"] = self._timestamp()
            p["recvWindow"] = RECV_WINDOW
            qs = "&".join(f"{k}={v}" for k, v in p.items())
            qs += f"&signature={self._sign(qs)}"
        else:
            qs = "&".join(f"{k}={v}" for k, v in p.items())
        url = f"{BASE_URL}{path}?{qs}" if qs else f"{BASE_URL}{path}"
        r = requests.get(url, headers={"X-MBX-APIKEY": self.key}, timeout=10)
        r.raise_for_status()
        return r.json()

    def _post(self, path: str, params: dict):
        params["timestamp"] = self._timestamp()
        params["recvWindow"] = RECV_WINDOW
        qs = "&".join(f"{k}={v}" for k, v in params.items())
        qs += f"&signature={self._sign(qs)}"
        r = requests.post(
            f"{BASE_URL}{path}",
            data=qs,
            headers={"X-MBX-APIKEY": self.key, "Content-Type": "application/x-www-form-urlencoded"},
            timeout=10
        )
        r.raise_for_status()
        return r.json()

    def _delete(self, path: str, params: dict):
        params["timestamp"] = self._timestamp()
        params["recvWindow"] = RECV_WINDOW
        qs = "&".join(f"{k}={v}" for k, v in params.items())
        qs += f"&signature={self._sign(qs)}"
        r = requests.delete(
            f"{BASE_URL}{path}?{qs}",
            headers={"X-MBX-APIKEY": self.key},
            timeout=10
        )
        r.raise_for_status()
        return r.json()

    def get_candles(self, limit: int = 100) -> pd.DataFrame:
        """ดึง Candle ล่าสุด"""
        data = self._get("/api/v1/klines", {"symbol": self.symbol, "interval": INTERVAL, "limit": limit})
        df = pd.DataFrame(data, columns=[
            'time','open','high','low','close','volume',
            'close_time','qav','trades','tbav','tbqv','ignore'
        ])
        for col in ['open','high','low','close','volume']:
            df[col] = df[col].astype(float)
        df['time'] = pd.to_datetime(df['time'], unit='ms')
        return df[['time','open','high','low','close','volume']]

    def get_price(self) -> float:
        """ดึงราคาปัจจุบัน"""
        data = self._get("/api/v1/ticker/price", {"symbol": self.symbol})
        return float(data['price'])

    def get_balance(self) -> dict:
        """ดึง Balance USDT และ XAUT"""
        account = self._get("/api/v1/account", signed=True)
        balances = {b['asset']: float(b['free']) for b in account['balances']}
        return {
            'usdt': balances.get('USDT', 0.0),
            'xaut': balances.get('XAUT', 0.0),
            'thb':  balances.get('THB',  0.0),
        }

    def place_market_order(self, side: str, quantity: float) -> dict:
        """
        ส่ง Market Order
        side: 'BUY' หรือ 'SELL'
        quantity: จำนวน XAUT
        """
        try:
            order = self._post("/api/v1/order", {
                "symbol": self.symbol,
                "side": side,
                "type": "MARKET",
                "quantity": round(quantity, 4),
            })
            return {'success': True, 'order': order}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_open_orders(self) -> list:
        """ดึง Orders ที่ยังเปิดอยู่"""
        return self._get("/api/v1/openOrders", {"symbol": self.symbol}, signed=True)

    def cancel_order(self, order_id: int) -> dict:
        """ยกเลิก Order"""
        return self._delete("/api/v1/order", {"symbol": self.symbol, "orderId": order_id})
