import sqlite3

try:
    conn = sqlite3.connect('stocks.db')
    cursor = conn.cursor()
    cursor.execute("ALTER TABLE stock_prices ADD COLUMN seven_day_low FLOAT;")
    conn.commit()
    conn.close()
    print("Database altered successfully with seven_day_low.")
except Exception as e:
    print(f"Error altering database: {e}")
