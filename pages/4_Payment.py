import os
import uuid
import streamlit as st
from database import get_connection

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
    st.warning("Please login first")
    st.stop()

user_id = st.session_state["user_id"]

conn = None
cursor = None

try:

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # ======================================================
    # FIND CUSTOMER TICKET
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
        AND status IN ('Pending Payment','Payment Submitted')
        LIMIT 1
        """,
        (user_id,)
    )

    ticket = cursor.fetchone()

    if ticket is None:
        st.warning("No pending ticket found. Please buy a ticket first.")
        st.stop()

    # ======================================================
    # CHECK EXISTING PAYMENT
    # ======================================================

    cursor.execute(
        """
        SELECT
            id,
            payment_status
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
        st.info("Payment already submitted. Waiting for approval.")
        st.stop()

    # ======================================================
    # PAYMENT INFORMATION
    # ======================================================

    st.info(
        f"""
Lottery Type: {ticket['lottery_type']}

Amount: {ticket['ticket_price']} ETB

🎟 Ticket number will be assigned after payment approval.
"""
    )

    # ======================================================
    # LOAD BANK ACCOUNT
    # ======================================================

    cursor.execute(
        """
        SELECT
            bank_id,
            bank_name,
            account_name,
            account_number
        FROM banks
        WHERE status='Active'
        ORDER BY bank_name
        """
    )

    banks = cursor.fetchall()

    if not banks:
        st.error("No active bank account found.")
        st.stop()

    bank_names = [bank["bank_name"] for bank in banks]

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

    transaction_reference = st.text_input(
        "Transaction Reference"
    )

    receipt = st.file_uploader(
        "Upload Payment Receipt",
        type=["jpg", "jpeg", "png", "pdf"]
    )

    # ======================================================
    # SUBMIT PAYMENT
    # ======================================================

    if st.button(
        "Submit Payment",
        use_container_width=True
    ):

        if transaction_reference.strip() == "":
            st.error("Please enter transaction reference.")

        elif receipt is None:
            st.error("Please upload the payment receipt.")

        else:

            # Optional: Save receipt locally
            upload_dir = "receipts"
            os.makedirs(upload_dir, exist_ok=True)

            file_extension = os.path.splitext(receipt.name)[1]
            filename = f"{uuid.uuid4()}{file_extension}"
            receipt_path = os.path.join(upload_dir, filename)

            with open(receipt_path, "wb") as f:
                f.write(receipt.getbuffer())

           # Insert payment
cursor.execute(
    """
    INSERT INTO payments
    (
        user_id,
        ticket_id,
        bank_id,
        transaction_reference,
        amount,
        receipt_path,
        payment_status
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
        transaction_reference.strip(),
        ticket["ticket_price"],
        receipt_path
    )
)

            # Update ticket
            cursor.execute(
                """
                UPDATE tickets
                SET status='Payment Submitted'
                WHERE id=%s
                """,
                (ticket["id"],)
            )

            conn.commit()

            st.success("✅ Payment submitted successfully.")
            st.info("Waiting for administrator approval.")

except Exception as e:

    if conn:
        conn.rollback()

    st.error(f"Error: {e}")

finally:

    if cursor:
        cursor.close()

    if conn:
        conn.close()
