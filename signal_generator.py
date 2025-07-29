import random


def generate_signal(df, patterns, pullbacks, trend_info, capital, leverage, stop_loss_pct=0.01, take_profit_pct=0.015):
    last = df.iloc[-1]
    entry_price = last["close"]

    stop_loss_price = entry_price * (1 - stop_loss_pct)
    take_profit_price = entry_price * (1 + take_profit_pct)

    position_size = (capital * leverage) / entry_price

    score = 50
    if last["rsi"] < 30:
        score += 10
    if last["rsi"] > 70:
        score -= 10
    if last["macd"] > last["macd_signal"]:
        score += 10
    if last["macd"] < last["macd_signal"]:
        score -= 10
    if last["mfi"] < 20:
        score += 10
    if last["mfi"] > 80:
        score -= 10
    if trend_info["trend"] == "Uptrend":
        score += 10
    if trend_info["trend"] == "Downtrend":
        score -= 10

    score += pullbacks * 5

    score = max(0, min(100, score))

    recommendation = "Buy" if score >= 50 else "Sell"

    community_score = random.randint(40, 60)

    signal = {
        "recommendation": recommendation,
        "entry_price": round(entry_price, 4),
        "stop_loss": {
            "price": round(stop_loss_price, 4),
            "percent": f"{stop_loss_pct*100:.2f}%"
        },
        "take_profit": {
            "price": round(take_profit_price, 4),
            "percent": f"{take_profit_pct*100:.2f}%"
        },
        "patterns_detected": patterns,
        "pullbacks_count": pullbacks,
        "trend_info": trend_info,
        "recommended_leverage": leverage,
        "position_size": round(position_size, 4),
        "prediction_accuracy": score,
        "community_score": community_score
    }

    return signal
