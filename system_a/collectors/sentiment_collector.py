import time
from db.db_interface import insert_sentiment
from cache_interface import set_sentiment

def compute_sentiment(text):
    # Dummy sentiment: return 0.5 if 'up' in text; else 0.0
    return 0.5 if 'up' in text.lower() else 0.0

def fetch_tweets():
    # Dummy tweet data; in production, use Tweepy
    return [{"text": "Bitcoin is going up!"}, {"text": "Market is stable."}]

def run_sentiment_collector():
    while True:
        tweets = fetch_tweets()
        sentiments = [compute_sentiment(tweet["text"]) for tweet in tweets]
        avg_sentiment = sum(sentiments) / len(sentiments)
        timestamp = time.time()
        # For example, track sentiment for BTC
        insert_sentiment("BTC", avg_sentiment, timestamp)
        set_sentiment("sentiment:BTC", avg_sentiment)
        print(f"Computed sentiment for BTC: {avg_sentiment}")
        time.sleep(60)  # every minute

if __name__ == '__main__':
    run_sentiment_collector()
