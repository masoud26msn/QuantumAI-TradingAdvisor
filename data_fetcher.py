import requests
import pandas as pd


def get_price(symbol):
    url = f"https://www.okx.com/api/v5/market/ticker?instId={symbol}"
    resp = requests.get(url).json()
    if "data" in resp and len(resp["data"]) > 0:
        return float(resp["data"][0]["last"])
    else:
        raise Exception("Failed to get price")


def get_ohlcv(symbol, timeframe, limit=100):
    url = f"https://www.okx.com/api/v5/market/candles?instId={symbol}&bar={timeframe}&limit={limit}"
    resp = requests.get(url).json()
    if "data" in resp:
        data = resp["data"]
        # داده 9 ستون دارد:
        # timestamp, open, high, low, close, volume, tradeNum, baseVolume, quoteVolume
        df = pd.DataFrame(data, columns=[
            "timestamp", "open", "high", "low", "close", "volume",
            "tradeNum", "baseVolume", "quoteVolume"
        ])
        # تبدیل ستون‌های عددی به float
        for col in ["open", "high", "low", "close", "volume", "tradeNum", "baseVolume", "quoteVolume"]:
            df[col] = df[col].astype(float)
        df = df[::-1].reset_index(drop=True)
        # فقط ستون‌های مورد نیاز را برمی‌گردانیم
        return df[["timestamp", "open", "high", "low", "close", "volume"]]
    else:
        raise Exception("Failed to get OHLCV data")
