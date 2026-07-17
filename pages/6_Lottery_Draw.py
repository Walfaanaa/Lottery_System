import streamlit as st
from database import get_connection
import random


st.title("🎯 Lottery Draw")


# ==============================
# CHECK ADMIN
# ==============================

if "logged_in" not in st.session_state:
    st.warning("Please login first")
    st.stop()


if st.session_state.get("role") != "Admin":
    st.error("Admin only")
    st.stop()



conn = get_connection()
cursor = conn.cursor(dictionary=True)



# ==============================
# LOAD LOTTERY
# ==============================

cursor.execute(
    """
    SELECT *
    FROM lotteries
    WHERE status='Open'
    """
)

lottery = cursor.fetchone()


if lottery is None:

    st.warning(
        "No open lottery found"
    )

    st.stop()



st.success(
    lottery["lottery_name"]
)



# ==============================
# CHECK EXISTING WINNER
# ==============================

cursor.execute(
    """
    SELECT COUNT(*) AS total
    FROM winners
    WHERE lottery_id=%s
    """,
    (
        lottery["lottery_id"],
    )
)


winner_check = cursor.fetchone()


if winner_check["total"] > 0:

    st.warning(
        "Winner already selected for this lottery"
    )

    cursor.close()
    conn.close()

    st.stop()



# ==============================
# SOLD TICKETS
# ==============================

cursor.execute(
    """
    SELECT
        t.ticket_id,
        t.ticket_no,
        t.buyer_id,
        u.full_name

    FROM tickets t

    JOIN users u
    ON t.buyer_id=u.user_id

    WHERE t.status='Sold'

    AND t.lottery_id=%s
    """,
    (
        lottery["lottery_id"],
    )
)


tickets = cursor.fetchall()



sold_count = len(tickets)


st.write(
    "Sold Tickets:",
    sold_count
)



if sold_count == 0:

    st.warning(
        "No sold tickets available"
    )

    st.stop()



# ==============================
# FINANCIAL CALCULATION
# ==============================

ticket_price = float(
    lottery["ticket_price"]
)


commission_percent = float(
    lottery["commission_percent"]
)


total_sales = sold_count * ticket_price


commission = (
    total_sales *
    commission_percent / 100
)


prize_pool = (
    total_sales -
    commission
)



st.write(
    "Total Sales:",
    total_sales,
    "ETB"
)


st.write(
    f"Commission ({commission_percent}%):",
    commission,
    "ETB"
)


st.write(
    "Prize Pool:",
    prize_pool,
    "ETB"
)



# ==============================
# DRAW BUTTON
# ==============================

if st.button("🎲 Draw Winner"):


    winner = random.choice(
        tickets
    )


    # Save winner

    cursor.execute(
        """
        INSERT INTO winners
        (
        lottery_id,
        ticket_id,
        buyer_id,
        prize_amount
        )

        VALUES
        (%s,%s,%s,%s)

        """,
        (
        lottery["lottery_id"],
        winner["ticket_id"],
        winner["buyer_id"],
        prize_pool
        )
    )



    # Close lottery

    cursor.execute(
        """
        UPDATE lotteries

        SET status='Closed'

        WHERE lottery_id=%s
        """,
        (
        lottery["lottery_id"],
        )
    )



    conn.commit()



    st.balloons()


    st.success(
        "🎉 Congratulations!"
    )


    st.write(
        "Winner:",
        winner["full_name"]
    )


    st.write(
        "Ticket No:",
        winner["ticket_no"]
    )


    st.write(
        "Prize:",
        prize_pool,
        "ETB"
    )



cursor.close()
conn.close()