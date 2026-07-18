import streamlit as st
import bcrypt
from database import get_connection


st.title("Lottery Customer Registration")


full_name = st.text_input("Full Name")
email = st.text_input("Email")
phone = st.text_input("Phone Number")
username = st.text_input("Username")
password = st.text_input(
    "Password",
    type="password"
)


if st.button("Register"):

    if not full_name or not username or not password or not phone:
        st.warning("Please fill all required fields.")
        st.stop()


    conn = get_connection()
    cursor = conn.cursor()


    try:

        # Automatically encrypt customer password
        hashed_password = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode()


        cursor.execute(
            """
            INSERT INTO users
            (
                username,
                password,
                email,
                role,
                status,
                full_name,
                phone
            )
            VALUES
            (
                %s,
                %s,
                %s,
                'customer',
                'Active',
                %s,
                %s
            )
            """,
            (
                username,
                hashed_password,
                email,
                full_name,
                phone
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
