import streamlit as st
import bcrypt
from database import get_connection


st.title("📝 User Registration")


full_name = st.text_input("Full Name")
phone = st.text_input("Phone Number")
email = st.text_input("Email")
username = st.text_input("Username")

password = st.text_input(
    "Password",
    type="password"
)

confirm_password = st.text_input(
    "Confirm Password",
    type="password"
)


if st.button("Register"):

    if password != confirm_password:
        st.error("Passwords do not match")

    elif not full_name or not username or not password:
        st.warning("Please fill required fields")

    else:

        try:

            conn = get_connection()

            cursor = conn.cursor()

            # Check existing username

            cursor.execute(
                """
                SELECT username 
                FROM users
                WHERE username=%s
                """,
                (username,)
            )

            existing = cursor.fetchone()


            if existing:

                st.error("Username already exists")

            else:

                # Encrypt password

                hashed_password = bcrypt.hashpw(
                    password.encode("utf-8"),
                    bcrypt.gensalt()
                )


                cursor.execute(
                    """
                    INSERT INTO users
                    (
                    full_name,
                    phone,
                    email,
                    username,
                    password,
                    role,
                    status
                    )
                    VALUES
                    (
                    %s,%s,%s,%s,%s,
                    'User',
                    'Active'
                    )
                    """,
                    (
                    full_name,
                    phone,
                    email,
                    username,
                    hashed_password.decode("utf-8")
                    )
                )


                conn.commit()

                st.success(
                    "Registration successful ✅"
                )


            cursor.close()
            conn.close()


        except Exception as e:

            st.error(e)