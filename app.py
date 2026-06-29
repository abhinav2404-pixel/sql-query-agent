import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

import os

# Auto create database if it doesn't exist
def initialize_database():
    if not os.path.exists("transactions.db"):
        import sqlite3
        conn = sqlite3.connect("transactions.db")
        
        transactions = {
            "transaction_id": [1, 2, 3, 4, 5, 6, 7, 8],
            "customer_id": [101, 102, 101, 103, 102, 104, 103, 101],
            "amount": [500, 15000, 200, 8000, 3000, 25000, 1200, 9500],
            "merchant": ["Amazon", "Jewelry Store", "Walmart", "Electronics", "Gas Station", "Wire Transfer", "Apple Store", "Casino"],
            "transaction_date": ["2024-01-01", "2024-01-01", "2024-01-02", "2024-01-03", "2024-01-03", "2024-01-04", "2024-01-04", "2024-01-05"],
            "is_fraud": [0, 1, 0, 1, 0, 1, 0, 1]
        }
        customers = {
            "customer_id": [101, 102, 103, 104],
            "name": ["John Smith", "Jane Doe", "Bob Johnson", "Alice Brown"],
            "age": [35, 28, 45, 52],
            "city": ["Chicago", "New York", "Los Angeles", "Houston"],
            "account_age_days": [365, 180, 730, 90],
            "credit_score": [720, 680, 750, 590]
        }
        merchants = {
            "merchant_name": ["Amazon", "Jewelry Store", "Walmart", "Electronics", "Gas Station", "Wire Transfer", "Apple Store", "Casino"],
            "merchant_category": ["Retail", "Luxury", "Retail", "Electronics", "Fuel", "Finance", "Electronics", "Gaming"],
            "risk_level": ["Low", "High", "Low", "Medium", "Low", "High", "Medium", "High"]
        }
        pd.DataFrame(transactions).to_sql("transactions", conn, if_exists="replace", index=False)
        pd.DataFrame(customers).to_sql("customers", conn, if_exists="replace", index=False)
        pd.DataFrame(merchants).to_sql("merchants", conn, if_exists="replace", index=False)
        conn.close()

initialize_database()

from agent import generate_sql, run_query, parse_response

st.title("SQL Query Agent")
st.write("Ask questions about your data in plain English")

# Sidebar for CSV upload
st.sidebar.title("Upload Your Data")
uploaded_file = st.sidebar.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    conn = sqlite3.connect("transactions.db")
    table_name = uploaded_file.name.replace(".csv", "").replace(" ", "_").lower()
    df.to_sql(table_name, conn, if_exists="replace", index=False)
    conn.close()
    st.sidebar.success(f"Loaded: {table_name}")
    st.sidebar.write("Preview:")
    st.sidebar.dataframe(df.head(3))
    import agent
    schema = f"Table: {table_name}\nColumns:\n"
    for col, dtype in zip(df.columns, df.dtypes):
        schema += f"- {col} ({dtype})\n"
    agent.SCHEMA = schema

st.subheader("Ask a Question")
user_question = st.text_input(
    "Ask a question:",
    placeholder="e.g. Show me all fraudulent transactions above $5000"
)

if st.button("Generate SQL"):
    if user_question:
        with st.spinner("Thinking..."):
            response = generate_sql(user_question)
            sql, explanation = parse_response(response)

            st.subheader("Generated SQL:")
            st.code(sql, language="sql")

            st.subheader("What this query does:")
            st.write(explanation)

            st.subheader("Results:")
            results = run_query(sql)
            st.dataframe(results)

            # Auto generate chart if results have numbers
            if isinstance(results, pd.DataFrame) and not results.empty:
                numeric_cols = results.select_dtypes(include="number").columns.tolist()
                text_cols = results.select_dtypes(include="object").columns.tolist()

                if numeric_cols and text_cols:
                    st.subheader("Chart:")
                    fig = px.bar(
                        results,
                        x=text_cols[0],
                        y=numeric_cols[0],
                        title=f"{numeric_cols[0]} by {text_cols[0]}",
                        color=numeric_cols[0],
                        color_continuous_scale="reds"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                elif numeric_cols:
                    st.subheader("Chart:")
                    fig = px.histogram(
                        results,
                        x=numeric_cols[0],
                        title=f"Distribution of {numeric_cols[0]}"
                    )
                    st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Please enter a question")