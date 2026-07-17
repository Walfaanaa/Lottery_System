import streamlit as st
import bcrypt
from database import get_connection


st.title("🔐 User Login")


username = st.text_input("Username")

password = st.text_input(
    "Password",
    type="password"
)


if st.button("Login"):

    try:

        conn = get_connection()

        cursor = conn.cursor(dictionary=True)


        cursor.execute(
            """
            SELECT *
            FROM users
            WHERE username=%s
            """,
            (username,)
        )


        user = cursor.fetchone()


        if user is None:

            st.error("Username not found")


        else:

            stored_password = user["password"]


            if bcrypt.checkpw(
                password.encode("utf-8"),
                stored_password.encode("utf-8")
            ):

                if user["status"] == "Inactive":

                    st.error(
                        "Your account is inactive"
                    )

                else:

                    st.session_state["logged_in"] = True
                    st.session_state["user_id"] = user["user_id"]
                    st.session_state["username"] = user["username"]
                    st.session_state["role"] = user["role"]


                    st.success(
                        f"Welcome {user['full_name']} ✅"
                    )


                    st.write(
                        "Role:",
                        user["role"]
                    )


            else:

                st.error(
                    "Incorrect password"
                )


        cursor.close()
        conn.close()


    except Exception as e:

        st.error(e)