import sqlite3

try:
    conn = sqlite3.connect('stocks.db')
    cursor = conn.cursor()
    cursor.execute("ALTER TABLE stock_prices ADD COLUMN two_fifty_day_avg FLOAT;")
    conn.commit()
    conn.close()
    print("Database altered: added two_fifty_day_avg.")
except Exception as e:
    print(f"Error: {e}")
