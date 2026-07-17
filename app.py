import streamlit as st
from database import get_connection


# ==========================
# LOGIN FUNCTION
# ==========================

def login(username, password):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT username, role, status
        FROM users
        WHERE username=%s
        AND password=%s
        """,
        (username, password)
    )

    user = cursor.fetchone()

    cursor.close()
    conn.close()

    return user


# ==========================
# LOGIN PAGE
# ==========================

st.title("Lottery Management System Login")


username = st.text_input("Username")

password = st.text_input(
    "Password",
    type="password"
)


if st.button("Login"):

    user = login(username, password)

    if user:

        if user[2] == "Active":

            st.session_state["logged_in"] = True
            st.session_state["username"] = user[0]
            st.session_state["role"] = user[1]

            st.success(
                f"Welcome {user[0]}"
            )

            st.rerun()

        else:
            st.error("Account inactive")

    else:
        st.error("Invalid username or password")


# ==========================
# AFTER LOGIN
# ==========================

if st.session_state.get("logged_in"):

    st.sidebar.success(
        f"User: {st.session_state['username']}"
    )

    st.write(
        "Your Lottery Dashboard will appear here"
    )
