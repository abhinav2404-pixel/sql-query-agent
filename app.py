import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import os
from agent import generate_sql, run_query, parse_response

st.set_page_config(
    page_title="SQL Query Agent",
    page_icon="🤖",
    layout="wide"
)

st.markdown("""
    <style>
    .stApp { background-color: #0f1117; }
    .header {
        background: linear-gradient(135deg, #1a1f2e 0%, #16213e 100%);
        padding: 2rem; border-radius: 12px;
        margin-bottom: 2rem; border: 1px solid #2d3561;
    }
    .header h1 { color: #ffffff; font-size: 2.5rem; font-weight: 700; margin: 0; }
    .header p { color: #a0aec0; font-size: 1rem; margin: 0.5rem 0 0 0; }
    .header a { color: #6c63ff; text-decoration: none; font-weight: 500; }
    .header a:hover { text-decoration: underline; }
    .stTextInput input {
        background-color: #1a1f2e !important; border: 1px solid #2d3561 !important;
        color: #ffffff !important; border-radius: 8px !important;
        font-size: 1rem !important; padding: 0.75rem !important;
    }
    .stButton button {
        background: linear-gradient(135deg, #6c63ff 0%, #5a52d5 100%) !important;
        color: white !important; border: none !important;
        border-radius: 8px !important; padding: 0.75rem 2rem !important;
        font-size: 1rem !important; font-weight: 600 !important; width: 100% !important;
    }
    .stButton button:hover { background: linear-gradient(135deg, #5a52d5 0%, #4840c0 100%) !important; }
    .section-header {
        color: #6c63ff; font-size: 0.85rem; font-weight: 600;
        text-transform: uppercase; letter-spacing: 1px; margin-bottom: 0.5rem;
    }
    .explanation-box {
        background: #1a1f2e; border-left: 3px solid #6c63ff;
        border-radius: 0 8px 8px 0; padding: 1rem 1.5rem;
        color: #a0aec0; font-size: 0.95rem; line-height: 1.6;
    }
    .footer {
        text-align: center; color: #4a5568; font-size: 0.8rem;
        margin-top: 3rem; padding-top: 1rem; border-top: 1px solid #2d3561;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

def initialize_database():
    if not os.path.exists("transactions.db"):
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

st.markdown("""
    <div class="header">
        <h1>🤖 SQL Query Agent</h1>
        <p>Ask questions about your data in plain English — powered by Claude AI</p>
        <p style="margin-top:0.75rem;">
            Built by <a href="https://www.linkedin.com/in/abhinav-dubey-30a913a6/" target="_blank">Abhinav Dubey</a> &nbsp;|&nbsp;
            <a href="https://github.com/abhinav2404-pixel/sql-query-agent" target="_blank">GitHub</a> &nbsp;|&nbsp;
            <a href="https://www.linkedin.com/in/abhinav-dubey-30a913a6/" target="_blank">LinkedIn</a>
        </p>
    </div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1, 2])

with col1:
    st.markdown('<p class="section-header">Upload Your Data</p>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"], label_visibility="collapsed")

    if st.button("Reset to Default Database"):
        import agent
        agent.SCHEMA = agent.DEFAULT_SCHEMA
        st.session_state.reset_clicked = True
        st.session_state.last_file = None
        st.session_state.pop("results", None)
        st.success("Schema reset. Please also click the X on the uploaded file above to fully switch back.")

    if uploaded_file:
        file_key = uploaded_file.name + str(uploaded_file.size)
        df = pd.read_csv(uploaded_file)
        table_name = uploaded_file.name.replace(".csv", "").replace(" ", "_").lower()
        if st.session_state.get("last_file") != file_key or st.session_state.get("reset_clicked"):
            conn = sqlite3.connect("transactions.db")
            df.to_sql(table_name, conn, if_exists="replace", index=False)
            conn.close()
            import agent
            schema = f"Table: {table_name}\nColumns:\n"
            for col, dtype in zip(df.columns, df.dtypes):
                schema += f"- {col} ({dtype})\n"
            agent.SCHEMA = schema
            st.session_state.last_file = file_key
            st.session_state.reset_clicked = False
        st.success(f"Loaded: {table_name} ({len(df)} rows)")
        st.warning("⚠️ Now asking questions about your uploaded file. Click 'Reset to Default Database' to switch back to the fraud data.")
        st.dataframe(df.head(3), use_container_width=True)

    st.markdown("---")
    st.markdown("""
        <div style="background:#1a1f2e; border:1px solid #2d3561; border-radius:8px; padding:1rem; margin-bottom:1rem;">
            <p style="color:#6c63ff; font-size:0.85rem; font-weight:600; text-transform:uppercase; letter-spacing:1px; margin:0 0 0.5rem 0;">About This App</p>
            <p style="color:#a0aec0; font-size:0.85rem; line-height:1.6; margin:0;">
                The default database contains <strong style="color:#ffffff;">fraud transaction data</strong>
                with customers and merchant tables. You can ask questions about it using the sample questions below.
                <br><br>
                Want to explore your own data? <strong style="color:#6c63ff;">Upload any CSV file</strong>
                above and ask questions about it in plain English.
            </p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown('<p class="section-header">Sample Questions</p>', unsafe_allow_html=True)
    sample_questions = [
        "Show me all fraudulent transactions",
        "Total fraud amount by merchant",
        "Which customer has highest credit score?",
        "Show transactions above $5000",
        "Count transactions by merchant category"
    ]
    for q in sample_questions:
        if st.button(q, key=q):
            st.session_state.question = q

with col2:
    st.markdown('<p class="section-header">Ask a Question</p>', unsafe_allow_html=True)

    question_value = st.session_state.get("question", "")
    user_question = st.text_input(
        "Question",
        value=question_value,
        placeholder="e.g. Show me all fraudulent transactions above $5000",
        label_visibility="collapsed"
    )

    if st.button("Generate SQL ✨"):
        if user_question:
            with st.spinner("Thinking..."):
                response = generate_sql(user_question)
                sql, explanation = parse_response(response)
                st.session_state.sql = sql
                st.session_state.explanation = explanation
                st.session_state.results = run_query(sql)
        else:
            st.warning("Please enter a question")

    if "results" in st.session_state:
        sql = st.session_state.sql
        explanation = st.session_state.explanation
        results = st.session_state.results

        st.markdown('<p class="section-header">Generated SQL</p>', unsafe_allow_html=True)
        st.code(sql, language="sql")

        st.markdown('<p class="section-header">What This Query Does</p>', unsafe_allow_html=True)
        st.markdown(f'<div class="explanation-box">{explanation}</div>', unsafe_allow_html=True)

        st.markdown('<p class="section-header">Results</p>', unsafe_allow_html=True)
        if isinstance(results, pd.DataFrame):
            st.dataframe(results, use_container_width=True)
        else:
            st.error(f"Query failed: {results}")
            st.info("Try rephrasing your question and make sure it matches the available data.")

        if isinstance(results, pd.DataFrame) and not results.empty:
            numeric_cols = results.select_dtypes(include="number").columns.tolist()
            text_cols = results.select_dtypes(include="object").columns.tolist()

            if numeric_cols and text_cols:
                st.markdown('<p class="section-header">Chart</p>', unsafe_allow_html=True)

                chart_type = st.selectbox(
                    "Select chart type",
                    ["Bar", "Line", "Pie", "Scatter"],
                    key="chart_type"
                )

                if chart_type == "Bar":
                    fig = px.bar(
                        results,
                        x=text_cols[0],
                        y=numeric_cols[0],
                        title=f"{numeric_cols[0]} by {text_cols[0]}",
                        color=numeric_cols[0],
                        color_continuous_scale="reds",
                        template="plotly_dark"
                    )
                elif chart_type == "Line":
                    fig = px.line(
                        results,
                        x=text_cols[0],
                        y=numeric_cols[0],
                        title=f"{numeric_cols[0]} over {text_cols[0]}",
                        template="plotly_dark",
                        markers=True
                    )
                elif chart_type == "Pie":
                    fig = px.pie(
                        results,
                        names=text_cols[0],
                        values=numeric_cols[0],
                        title=f"{numeric_cols[0]} by {text_cols[0]}",
                        template="plotly_dark",
                        color_discrete_sequence=px.colors.sequential.Reds
                    )
                elif chart_type == "Scatter":
                    if len(numeric_cols) >= 2:
                        fig = px.scatter(
                            results,
                            x=numeric_cols[0],
                            y=numeric_cols[1],
                            text=text_cols[0] if text_cols else None,
                            title=f"{numeric_cols[0]} vs {numeric_cols[1]}",
                            template="plotly_dark"
                        )
                    else:
                        fig = px.bar(
                            results,
                            x=text_cols[0],
                            y=numeric_cols[0],
                            title=f"{numeric_cols[0]} by {text_cols[0]}",
                            color=numeric_cols[0],
                            color_continuous_scale="reds",
                            template="plotly_dark"
                        )

                fig.update_layout(
                    paper_bgcolor="#1a1f2e",
                    plot_bgcolor="#1a1f2e",
                    font_color="#a0aec0"
                )
                st.plotly_chart(fig, use_container_width=True)

st.markdown("""
    <div class="footer">
        Built with Python, Claude AI, Streamlit & Plotly &nbsp;|&nbsp;
        Abhinav Dubey &nbsp;|&nbsp; 2026
    </div>
""", unsafe_allow_html=True)