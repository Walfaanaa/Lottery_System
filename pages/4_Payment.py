import streamlit as st
from database import get_connection
import os


st.title("💳 Lottery Payment")


# Check login
if "logged_in" not in st.session_state:
    st.warning("Please login first")
    st.stop()


buyer_id = st.session_state["user_id"]


try:

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)


    # Get user's pending ticket

    cursor.execute(
        """
        SELECT 
            t.ticket_id,
            t.ticket_no,
            t.price
        FROM tickets t
        WHERE t.buyer_id=%s
        AND t.status='Pending'
        """,
        (buyer_id,)
    )

    ticket = cursor.fetchone()


    if ticket is None:

        st.warning(
            "No pending ticket found. Please reserve a ticket first."
        )

        st.stop()


    st.success(
        f"Ticket Number: {ticket['ticket_no']}"
    )

    st.write(
        "Payment Amount:",
        ticket["price"],
        "ETB"
    )


    # Get active banks

    cursor.execute(
        """
        SELECT *
        FROM banks
        WHERE status='Active'
        """
    )

    banks = cursor.fetchall()


    bank_names = [
        bank["bank_name"]
        for bank in banks
    ]


    selected_bank = st.selectbox(
        "Select Payment Bank",
        bank_names
    )


    bank_info = next(
        bank for bank in banks
        if bank["bank_name"] == selected_bank
    )


    st.info(
        f"""
Bank: {bank_info['bank_name']}

Account Name:
{bank_info['account_name']}

Account Number:
{bank_info['account_number']}
"""
    )


    receipt = st.file_uploader(
        "Upload Payment Receipt",
        type=[
            "png",
            "jpg",
            "jpeg",
            "pdf"
        ]
    )


    transaction_reference = st.text_input(
        "Transaction Reference"
    )


    if st.button("Submit Payment"):


        if receipt is None:

            st.error(
                "Please upload receipt"
            )

        elif transaction_reference == "":

            st.error(
                "Enter transaction reference"
            )

        else:


            # Save receipt

            upload_folder = "uploads"

            os.makedirs(
                upload_folder,
                exist_ok=True
            )


            file_path = os.path.join(
                upload_folder,
                receipt.name
            )


            with open(
                file_path,
                "wb"
            ) as f:

                f.write(
                    receipt.getbuffer()
                )


            # Insert payment

            cursor.execute(
                """
                INSERT INTO payments
                (
                buyer_id,
                ticket_id,
                bank_id,
                amount,
                receipt_file,
                transaction_reference,
                status
                )
                VALUES
                (
                %s,%s,%s,%s,%s,%s,
                'Pending'
                )
                """,
                (
                buyer_id,
                ticket["ticket_id"],
                bank_info["bank_id"],
                ticket["price"],
                file_path,
                transaction_reference
                )
            )


            payment_id = cursor.lastrowid


            # Link payment to ticket

            cursor.execute(
                """
                UPDATE tickets

                SET payment_id=%s

                WHERE ticket_id=%s
                """,
                (
                payment_id,
                ticket["ticket_id"]
                )
            )


            conn.commit()


            st.success(
                "Payment submitted successfully. Waiting for approval."
            )


    cursor.close()
    conn.close()


except Exception as e:

    st.error(e)