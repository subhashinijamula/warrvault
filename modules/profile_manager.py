
import streamlit as st
import bcrypt
import sqlite3

from database.db_connection import get_connection


# Get the logged-in user's details
def get_profile(user_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT name, email, created_at
        FROM users
        WHERE user_id = ?
    """, (user_id,))

    profile = cursor.fetchone()

    connection.close()

    return profile


# Update name and email
def update_profile(user_id, name, email):

    connection = get_connection()
    cursor = connection.cursor()

    try:

        cursor.execute("""
            UPDATE users
            SET name = ?, email = ?
            WHERE user_id = ?
        """, (name, email, user_id))

        connection.commit()
        connection.close()

        return True, "Profile updated successfully!"

    except sqlite3.IntegrityError:

        connection.close()

        return False, "This email address is already registered."


# Change account password
def update_password(user_id, current_password, new_password):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT password_hash
        FROM users
        WHERE user_id = ?
    """, (user_id,))

    result = cursor.fetchone()

    if result is None:

        connection.close()

        return False, "User account not found."

    stored_password = result[0].encode("utf-8")

    # Verify current password
    if not bcrypt.checkpw(
        current_password.encode("utf-8"),
        stored_password
    ):

        connection.close()

        return False, "Current password is incorrect."

    # Hash the new password
    new_password_hash = bcrypt.hashpw(
        new_password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    cursor.execute("""
        UPDATE users
        SET password_hash = ?
        WHERE user_id = ?
    """, (new_password_hash, user_id))

    connection.commit()
    connection.close()

    return True, "Password changed successfully!"


# Display profile page
def render_profile(user):

    user_id = user["user_id"]

    st.title("👤 My Profile")

    st.caption(
        "Manage your personal information and account security."
    )

    profile = get_profile(user_id)

    if profile is None:

        st.error("Unable to load your profile.")

        return

    name, email, created_at = profile

    # Account information
    st.subheader("Account Information")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Account Name", name)

    with col2:
        st.metric("Registered Email", email)

    st.caption(f"Account created: {created_at}")

    st.divider()

    # Update profile
    st.subheader("Update Personal Information")

    with st.form("update_profile_form"):

        new_name = st.text_input(
            "Full Name",
            value=name
        )

        new_email = st.text_input(
            "Email Address",
            value=email
        )

        update_button = st.form_submit_button(
            "Update Profile"
        )

        if update_button:

            if not new_name.strip() or not new_email.strip():

                st.error("Please fill in all fields.")

            elif "@" not in new_email or "." not in new_email:

                st.error("Please enter a valid email address.")

            else:

                success, message = update_profile(
                    user_id,
                    new_name.strip(),
                    new_email.strip().lower()
                )

                if success:

                    st.session_state.user["name"] = new_name.strip()
                    st.session_state.user["email"] = new_email.strip().lower()

                    st.success(message)

                    st.rerun()

                else:

                    st.error(message)

    st.divider()

    # Change password
    st.subheader("Change Password")

    with st.form("change_password_form"):

        current_password = st.text_input(
            "Current Password",
            type="password"
        )

        new_password = st.text_input(
            "New Password",
            type="password"
        )

        confirm_password = st.text_input(
            "Confirm New Password",
            type="password"
        )

        password_button = st.form_submit_button(
            "Change Password"
        )

        if password_button:

            if not current_password or not new_password or not confirm_password:

                st.error("Please fill in all password fields.")

            elif len(new_password) < 8:

                st.error("New password must contain at least 8 characters.")

            elif new_password != confirm_password:

                st.error("New passwords do not match.")

            else:

                success, message = update_password(
                    user_id,
                    current_password,
                    new_password
                )

                if success:

                    st.success(message)

                else:

                    st.error(message)
