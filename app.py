import streamlit as st
from database import get_connection

st.set_page_config(
    page_title="Lottery Management System",
    layout="wide"
)

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


if "logged_in" not in st.session_state:
    st.session_state.logged_in = False


if not st.session_state.logged_in:

    st.title("Lottery Management System Login")

    username = st.text_input("Username")
    password = st.text_input(
        "Password",
        type="password"
    )

    if st.button("Login"):

        user = login(username, password)

        if user and user[2] == "Active":

            st.session_state.logged_in = True
            st.session_state.username = user[0]
            st.session_state.role = user[1]

            st.rerun()

        else:
            st.error("Invalid login")

else:

    st.success(
        f"Welcome {st.session_state.username}"
    )

    st.write(
        "Dashboard will load here"
    )
