import yfinance as yf
from database import SessionLocal, Stock, StockPrice
from datetime import datetime
from fetcher import analyze_stock

def add_single_stock(symbol, name):
    session = SessionLocal()
    try:
        existing = session.query(Stock).filter(Stock.symbol == symbol).first()
        if not existing:
            new_stock = Stock(symbol=symbol, name=name)
            session.add(new_stock)
            session.commit()
            print(f"Added {name} ({symbol}) to Stock table.")
        
        print(f"Fetching data for {symbol}...")
        data = analyze_stock(symbol)
        if data:
            new_price = StockPrice(
                symbol=data["symbol"],
                price=data["price"],
                change_percent=data["change_percent"],
                status=data["status"],
                is_low=data["is_low"],
                details=data["details"],
                timestamp=datetime.utcnow(),
                market_cap=data.get("market_cap"),
                volume=data.get("volume"),
                open_price=data.get("open_price"),
                day_high=data.get("day_high"),
                day_low=data.get("day_low"),
                fifty_two_week_high=data.get("fifty_two_week_high"),
                fifty_two_week_low=data.get("fifty_two_week_low"),
                pe_ratio=data.get("pe_ratio"),
                seven_day_avg=data.get("seven_day_avg"),
                seven_day_low=data.get("seven_day_low"),
                two_fifty_day_low=data.get("two_fifty_day_low"),
                two_fifty_day_avg=data.get("two_fifty_day_avg")
            )
            session.add(new_price)
            session.commit()
            print(f"Successfully fetched and saved price for {symbol}: {data['price']}")
        else:
            print(f"Failed to fetch data for {symbol}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    add_single_stock("TATAGOLD.NS", "Tata Gold ETF")
