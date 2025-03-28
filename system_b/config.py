import os

BINANCE_API_KEY = os.getenv("BINANCE_API_KEY", "your_api_key")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET", "your_api_secret")
USE_TESTNET = True  # Use Testnet mode by default

# Trading risk parameters
STOP_LOSS_PCT = 0.02        # 2% stop-loss from entry price
TAKE_PROFIT_PCT = 0.03      # Initial take-profit at 3% above entry
ADJUSTMENT_TARGET_PCT = 0.01  # Increase take-profit by 1% when adjusting

TRADE_AMOUNT_USD = 100      # USD amount per trade
