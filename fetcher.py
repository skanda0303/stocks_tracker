import yfinance as yf
import pandas as pd
from database import SessionLocal, Stock, StockPrice
import json
from datetime import datetime, timedelta
import os

from notifier import send_telegram_message

def is_market_open():
    """Checks if the Indian Stock Market is open (9:00 AM to 3:30 PM IST, Mon-Fri)"""
    # Get current time in UTC (Standard for most servers like Render)
    utc_now = datetime.utcnow()
    # Convert to IST (UTC + 5:30)
    ist_now = utc_now + timedelta(hours=5, minutes=30)
    
    # Monday = 0, Sunday = 6
    weekday = ist_now.weekday()
    current_time = ist_now.time()
    
    market_start = datetime.strptime("09:00", "%H:%M").time()
    market_end = datetime.strptime("15:30", "%H:%M").time()
    
    is_weekday = weekday < 5
    is_during_hours = market_start <= current_time <= market_end
    
    return is_weekday and is_during_hours

def analyze_stock(symbol):
    print(f"Fetching data for {symbol}...")
    try:
        ticker = yf.Ticker(symbol)
        # Fetch 2y history to ensure we have 250 trading days
        hist = ticker.history(period="2y")
        
        if hist.empty:
            print(f"No data found for {symbol} (History Empty)")
            return None

        print(f"Fetched {len(hist)} rows for {symbol}")
        current_price = hist['Close'].iloc[-1]
        
        # Calculate calculated metrics
        # 1. 20-day Moving Average (SMA)
        ma_20 = hist['Close'].rolling(window=20).mean().iloc[-1]
        
        # 2. 7-day Average & Low
        seven_day_avg = hist['Close'].tail(7).mean()
        seven_day_low = hist['Close'].tail(7).min()
        
        # 3. 250-day Low & Avg (Roughly 1 year)
        if len(hist) >= 250:
            last_250 = hist['Close'].tail(250)
            two_fifty_day_low = last_250.min()
            two_fifty_day_avg = last_250.mean()
        else:
            two_fifty_day_low = hist['Close'].min() # Fallback
            two_fifty_day_avg = hist['Close'].mean()

        # 4. 30-day Range
        last_30_days = hist['Close'].tail(30)
        min_30 = last_30_days.min()
        max_30 = last_30_days.max()
        
        # 5. Percent Change from previous day
        if len(hist) >= 2:
            prev_close = hist['Close'].iloc[-2]
            change_percent = ((current_price - prev_close) / prev_close) * 100
        else:
            change_percent = 0.0

        # "Relatively Low" Logic
        reasons = []
        is_low = False
        
        # Condition A: Price <= 20-day MA
        if current_price <= ma_20:
            reasons.append(f"Below 20-day MA ({ma_20:.2f})")
            is_low = True
            
        # Condition B: Price within bottom 20% of 30-day range
        range_30 = max_30 - min_30
        threshold_20_percent = min_30 + (range_30 * 0.20)
        if current_price <= threshold_20_percent:
            reasons.append(f"In bottom 20% of 30-day range ( Low: {min_30:.2f} )")
            is_low = True
            
        # Condition C: Drop from 30-day high (e.g. > 15% drop)
        drop_from_high = ((max_30 - current_price) / max_30) * 100
        if drop_from_high >= 15:
            reasons.append(f"Dropped {drop_from_high:.1f}% from 30-day high ({max_30:.2f})")
            is_low = True

        # Special Condition: Below 250-day low
        if current_price <= two_fifty_day_low:
            reasons.append(f"At/Below 250-day low ({two_fifty_day_low:.2f})")

        # Logic to fetch extended info
        try:
            info = ticker.info
            market_cap = info.get('marketCap')
            volume = info.get('volume')
            open_price = info.get('open')
            day_high = info.get('dayHigh')
            day_low = info.get('dayLow')
            fifty_two_week_high = info.get('fiftyTwoWeekHigh')
            fifty_two_week_low = info.get('fiftyTwoWeekLow')
            pe_ratio = info.get('trailingPE')
        except:
             # Fallback if info fetch fails or is throttled
            market_cap, volume, open_price, day_high, day_low, fifty_two_week_high, fifty_two_week_low, pe_ratio = (None,) * 8

        status = "NORMAL"
        if current_price <= two_fifty_day_low * 1.05: # Within 5% of yearly low
             status = "CRITICAL DIP"
             is_low = True
        elif is_low:
            status = "LOW"
        elif current_price >= max_30 * 0.98: # Near high
            status = "HIGH"

        return {
            "symbol": symbol,
            "price": current_price,
            "change_percent": change_percent,
            "status": status,
            "is_low": is_low,
            "details": ", ".join(reasons) if reasons else "Normal price action",
            "market_cap": market_cap,
            "volume": volume,
            "open_price": open_price,
            "day_high": day_high,
            "day_low": day_low,
            "fifty_two_week_high": fifty_two_week_high,
            "fifty_two_week_low": fifty_two_week_low,
            "pe_ratio": pe_ratio,
            "seven_day_avg": seven_day_avg,
            "seven_day_low": seven_day_low,
            "two_fifty_day_low": two_fifty_day_low,
            "two_fifty_day_avg": two_fifty_day_avg
        }

    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        return None

def update_all_stocks():
    if not is_market_open():
        print("Market is closed. Skipping update.")
        return

    session = SessionLocal()
    stocks = session.query(Stock).all()
    base_url = os.getenv("BASE_URL", "http://localhost:8000")
    
    for stock in stocks:
        print(f"Analyzing {stock.symbol}...")
        data = analyze_stock(stock.symbol)
        if data:
            print(f" > Got data for {stock.symbol}: {data['price']}")
            
            # Automated Alert Logic: BELOW 250-DAY LOW (Golden Opportunity)
            if data["price"] <= data["two_fifty_day_low"]:
                msg = (
                    f"\ud83d\udd25 <b>GOLDEN OPPORTUNITY: {stock.name} ({stock.symbol})</b>\n\n"
                    f"Current Price: \u20b9{data['price']:.2f}\n"
                    f"<b>250-Day Lowest: \u20b9{data['two_fifty_day_low']:.2f}</b>\n"
                    f"Action: Price has hit a 1-YEAR (250-day) LOW!\n\n"
                    f"<a href='{base_url}/static/details.html?symbol={stock.symbol}'>Investigate Now</a>"
                )
                send_telegram_message(msg)

            # Save to DB
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
    session.close()
    print("All stocks updated.")

if __name__ == "__main__":
    update_all_stocks()
