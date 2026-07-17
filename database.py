import os
import streamlit as st
import mysql.connector


def get_connection():
    try:
        # Read from Streamlit Secrets first, then environment variables
        host = st.secrets.get("DB_HOST", os.getenv("DB_HOST"))
        port = int(st.secrets.get("DB_PORT", os.getenv("DB_PORT", "4000")))
        user = st.secrets.get("DB_USER", os.getenv("DB_USER"))
        password = st.secrets.get("DB_PASSWORD", os.getenv("DB_PASSWORD"))
        database = st.secrets.get("DB_NAME", os.getenv("DB_NAME"))

        # Check required values
        if not host:
            raise Exception("DB_HOST is not configured.")

        if not user:
            raise Exception("DB_USER is not configured.")

        if password is None:
            raise Exception("DB_PASSWORD is not configured.")

        if not database:
            raise Exception("DB_NAME is not configured.")

        conn = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            ssl_disabled=False,
            connection_timeout=20,
            autocommit=False
        )

        return conn

    except mysql.connector.Error as err:
        st.error(f"Database connection failed: {err}")
        raise

    except Exception as e:
        st.error(f"Configuration error: {e}")
        raise
