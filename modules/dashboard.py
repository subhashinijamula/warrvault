
import streamlit as st
from datetime import date

from database.db_connection import get_connection


# Get dashboard information from the database
def get_dashboard_data(user_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT purchase_price, expiry_date
        FROM products
        WHERE user_id = ?
    """, (user_id,))

    products = cursor.fetchall()

    connection.close()

    total_products = len(products)
    active = 0
    expiring_soon = 0
    expired = 0
    total_purchase_value = 0

    today = date.today()

    for product in products:

        purchase_price = product[0]
        expiry_date = product[1]

        if purchase_price is not None:
            total_purchase_value += float(purchase_price)

        if expiry_date:

            expiry = date.fromisoformat(expiry_date)
            remaining_days = (expiry - today).days

            if remaining_days < 0:
                expired += 1

            elif remaining_days <= 30:
                expiring_soon += 1

            else:
                active += 1

    return (
        total_products,
        active,
        expiring_soon,
        expired,
        total_purchase_value
    )


# Display dashboard
def render_dashboard(user):

    st.title("🏠 Dashboard")

    st.write(f"Welcome back, {user['name']}!")
    st.markdown(
    """
    <div class="welcome-card">
        <h3>Welcome to Your Personal Warranty Vault</h3>
        <p>
            Keep track of your purchases, protect your documents,
            and stay informed about warranty expiration dates.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)
    st.caption(
        "Here is an overview of your personal warranty vault."
    )

    # Fetch actual database values
    (
        total_products,
        active,
        expiring_soon,
        expired,
        total_purchase_value
    ) = get_dashboard_data(user["user_id"])

    st.divider()

    # Display dynamic metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "📦 Total Products",
            total_products
        )

    with col2:
        st.metric(
            "🟢 Active Warranties",
            active
        )

    with col3:
        st.metric(
            "🟡 Expiring Soon",
            expiring_soon
        )

    with col4:
        st.metric(
            "🔴 Expired Warranties",
            expired
        )

    st.divider()

    st.subheader("💰 Purchase Overview")

    st.metric(
        "Total Purchase Value",
        f"₹{total_purchase_value:,.2f}"
    )

    if total_products == 0:

        st.info(
            "You haven't added any products yet. "
            "Start by adding your first product."
        )

    else:

        st.success(
            f"You have registered {total_products} products "
            "in your personal warranty vault."
        )
