import streamlit as st
from database import get_connection
import os
import uuid

st.set_page_config(page_title="Lottery Payment", layout="centered")

st.title("💳 Lottery Payment")

# ======================================================
# CHECK LOGIN
# ======================================================
if (
    not st.session_state.get("logged_in", False)
    or "user_id" not in st.session_state
):
    st.warning("Your session has expired. Please login again.")

    try:
        st.switch_page("app.py")
    except Exception:
        pass

    st.stop()

buyer_id = st.session_state.get("user_id")

conn = None
cursor = None

try:

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # ======================================================
    # GET PENDING TICKET
    # ======================================================

    cursor.execute(
        """
        SELECT
            ticket_id,
            ticket_no,
            price,
            payment_id
        FROM tickets
        WHERE buyer_id=%s
        AND status='Pending'
        LIMIT 1
        """,
        (buyer_id,)
    )

    ticket = cursor.fetchone()

    if ticket is None:
        st.warning("No pending ticket found. Please reserve a ticket first.")
        st.stop()

    # ======================================================
    # CHECK DUPLICATE PAYMENT
    # ======================================================

    cursor.execute(
        """
        SELECT payment_id
        FROM payments
        WHERE ticket_id=%s
        """,
        (ticket["ticket_id"],)
    )

    payment = cursor.fetchone()

    if payment:
        st.info("Payment has already been submitted for this ticket.")
        st.stop()

    # ======================================================
    # SHOW TICKET
    # ======================================================

    st.success(f"🎟 Ticket Number: {ticket['ticket_no']}")
    st.write(f"**Payment Amount:** {ticket['price']} ETB")

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
**Bank:** {bank_info['bank_name']}

**Account Name:** {bank_info['account_name']}

**Account Number:** {bank_info['account_number']}
"""
    )

    # ======================================================
    # PAYMENT FORM
    # ======================================================

    receipt = st.file_uploader(
        "Upload Receipt",
        type=["png", "jpg", "jpeg", "pdf"]
    )

    transaction_reference = st.text_input(
        "Transaction Reference"
    )

    # ======================================================
    # SUBMIT
    # ======================================================

    if st.button("Submit Payment", use_container_width=True):

        if receipt is None:
            st.error("Please upload your payment receipt.")

        elif transaction_reference.strip() == "":
            st.error("Please enter the transaction reference.")

        else:

            upload_folder = "uploads"
            os.makedirs(upload_folder, exist_ok=True)

            extension = os.path.splitext(receipt.name)[1]

            filename = f"{uuid.uuid4().hex}{extension}"

            file_path = os.path.join(upload_folder, filename)

            with open(file_path, "wb") as f:
                f.write(receipt.getbuffer())

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
                    buyer_id,
                    ticket["ticket_id"],
                    bank_info["bank_id"],
                    ticket["price"],
                    file_path,
                    transaction_reference.strip()
                )
            )

            payment_id = cursor.lastrowid

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
