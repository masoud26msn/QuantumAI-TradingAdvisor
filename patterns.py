def detect_candlestick_patterns(df):
    patterns = []

    if len(df) < 3:
        return patterns

    last = df.iloc[-1]
    prev = df.iloc[-2]
    prev2 = df.iloc[-3]

    # Bullish Engulfing
    if prev["close"] < prev["open"] and last["close"] > last["open"] and last["close"] > prev["open"]:
        patterns.append("Bullish Engulfing")

    # Bearish Engulfing
    if prev["close"] > prev["open"] and last["close"] < last["open"] and last["close"] < prev["open"]:
        patterns.append("Bearish Engulfing")

    # Hammer
    body = abs(last["close"] - last["open"])
    lower_shadow = (last["open"] - last["low"]
                    ) if last["close"] > last["open"] else (last["close"] - last["low"])
    upper_shadow = last["high"] - max(last["close"], last["open"])
    if lower_shadow > 2 * body and upper_shadow < body:
        patterns.append("Hammer")

    # Shooting Star
    if upper_shadow > 2 * body and lower_shadow < body:
        patterns.append("Shooting Star")

    # Doji
    if body < (last["high"] - last["low"]) * 0.1:
        patterns.append("Doji")

    # Morning Star
    if prev2["close"] < prev2["open"] and prev["close"] < prev["open"] and last["close"] > last["open"] and last["close"] > (prev2["close"] + prev["close"]) / 2:
        patterns.append("Morning Star")

    # Evening Star
    if prev2["close"] > prev2["open"] and prev["close"] > prev["open"] and last["close"] < last["open"] and last["close"] < (prev2["close"] + prev["close"]) / 2:
        patterns.append("Evening Star")

    return patterns


def detect_pullbacks(df):
    pullbacks = 0
    last = df.iloc[-1]

    dist_ema20 = abs(last["close"] - last["ema20"]) / last["ema20"]
    dist_ema50 = abs(last["close"] - last["ema50"]) / last["ema50"]

    if dist_ema20 < 0.01 or dist_ema50 < 0.01:
        pullbacks += 1

    if last["close"] < last["bb_low"] * 1.01 or last["close"] > last["bb_high"] * 0.99:
        pullbacks += 1

    dist_sma200 = abs(last["close"] - last["sma200"]) / last["sma200"]
    if dist_sma200 < 0.015:
        pullbacks += 1

    return pullbacks


def detect_patterns_and_pullbacks(df):
    patterns = detect_candlestick_patterns(df)
    pullbacks = detect_pullbacks(df)
    return patterns, pullbacks
