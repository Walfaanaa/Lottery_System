import streamlit as st
from database import get_connection
import uuid


st.title("🎟 Buy Lottery Ticket")


# Check login
if "logged_in" not in st.session_state:

    st.warning("Please login first")
    st.stop()


user_id = st.session_state["user_id"]


try:

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)


    # Lottery information
    lottery_type = st.selectbox(
        "Select Lottery Type",
        [
            "Weekly Lottery",
            "Monthly Lottery"
        ]
    )


    ticket_price = st.number_input(
        "Ticket Price (ETB)",
        min_value=10,
        value=100
    )


    if st.button("Buy Ticket"):


        # Generate ticket number
        ticket_number = (
            "LOT-"
            + str(uuid.uuid4())[:8].upper()
        )


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
            (%s,%s,%s,%s,%s)
            """,
            (
                user_id,
                ticket_number,
                lottery_type,
                ticket_price,
                "Pending"
            )
        )


        conn.commit()


        st.success(
            "Ticket created successfully"
        )


        st.info(
            f"""
            Ticket Number:
            {ticket_number}

            Amount:
            {ticket_price} ETB

            Status:
            Pending
            """
        )


    cursor.close()
    conn.close()


except Exception as e:

    st.error(e)
