import psycopg2, os

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "crypto_bot")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")

def get_connection():
    return psycopg2.connect(host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD)

def insert_tick(symbol, price, volume, timestamp):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO crypto_ticks (symbol, price, volume, timestamp) VALUES (%s, %s, %s, %s)",
        (symbol, price, volume, timestamp)
    )
    conn.commit()
    cur.close()
    conn.close()

def insert_global_market(market, price, timestamp):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO global_markets (market, price, timestamp) VALUES (%s, %s, %s)",
        (market, price, timestamp)
    )
    conn.commit()
    cur.close()
    conn.close()

def insert_sentiment(coin, sentiment_score, timestamp):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO social_sentiment (coin, sentiment_score, timestamp) VALUES (%s, %s, %s)",
        (coin, sentiment_score, timestamp)
    )
    conn.commit()
    cur.close()
    conn.close()
