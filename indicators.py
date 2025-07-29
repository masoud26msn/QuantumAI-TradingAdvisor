import pandas as pd
import numpy as np


def calculate_indicators(df):
    # EMA
    df["ema20"] = df["close"].ewm(span=20, adjust=False).mean()
    df["ema50"] = df["close"].ewm(span=50, adjust=False).mean()
    df["sma200"] = df["close"].rolling(window=200).mean()

    # RSI
    delta = df["close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df["rsi"] = 100 - (100 / (1 + rs))

    # MACD
    ema12 = df["close"].ewm(span=12, adjust=False).mean()
    ema26 = df["close"].ewm(span=26, adjust=False).mean()
    df["macd"] = ema12 - ema26
    df["macd_signal"] = df["macd"].ewm(span=9, adjust=False).mean()

    # MFI
    typical_price = (df["high"] + df["low"] + df["close"]) / 3
    money_flow = typical_price * df["volume"]
    positive_flow = money_flow.where(
        typical_price > typical_price.shift(1), 0).rolling(window=14).sum()
    negative_flow = money_flow.where(
        typical_price < typical_price.shift(1), 0).rolling(window=14).sum()
    mfr = positive_flow / negative_flow
    df["mfi"] = 100 - (100 / (1 + mfr))

    # ADX (simple version)
    high = df["high"]
    low = df["low"]
    close = df["close"]

    plus_dm = high.diff()
    minus_dm = low.diff().abs()

    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm < 0] = 0

    tr = pd.concat([
        high - low,
        abs(high - close.shift()),
        abs(low - close.shift())
    ], axis=1).max(axis=1)

    atr = tr.rolling(14).mean()
    plus_di = 100 * (plus_dm.rolling(14).sum() / atr)
    minus_di = 100 * (minus_dm.rolling(14).sum() / atr)

    dx = 100 * (abs(plus_di - minus_di) / (plus_di + minus_di))
    df["adx"] = dx.rolling(14).mean()

    # Bollinger Bands
    df["bb_mid"] = df["close"].rolling(window=20).mean()
    df["bb_std"] = df["close"].rolling(window=20).std()
    df["bb_high"] = df["bb_mid"] + 2 * df["bb_std"]
    df["bb_low"] = df["bb_mid"] - 2 * df["bb_std"]

    # Stochastic %K and %D
    low_14 = low.rolling(14).min()
    high_14 = high.rolling(14).max()
    df["stoch_k"] = 100 * (df["close"] - low_14) / (high_14 - low_14)
    df["stoch_d"] = df["stoch_k"].rolling(3).mean()

    # CCI
    tp = typical_price
    ma_tp = tp.rolling(20).mean()
    md = tp.rolling(20).apply(lambda x: np.fabs(x - x.mean()).mean())
    df["cci"] = (tp - ma_tp) / (0.015 * md)

    # OBV
    obv = [0]
    for i in range(1, len(df)):
        if df["close"].iloc[i] > df["close"].iloc[i-1]:
            obv.append(obv[-1] + df["volume"].iloc[i])
        elif df["close"].iloc[i] < df["close"].iloc[i-1]:
            obv.append(obv[-1] - df["volume"].iloc[i])
        else:
            obv.append(obv[-1])
    df["obv"] = obv

    # VWAP
    df["vwap"] = (df["volume"] * (df["high"] + df["low"] +
                  df["close"]) / 3).cumsum() / df["volume"].cumsum()

    # Williams %R
    highest_high = high.rolling(14).max()
    lowest_low = low.rolling(14).min()
    df["willr"] = (highest_high - df["close"]) / \
        (highest_high - lowest_low) * -100

    # Ultimate Oscillator (simplified)
    bp = df["close"] - low.shift(1)
    tr = high.combine(low.shift(1), max) - low.combine(high.shift(1), min)
    avg7 = bp.rolling(7).sum() / tr.rolling(7).sum()
    avg14 = bp.rolling(14).sum() / tr.rolling(14).sum()
    avg28 = bp.rolling(28).sum() / tr.rolling(28).sum()
    df["ult_osc"] = 100 * (4 * avg7 + 2 * avg14 + avg28) / 7

    return df
