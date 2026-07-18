import streamlit as st
from database import get_connection


st.title("🛠 Admin Dashboard")


# ==============================
# CHECK LOGIN
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
# PENDING PAYMENTS
# ==============================

st.subheader("💳 Pending Payments")


cursor.execute(
    """
    SELECT

        p.id AS payment_id,

        p.amount,

        p.transaction_reference,

        p.payment_status,

        t.id AS ticket_id,

        t.ticket_number,

        t.lottery_type,

        u.full_name,

        u.phone,

        b.bank_name,

        b.account_number


    FROM payments p


    JOIN tickets t
        ON p.ticket_id = t.id


    JOIN users u
        ON p.user_id = u.id


    JOIN banks b
        ON p.bank_id = b.bank_id


    WHERE p.payment_status='Pending'

    ORDER BY p.payment_date DESC

    """
)



payments = cursor.fetchall()



if not payments:

    st.info("No pending payments")


else:


    for payment in payments:


        st.divider()


        st.write(
            "Customer:",
            payment["full_name"]
        )


        st.write(
            "Phone:",
            payment["phone"]
        )


        st.write(
            "Lottery:",
            payment["lottery_type"]
        )


        st.write(
            "Amount:",
            payment["amount"],
            "ETB"
        )


        st.write(
            "Transaction:",
            payment["transaction_reference"]
        )


        st.write(
            "Bank:",
            payment["bank_name"]
        )


        st.write(
            "Account:",
            payment["account_number"]
        )



        col1, col2 = st.columns(2)



        # ==============================
        # APPROVE
        # ==============================

        with col1:


            if st.button(
                "✅ Approve Payment",
                key=f"approve_{payment['payment_id']}"
            ):


                # Find available ticket number 1-100

                cursor.execute(
                    """
                    SELECT ticket_number
                    FROM tickets
                    WHERE ticket_number IS NOT NULL
                    """
                )


                sold_numbers = [
                    row["ticket_number"]
                    for row in cursor.fetchall()
                ]


                available = [
                    x for x in range(1,101)
                    if x not in sold_numbers
                ]


                if not available:

                    st.error(
                        "All tickets sold"
                    )

                    st.stop()


                import random

                ticket_number = random.choice(
                    available
                )



                # Update payment

                cursor.execute(
                    """
                    UPDATE payments

                    SET payment_status='Approved'

                    WHERE id=%s
                    """,
                    (
                        payment["payment_id"],
                    )
                )



                # Assign ticket

                cursor.execute(
                    """
                    UPDATE tickets

                    SET
                    ticket_number=%s,
                    status='Sold'

                    WHERE id=%s

                    """,
                    (
                        ticket_number,
                        payment["ticket_id"]
                    )
                )


                conn.commit()


                st.success(
                    f"Payment approved. Ticket Number: {ticket_number}"
                )


                st.rerun()



        # ==============================
        # REJECT
        # ==============================


        with col2:


            if st.button(
                "❌ Reject Payment",
                key=f"reject_{payment['payment_id']}"
            ):


                cursor.execute(
                    """
                    UPDATE payments

                    SET payment_status='Rejected'

                    WHERE id=%s

                    """,
                    (
                        payment["payment_id"],
                    )
                )


                cursor.execute(
                    """
                    UPDATE tickets

                    SET status='Rejected'

                    WHERE id=%s

                    """,
                    (
                        payment["ticket_id"],
                    )
                )


                conn.commit()


                st.warning(
                    "Payment rejected"
                )


                st.rerun()



cursor.close()
conn.close()
