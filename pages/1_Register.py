import streamlit as st
from database import get_connection

st.set_page_config(
    page_title="Register User",
    layout="centered"
)

st.title("Customer Registration")


username = st.text_input("Username")
password = st.text_input("Password", type="password")
email = st.text_input("Email")
full_name = st.text_input("Full Name")
phone = st.text_input("Phone Number")


if st.button("Register"):

    conn = get_connection()
    cursor = conn.cursor()

    # Check existing username
    cursor.execute(
        "SELECT username FROM users WHERE username=%s",
        (username,)
    )

    existing = cursor.fetchone()

    if existing:
        st.error("Username already exists")

    else:
        cursor.execute(
            """
            INSERT INTO users
            (username, password, email, role, status, full_name, ph)
            VALUES
            (%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                username,
                password,
                email,
                "Member",
                "Active",
                full_name,
                phone
            )
        )

        conn.commit()

        st.success("Registration successful. You can login now.")

    cursor.close()
    conn.close()
