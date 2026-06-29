import sqlite3
import pandas as pd

conn = sqlite3.connect("transactions.db")

data = {
    "transaction_id": [1, 2, 3, 4, 5, 6, 7, 8],
    "customer_id": [101, 102, 101, 103, 102, 104, 103, 101],
    "amount": [500, 15000, 200, 8000, 3000, 25000, 1200, 9500],
    "merchant": ["Amazon", "Jewelry Store", "Walmart", "Electronics", "Gas Station", "Wire Transfer", "Apple Store", "Casino"],
    "transaction_date": ["2024-01-01", "2024-01-01", "2024-01-02", "2024-01-03", "2024-01-03", "2024-01-04", "2024-01-04", "2024-01-05"],
    "is_fraud": [0, 1, 0, 1, 0, 1, 0, 1]
}

df = pd.DataFrame(data)
df.to_sql("transactions", conn, if_exists="replace", index=False)
conn.close()
print("Database created successfully")