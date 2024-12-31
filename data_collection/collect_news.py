# data_collection/collect_news.py

import requests
from bs4 import BeautifulSoup
import yaml
from datetime import datetime
from data_storage.database import NewsData, get_session
from textblob import TextBlob
import logging
from urllib.parse import urljoin

# Configure logging
logging.basicConfig(filename='collect_news.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

# Load configuration
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

NEWS_SOURCES = config['data_collection']['news_sources']

def fetch_news(source_url):
    try:
        response = requests.get(source_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        # Parsing depends on the website's structure
        # Example for CoinDesk and CoinTelegraph
        if 'coindesk.com' in source_url:
            headlines = soup.find_all('h4', class_='headline')
        elif 'cointelegraph.com' in source_url:
            headlines = soup.find_all('a', class_='post-card-inline__title-link')
        else:
            headlines = []
        
        news = []
        for headline in headlines:
            title = headline.get_text(strip=True)
            link = headline.get('href')
            full_url = urljoin(source_url, link)
            content = fetch_article_content(full_url)
            sentiment = analyze_sentiment(content)
            news.append({
                'source': source_url,
                'title': title,
                'content': content,
                'sentiment_score': sentiment
            })
        return news
    except Exception as e:
        logging.error(f"Error fetching news from {source_url}: {e}")
        return []

def fetch_article_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        paragraphs = soup.find_all('p')
        content = ' '.join([para.get_text() for para in paragraphs])
        return content
    except Exception as e:
        logging.error(f"Error fetching article content from {url}: {e}")
        return ""

def analyze_sentiment(text):
    try:
        blob = TextBlob(text)
        return blob.sentiment.polarity  # Range: -1.0 (negative) to 1.0 (positive)
    except Exception as e:
        logging.error(f"Error analyzing sentiment: {e}")
        return 0.0

def save_news_data(news_list):
    if not news_list:
        return
    session = get_session()
    for news in news_list:
        news_entry = NewsData(
            timestamp=datetime.utcnow(),
            source=news['source'],
            title=news['title'],
            content=news['content'],
            sentiment_score=news['sentiment_score']
        )
        session.add(news_entry)
    session.commit()
    logging.info(f"Saved {len(news_list)} news articles.")

def collect_news():
    all_news = []
    for source in NEWS_SOURCES:
        news = fetch_news(source)
        all_news.extend(news)
    save_news_data(all_news)

if __name__ == "__main__":
    collect_news()
