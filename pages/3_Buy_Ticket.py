import streamlit as st
from database import get_connection


st.title("🎟 Buy Lottery Ticket")


# ======================================================
# CHECK LOGIN
# ======================================================

if (
    "logged_in" not in st.session_state
    or not st.session_state["logged_in"]
    or "user_id" not in st.session_state
):

    st.warning("Please login first")
    st.stop()


user_id = st.session_state["user_id"]


st.info(
    f"Customer: {st.session_state['full_name']}"
)


conn = None
cursor = None


try:

    conn = get_connection()

    cursor = conn.cursor(dictionary=True)


    lottery_type = st.selectbox(
        "Lottery Type",
        [
            "Weekly Lottery",
            "Monthly Lottery"
        ]
    )


    ticket_price = st.number_input(
        "Ticket Price",
        min_value=10,
        value=100
    )


    if st.button("Buy Ticket"):


        # Check existing pending ticket

        cursor.execute(
            """
            SELECT id
            FROM tickets
            WHERE user_id=%s
            AND status IN ('Pending Payment','Payment Submitted')
            LIMIT 1
            """,
            (user_id,)
        )


        existing_ticket = cursor.fetchone()


        if existing_ticket:

            st.warning(
                "You already have a pending payment ticket."
            )

            st.stop()



        # Create ticket reservation WITHOUT number

        cursor.execute(
            """
            INSERT INTO tickets
            (
                user_id,
                ticket_number,
                lottery_type,
                ticket_price,
                status
            )
            VALUES
            (
                %s,
                NULL,
                %s,
                %s,
                'Pending Payment'
            )
            """,
            (
                user_id,
                lottery_type,
                ticket_price
            )
        )


        conn.commit()


        st.success(
            "Ticket reservation created successfully ✅"
        )


        st.info(
            """
Please complete payment.

Your ticket number will be assigned after payment approval.
"""
        )



except Exception as e:

    if conn:
        conn.rollback()

    st.error(
        f"Error: {e}"
    )


finally:

    if cursor:
        cursor.close()

    if conn:
        conn.close()
