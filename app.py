import streamlit as st
from database import get_connection


st.set_page_config(
    page_title="Lottery System",
    page_icon="🎟"
)


st.title("🎟 Lottery Management System")


try:

    conn = get_connection()

    if conn.is_connected():
        st.success("✅ Connected to lottery_db successfully")

    conn.close()


except Exception as e:

    st.error(f"Connection Error: {e}")
