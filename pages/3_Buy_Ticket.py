import streamlit as st
from database import get_connection


st.title("🎟 Buy Lottery Ticket")


# Check login

if "logged_in" not in st.session_state:

    st.warning("Please login first")

    st.stop()


user_id = st.session_state["user_id"]


try:

    conn = get_connection()

    cursor = conn.cursor(dictionary=True)


    # Get active lottery

    cursor.execute(
        """
        SELECT *
        FROM lotteries
        WHERE status='Open'
        LIMIT 1
        """
    )

    lottery = cursor.fetchone()


    if lottery is None:

        st.error("No active lottery available")

        st.stop()


    st.subheader(
        lottery["lottery_name"]
    )

    st.write(
        "Ticket Price:",
        lottery["ticket_price"],
        "ETB"
    )


    # Available tickets

    cursor.execute(
        """
        SELECT ticket_no
        FROM tickets
        WHERE lottery_id=%s
        AND status='Available'
        ORDER BY ticket_no
        """,
        (lottery["lottery_id"],)
    )


    tickets = cursor.fetchall()


    available_numbers = [
        row["ticket_no"]
        for row in tickets
    ]


    if len(available_numbers) == 0:

        st.error(
            "🚨 All tickets have been sold!"
        )

    else:

        st.success(
            f"Available Tickets: {len(available_numbers)}"
        )


        selected_ticket = st.selectbox(
            "Select Ticket Number",
            available_numbers
        )


        if st.button("Reserve Ticket"):


            cursor.execute(
                """
                UPDATE tickets

                SET
                status='Pending',
                buyer_id=%s

                WHERE
                lottery_id=%s
                AND ticket_no=%s
                AND status='Available'
                """,
                (
                user_id,
                lottery["lottery_id"],
                selected_ticket
                )
            )


            conn.commit()


            st.success(
                f"Ticket {selected_ticket} reserved successfully"
            )


    cursor.close()
    conn.close()


except Exception as e:

    st.error(e)