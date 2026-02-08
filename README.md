# Stock Price Tracker 📈

A self-hosted, simplified stock price dashboard for Indian stocks (NSE).
Features a "Low Price" indicator based on 20-day Moving Averages and recent price range analysis.

## 🚀 Features
- **Real-time Price Tracking**: Fetches data from Yahoo Finance.
- **Low Price Detection**: Visual badges for stocks trading at attractive levels.
- **Responsive Dashboard**: Beautiful dark-mode UI.
- **No API Keys**: Uses open-source libraries.

## 🛠️ Setup

### Prerequisites
- Python 3.8+
- Internet connection

### Installation
1.  **Clone/Navigate** to the project folder:
    ```bash
    cd stock_tracker
    ```

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Initialize Database**:
    ```bash
    python database.py
    ```
    *(This creates `stocks.db` and loads default stocks like RELIANCE, TCS, etc.)*

## ▶️ Running the App

Start the server with the following command:

```bash
uvicorn main:app --reload
```

Then open your browser to:
👉 **[http://localhost:8000/static/index.html](http://localhost:8000/static/index.html)**

## ⚙️ Configuration
- **Add Stocks**: Edit `database.py` (initial list) or manually add to SQLite.
- **Refresh Rate**: Default is every 15 minutes. Edit `scheduler.py` to change.
- **Low Price Logic**: Edit `fetcher.py` to tweak the algorithms.

## 🖥️ Tech Stack
- **Backend**: FastAPI, APScheduler
- **Database**: SQLite, SQLAlchemy
- **Data**: yfinance
- **Frontend**: Vanilla JS, Chart.js, Glassmorphism CSS
