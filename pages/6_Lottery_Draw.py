import streamlit as st
from database import get_connection
import random


st.title("🎲 Lottery Draw")


# ==============================
# ADMIN CHECK
# ==============================

if not st.session_state.get("logged_in", False):

    st.warning("Please login first")
    st.stop()


if st.session_state.get("role","").lower() != "admin":

    st.error("Access denied. Admin only.")
    st.stop()



conn = get_connection()
cursor = conn.cursor(dictionary=True)



# ==============================
# SOLD TICKETS
# ==============================

cursor.execute(
    """
    SELECT

        t.id,
        t.ticket_number,
        t.lottery_type,
        t.ticket_price,

        u.full_name,
        u.phone


    FROM tickets t


    JOIN users u

        ON t.user_id = u.id


    WHERE t.status='Sold'

    AND t.ticket_number IS NOT NULL

    ORDER BY t.ticket_number

    """
)


tickets = cursor.fetchall()



st.subheader("🎟 Sold Tickets")


if not tickets:

    st.info(
        "No approved tickets available for draw."
    )

    st.stop()



for ticket in tickets:

    st.write(
        f"""
Ticket Number: {ticket['ticket_number']}

Customer: {ticket['full_name']}

Phone: {ticket['phone']}

Lottery: {ticket['lottery_type']}
"""
    )

    st.divider()



# ==============================
# DRAW BUTTON
# ==============================

if st.button(
    "🎉 Run Lottery Draw",
    use_container_width=True
):


    winner = random.choice(
        tickets
    )


    st.success(
        "🎊 Winner Selected!"
    )


    st.write(
        "Winning Ticket:",
        winner["ticket_number"]
    )


    st.write(
        "Winner:",
        winner["full_name"]
    )


    st.write(
        "Phone:",
        winner["phone"]
    )



cursor.close()
conn.close()


