import streamlit as st
from database import get_connection


st.title("Lottery Customer Registration")

full_name = st.text_input("Full Name")
email = st.text_input("Email")
username = st.text_input("Username")
password = st.text_input("Password", type="password")


if st.button("Register"):

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            INSERT INTO users
            (
                username,
                password,
                email,
                role,
                status,
                full_name
            )
            VALUES
            (
                %s,
                %s,
                %s,
                'customer',
                'Active',
                %s
            )
            """,
            (
                username,
                password,
                email,
                full_name
            )
        )

        conn.commit()

        st.success(
            "Registration successful. Please login."
        )

    except Exception as e:

        conn.rollback()
        st.error(e)

    finally:

        cursor.close()
        conn.close()
