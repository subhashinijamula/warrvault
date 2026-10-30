
import streamlit as st
import pandas as pd
import plotly.express as px

from datetime import date
from database.db_connection import get_connection


# Get all products belonging to the logged-in user
def get_analytics_data(user_id):

    connection = get_connection()

    query = """
        SELECT
            product_name,
            brand,
            category,
            purchase_date,
            purchase_price,
            expiry_date
        FROM products
        WHERE user_id = ?
    """

    data = pd.read_sql_query(
        query,
        connection,
        params=(user_id,)
    )

    connection.close()

    return data


# Calculate warranty status
def calculate_status(expiry_date):

    if pd.isna(expiry_date):
        return "Unknown"

    expiry = date.fromisoformat(expiry_date)
    remaining_days = (expiry - date.today()).days

    if remaining_days < 0:
        return "Expired"

    elif remaining_days <= 30:
        return "Expiring Soon"

    else:
        return "Active"


# Main analytics page
def render_analytics(user):

    st.title("📊 Purchase Analytics")

    st.caption(
        "Understand your purchases, spending and warranty information."
    )

    user_id = user["user_id"]

    data = get_analytics_data(user_id)

    # Check whether products are available
    if data.empty:

        st.info(
            "No product data available. Add products to view analytics."
        )

        return

    # Convert price column into numbers
    data["purchase_price"] = pd.to_numeric(
        data["purchase_price"],
        errors="coerce"
    ).fillna(0)

    # Calculate important values
    total_products = len(data)

    total_spending = data["purchase_price"].sum()

    average_price = (
        total_spending / total_products
        if total_products > 0
        else 0
    )

    # Calculate warranty status for every product
    data["warranty_status"] = data["expiry_date"].apply(
        calculate_status
    )

    active_count = len(
        data[data["warranty_status"] == "Active"]
    )

    expiring_count = len(
        data[data["warranty_status"] == "Expiring Soon"]
    )

    expired_count = len(
        data[data["warranty_status"] == "Expired"]
    )

    # Display summary metrics
    st.subheader("Purchase Overview")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Total Products",
            total_products
        )

    with col2:
        st.metric(
            "Total Spending",
            f"₹{total_spending:,.2f}"
        )

    with col3:
        st.metric(
            "Average Price",
            f"₹{average_price:,.2f}"
        )

    st.divider()

    # Warranty status chart
    st.subheader("Warranty Status Distribution")

    warranty_data = pd.DataFrame({
        "Status": [
            "Active",
            "Expiring Soon",
            "Expired"
        ],
        "Products": [
            active_count,
            expiring_count,
            expired_count
        ]
    })

    warranty_data = warranty_data[
        warranty_data["Products"] > 0
    ]

    if not warranty_data.empty:

        fig1 = px.pie(
            warranty_data,
            names="Status",
            values="Products",
            hole=0.4,
            title="Product Warranty Status"
        )

        st.plotly_chart(
            fig1,
            use_container_width=True
        )

    else:

        st.info("No warranty status information available.")

    st.divider()

    # Category-wise spending chart
    st.subheader("Category-wise Spending")

    category_data = (
        data.groupby("category")["purchase_price"]
        .sum()
        .reset_index()
    )

    fig2 = px.bar(
        category_data,
        x="category",
        y="purchase_price",
        title="Amount Spent on Each Category",
        labels={
            "category": "Product Category",
            "purchase_price": "Amount (₹)"
        },
        text_auto=True
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

    st.divider()

    # Purchase history chart
    st.subheader("Purchase History")

    data["purchase_date"] = pd.to_datetime(
        data["purchase_date"],
        errors="coerce"
    )

    purchase_data = data.dropna(
        subset=["purchase_date"]
    ).copy()

    if not purchase_data.empty:

        purchase_data["Purchase Month"] = (
            purchase_data["purchase_date"]
            .dt.to_period("M")
            .astype(str)
        )

        monthly_data = (
            purchase_data.groupby("Purchase Month")
            .size()
            .reset_index(name="Number of Products")
        )

        fig3 = px.line(
            monthly_data,
            x="Purchase Month",
            y="Number of Products",
            markers=True,
            title="Products Purchased Over Time"
        )

        st.plotly_chart(
            fig3,
            use_container_width=True
        )

    else:

        st.info("No purchase date information available.")

    st.divider()

    # Product details table
    st.subheader("Product Summary")

    display_data = data[
        [
            "product_name",
            "brand",
            "category",
            "purchase_price",
            "expiry_date",
            "warranty_status"
        ]
    ].copy()

    display_data.columns = [
        "Product",
        "Brand",
        "Category",
        "Purchase Price",
        "Warranty Expiry",
        "Warranty Status"
    ]

    st.dataframe(
        display_data,
        use_container_width=True,
        hide_index=True
    )
