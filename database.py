from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

DATABASE_URL = "sqlite:///./stocks.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Stock(Base):
    __tablename__ = "stocks"
    symbol = Column(String, primary_key=True, index=True)
    name = Column(String)

class StockPrice(Base):
    __tablename__ = "stock_prices"
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    price = Column(Float)
    change_percent = Column(Float)
    status = Column(String)  # LOW, NORMAL, HIGH
    is_low = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    details = Column(String) # JSON string or text description of why it's low
    
    # Extended Details
    market_cap = Column(Float, nullable=True)
    volume = Column(Integer, nullable=True)
    open_price = Column(Float, nullable=True)
    day_high = Column(Float, nullable=True)
    day_low = Column(Float, nullable=True)
    fifty_two_week_high = Column(Float, nullable=True)
    fifty_two_week_low = Column(Float, nullable=True)
    pe_ratio = Column(Float, nullable=True)
    seven_day_avg = Column(Float, nullable=True)
    seven_day_low = Column(Float, nullable=True)
    two_fifty_day_low = Column(Float, nullable=True)
    two_fifty_day_avg = Column(Float, nullable=True)

def create_tables_and_seed():
    Base.metadata.create_all(bind=engine)
    
    # Pre-populate stocks if empty
    session = SessionLocal()
    try:
        if session.query(Stock).count() == 0:
            print("Seeding database with initial stocks...")
            initial_stocks = [
                ("RELIANCE.NS", "Reliance Industries"),
                ("TCS.NS", "Tata Consultancy Services"),
                ("INFY.NS", "Infosys"),
                ("HDFCBANK.NS", "HDFC Bank"),
                ("ICICIBANK.NS", "ICICI Bank"),
                ("SBIN.NS", "State Bank of India"),
                ("ITC.NS", "ITC Ltd"),
                ("LT.NS", "Larsen & Toubro"),
                ("AXISBANK.NS", "Axis Bank"),
                ("WIPRO.NS", "Wipro"),
                ("TATAGOLD.NS", "Tata Gold ETF")
            ]
            for symbol, name in initial_stocks:
                db_stock = Stock(symbol=symbol, name=name)
                session.add(db_stock)
            session.commit()
            print("Database seeded.")
        else:
            print("Database already seeded.")
    except Exception as e:
        print(f"Error seeding database: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    create_tables_and_seed()
