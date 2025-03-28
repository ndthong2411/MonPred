import joblib, pandas as pd
from db.db_interface import get_connection

class Predictor:
    def __init__(self, model_file="model/model.pkl"):
        self.model = joblib.load(model_file)
    
    def predict_next(self, symbol):
        # Dummy predictor: Get last two ticks and compare change with model avg
        conn = get_connection()
        df = pd.read_sql(f"SELECT * FROM crypto_ticks WHERE symbol = '{symbol}' ORDER BY timestamp DESC LIMIT 10", conn)
        conn.close()
        if len(df) < 2:
            return -1  # Insufficient data, default to bearish
        last_change = df.iloc[0]['price'] - df.iloc[1]['price']
        return 1 if last_change > self.model["avg_change"] else -1

if __name__ == '__main__':
    predictor = Predictor()
    signal = predictor.predict_next("BTCUSDT")
    print("Prediction signal for BTCUSDT:", signal)
