import streamlit as st
import bcrypt
from database import get_connection


st.title("🔐 User Login")


# If already logged in
if "logged_in" in st.session_state and st.session_state["logged_in"]:

    st.success(
        f"Already logged in as {st.session_state['full_name']}"
    )

    st.write(
        "Role:",
        st.session_state["role"]
    )

    if st.button("Logout"):

        st.session_state.clear()
        st.rerun()

    st.stop()


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
            SELECT
                id,
                username,
                password,
                email,
                role,
                status,
                full_name,
                phone
            FROM users
            WHERE username=%s
            """,
            (username,)
        )


        user = cursor.fetchone()


        if user is None:

            st.error("Username not found")


        else:

            if user["status"] != "Active":

                st.error(
                    "Account is inactive"
                )

            else:

                stored_password = user["password"]


                if bcrypt.checkpw(
                    password.encode("utf-8"),
                    stored_password.encode("utf-8")
                ):


                    # Create session
                    st.session_state["logged_in"] = True
                    st.session_state["user_id"] = user["id"]
                    st.session_state["username"] = user["username"]
                    st.session_state["role"] = user["role"]
                    st.session_state["full_name"] = user["full_name"]


                    st.success(
                        f"Welcome {user['full_name']} ✅"
                    )

                    st.rerun()


                else:

                    st.error(
                        "Incorrect password"
                    )


        cursor.close()
        conn.close()


    except Exception as e:

        st.error(e)
