from database import SessionLocal, Stock

def add_stocks():
    session = SessionLocal()
    try:
        stocks_to_add = [
            ("KOTAKBANK.NS", "Kotak Mahindra Bank"),
            ("HINDUNILVR.NS", "Hindustan Unilever"),
            ("BHARTIARTL.NS", "Bharti Airtel"),
            ("SBIN.NS", "State Bank of India"),
            ("BAJFINANCE.NS", "Bajaj Finance"),
            ("ASIANPAINT.NS", "Asian Paints"),
            ("MARUTI.NS", "Maruti Suzuki"),
            ("TITAN.NS", "Titan Company"),
            ("SUNPHARMA.NS", "Sun Pharma"),
            ("ULTRACEMCO.NS", "UltraTech Cement"),
            ("ADANIENT.NS", "Adani Enterprises"),
            ("ADANIPORTS.NS", "Adani Ports"),
            ("AXISBANK.NS", "Axis Bank"),
            ("M&M.NS", "Mahindra & Mahindra"),
            ("NTPC.NS", "NTPC"),
            ("POWERGRID.NS", "Power Grid"),
            ("TATASTEEL.NS", "Tata Steel"),
            ("TATAMOTORS.NS", "Tata Motors"),
            ("JSWSTEEL.NS", "JSW Steel"),
            ("COALINDIA.NS", "Coal India"),
            ("LICI.NS", "LIC of India"),
            ("ONGC.NS", "ONGC"),
            ("HCLTECH.NS", "HCL Technologies"),
            ("WIPRO.NS", "Wipro"),
            ("GRASIM.NS", "Grasim Industries"),
            ("BAJAJFINSV.NS", "Bajaj Finserv"),
            ("NESTLEIND.NS", "Nestle India"),
            ("INDUSINDBK.NS", "IndusInd Bank"),
            ("HDFCLIFE.NS", "HDFC Life"),
            ("SBILIFE.NS", "SBI Life Insurance"),
            ("BAJAJ-AUTO.NS", "Bajaj Auto"),
            ("DRREDDY.NS", "Dr. Reddy's"),
            ("IOC.NS", "Indian Oil"),
            ("BPCL.NS", "BPCL"),
            ("BRITANNIA.NS", "Britannia Industries"),
            ("TATAGOLD.NS", "Tata Gold ETF")
        ]
        
        for symbol, name in stocks_to_add:
            existing = session.query(Stock).filter(Stock.symbol == symbol).first()
            if not existing:
                new_stock = Stock(symbol=symbol, name=name)
                session.add(new_stock)
                print(f"Added {name} ({symbol})")
        
        session.commit()
        print("Bulk addition complete.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    add_stocks()
