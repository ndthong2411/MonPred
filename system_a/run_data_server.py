import threading
from collectors import binance_collector, global_market_collector, sentiment_collector

if __name__ == '__main__':
    t1 = threading.Thread(target=binance_collector.start_binance_ws)
    t2 = threading.Thread(target=global_market_collector.run_global_market_collector)
    t3 = threading.Thread(target=sentiment_collector.run_sentiment_collector)
    
    t1.start()
    t2.start()
    t3.start()
    
    t1.join()
    t2.join()
    t3.join()
