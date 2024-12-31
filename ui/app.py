# ui/app.py

import streamlit as st
import yaml
from models.predict import load_model, load_scaler, make_prediction
from auto_trade.trader import AutoTrader
import threading
import time
import pandas as pd
import plotly.express as px
from data_storage.database import PriceData, NewsData, get_session
from datetime import datetime, timedelta

# Load configuration
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

UI_CONFIG = config['ui']

# Initialize Streamlit page
st.set_page_config(page_title="Bitcoin Auto-Trade App", layout="wide")

st.title("Bitcoin Auto-Trade Application")

# Sidebar for controls
st.sidebar.header("Controls")

# Session state for trading
if 'trading' not in st.session_state:
    st.session_state['trading'] = False
    st.session_state['trader'] = None

def start_trading():
    if not st.session_state['trading']:
        trader = AutoTrader()
        trader_thread = threading.Thread(target=trader.run, daemon=True)
        trader_thread.start()
        st.session_state['trading'] = True
        st.session_state['trader'] = trader
        st.sidebar.success("Auto Trading Started.")

def stop_trading():
    if st.session_state['trading'] and st.session_state['trader']:
        st.session_state['trader'].stop_trading()
        st.session_state['trading'] = False
        st.sidebar.warning("Auto Trading Stopped.")

# Buttons to start/stop trading
if st.sidebar.button("Start Trading"):
    start_trading()

if st.sidebar.button("Stop Trading"):
    stop_trading()

# Display Trading Status
st.sidebar.header("Trading Status")
if st.session_state['trading']:
    st.sidebar.success("Auto Trading is Active.")
else:
    st.sidebar.info("Auto Trading is Inactive.")

# Live Prediction Section
st.header("Live Prediction")
model = load_model()
scaler = load_scaler()
prediction, probability = make_prediction(model, scaler)
st.write(f"**Prediction:** {'Up' if prediction ==1 else 'Down'}")
st.write(f"**Probability:** {probability:.2f}")

# Plot Recent Prices
st.header("Recent Prices")
session = get_session()
time_threshold = datetime.utcnow() - timedelta(hours=24)
price_records = session.query(PriceData).filter(PriceData.timestamp >= time_threshold).order_by(PriceData.timestamp).all()
price_df = pd.DataFrame([{
    'timestamp': record.timestamp,
    'close': record.close
} for record in price_records])

if not price_df.empty:
    fig = px.line(price_df, x='timestamp', y='close', title='BTC/USDT Closing Prices (Last 24 Hours)')
    st.plotly_chart(fig)
else:
    st.write("No price data available.")

# Display Recent News Sentiment
st.header("Recent News Sentiment")
news_records = session.query(NewsData).filter(NewsData.timestamp >= time_threshold).order_by(NewsData.timestamp.desc()).limit(20).all()
news_df = pd.DataFrame([{
    'timestamp': record.timestamp,
    'title': record.title,
    'sentiment_score': record.sentiment_score
} for record in news_records])

if not news_df.empty:
    news_df['sentiment'] = news_df['sentiment_score'].apply(lambda x: 'Positive' if x > 0 else ('Negative' if x < 0 else 'Neutral'))
    st.table(news_df[['timestamp', 'title', 'sentiment']])
else:
    st.write("No news data available.")

# Display Trading Logs
st.header("Trading Logs")
try:
    with open('auto_trade.log', 'r') as f:
        logs = f.readlines()[-100:]
    logs = ''.join(logs)
    st.text_area("Logs", logs, height=300)
except FileNotFoundError:
    st.write("No logs available.")

# Additional Features: Setting thresholds, viewing trading history, etc., can be added here.
