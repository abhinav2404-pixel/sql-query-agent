import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
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