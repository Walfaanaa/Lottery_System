import os
import mysql.connector
import streamlit as st

def get_connection():
    try:
        return mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT", 4000)),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
    except Exception as e:
        st.exception(e)
        raise
