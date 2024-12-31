# data_storage/database.py

from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import yaml
from datetime import datetime

# Load configuration
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

DATABASE_CONFIG = config['database']

Base = declarative_base()

class PriceData(Base):
    __tablename__ = 'price_data'
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, index=True, unique=True)
    symbol = Column(String)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float)

class NewsData(Base):
    __tablename__ = 'news_data'
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, index=True)
    source = Column(String)
    title = Column(String)
    content = Column(String)
    sentiment_score = Column(Float)

def get_engine():
    if DATABASE_CONFIG['type'] == 'sqlite':
        engine = create_engine(f"sqlite:///{DATABASE_CONFIG['name']}")
    else:
        raise ValueError("Unsupported database type.")
    return engine

def create_tables():
    engine = get_engine()
    Base.metadata.create_all(engine)

def get_session():
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    session = Session()
    return session
