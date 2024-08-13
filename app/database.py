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

DATABASE_URL = 'postgresql://render_1_ssjk_user:wwuDljEgJ5HoCD0D5HrCfBf5YK6crvCp@dpg-cqtd6raj1k6c738j8g30-a.oregon-postgres.render.com/render_1_ssjk'
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)

session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

# Session = sessionmaker(bind=engine)
# session = Session()