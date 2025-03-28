import time
from model.predictor import Predictor
from trading.strategy import Strategy
from trading.trader import Trader
from state import BotState
from config import BINANCE_API_KEY, BINANCE_API_SECRET, TRADE_AMOUNT_USD, STOP_LOSS_PCT, TAKE_PROFIT_PCT

# For retrieving latest price from Redis
def get_latest_price(symbol):
    from system_a.cache_interface import get_value
    price = get_value(f"price:{symbol}")
    return float(price) if price else None

def calculate_order_qty(price, trade_amount):
    return trade_amount / price

def main():
    predictor = Predictor()
    import system_b.config as config
    strategy = Strategy(config)
    trader = Trader(BINANCE_API_KEY, BINANCE_API_SECRET)
    state = BotState()
    symbol = "BTCUSDT"
    
    while True:
        current_price = get_latest_price(symbol)
        if current_price is None:
            time.sleep(1)
            continue

        # No open position: look for entry signal
        if not state.has_position(symbol):
            signal = predictor.predict_next(symbol)
            if strategy.check_entry_condition(signal, False):
                qty = calculate_order_qty(current_price, TRADE_AMOUNT_USD)
                print(f"Placing BUY order for {symbol} at {current_price}, quantity: {qty}")
                order = trader.buy(symbol, qty)
                if order:
                    # Set initial stop-loss and take-profit
                    stop_loss = current_price * (1 - STOP_LOSS_PCT)
                    take_profit = current_price * (1 + TAKE_PROFIT_PCT)
                    state.open_position(symbol, current_price, qty, stop_loss, take_profit)
                    print(f"Opened position for {symbol} at {current_price} | Stop-loss: {stop_loss}, Target: {take_profit}")
        else:
            # Position is open, monitor for exit or adjustment
            pos = state.get_position(symbol)
            # Get new prediction for potential adjustment
            prediction = predictor.predict_next(symbol)
            action, new_stop, new_target = strategy.check_trade_exit(pos.entry_price, current_price, pos.stop_loss, pos.take_profit, prediction)
            
            if action.startswith("SELL"):
                print(f"Action {action} triggered for {symbol} at price {current_price}")
                order = trader.sell(symbol, pos.quantity)
                if order:
                    state.close_position(symbol)
                    print(f"Closed position for {symbol} at {current_price}")
            elif action == "ADJUST":
                # Update the trade parameters (in-memory state)
                pos.stop_loss = new_stop
                pos.take_profit = new_target
                print(f"Adjusted position for {symbol}: New stop-loss = {new_stop}, New target = {new_target}")
            else:
                print(f"Holding position for {symbol}. Current price: {current_price} | Stop-loss: {pos.stop_loss} | Target: {pos.take_profit}")
        time.sleep(1)

if __name__ == '__main__':
    main()
