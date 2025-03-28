from binance.client import Client
from system_b.config import USE_TESTNET

class Trader:
    def __init__(self, api_key, api_secret):
        if USE_TESTNET:
            self.client = Client(api_key, api_secret, testnet=True)
        else:
            self.client = Client(api_key, api_secret)

    def buy(self, symbol, quantity):
        try:
            order = self.client.create_order(
                symbol=symbol,
                side=Client.SIDE_BUY,
                type=Client.ORDER_TYPE_MARKET,
                quantity=quantity
            )
            print(f"BUY order placed: {order}")
            return order
        except Exception as e:
            print("Buy order failed:", e)
            return None

    def sell(self, symbol, quantity):
        try:
            order = self.client.create_order(
                symbol=symbol,
                side=Client.SIDE_SELL,
                type=Client.ORDER_TYPE_MARKET,
                quantity=quantity
            )
            print(f"SELL order placed: {order}")
            return order
        except Exception as e:
            print("Sell order failed:", e)
            return None
