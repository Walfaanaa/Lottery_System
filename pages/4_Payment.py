import streamlit as st
from database import get_connection
import os
import uuid


st.set_page_config(
    page_title="Lottery Payment",
    layout="centered"
)


st.title("💳 Lottery Payment")


# ======================================================
# CHECK LOGIN
# ======================================================

if (
    not st.session_state.get("logged_in", False)
    or "user_id" not in st.session_state
):

    st.warning(
        "Your session has expired. Please login again."
    )

    st.stop()


user_id = st.session_state["user_id"]


conn = None
cursor = None


try:

    conn = get_connection()

    cursor = conn.cursor(dictionary=True)


    # ======================================================
    # GET PENDING PAYMENT TICKET
    # ======================================================

    cursor.execute(
        """
        SELECT
            id,
            lottery_type,
            ticket_price,
            status
        FROM tickets
        WHERE user_id=%s
        AND status='Pending Payment'
        LIMIT 1
        """,
        (user_id,)
    )


    ticket = cursor.fetchone()


    if ticket is None:

        st.warning(
            "No pending ticket found. Please buy a ticket first."
        )

        st.stop()



    # ======================================================
    # CHECK EXISTING PAYMENT
    # ======================================================

    cursor.execute(
        """
        SELECT id
        FROM payments
        WHERE ticket_id=%s
        AND user_id=%s
        """,
        (
            ticket["id"],
            user_id
        )
    )


    payment = cursor.fetchone()


    if payment:

        st.info(
            "Payment already submitted. Waiting for approval."
        )

        st.stop()



    # ======================================================
    # SHOW PAYMENT INFORMATION
    # ======================================================


    st.info(
        f"""
Lottery Type: {ticket['lottery_type']}

Amount: {ticket['ticket_price']} ETB

Ticket number will be assigned after payment approval.
"""
    )



    # ======================================================
    # LOAD BANKS
    # ======================================================

    cursor.execute(
        """
        SELECT *
        FROM banks
        WHERE status='Active'
        ORDER BY bank_name
        """
    )


    banks = cursor.fetchall()


    if not banks:

        st.error(
            "No active bank account found."
        )

        st.stop()



    bank_names = [
        bank["bank_name"]
        for bank in banks
    ]


    selected_bank = st.selectbox(
        "Select Payment Bank",
        bank_names
    )


    bank_info = next(
        bank
        for bank in banks
        if bank["bank_name"] == selected_bank
    )



    st.info(
        f"""
Bank: {bank_info['bank_name']}

Account Name: {bank_info['account_name']}

Account Number: {bank_info['account_number']}
"""
    )



    # ======================================================
    # PAYMENT DETAILS
    # ======================================================

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



    # ======================================================
    # SUBMIT PAYMENT
    # ======================================================

    if st.button(
        "Submit Payment",
        use_container_width=True
    ):


        if receipt is None:

            st.error(
                "Please upload receipt."
            )


        elif transaction_reference.strip()=="":
            
            st.error(
                "Please enter transaction reference."
            )


        else:


            # Save receipt

            upload_folder = "uploads"

            os.makedirs(
                upload_folder,
                exist_ok=True
            )


            extension = os.path.splitext(
                receipt.name
            )[1]


            filename = (
                f"{uuid.uuid4().hex}"
                f"{extension}"
            )


            file_path = os.path.join(
                upload_folder,
                filename
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
                    user_id,
                    ticket_id,
                    bank_id,
                    amount,
                    receipt_file,
                    transaction_reference,
                    status
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    'Pending'
                )
                """,
                (
                    user_id,
                    ticket["id"],
                    bank_info["bank_id"],
                    ticket["ticket_price"],
                    file_path,
                    transaction_reference.strip()
                )
            )



            # Update ticket status

            cursor.execute(
                """
                UPDATE tickets
                SET status='Payment Submitted'
                WHERE id=%s
                """,
                (
                    ticket["id"],
                )
            )



            conn.commit()



            st.success(
                "✅ Payment submitted successfully."
            )


            st.info(
                "Waiting for administrator approval."
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
