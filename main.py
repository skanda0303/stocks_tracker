from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import SessionLocal, Stock, StockPrice, engine, Base
from scheduler import start_scheduler
import fetcher
import uvicorn

app = FastAPI(title="Stock Price Tracker")

# CORS (Allow local dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Start Scheduler
@app.on_event("startup")
def startup_event():
    # Ensure DB is init and seeded
    from database import create_tables_and_seed
    create_tables_and_seed()
    
    # Send Startup Message to Telegram
    try:
        from notifier import send_telegram_message
        from database import SessionLocal, Stock, StockPrice
        db = SessionLocal()
        stocks = db.query(Stock).all()
        
        message_lines = ["\ud83d\ude80 <b>Server Started! Initial Stock Report:</b>\n"]
        for stock in stocks:
            latest = db.query(StockPrice).filter(StockPrice.symbol == stock.symbol).order_by(StockPrice.timestamp.desc()).first()
            if latest:
                message_lines.append(f"\u2022 {stock.name}: \u20b9{latest.price:.2f} ({latest.change_percent:+.2f}%)")
        
        db.close()
        send_telegram_message("\n".join(message_lines))
    except Exception as e:
        print(f"Error sending startup notification: {e}")

    start_scheduler()

@app.get("/")
def read_root():
    return {"message": "Stock Tracker API Running. Go to /static/index.html"}

@app.get("/api/stocks")
def get_stocks(db: Session = Depends(get_db)):
    # Get list of tracked stocks
    stocks = db.query(Stock).all()
    results = []
    
    for stock in stocks:
        # Get latest price entry
        latest = db.query(StockPrice).filter(StockPrice.symbol == stock.symbol).order_by(StockPrice.timestamp.desc()).first()
        
        stock_data = {
            "symbol": stock.symbol,
            "name": stock.name,
            "price": latest.price if latest else 0.0,
            "change": latest.change_percent if latest else 0.0,
            "status": latest.status if latest else "PENDING",
            "is_low": latest.is_low if latest else False,
            "details": latest.details if latest else "No data yet",
            "timestamp": latest.timestamp if latest else None,
            "seven_day_avg": latest.seven_day_avg if latest else 0.0,
            "two_fifty_day_low": latest.two_fifty_day_low if latest else 0.0,
            "two_fifty_day_avg": latest.two_fifty_day_avg if latest else 0.0
        }
        results.append(stock_data)
        
    return results

@app.get("/api/stocks/{symbol}")
def get_stock_detail(symbol: str, db: Session = Depends(get_db)):
    stock = db.query(Stock).filter(Stock.symbol == symbol).first()
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")
        
    latest = db.query(StockPrice).filter(StockPrice.symbol == stock.symbol).order_by(StockPrice.timestamp.desc()).first()
    
    # Calculate 7-Day Stats (On-fly to avoid DB reset)
    import yfinance as yf
    seven_day_avg = None
    seven_day_min = None
    seven_day_max = None
    try:
        # Fetch 7 days of daily data
        t = yf.Ticker(symbol)
        h7 = t.history(period="7d")
        if not h7.empty:
            seven_day_avg = h7['Close'].mean()
            seven_day_min = h7['Close'].min()
            seven_day_max = h7['Close'].max()
    except Exception as e:
        print(f"Error 7d stats: {e}")

    return {
        "symbol": stock.symbol,
        "name": stock.name,
        "price": latest.price if latest else 0.0,
        "change": latest.change_percent if latest else 0.0,
        "status": latest.status if latest else "PENDING",
        "is_low": latest.is_low if latest else False,
        "details": latest.details if latest else "No data yet",
        "market_cap": latest.market_cap if latest else None,
        "volume": latest.volume if latest else None,
        "open_price": latest.open_price if latest else None,
        "day_high": latest.day_high if latest else None,
        "day_low": latest.day_low if latest else None,
        "fifty_two_week_high": latest.fifty_two_week_high if latest else None,
        "fifty_two_week_low": latest.fifty_two_week_low if latest else None,
        "pe_ratio": latest.pe_ratio if latest else None,
        "timestamp": latest.timestamp if latest else None,
        # New Stats
        "seven_day_avg": seven_day_avg,
        "seven_day_min": seven_day_min,
        "seven_day_max": seven_day_max,
        "seven_day_low": seven_day_min, # Unified naming
        "two_fifty_day_low": latest.two_fifty_day_low if latest else None
    }

@app.get("/api/history/{symbol}")
def get_stock_history(symbol: str, period: str = "5d", interval: str = "60m"):
    """Fetch recent history for charting. Defaults to 5 days hourly."""
    import yfinance as yf
    try:
        ticker = yf.Ticker(symbol)
        # Fetch history
        hist = ticker.history(period=period, interval=interval)
        data = []
        for date, row in hist.iterrows():
            data.append({
                "date": date.strftime("%Y-%m-%d %H:%M"),
                "close": row['Close']
            })
        return data
    except Exception as e:
        print(f"Error fetching history: {e}")
        return []

@app.post("/api/refresh")
def refresh_data():
    """Manually trigger a data refresh"""
    fetcher.update_all_stocks()
    return {"message": "Update triggered"}

@app.post("/api/notify/{symbol}")
def manual_notify(symbol: str, db: Session = Depends(get_db)):
    """Manually send a status alert to Telegram"""
    from notifier import send_telegram_message
    import os
    
    stock = db.query(Stock).filter(Stock.symbol == symbol).first()
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")
        
    latest = db.query(StockPrice).filter(StockPrice.symbol == stock.symbol).order_by(StockPrice.timestamp.desc()).first()
    
    if not latest:
        raise HTTPException(status_code=400, detail="No data available for this stock")
        
    status_emoji = "\ud83d\udfe2" if latest.status == "NORMAL" else "\ud83d\udd34" if latest.status == "LOW" else "\ud83d\udd35"
    base_url = os.getenv("BASE_URL", "http://localhost:8000")
    
    msg = (
        f"{status_emoji} <b>Manual Status Report: {stock.name}</b>\n\n"
        f"Symbol: <code>{stock.symbol}</code>\n"
        f"Current Price: \u20b9{latest.price:.2f}\n"
        f"Change: {latest.change_percent:+.2f}%\n"
        f"Status: {latest.status}\n"
        f"Note: {latest.details}\n\n"
        f"<a href='{base_url}/static/details.html?symbol={stock.symbol}'>Open Dashboard</a>"
    )
    
    success = send_telegram_message(msg)
    if success:
        return {"message": "Notification sent successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to send Telegram message")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
