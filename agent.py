import anthropic
import sqlite3
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

DEFAULT_SCHEMA = """
Table: transactions
Columns:
- transaction_id (INTEGER): unique transaction identifier
- customer_id (INTEGER): foreign key linking to customers table
- amount (FLOAT): transaction amount in dollars
- merchant (TEXT): merchant name, foreign key linking to merchants table
- transaction_date (DATE): date of transaction
- is_fraud (INTEGER): 1 if fraudulent, 0 if legitimate

Table: customers
Columns:
- customer_id (INTEGER): unique customer identifier
- name (TEXT): full name of customer
- age (INTEGER): age of customer
- city (TEXT): city where customer lives
- account_age_days (INTEGER): how long the account has been open in days
- credit_score (INTEGER): customer credit score

Table: merchants
Columns:
- merchant_name (TEXT): name of the merchant
- merchant_category (TEXT): category of merchant e.g. Retail, Luxury, Finance
- risk_level (TEXT): merchant risk level - Low, Medium, or High
"""

SCHEMA = DEFAULT_SCHEMA

def generate_sql(user_question):
    import agent
    current_schema = agent.SCHEMA
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        messages=[
            {
                "role": "user",
                "content": f"""You are a SQL expert. Given this database schema:

{current_schema}

Convert this question to SQL and explain it:
Question: {user_question}

Respond in this exact format:
SQL: <your sql query here>
EXPLANATION: <plain english explanation of what the query does>"""
            }
        ]
    )
    return response.content[0].text

def run_query(sql):
    conn = sqlite3.connect("transactions.db")
    try:
        df = pd.read_sql_query(sql, conn)
        return df
    except Exception as e:
        return f"Error running query: {e}"
    finally:
        conn.close()

def parse_response(response_text):
    sql = ""
    explanation = ""
    lines = response_text.split("\n")
    sql_lines = []
    explanation_lines = []
    in_sql = False
    in_explanation = False

    for line in lines:
        if line.startswith("SQL:"):
            in_sql = True
            in_explanation = False
            first_part = line.replace("SQL:", "").strip()
            if first_part:
                sql_lines.append(first_part)
        elif line.startswith("EXPLANATION:"):
            in_sql = False
            in_explanation = True
            first_part = line.replace("EXPLANATION:", "").strip()
            if first_part:
                explanation_lines.append(first_part)
        elif in_sql:
            if line.strip():
                sql_lines.append(line.strip())
        elif in_explanation:
            if line.strip():
                explanation_lines.append(line.strip())

    sql = " ".join(sql_lines)
    sql = sql.replace("`", "").strip()
    explanation = " ".join(explanation_lines)
    return sql, explanation