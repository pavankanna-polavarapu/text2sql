import streamlit as st
from langchain_ollama import ChatOllama
from langchain_community.utilities import SQLDatabase
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

st.set_page_config(page_title="Text2sql App", layout="centered")
st.title("Talk to your database with Ollama")
st.write("Ask any questions about the student grades database in plain English.")

db = SQLDatabase.from_uri("sqlite:///student_grade.db")

llm = ChatOllama(
    model = "llama3.2:1b",
    temperature=0
)

prompt = ChatPromptTemplate.from_template(
    '''you're a helpful data analyst and sql assistant.
    Given the database and schema, write a SQL query to answer the question.

    Rules:
     - only use the tables and columns provided in the schema.
     - Do not explain anything
     - Return only the SQL query, nothing else.

    Database Schema:
    {schema}
    Question: 
    {question}
''')

sql_chain = prompt | llm | StrOutputParser()

schema = db.get_table_info()



question = st.text_input("Enter your question", 
                         placeholder="e.g. What is the average score for each subject?")


if question:
    try:
        sql_query = sql_chain.invoke({"schema": schema, "question": question}).strip()
        st.subheader("Generated SQL Query:")
        st.code(sql_query, language="sql")

        st.subheader("Query Results:")
        results = db.run(sql_query)
        st.write(results)
    except Exception as e:
        st.error(f"An error occurred: {e}")