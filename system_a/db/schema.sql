-- Table for Binance ticks
CREATE TABLE IF NOT EXISTS crypto_ticks (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10),
    price NUMERIC,
    volume NUMERIC,
    timestamp NUMERIC
);

-- Table for global market data
CREATE TABLE IF NOT EXISTS global_markets (
    id SERIAL PRIMARY KEY,
    market VARCHAR(10),
    price NUMERIC,
    timestamp NUMERIC
);

-- Table for social sentiment data
CREATE TABLE IF NOT EXISTS social_sentiment (
    id SERIAL PRIMARY KEY,
    coin VARCHAR(10),
    sentiment_score NUMERIC,
    timestamp NUMERIC
);
