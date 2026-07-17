import streamlit as st
from database import get_connection
import os


st.title("🛠 Admin Dashboard")


# ==============================
# CHECK LOGIN
# ==============================

if "logged_in" not in st.session_state:
    st.warning("Please login first")
    st.stop()


if st.session_state.get("role") != "Admin":
    st.error("Access denied. Admin only.")
    st.stop()


# ==============================
# DATABASE CONNECTION
# ==============================

conn = get_connection()
cursor = conn.cursor(dictionary=True)


# ==============================
# PENDING PAYMENTS
# ==============================

st.subheader("💳 Pending Payments")


cursor.execute(
    """
    SELECT
        p.payment_id,
        p.amount,
        p.transaction_reference,
        p.receipt_file,
        p.status,

        t.ticket_id,
        t.ticket_no,

        u.full_name,

        b.bank_name,
        b.account_number

    FROM payments p

    JOIN tickets t
        ON p.ticket_id = t.ticket_id

    JOIN users u
        ON p.buyer_id = u.user_id

    JOIN banks b
        ON p.bank_id = b.bank_id

    WHERE p.status='Pending'
    """
)


payments = cursor.fetchall()


if not payments:

    st.info("No pending payments")


else:

    for payment in payments:

        st.write("--------------------------")

        st.write(
            "Buyer:",
            payment["full_name"]
        )

        st.write(
            "Ticket No:",
            payment["ticket_no"]
        )

        st.write(
            "Bank:",
            payment["bank_name"]
        )

        st.write(
            "Account Number:",
            payment["account_number"]
        )

        st.write(
            "Amount:",
            payment["amount"],
            "ETB"
        )

        st.write(
            "Transaction Reference:",
            payment["transaction_reference"]
        )


        # Receipt preview

        receipt_path = payment["receipt_file"]

        if receipt_path:

            st.write("Receipt:")

            if os.path.exists(receipt_path):

                if receipt_path.lower().endswith(
                    (".png",".jpg",".jpeg")
                ):

                    st.image(receipt_path)

                else:

                    st.write(receipt_path)

            else:

                st.warning(
                    "Receipt file not found"
                )


        col1, col2 = st.columns(2)


        # ==============================
        # APPROVE PAYMENT
        # ==============================

        with col1:

            if st.button(
                "✅ Approve",
                key=f"approve_{payment['payment_id']}"
            ):


                # Update payment

                cursor.execute(
                    """
                    UPDATE payments

                    SET status='Approved'

                    WHERE payment_id=%s
                    """,
                    (
                        payment["payment_id"],
                    )
                )


                # Update ticket

                cursor.execute(
                    """
                    UPDATE tickets

                    SET
                    status='Sold',
                    sold_date=NOW()

                    WHERE ticket_id=%s
                    """,
                    (
                        payment["ticket_id"],
                    )
                )


                conn.commit()


                st.success(
                    "Payment approved and ticket sold"
                )

                st.rerun()



        # ==============================
        # REJECT PAYMENT
        # ==============================

        with col2:

            if st.button(
                "❌ Reject",
                key=f"reject_{payment['payment_id']}"
            ):


                # Update payment

                cursor.execute(
                    """
                    UPDATE payments

                    SET status='Rejected'

                    WHERE payment_id=%s
                    """,
                    (
                        payment["payment_id"],
                    )
                )


                # Release ticket

                cursor.execute(
                    """
                    UPDATE tickets

                    SET
                    status='Available',
                    buyer_id=NULL,
                    payment_id=NULL

                    WHERE ticket_id=%s
                    """,
                    (
                        payment["ticket_id"],
                    )
                )


                conn.commit()


                st.warning(
                    "Payment rejected and ticket released"
                )

                st.rerun()



cursor.close()
conn.close()