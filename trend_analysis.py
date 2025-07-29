def analyze_trend(df):
    last = df.iloc[-1]
    if last["ema20"] > last["ema50"] > last["sma200"]:
        trend = "Uptrend"
        strength = "Strong"
    elif last["ema20"] < last["ema50"] < last["sma200"]:
        trend = "Downtrend"
        strength = "Strong"
    else:
        trend = "Sideways"
        strength = "Weak"
    return {"trend": trend, "strength": strength}
