# data_collection/collect_prices.py

import requests
import time
import yaml
from datetime import datetime
from data_storage.database import PriceData, get_session
from sqlalchemy.exc import IntegrityError
import logging

# Configure logging
logging.basicConfig(filename='collect_prices.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

# Load configuration
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

PRICE_INTERVAL = config['data_collection']['price_interval_seconds']
SYMBOL = 'BTCUSDT'

def get_binance_klines(symbol='BTCUSDT', interval='1m', limit=1):
    url = 'https://api.binance.com/api/v3/klines'
    params = {
        'symbol': symbol,
        'interval': interval,
        'limit': limit
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return data
    except Exception as e:
        logging.error(f"Error fetching klines: {e}")
        return None

def save_price_data(data):
    if not data:
        return
    session = get_session()
    for entry in data:
        price_entry = PriceData(
            timestamp=datetime.fromtimestamp(entry[0]/1000),
            symbol=SYMBOL,
            open=float(entry[1]),
            high=float(entry[2]),
            low=float(entry[3]),
            close=float(entry[4]),
            volume=float(entry[5])
        )
        try:
            session.add(price_entry)
            session.commit()
            logging.info(f"Saved price data for {price_entry.timestamp}")
        except IntegrityError:
            session.rollback()
            logging.warning(f"Duplicate entry detected for {price_entry.timestamp}. Skipping.")

def collect_prices():
    data = get_binance_klines(symbol=SYMBOL, interval='1m', limit=1)
    save_price_data(data)

if __name__ == "__main__":
    # Simple loop to collect data every minute
    while True:
        collect_prices()
        time.sleep(PRICE_INTERVAL)
