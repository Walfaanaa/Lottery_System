import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": st.secrets.get("DB_HOST", os.getenv("DB_HOST")),
    "user": st.secrets.get("DB_USER", os.getenv("DB_USER")),
    "password": st.secrets.get("DB_PASSWORD", os.getenv("DB_PASSWORD")),
    "database": st.secrets.get("DB_NAME", os.getenv("DB_NAME")),
}
