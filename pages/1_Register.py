import streamlit as st
import bcrypt
from database import get_connection


st.title("📝 Lottery Customer Registration")


# ==============================
# REGISTRATION FORM
# ==============================

with st.form("registration_form"):

    full_name = st.text_input("Full Name")

    email = st.text_input("Email")

    phone = st.text_input("Phone Number")

    username = st.text_input("Username")

    password = st.text_input(
        "Password",
        type="password"
    )


    submit = st.form_submit_button(
        "Register"
    )



# ==============================
# PROCESS REGISTRATION
# ==============================

if submit:


    # Clean data

    full_name = full_name.strip()
    email = email.strip()
    phone = phone.strip()
    username = username.strip()
    password = password.strip()



    # Debug check (keep temporarily)

    st.write("Full Name:", repr(full_name))
    st.write("Email:", repr(email))
    st.write("Phone:", repr(phone))
    st.write("Username:", repr(username))
    st.write("Password Length:", len(password))



    # Validation

    if (
        len(full_name) == 0
        or len(email) == 0
        or len(phone) == 0
        or len(username) == 0
        or len(password) == 0
    ):

        st.error(
            "Please fill all required fields."
        )

        st.stop()



    conn = None
    cursor = None


    try:

        conn = get_connection()

        cursor = conn.cursor()



        # Check duplicate username

        cursor.execute(
            """
            SELECT id
            FROM users
            WHERE username=%s
            """,
            (username,)
        )


        if cursor.fetchone():

            st.error(
                "Username already exists."
            )

            st.stop()



        # Encrypt password

        hashed_password = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode()



        # Insert customer

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
            "✅ Registration successful. Please login."
        )


    except Exception as e:

        if conn:
            conn.rollback()

        st.error(
            f"Registration failed: {e}"
        )


    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()
