import json, time, websocket
from db.db_interface import insert_tick
from cache_interface import set_price

BINANCE_WS_URL = "wss://stream.binance.com:9443/ws/!ticker@arr"

def on_message(ws, message):
    data = json.loads(message)
    for tick in data:
        symbol = tick.get('s')
        price = float(tick.get('c'))
        timestamp = time.time()
        # Store tick data in PostgreSQL
        insert_tick(symbol, price, tick.get('v', 0), timestamp)
        # Update Redis cache
        set_price(f"price:{symbol}", price)
        print(f"Tick: {symbol} @ {price}")

def on_error(ws, error):
    print("Binance WebSocket error:", error)

def on_close(ws):
    print("Binance WebSocket closed")

def on_open(ws):
    print("Connected to Binance WebSocket")

def start_binance_ws():
    ws = websocket.WebSocketApp(BINANCE_WS_URL,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()

if __name__ == '__main__':
    start_binance_ws()
