import streamlit as st
from agent import generate_sql, run_query, parse_response

st.title("SQL Query Agent")
st.write("Ask questions about fraud transaction data in plain English")

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
    else:
        st.warning("Please enter a question")