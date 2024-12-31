# models/predict.py

import torch
import pandas as pd
import yaml
from data_storage.database import PriceData, NewsData, get_session
from sklearn.preprocessing import StandardScaler
import pickle
import logging

# Configure logging
logging.basicConfig(filename='predict.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

# Load configuration
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

MODEL_CONFIG = config['model']

# Define the neural network (must match the architecture used in training)
class BitcoinPredictor(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, output_size):
        super(BitcoinPredictor, self).__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, output_size)
        self.relu = nn.ReLU()
    
    def forward(self, x):
        out, _ = self.lstm(x)
        out = self.fc(self.relu(out[:, -1, :]))
        return out

def load_model():
    model = BitcoinPredictor(
        input_size=MODEL_CONFIG['input_size'],
        hidden_size=MODEL_CONFIG['hidden_size'],
        num_layers=MODEL_CONFIG['num_layers'],
        output_size=MODEL_CONFIG['output_size']
    )
    model.load_state_dict(torch.load('models/bitcoin_model.pth'))
    model.eval()
    return model

def load_scaler():
    with open('models/scaler.pkl', 'rb') as f:
        scaler = pickle.load(f)
    return scaler

def prepare_latest_data(scaler):
    session = get_session()
    # Fetch latest N minutes of price data
    N = 10
    price_records = session.query(PriceData).order_by(PriceData.timestamp.desc()).limit(N).all()
    price_df = pd.DataFrame([{
        'timestamp': record.timestamp,
        'close': record.close
    } for record in price_records])
    price_df = price_df.sort_values('timestamp')

    # Fetch latest news sentiment
    news_records = session.query(NewsData).filter(NewsData.timestamp >= price_df['timestamp'].min()).all()
    news_df = pd.DataFrame([{
        'timestamp': record.timestamp,
        'sentiment_score': record.sentiment_score
    } for record in news_records])

    # Aggregate sentiment
    if not news_df.empty:
        sentiment = news_df['sentiment_score'].mean()
    else:
        sentiment = 0.0

    # Prepare features
    features = price_df['close'].values[::-1]  # Last N closes
    feature_dict = {f'close_lag_{i}': features[i] for i in range(N)}
    feature_dict['sentiment_score'] = sentiment
    feature_df = pd.DataFrame([feature_dict])

    # Scale features
    scaled_features = scaler.transform(feature_df)
    return torch.tensor(scaled_features, dtype=torch.float32).unsqueeze(0)  # Shape: (1, 1, input_size)

def make_prediction(model, scaler):
    X = prepare_latest_data(scaler)
    with torch.no_grad():
        output = model(X)
        probability = torch.sigmoid(output).item()
        prediction = 1 if probability > 0.5 else 0
    logging.info(f'Prediction: {"Up" if prediction ==1 else "Down"}, Probability: {probability:.4f}')
    return prediction, probability

if __name__ == "__main__":
    model = load_model()
    scaler = load_scaler()
    prediction, probability = make_prediction(model, scaler)
    print(f'Prediction: {"Up" if prediction ==1 else "Down"}, Probability: {probability:.4f}')
