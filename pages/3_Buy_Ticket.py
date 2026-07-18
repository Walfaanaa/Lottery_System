import streamlit as st
from database import get_connection
import random


st.title("🎟 Buy Lottery Ticket")


# Secure session check
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


        # Get already sold ticket numbers
        cursor.execute(
            """
            SELECT ticket_number
            FROM tickets
            """
        )


        sold_numbers = [
            row["ticket_number"]
            for row in cursor.fetchall()
        ]


        # Available numbers 1-100
        available_numbers = [
            x for x in range(1, 101)
            if x not in sold_numbers
        ]


        if not available_numbers:

            st.error(
                "All lottery tickets have been sold!"
            )

            st.stop()


        # Select ticket number
        ticket_number = random.choice(
            available_numbers
        )


        # Insert purchased ticket
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
                %s,
                %s,
                %s,
                %s
            )
            """,
            (
                user_id,
                ticket_number,
                lottery_type,
                ticket_price,
                "Sold"
            )
        )


        conn.commit()


        st.success(
            "Ticket purchased successfully ✅"
        )


        st.write(
            "Ticket Number:",
            ticket_number
        )


        st.write(
            "Amount:",
            ticket_price,
            "ETB"
        )


    cursor.close()
    conn.close()


except Exception as e:

    st.error(e)
