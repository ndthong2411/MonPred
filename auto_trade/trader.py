# auto_trade/trader.py

from binance.client import Client
import yaml
import time
from models.predict import load_model, load_scaler, make_prediction
from data_storage.database import get_session
from datetime import datetime
import logging
from tenacity import retry, wait_fixed, stop_after_attempt
import threading

# Configure logging
logging.basicConfig(filename='auto_trade.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

# Load configuration
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

BINANCE_API_KEY = config['binance']['api_key']
BINANCE_API_SECRET = config['binance']['api_secret']
THRESHOLD_BUY = config['auto_trade']['threshold_buy']
THRESHOLD_SELL = config['auto_trade']['threshold_sell']
DAILY_PROFIT_TARGET = config['auto_trade']['daily_profit_target']
TRADE_AMOUNT_USDT = config['auto_trade']['trade_amount_usdt']

SYMBOL = 'BTCUSDT'

# Initialize Binance Client
client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)

class AutoTrader:
    def __init__(self):
        self.model = load_model()
        self.scaler = load_scaler()
        self.daily_profit = 0.0
        self.start_time = datetime.utcnow()
        self.symbol = SYMBOL
        self.trade_amount_usdt = TRADE_AMOUNT_USDT
        self.lock = threading.Lock()
        self.stop_event = threading.Event()
    
    @retry(wait=wait_fixed(5), stop=stop_after_attempt(3))
    def get_account_balance(self, asset):
        account = client.get_account()
        balances = {balance['asset']: float(balance['free']) for balance in account['balances']}
        return balances.get(asset, 0.0)
    
    @retry(wait=wait_fixed(5), stop=stop_after_attempt(3))
    def get_current_price(self):
        ticker = client.get_symbol_ticker(symbol=self.symbol)
        return float(ticker['price'])
    
    @retry(wait=wait_fixed(5), stop=stop_after_attempt(3))
    def execute_market_buy(self, quantity):
        try:
            order = client.order_market_buy(
                symbol=self.symbol,
                quantity=quantity
            )
            logging.info(f"Executed Market Buy: {order}")
            return order
        except Exception as e:
            logging.error(f"Error executing market buy: {e}")
            return None
    
    @retry(wait=wait_fixed(5), stop=stop_after_attempt(3))
    def execute_market_sell(self, quantity):
        try:
            order = client.order_market_sell(
                symbol=self.symbol,
                quantity=quantity
            )
            logging.info(f"Executed Market Sell: {order}")
            return order
        except Exception as e:
            logging.error(f"Error executing market sell: {e}")
            return None

    def execute_trade(self, prediction, probability):
        with self.lock:
            current_price = self.get_current_price()
            usdt_balance = self.get_account_balance('USDT')
            btc_balance = self.get_account_balance('BTC')

            if prediction >= THRESHOLD_BUY and usdt_balance >= self.trade_amount_usdt:
                # Calculate quantity to buy
                quantity = self.trade_amount_usdt / current_price
                quantity = round(quantity, 6)  # Binance requires specific precision
                order = self.execute_market_buy(quantity)
                if order:
                    # Update daily profit (simplistic approach)
                    self.daily_profit -= self.trade_amount_usdt
            elif prediction <= THRESHOLD_SELL and btc_balance >= 0.0001:
                # Calculate quantity to sell
                quantity = btc_balance
                quantity = round(quantity, 6)
                order = self.execute_market_sell(quantity)
                if order:
                    # Update daily profit (simplistic approach)
                    self.daily_profit += btc_balance * current_price

    def check_profit_target(self):
        elapsed_time = (datetime.utcnow() - self.start_time).total_seconds()
        if elapsed_time >= 86400:  # 24 hours
            if self.daily_profit >= DAILY_PROFIT_TARGET:
                logging.info("Daily profit target reached. Stopping trades for today.")
                self.stop_trading()
            # Reset daily profit and timer
            self.daily_profit = 0.0
            self.start_time = datetime.utcnow()
            logging.info("Daily profit target reset.")

    def run(self):
        logging.info("AutoTrader started.")
        while not self.stop_event.is_set():
            prediction, probability = make_prediction(self.model, self.scaler)
            logging.info(f"Prediction: {'Up' if prediction ==1 else 'Down'}, Probability: {probability:.4f}")

            # Execute trade based on prediction
            self.execute_trade(prediction, probability)

            # Check daily profit target
            self.check_profit_target()

            time.sleep(60)  # Wait for 1 minute before next prediction
        logging.info("AutoTrader stopped.")

    def stop_trading(self):
        self.stop_event.set()

def start_trading():
    trader = AutoTrader()
    trader_thread = threading.Thread(target=trader.run, daemon=True)
    trader_thread.start()
    logging.info("Trading thread started.")
    return trader

if __name__ == "__main__":
    trader = AutoTrader()
    trader.run()
