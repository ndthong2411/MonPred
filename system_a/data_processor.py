# Optional: Compute technical indicators or aggregate data
def compute_moving_average(prices, window=10):
    if len(prices) < window:
        return sum(prices) / len(prices)
    return sum(prices[-window:]) / window

if __name__ == '__main__':
    sample_prices = [30000, 30010, 30020, 30015, 30005]
    print("3-period moving average:", compute_moving_average(sample_prices, window=3))
