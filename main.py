import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd
from data_fetcher import get_ohlcv, get_price
from indicators import calculate_indicators
from patterns import detect_patterns_and_pullbacks
from trend_analysis import analyze_trend
from signal_generator import generate_signal

LOG_FILE = "signals_history.json"


def load_logs():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            return json.load(f)
    return []


def save_log(log_data):
    logs = load_logs()
    logs.append(log_data)
    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=2)


# Professional Trading UI Styling
st.markdown("""
<style>
:root {
    --primary: #2563eb;
    --primary-light: #3b82f6;
    --secondary: #4338ca;
    --accent: #10b981;
    --danger: #dc2626;
    --warning: #d97706;
    --bg-light: #f8fafc;
    --bg-card: #ffffff;
    --text-dark: #1e293b;
    --text-medium: #64748b;
    --border: #e2e8f0;
}

* {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    font-size: 14px;
}

body {
    background-color: var(--bg-light);
    color: var(--text-dark);
}

.stApp {
    background: transparent;
}

h1 {
    font-size: 1.8rem;
    font-weight: 700;
    color: var(--text-dark);
    margin-bottom: 0.5rem;
}

h2 {
    font-size: 1.5rem;
    font-weight: 600;
}

h3 {
    font-size: 1.3rem;
    font-weight: 600;
}

h4 {
    font-size: 1.1rem;
    font-weight: 600;
}

/* Card styling */
.custom-card {
    background: var(--bg-card);
    border-radius: 10px;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
    border: 1px solid var(--border);
    padding: 1.2rem;
    margin-bottom: 1.2rem;
}

/* Button styling */
.stButton>button {
    background-color: var(--primary);
    color: white;
    border: none;
    border-radius: 6px;
    padding: 0.6rem 1.2rem;
    font-weight: 500;
    font-size: 0.9rem;
    transition: all 0.2s ease;
}

.stButton>button:hover {
    background-color: var(--primary-light);
    transform: translateY(-1px);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* Signal indicators */
.buy-signal {
    border-left: 4px solid var(--accent);
    background-color: rgba(16, 185, 129, 0.05);
}

.sell-signal {
    border-left: 4px solid var(--danger);
    background-color: rgba(239, 68, 68, 0.05);
}

/* Input styling */
.stSelectbox, .stNumberInput, .stSlider {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
    padding: 0.4rem 0.8rem !important;
    font-size: 0.9rem !important;
}

/* Table styling */
.stDataFrame {
    background: var(--bg-card) !important;
    border-radius: 8px !important;
    border: 1px solid var(--border) !important;
    font-size: 0.85rem !important;
}

/* Metric styling */
.metric-value {
    font-size: 1.5rem;
    font-weight: 600;
    color: var(--primary);
    margin: 0.3rem 0;
}

.metric-label {
    color: var(--text-medium);
    font-size: 0.8rem;
    margin-bottom: 0.2rem;
}

/* Divider styling */
.custom-divider {
    height: 1px;
    background-color: var(--border);
    margin: 1.2rem 0;
    border: none;
}

/* Badge styling */
.status-badge {
    display: inline-block;
    padding: 0.2rem 0.5rem;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.5px;
}

.buy-badge {
    background-color: rgba(16, 185, 129, 0.1);
    color: var(--accent);
}

.sell-badge {
    background-color: rgba(239, 68, 68, 0.1);
    color: var(--danger);
}

/* Tabs styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 6px;
}

.stTabs [data-baseweb="tab"] {
    padding: 0.4rem 0.8rem !important;
    border-radius: 6px !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
}

.stTabs [aria-selected="true"] {
    background-color: var(--primary) !important;
    color: white !important;
}

/* Compact grid styling */
.grid-container {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 0.8rem;
}

.grid-item {
    background: var(--bg-card);
    border-radius: 8px;
    padding: 0.8rem;
    border: 1px solid var(--border);
}

/* Price display */
.price-display {
    font-size: 1.6rem;
    font-weight: 700;
    color: var(--primary);
}
</style>
""", unsafe_allow_html=True)

# App Layout
st.title("Quantum AI Trading Advisor")
st.markdown("""
<div class="custom-card" style="border-left: 4px solid var(--primary); padding: 1rem;">
    <p style="margin: 0; color: var(--text-medium); font-size: 0.9rem;">
    Advanced algorithmic trading system powered by quantum-inspired AI
    </p>
</div>
""", unsafe_allow_html=True)

# Sidebar with professional design
with st.sidebar:
    st.markdown("""
    <div class="custom-card" style="padding: 1rem;">
        <h3 style="margin-top: 0; font-size: 1.1rem;">Trading Parameters</h3>
    </div>
    """, unsafe_allow_html=True)

    # Expanded cryptocurrency list
    symbols = [
        "BTC-USDT", "ETH-USDT", "BNB-USDT", "SOL-USDT",
        "XRP-USDT", "ADA-USDT", "DOGE-USDT", "DOT-USDT",
        "MATIC-USDT", "AVAX-USDT", "LINK-USDT", "ATOM-USDT"
    ]
    symbol = st.selectbox("Trading Pair", symbols)
    timeframe = st.selectbox(
        "Timeframe", ["1m", "5m", "15m", "30m", "1h", "4h", "1d"])
    capital = st.number_input(
        "Capital (USDT)", min_value=10.0, value=5000.0, step=100.0)
    leverage = st.slider("Leverage", 1, 100, 10)

    st.markdown("""
    <div style="margin-top: 1.5rem; text-align: center;">
        <small style="color: var(--text-medium); font-size: 0.75rem;">Quantum AI v3.1</small>
    </div>
    """, unsafe_allow_html=True)

# Main content
if st.button("Run Quantum Analysis", use_container_width=True):
    try:
        price = get_price(symbol)
        df = get_ohlcv(symbol, timeframe)
        df = calculate_indicators(df)
        patterns, pullbacks = detect_patterns_and_pullbacks(df)
        trend_info = analyze_trend(df)

        signal = generate_signal(
            df=df,
            patterns=patterns,
            pullbacks=pullbacks,
            trend_info=trend_info,
            capital=capital,
            leverage=leverage,
            stop_loss_pct=0.01,
            take_profit_pct=0.015,
        )

        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "symbol": symbol,
            "timeframe": timeframe,
            "price": price,
            "signal": signal["recommendation"],
            "entry_price": signal["entry_price"],
            "stop_loss_price": signal["stop_loss"]["price"],
            "stop_loss_percent": signal["stop_loss"]["percent"],
            "take_profit_price": signal["take_profit"]["price"],
            "take_profit_percent": signal["take_profit"]["percent"],
            "position_size": signal["position_size"],
            "leverage": leverage,
            "capital": capital,
            "prediction_accuracy": signal.get("prediction_accuracy", "N/A"),
            "market_trend": trend_info.get("trend", "N/A")
        }
        save_log(log_entry)

        # Results display
        st.markdown(f"""
        <div class="custom-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h2 style="margin: 0; font-size: 1.3rem;">{symbol} Market Analysis</h2>
                <div style="text-align: right;">
                    <div style="color: var(--text-medium); font-size: 0.8rem;">Current Price</div>
                    <div class="price-display">{price:.2f} USDT</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            if signal["recommendation"].lower() == "buy":
                st.markdown(f"""
                <div class="custom-card buy-signal">
                    <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 0.8rem;">
                        <span class="status-badge buy-badge">BUY SIGNAL</span>
                    </div>
                    <div class="grid-container">
                        <div class="grid-item">
                            <div class="metric-label">Entry Price</div>
                            <div class="metric-value">{signal['entry_price']:.2f}</div>
                            <div class="metric-label">USDT</div>
                        </div>
                        <div class="grid-item">
                            <div class="metric-label">Position Size</div>
                            <div class="metric-value">{signal['position_size']:.4f}</div>
                            <div class="metric-label">{symbol.split('-')[0]}</div>
                        </div>
                        <div class="grid-item">
                            <div class="metric-label">Leverage</div>
                            <div style="font-size: 1.3rem; font-weight: 600; margin: 0.3rem 0; color: var(--text-dark);">{leverage}x</div>
                        </div>
                        <div class="grid-item">
                            <div class="metric-label">Capital</div>
                            <div style="font-size: 1.3rem; font-weight: 600; margin: 0.3rem 0; color: var(--text-dark);">{capital:.0f}</div>
                            <div class="metric-label">USDT</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="custom-card sell-signal">
                    <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 0.8rem;">
                        <span class="status-badge sell-badge">SELL SIGNAL</span>
                    </div>
                    <div class="grid-container">
                        <div class="grid-item">
                            <div class="metric-label">Entry Price</div>
                            <div class="metric-value">{signal['entry_price']:.2f}</div>
                            <div class="metric-label">USDT</div>
                        </div>
                        <div class="grid-item">
                            <div class="metric-label">Position Size</div>
                            <div class="metric-value">{signal['position_size']:.4f}</div>
                            <div class="metric-label">{symbol.split('-')[0]}</div>
                        </div>
                        <div class="grid-item">
                            <div class="metric-label">Leverage</div>
                            <div style="font-size: 1.3rem; font-weight: 600; margin: 0.3rem 0; color: var(--text-dark);">{leverage}x</div>
                        </div>
                        <div class="grid-item">
                            <div class="metric-label">Capital</div>
                            <div style="font-size: 1.3rem; font-weight: 600; margin: 0.3rem 0; color: var(--text-dark);">{capital:.0f}</div>
                            <div class="metric-label">USDT</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div class="custom-card">
                <h3 style="margin-top: 0; font-size: 1.1rem;">Risk Management</h3>
                <div class="grid-container">
                    <div class="grid-item">
                        <div class="metric-label">Stop Loss</div>
                        <div class="metric-value">{:.2f}</div>
                        <div class="metric-label">USDT ({})</div>
                    </div>
                    <div class="grid-item">
                        <div class="metric-label">Take Profit</div>
                        <div class="metric-value">{:.2f}</div>
                        <div class="metric-label">USDT ({})</div>
                    </div>
                    <div class="grid-item">
                        <div class="metric-label">Market Trend</div>
                        <div style="font-size: 1.3rem; font-weight: 600; margin: 0.3rem 0; color: var(--text-dark);">{}</div>
                    </div>
                    <div class="grid-item">
                        <div class="metric-label">Prediction</div>
                        <div style="font-size: 1.3rem; font-weight: 600; margin: 0.3rem 0; color: var(--text-dark);">{}</div>
                        <div class="metric-label">Accuracy</div>
                    </div>
                </div>
                <div style="margin-top: 1rem;">
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.8rem;">
                        <div>
                            <div style="color: var(--text-medium); font-weight: 500; font-size: 0.85rem;">Patterns:</div>
                            <div style="margin-top: 0.3rem; color: var(--text-dark); font-size: 0.85rem;">{}</div>
                        </div>
                        <div>
                            <div style="color: var(--text-medium); font-weight: 500; font-size: 0.85rem;">Pullbacks:</div>
                            <div style="margin-top: 0.3rem; color: var(--text-dark); font-size: 0.85rem;">{}</div>
                        </div>
                    </div>
                </div>
            </div>
            """.format(
                signal['stop_loss']['price'],
                signal['stop_loss']['percent'],
                signal['take_profit']['price'],
                signal['take_profit']['percent'],
                trend_info.get('trend', 'N/A'),
                signal.get('prediction_accuracy', 'N/A'),
                patterns,
                pullbacks
            ), unsafe_allow_html=True)

        # Divider
        st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

        # Logs section with tabs
        tab1, tab2 = st.tabs(["Signal History", "Performance Metrics"])

        with tab1:
            st.subheader("Signal History")
            logs = load_logs()
            if not logs:
                st.markdown("""
                <div class="custom-card" style="text-align: center; padding: 1rem;">
                    <p style="color: var(--text-medium); font-size: 0.9rem;">No signals recorded yet</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                df_logs = pd.DataFrame(logs)
                df_logs["timestamp"] = pd.to_datetime(
                    df_logs["timestamp"]).dt.tz_localize(None)

                # Apply color formatting
                def color_signal(val):
                    color = '#10b981' if val.lower() == 'buy' else '#ef4444'
                    return f'color: {color}; font-weight: 500;'

                styled_df = df_logs.sort_values(by="timestamp", ascending=False).style.applymap(
                    color_signal, subset=['signal'])

                st.dataframe(
                    styled_df,
                    use_container_width=True,
                    column_config={
                        "timestamp": "Time",
                        "symbol": "Pair",
                        "signal": "Signal",
                        "price": "Price",
                        "leverage": "Leverage"
                    },
                    hide_index=True
                )

        with tab2:
            st.subheader("Performance Metrics")
            if not logs:
                st.markdown("""
                <div class="custom-card" style="text-align: center; padding: 1rem;">
                    <p style="color: var(--text-medium); font-size: 0.9rem;">No performance data available yet</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                df_logs = pd.DataFrame(logs)
                if not df_logs.empty:
                    cols = st.columns(4)
                    metrics = [
                        ("Total Signals", len(df_logs), ""),
                        ("Buy Signals", len(
                            df_logs[df_logs['signal'].str.lower() == 'buy']), "buy-badge"),
                        ("Sell Signals", len(
                            df_logs[df_logs['signal'].str.lower() == 'sell']), "sell-badge"),
                        ("Avg Leverage",
                         f"{df_logs['leverage'].mean():.1f}x", "")
                    ]

                    for col, (label, value, badge_class) in zip(cols, metrics):
                        with col:
                            st.markdown(f"""
                            <div class="custom-card" style="text-align: center; padding: 0.8rem;">
                                <div class="metric-label">{label}</div>
                                <div style="font-size: 1.3rem; font-weight: 600; margin: 0.3rem 0; color: var(--{'accent' if badge_class == 'buy-badge' else 'danger' if badge_class == 'sell-badge' else 'primary'});">
                                    {value}
                                </div>
                                {f'<span class="status-badge {badge_class}" style="display: inline-block; margin-top: 0.2rem;">{label.split()[0].upper()}</span>' if badge_class else ''}
                            </div>
                            """, unsafe_allow_html=True)

                    st.markdown('<hr class="custom-divider">',
                                unsafe_allow_html=True)

                    st.markdown("""
                    <div class="custom-card">
                        <h4 style="margin-top: 0;">Advanced Analytics</h4>
                        <div style="color: var(--text-medium); font-size: 0.9rem;">
                            Quantum AI is analyzing your trading patterns...
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="custom-card" style="text-align: center; padding: 1rem;">
                        <p style="color: var(--text-medium); font-size: 0.9rem;">No performance data available yet</p>
                    </div>
                    """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Quantum analysis failed: {str(e)}")
        st.markdown("""
        <div class="custom-card">
            <p style="color: var(--danger); font-weight: 500; font-size: 0.9rem;">
            Quantum analysis engine encountered an error. Please check your connection and try again.
            </p>
        </div>
        """, unsafe_allow_html=True)
