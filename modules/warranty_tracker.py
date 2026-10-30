
import streamlit as st

from datetime import date
from dateutil.relativedelta import relativedelta

from database.db_connection import get_connection


# -----------------------------------
# CALCULATE WARRANTY EXPIRY
# -----------------------------------

def calculate_expiry(purchase_date, duration, unit):

    if isinstance(purchase_date, str):
        purchase_date = date.fromisoformat(purchase_date)

    if unit == "Years":

        expiry_date = purchase_date + relativedelta(
            years=duration
        )

    else:

        expiry_date = purchase_date + relativedelta(
            months=duration
        )

    return expiry_date


# -----------------------------------
# CALCULATE REMAINING DAYS AND STATUS
# -----------------------------------

def get_warranty_status(expiry_date):

    if isinstance(expiry_date, str):
        expiry_date = date.fromisoformat(expiry_date)

    today = date.today()

    remaining_days = (expiry_date - today).days

    if remaining_days < 0:

        status = "Expired"

    elif remaining_days <= 30:

        status = "Expiring Soon"

    else:

        status = "Active"

    return status, remaining_days


# -----------------------------------
# GET BUYER'S WARRANTY INFORMATION
# -----------------------------------

def get_warranties(user_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            product_id,
            product_name,
            brand,
            model,
            category,
            purchase_date,
            warranty_duration,
            warranty_unit,
            expiry_date,
            purchase_price
        FROM products
        WHERE user_id = ?
        ORDER BY expiry_date ASC
    """, (user_id,))

    warranties = cursor.fetchall()

    connection.close()

    return warranties


# -----------------------------------
# UPDATE WARRANTY EXPIRY DATE
# -----------------------------------

def update_expiry_date(product_id, user_id, new_expiry_date):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE products
        SET expiry_date = ?
        WHERE product_id = ?
        AND user_id = ?
    """, (
        new_expiry_date.isoformat(),
        product_id,
        user_id
    ))

    connection.commit()

    updated = cursor.rowcount > 0

    connection.close()

    return updated


# -----------------------------------
# DISPLAY WARRANTY SUMMARY
# -----------------------------------

def warranty_summary(warranties):

    active = 0
    expiring = 0
    expired = 0

    for warranty in warranties:

        status, remaining_days = get_warranty_status(
            warranty[8]
        )

        if status == "Active":

            active += 1

        elif status == "Expiring Soon":

            expiring += 1

        else:

            expired += 1

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "📦 Total Products",
            len(warranties)
        )

    with col2:

        st.metric(
            "🟢 Active",
            active
        )

    with col3:

        st.metric(
            "🟡 Expiring Soon",
            expiring
        )

    with col4:

        st.metric(
            "🔴 Expired",
            expired
        )


# -----------------------------------
# DISPLAY WARRANTY CARDS
# -----------------------------------

def display_warranty_cards(warranties):

    if not warranties:

        st.info(
            "No registered products found. "
            "Add a product to start tracking warranties."
        )

        return

    for warranty in warranties:

        (
            product_id,
            product_name,
            brand,
            model,
            category,
            purchase_date,
            duration,
            unit,
            expiry_date,
            price
        ) = warranty

        status, remaining_days = get_warranty_status(
            expiry_date
        )

        with st.container(border=True):

            col1, col2 = st.columns([3, 1])

            with col1:

                st.markdown(f"### 📦 {product_name}")

                st.write(
                    f"**Brand:** {brand or 'Not provided'}"
                )

                st.write(
                    f"**Model:** {model or 'Not provided'}"
                )

                st.write(
                    f"**Category:** {category or 'Not provided'}"
                )

                st.write(
                    f"**Purchase Date:** {purchase_date}"
                )

                st.write(
                    f"**Warranty Duration:** {duration} {unit}"
                )

                formatted_expiry = date.fromisoformat(
                    expiry_date
                ).strftime("%d-%m-%Y")

                st.write(
                    f"**Warranty Expiry:** {formatted_expiry}"
                )

            with col2:

                st.write("**Warranty Status**")

                if status == "Active":

                    st.success("Active")

                    st.caption(
                        f"{remaining_days} days remaining"
                    )

                elif status == "Expiring Soon":

                    st.warning("Expiring Soon")

                    if remaining_days == 0:

                        st.caption("Expires today")

                    else:

                        st.caption(
                            f"Only {remaining_days} days remaining"
                        )

                else:

                    st.error("Expired")

                    st.caption(
                        f"Expired {abs(remaining_days)} days ago"
                    )


# -----------------------------------
# SEARCH AND FILTER WARRANTIES
# -----------------------------------

def warranty_filter_page(warranties):

    search = st.text_input(
        "🔍 Search by product name or brand",
        key="warranty_search"
    )

    selected_status = st.selectbox(
        "Filter by Warranty Status",
        [
            "All",
            "Active",
            "Expiring Soon",
            "Expired"
        ]
    )

    filtered_warranties = []

    for warranty in warranties:

        name = warranty[1].lower()

        brand = (warranty[2] or "").lower()

        status, remaining_days = get_warranty_status(
            warranty[8]
        )

        matches_search = (
            search.lower() in name
            or search.lower() in brand
        )

        matches_status = (
            selected_status == "All"
            or selected_status == status
        )

        if matches_search and matches_status:

            filtered_warranties.append(warranty)

    display_warranty_cards(filtered_warranties)


# -----------------------------------
# CORRECT WARRANTY EXPIRY DATE
# -----------------------------------

def correct_warranty_expiry(user_id, warranties):

    st.subheader("✏️ Correct Warranty Expiry Date")

    if not warranties:

        st.info("No products available.")

        return

    product_options = {
        f"{w[0]} - {w[1]} ({w[2] or 'No Brand'})": w
        for w in warranties
    }

    selected_product = st.selectbox(
        "Select Product",
        list(product_options.keys()),
        key="expiry_product"
    )

    product = product_options[selected_product]

    product_id = product[0]

    current_expiry = date.fromisoformat(product[8])

    st.write(
        f"**Currently recorded expiry:** "
        f"{current_expiry.strftime('%d-%m-%Y')}"
    )

    st.caption(
        "Check your manufacturer's warranty document before changing this date."
    )

    new_expiry = st.date_input(
        "Select Correct Warranty Expiry Date",
        value=current_expiry,
        key=f"new_expiry_{product_id}"
    )

    if st.button(
        "Save Corrected Expiry Date",
        use_container_width=True
    ):

        updated = update_expiry_date(
            product_id,
            user_id,
            new_expiry
        )

        if updated:

            st.success(
                "Warranty expiry date updated successfully!"
            )

            st.rerun()

        else:

            st.error("Unable to update warranty expiry date.")


# -----------------------------------
# MAIN WARRANTY TRACKER PAGE
# -----------------------------------

def render_warranty_tracker(user):

    st.title("🛡️ Warranty Tracker")

    st.caption(
        "Monitor your product warranties and never miss an expiry date."
    )

    st.divider()

    warranties = get_warranties(user["user_id"])

    # Summary
    warranty_summary(warranties)

    st.divider()

    tab1, tab2, tab3 = st.tabs([
        "📋 All Warranties",
        "🔍 Search & Filter",
        "✏️ Correct Expiry Date"
    ])

    with tab1:

        st.subheader("All Registered Warranties")

        display_warranty_cards(warranties)

    with tab2:

        st.subheader("Find Your Warranty")

        warranty_filter_page(warranties)

    with tab3:

        correct_warranty_expiry(
            user["user_id"],
            warranties
        )
