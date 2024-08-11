from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

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

engine = create_engine('sqlite:///crypto_data.db')
Base.metadata.create_all(engine)

session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

# Session = sessionmaker(bind=engine)
# session = Session()