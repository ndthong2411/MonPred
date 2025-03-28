import pandas as pd, joblib
from db.db_interface import get_connection

def train_model():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM crypto_ticks", conn)
    conn.close()
    # Dummy feature: use average price change
    df = df.sort_values('timestamp')
    df['price_change'] = df['price'].diff()
    avg_change = df['price_change'].mean() if not df['price_change'].isnull().all() else 0
    model = {"avg_change": avg_change}
    joblib.dump(model, "model/model.pkl")
    print("Model trained. Average price change:", avg_change)

if __name__ == '__main__':
    train_model()
