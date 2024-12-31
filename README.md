# Bitcoin Auto-Trade App

A comprehensive Bitcoin auto-trading application that collects real-time price data and news sentiment, trains a machine learning model to predict price movements, and executes trades on Binance based on these predictions. The application includes a user-friendly dashboard for monitoring and control.

## Features

- **Data Collection**: Real-time price data from Binance and news sentiment from CoinDesk and CoinTelegraph.
- **Data Storage**: Efficient storage using SQLite via SQLAlchemy.
- **Machine Learning**: LSTM-based PyTorch model for predicting Bitcoin price movements.
- **Auto Trading**: Executes buy/sell orders on Binance based on model predictions.
- **User Interface**: Interactive dashboard using Streamlit for monitoring and controlling the application.
- **Logging**: Comprehensive logging for monitoring and debugging.

## Requirements

- Python 3.7 or higher
- Binance Account with API keys
- Internet connection for data collection and trading

## Setup Instructions

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/bitcoin_autotrade_app.git
   cd bitcoin_autotrade_app
