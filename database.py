import streamlit as st
import mysql.connector


def get_connection():

    conn = mysql.connector.connect(
        host=st.secrets["DB_HOST"],
        port=int(st.secrets["DB_PORT"]),
        user=st.secrets["DB_USER"],
        password=st.secrets["DB_PASSWORD"],
        database=st.secrets["DB_NAME"],
        ssl_disabled=False,
        connection_timeout=20
    )

    return conn
