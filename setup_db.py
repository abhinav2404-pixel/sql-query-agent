import sqlite3
import pandas as pd

conn = sqlite3.connect("transactions.db")

# Transactions table
transactions = {
    "transaction_id": [1, 2, 3, 4, 5, 6, 7, 8],
    "customer_id": [101, 102, 101, 103, 102, 104, 103, 101],
    "amount": [500, 15000, 200, 8000, 3000, 25000, 1200, 9500],
    "merchant": ["Amazon", "Jewelry Store", "Walmart", "Electronics", "Gas Station", "Wire Transfer", "Apple Store", "Casino"],
    "transaction_date": ["2024-01-01", "2024-01-01", "2024-01-02", "2024-01-03", "2024-01-03", "2024-01-04", "2024-01-04", "2024-01-05"],
    "is_fraud": [0, 1, 0, 1, 0, 1, 0, 1]
}

# Customers table
customers = {
    "customer_id": [101, 102, 103, 104],
    "name": ["John Smith", "Jane Doe", "Bob Johnson", "Alice Brown"],
    "age": [35, 28, 45, 52],
    "city": ["Chicago", "New York", "Los Angeles", "Houston"],
    "account_age_days": [365, 180, 730, 90],
    "credit_score": [720, 680, 750, 590]
}

# Merchants table
merchants = {
    "merchant_name": ["Amazon", "Jewelry Store", "Walmart", "Electronics", "Gas Station", "Wire Transfer", "Apple Store", "Casino"],
    "merchant_category": ["Retail", "Luxury", "Retail", "Electronics", "Fuel", "Finance", "Electronics", "Gaming"],
    "risk_level": ["Low", "High", "Low", "Medium", "Low", "High", "Medium", "High"]
}

pd.DataFrame(transactions).to_sql("transactions", conn, if_exists="replace", index=False)
pd.DataFrame(customers).to_sql("customers", conn, if_exists="replace", index=False)
pd.DataFrame(merchants).to_sql("merchants", conn, if_exists="replace", index=False)

conn.close()
print("Database with 3 tables created successfully")