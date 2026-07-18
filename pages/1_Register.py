import streamlit as st
import bcrypt
from database import get_connection


st.title("📝 Lottery Customer Registration")


# ==============================
# REGISTRATION FORM
# ==============================

full_name = st.text_input("Full Name")

email = st.text_input("Email")

phone = st.text_input("Phone Number")

username = st.text_input("Username")

password = st.text_input(
    "Password",
    type="password"
)



# ==============================
# REGISTER BUTTON
# ==============================

if st.button("Register"):


    # Clean input values

    full_name = full_name.strip()
    email = email.strip()
    phone = phone.strip()
    username = username.strip()
    password = password.strip()



    # Required fields check

    if (
        full_name == ""
        or username == ""
        or password == ""
        or phone == ""
    ):

        st.warning(
            "Please fill all required fields."
        )

        st.stop()



    conn = None
    cursor = None


    try:


        conn = get_connection()

        cursor = conn.cursor()



        # ==============================
        # CHECK DUPLICATE USERNAME
        # ==============================


        cursor.execute(
            """
            SELECT id
            FROM users
            WHERE username=%s
            """,
            (username,)
        )


        existing_user = cursor.fetchone()



        if existing_user:

            st.error(
                "Username already exists. Please choose another."
            )

            st.stop()



        # ==============================
        # HASH PASSWORD
        # ==============================


        hashed_password = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode()



        # ==============================
        # INSERT CUSTOMER
        # ==============================


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
