import streamlit as st
from database import get_connection
import uuid


st.title("🎟 Buy Lottery Ticket")


# Secure session check
if (
    "logged_in" not in st.session_state
    or not st.session_state["logged_in"]
    or "user_id" not in st.session_state
):

    st.warning(
        "Please login first"
    )

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
            "Ticket purchased successfully"
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
