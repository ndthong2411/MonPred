import time
from db.db_interface import insert_global_market
from cache_interface import set_global_market

def fetch_global_market_data():
    # Dummy: In production, fetch via API (e.g., yfinance)
    gold_price = 1800.0
    timestamp = time.time()
    insert_global_market("XAU", gold_price, timestamp)
    set_global_market("global:XAU", gold_price)
    print(f"Fetched global market data: Gold = {gold_price}")

def run_global_market_collector():
    while True:
        fetch_global_market_data()
        time.sleep(60)  # update every minute

if __name__ == '__main__':
    run_global_market_collector()
