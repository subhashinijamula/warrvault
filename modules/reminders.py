
import streamlit as st
from datetime import date
from dateutil.relativedelta import relativedelta

from database.db_connection import get_connection


# Generate reminders for all products
def generate_reminders(user_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT product_id, expiry_date
        FROM products
        WHERE user_id = ?
    """, (user_id,))

    products = cursor.fetchall()

    reminder_days = [30, 15, 7, 0]

    for product in products:

        product_id = product[0]
        expiry_date = date.fromisoformat(product[1])

        for days in reminder_days:

            reminder_date = expiry_date - relativedelta(days=days)

            # Check whether this reminder already exists
            cursor.execute("""
                SELECT reminder_id
                FROM reminders
                WHERE product_id = ?
                AND reminder_date = ?
                AND reminder_type = ?
            """, (
                product_id,
                reminder_date.isoformat(),
                f"{days} Days Before" if days > 0 else "Expiry Day"
            ))

            existing = cursor.fetchone()

            if existing is None:

                cursor.execute("""
                    INSERT INTO reminders
                    (product_id, reminder_date, reminder_type, status)
                    VALUES (?, ?, ?, ?)
                """, (
                    product_id,
                    reminder_date.isoformat(),
                    f"{days} Days Before" if days > 0 else "Expiry Day",
                    "Pending"
                ))

    connection.commit()
    connection.close()


# Get all reminders for the logged-in user
def get_reminders(user_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            reminders.reminder_id,
            products.product_name,
            products.brand,
            reminders.reminder_date,
            reminders.reminder_type,
            reminders.status,
            products.expiry_date
        FROM reminders
        JOIN products
        ON reminders.product_id = products.product_id
        WHERE products.user_id = ?
        ORDER BY reminders.reminder_date
    """, (user_id,))

    reminders = cursor.fetchall()

    connection.close()

    return reminders


# Mark a reminder as completed
def complete_reminder(reminder_id, user_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE reminders
        SET status = 'Completed'
        WHERE reminder_id = ?
        AND product_id IN (
            SELECT product_id
            FROM products
            WHERE user_id = ?
        )
    """, (reminder_id, user_id))

    connection.commit()
    connection.close()


# Display reminder information
def render_reminder_list(reminders):

    today = date.today()

    if not reminders:
        st.info("No reminders available.")
        return

    for reminder in reminders:

        reminder_id = reminder[0]
        product_name = reminder[1]
        brand = reminder[2]
        reminder_date = date.fromisoformat(reminder[3])
        reminder_type = reminder[4]
        status = reminder[5]

        st.divider()

        st.subheader(f"📦 {product_name}")

        st.write(f"Brand: {brand}")
        st.write(f"Reminder: {reminder_type}")
        st.write(f"Date: {reminder_date.strftime('%d-%m-%Y')}")

        if status == "Completed":

            st.success("Completed")

        elif reminder_date <= today:

            st.warning("Reminder Due")

        else:

            st.info("Upcoming Reminder")

        if status != "Completed":

            if st.button(
                "Mark as Completed",
                key=f"complete_{reminder_id}"
            ):

                st.session_state.completed_reminder = reminder_id
                st.rerun()


# Main reminder page
def render_reminders(user):

    user_id = user["user_id"]

    st.title("🔔 Warranty Reminders")

    st.caption(
        "Stay informed about your upcoming warranty expirations."
    )

    # Generate reminders automatically
    generate_reminders(user_id)

    # Complete reminder action
    if "completed_reminder" in st.session_state:

        complete_reminder(
            st.session_state.completed_reminder,
            user_id
        )

        del st.session_state.completed_reminder
        st.rerun()

    reminders = get_reminders(user_id)

    if reminders:

        today = date.today()

        upcoming = [
            r for r in reminders
            if date.fromisoformat(r[3]) > today
            and r[5] != "Completed"
        ]

        due = [
            r for r in reminders
            if date.fromisoformat(r[3]) <= today
            and r[5] != "Completed"
        ]

        completed = [
            r for r in reminders
            if r[5] == "Completed"
        ]

        tab1, tab2, tab3 = st.tabs([
            "📅 Upcoming",
            "⚠️ Due",
            "✅ Completed"
        ])

        with tab1:
            st.subheader("Upcoming Reminders")
            render_reminder_list(upcoming)

        with tab2:
            st.subheader("Reminders Due")
            render_reminder_list(due)

        with tab3:
            st.subheader("Completed Reminders")
            render_reminder_list(completed)

    else:

        st.info(
            "Add a product with a warranty to generate reminders."
        )
