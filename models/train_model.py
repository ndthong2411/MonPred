# models/train_model.py

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import pandas as pd
import yaml
from data_storage.database import PriceData, NewsData, get_session
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import logging
import pickle

# Configure logging
logging.basicConfig(filename='train_model.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

# Load configuration
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

MODEL_CONFIG = config['model']

# Define the dataset
class BitcoinDataset(Dataset):
    def __init__(self, dataframe, scaler):
        self.X = scaler.transform(dataframe.drop('target', axis=1).values)
        self.y = dataframe['target'].values
        self.X = torch.tensor(self.X, dtype=torch.float32)
        self.y = torch.tensor(self.y, dtype=torch.float32).unsqueeze(1)

    def __len__(self):
        return len(self.y)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]

# Define the neural network
class BitcoinPredictor(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, output_size):
        super(BitcoinPredictor, self).__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, output_size)
        self.relu = nn.ReLU()
    
    def forward(self, x):
        # x shape: (batch, seq_length, input_size)
        out, _ = self.lstm(x)
        out = self.fc(self.relu(out[:, -1, :]))
        return out

def prepare_data():
    session = get_session()
    # Fetch price data
    price_records = session.query(PriceData).order_by(PriceData.timestamp).all()
    price_df = pd.DataFrame([{
        'timestamp': record.timestamp,
        'open': record.open,
        'high': record.high,
        'low': record.low,
        'close': record.close,
        'volume': record.volume
    } for record in price_records])

    # Calculate target: 1 if price increases next interval, else 0
    price_df['target'] = (price_df['close'].shift(-1) > price_df['close']).astype(int)
    price_df.dropna(inplace=True)

    # Fetch news data and aggregate sentiment
    news_records = session.query(NewsData).filter(NewsData.timestamp >= price_df['timestamp'].min()).all()
    news_df = pd.DataFrame([{
        'timestamp': record.timestamp,
        'sentiment_score': record.sentiment_score
    } for record in news_records])

    # Aggregate sentiment by timestamp (average sentiment per minute)
    news_df.set_index('timestamp', inplace=True)
    news_agg = news_df.resample('1Min').mean().reset_index()
    price_df = pd.merge(price_df, news_agg, on='timestamp', how='left')
    price_df['sentiment_score'].fillna(0, inplace=True)  # Fill missing sentiment with 0

    # Feature engineering: use previous N minutes' data
    N = 10  # Number of previous minutes to consider
    for i in range(1, N+1):
        price_df[f'close_lag_{i}'] = price_df['close'].shift(i)
    price_df.dropna(inplace=True)

    feature_cols = [f'close_lag_{i}' for i in range(1, N+1)] + ['sentiment_score']
    scaler = StandardScaler()
    price_df_features = price_df[feature_cols]
    scaler.fit(price_df_features)

    # Save the scaler
    with open('models/scaler.pkl', 'wb') as f:
        pickle.dump(scaler, f)
    logging.info("Scaler saved.")

    # Prepare dataset
    dataset = BitcoinDataset(price_df[feature_cols + ['target']], scaler)
    return dataset, scaler

def train_model():
    dataset, scaler = prepare_data()
    train_size = int(0.8 * len(dataset))
    test_size = len(dataset) - train_size
    train_dataset, test_dataset = torch.utils.data.random_split(dataset, [train_size, test_size])

    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)

    model = BitcoinPredictor(
        input_size=MODEL_CONFIG['input_size'],
        hidden_size=MODEL_CONFIG['hidden_size'],
        num_layers=MODEL_CONFIG['num_layers'],
        output_size=MODEL_CONFIG['output_size']
    )

    criterion = nn.BCEWithLogitsLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=MODEL_CONFIG['learning_rate'])

    for epoch in range(MODEL_CONFIG['num_epochs']):
        model.train()
        running_loss = 0.0
        for X_batch, y_batch in train_loader:
            X_batch = X_batch.unsqueeze(1)  # Adding sequence dimension
            outputs = model(X_batch)
            loss = criterion(outputs, y_batch)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            running_loss += loss.item()
        
        avg_loss = running_loss / len(train_loader)
        
        # Evaluation
        model.eval()
        correct = 0
        total = 0
        with torch.no_grad():
            for X_batch, y_batch in test_loader:
                X_batch = X_batch.unsqueeze(1)
                outputs = model(X_batch)
                predicted = (torch.sigmoid(outputs) > 0.5).float()
                total += y_batch.size(0)
                correct += (predicted == y_batch).sum().item()
        accuracy = correct / total
        logging.info(f'Epoch [{epoch+1}/{MODEL_CONFIG["num_epochs"]}], Loss: {avg_loss:.4f}, Accuracy: {accuracy:.4f}')

    # Save the model
    torch.save(model.state_dict(), 'models/bitcoin_model.pth')
    logging.info("Model trained and saved.")

if __name__ == "__main__":
    train_model()
