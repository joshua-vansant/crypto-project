from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from datetime import datetime
import os


Base = declarative_base()

class BitcoinPriceData(Base):
    __tablename__ = 'bitcoin_prices'
    id = Column(Integer, primary_key=True)
    date = Column(DateTime)
    price = Column(Float)

class EthereumPriceData(Base):
    __tablename__ = 'ethereum_prices'
    id = Column(Integer, primary_key=True)
    date = Column(DateTime)
    price = Column(Float)

class TetherPriceData(Base):
    __tablename__ = 'tether_prices'
    id = Column(Integer, primary_key=True)
    date = Column(DateTime)
    price = Column(Float)

class RecipeTable(Base):
    __tablename__ = 'recipe_table'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    ingredients = Column(Text, nullable=False)
    instructions = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)

session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)