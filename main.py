# main.py

import threading
import time
from data_collection.collect_prices import collect_prices
from data_collection.collect_news import collect_news
from models.train_model import train_model
import yaml
from data_storage.database import create_tables
import logging

# Configure logging
logging.basicConfig(filename='main.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

# Load configuration
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

PRICE_INTERVAL = config['data_collection']['price_interval_seconds']
NEWS_INTERVAL = config['data_collection']['news_collection_interval_seconds']

def start_price_collection():
    while True:
        collect_prices()
        time.sleep(PRICE_INTERVAL)

def start_news_collection():
    while True:
        collect_news()
        time.sleep(NEWS_INTERVAL)

def start_model_training():
    while True:
        logging.info("Starting model training.")
        train_model()
        # Retrain model daily or based on new data availability
        time.sleep(86400)  # Train once a day

def main():
    # Initialize database
    create_tables()
    logging.info("Database tables created or verified.")

    # Optionally, train the model initially
    # train_model()

    # Start data collection in separate threads
    price_thread = threading.Thread(target=start_price_collection, daemon=True)
    news_thread = threading.Thread(target=start_news_collection, daemon=True)
    model_thread = threading.Thread(target=start_model_training, daemon=True)

    price_thread.start()
    news_thread.start()
    model_thread.start()

    logging.info("Data collection threads started.")

    # Keep the main thread alive
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
