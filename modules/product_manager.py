
import streamlit as st
import pandas as pd

from datetime import date
from dateutil.relativedelta import relativedelta

from database.db_connection import get_connection


# -----------------------------------
# WARRANTY EXPIRY CALCULATION
# -----------------------------------

def calculate_expiry(purchase_date, duration, unit):

    if unit == "Years":
        expiry_date = purchase_date + relativedelta(years=duration)

    else:
        expiry_date = purchase_date + relativedelta(months=duration)

    return expiry_date



# -----------------------------------
# ADD PRODUCT TO DATABASE
# -----------------------------------

def add_product(user_id, product_name, brand, model,
                category, purchase_date, price,
                purchase_source, serial_number,
                warranty_duration, warranty_unit):

    # Validate product details
    if not product_name.strip():
        return False, "Product name is required."

    if price < 0:
        return False, "Purchase price cannot be negative."

    if warranty_duration <= 0:
        return False, "Warranty duration must be greater than zero."

    if purchase_date > date.today():
        return False, "Purchase date cannot be in the future."

    # Calculate warranty expiry date
    expiry_date = calculate_expiry(
        purchase_date,
        warranty_duration,
        warranty_unit
    )

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO products (
            user_id,
            product_name,
            brand,
            model,
            category,
            purchase_date,
            purchase_price,
            purchase_source,
            serial_number,
            warranty_duration,
            warranty_unit,
            expiry_date
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        product_name.strip(),
        brand,
        model,
        category,
        purchase_date.isoformat(),
        price,
        purchase_source,
        serial_number,
        warranty_duration,
        warranty_unit,
        expiry_date.isoformat()
    ))

    connection.commit()
    connection.close()

    return True, expiry_date



# -----------------------------------
# GET BUYER'S PRODUCTS
# -----------------------------------

def get_products(user_id):

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
            purchase_price,
            purchase_source,
            serial_number,
            warranty_duration,
            warranty_unit,
            expiry_date
        FROM products
        WHERE user_id = ?
        ORDER BY product_id DESC
    """, (user_id,))

    products = cursor.fetchall()

    connection.close()

    return products


# -----------------------------------
# UPDATE PRODUCT
# -----------------------------------

def update_product(product_id, user_id, product_name, brand,
                   model, category, purchase_date, price,
                   purchase_source, serial_number,
                   warranty_duration, warranty_unit):

    expiry_date = calculate_expiry(
        purchase_date,
        warranty_duration,
        warranty_unit
    )

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE products
        SET
            product_name = ?,
            brand = ?,
            model = ?,
            category = ?,
            purchase_date = ?,
            purchase_price = ?,
            purchase_source = ?,
            serial_number = ?,
            warranty_duration = ?,
            warranty_unit = ?,
            expiry_date = ?
        WHERE product_id = ? AND user_id = ?
    """, (
        product_name,
        brand,
        model,
        category,
        purchase_date.isoformat(),
        price,
        purchase_source,
        serial_number,
        warranty_duration,
        warranty_unit,
        expiry_date.isoformat(),
        product_id,
        user_id
    ))

    connection.commit()

    updated = cursor.rowcount > 0

    connection.close()

    return updated


# -----------------------------------
# DELETE PRODUCT
# -----------------------------------

def delete_product(product_id, user_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM products
        WHERE product_id = ? AND user_id = ?
    """, (product_id, user_id))

    connection.commit()

    deleted = cursor.rowcount > 0

    connection.close()

    return deleted


# -----------------------------------
# GET WARRANTY STATUS
# -----------------------------------

def get_warranty_status(expiry_date):

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
# DISPLAY ADD PRODUCT FORM
# -----------------------------------

def add_product_page(user_id):

    st.subheader("➕ Register a Purchased Product")

    with st.form("add_product_form"):

        col1, col2 = st.columns(2)

        with col1:

            product_name = st.text_input("Product Name *")

            brand = st.text_input("Brand")

            model = st.text_input("Model")

            category = st.selectbox(
                "Product Category",
                [
                    "Laptop",
                    "Mobile",
                    "Tablet",
                    "Television",
                    "Refrigerator",
                    "Washing Machine",
                    "Home Appliance",
                    "Headphones",
                    "Camera",
                    "Other"
                ]
            )

        with col2:

            purchase_date = st.date_input(
                "Purchase Date",
                value=date.today(),
                max_value=date.today()
            )

            price = st.number_input(
                "Purchase Price (₹)",
                min_value=0.0,
                value=0.0,
                step=500.0
            )

            purchase_source = st.text_input(
                "Purchased From (Shop / Website)"
            )

            serial_number = st.text_input(
                "Serial Number (Optional)"
            )

        st.divider()

        st.subheader("Warranty Information")

        col3, col4 = st.columns(2)

        with col3:

            warranty_duration = st.number_input(
                "Warranty Duration",
                min_value=1,
                max_value=120,
                value=1,
                step=1
            )

        with col4:

            warranty_unit = st.selectbox(
                "Duration Unit",
                ["Years", "Months"]
            )

        submitted = st.form_submit_button(
            "Save Product",
            use_container_width=True
        )

        if submitted:

            if not product_name.strip():

                st.error("Please enter the product name.")

            else:

                expiry_date = add_product(
                    user_id,
                    product_name.strip(),
                    brand.strip(),
                    model.strip(),
                    category,
                    purchase_date,
                    price,
                    purchase_source.strip(),
                    serial_number.strip(),
                    int(warranty_duration),
                    warranty_unit
                )

                st.success("Product registered successfully!")

                st.info(
                    f"Calculated Warranty Expiry Date: "
                    f"{expiry_date.strftime('%d-%m-%Y')}"
                )

                st.rerun()


# -----------------------------------
# DISPLAY ALL PRODUCTS
# -----------------------------------

def view_products_page(user_id):

    st.subheader("📦 Your Registered Products")

    products = get_products(user_id)

    if not products:

        st.info(
            "No products registered yet. "
            "Use Add Product to register your first purchase."
        )

        return

    search = st.text_input(
        "🔍 Search by product name or brand"
    )

    categories = ["All"] + sorted(
        set(product[4] for product in products if product[4])
    )

    selected_category = st.selectbox(
        "Filter by Category",
        categories
    )

    filtered_products = []

    for product in products:

        matches_search = (
            search.lower() in product[1].lower()
            or search.lower() in (product[2] or "").lower()
        )

        matches_category = (
            selected_category == "All"
            or product[4] == selected_category
        )

        if matches_search and matches_category:
            filtered_products.append(product)

    if not filtered_products:

        st.warning("No matching products found.")

        return

    for product in filtered_products:

        (
            product_id,
            name,
            brand,
            model,
            category,
            purchase_date,
            price,
            source,
            serial,
            duration,
            unit,
            expiry
        ) = product

        expiry_date = date.fromisoformat(expiry)

        status, remaining_days = get_warranty_status(
            expiry_date
        )

        with st.container(border=True):

            col1, col2 = st.columns([3, 1])

            with col1:

                st.markdown(f"### 📦 {name}")

                st.write(f"**Brand:** {brand or 'Not provided'}")

                st.write(f"**Model:** {model or 'Not provided'}")

                st.write(f"**Category:** {category or 'Not provided'}")

                st.write(f"**Purchase Date:** {purchase_date}")

                st.write(
                    f"**Warranty:** {duration} {unit}"
                )

                st.write(
                    f"**Expiry Date:** {expiry_date.strftime('%d-%m-%Y')}"
                )

                st.write(
                    f"**Purchase Price:** ₹{price:,.2f}"
                    if price is not None else "Purchase Price: Not provided"
                )

                if source:
                    st.write(f"**Purchased From:** {source}")

            with col2:

                st.write("**Warranty Status**")

                if status == "Active":

                    st.success(status)

                elif status == "Expiring Soon":

                    st.warning(status)

                else:

                    st.error(status)

                if remaining_days >= 0:

                    st.caption(
                        f"{remaining_days} days remaining"
                    )

                else:

                    st.caption(
                        f"Expired {abs(remaining_days)} days ago"
                    )


# -----------------------------------
# EDIT AND DELETE PRODUCTS
# -----------------------------------

def manage_products_page(user_id):

    st.subheader("✏️ Edit or Delete Products")

    products = get_products(user_id)

    if not products:

        st.info("No products available to manage.")

        return

    product_options = {
        f"{p[0]} - {p[1]} ({p[2] or 'No brand'})": p
        for p in products
    }

    selected_label = st.selectbox(
        "Select Product",
        list(product_options.keys())
    )

    selected_product = product_options[selected_label]

    (
        product_id,
        name,
        brand,
        model,
        category,
        purchase_date,
        price,
        source,
        serial,
        duration,
        unit,
        expiry
    ) = selected_product

    st.write("Update the product information below.")

    with st.form(f"edit_product_{product_id}"):

        col1, col2 = st.columns(2)

        with col1:

            new_name = st.text_input(
                "Product Name",
                value=name
            )

            new_brand = st.text_input(
                "Brand",
                value=brand or ""
            )

            new_model = st.text_input(
                "Model",
                value=model or ""
            )

            categories = [
                "Laptop", "Mobile", "Tablet", "Television",
                "Refrigerator", "Washing Machine",
                "Home Appliance", "Headphones", "Camera", "Other"
            ]

            if category and category not in categories:
                categories.append(category)

            category_index = (
                categories.index(category)
                if category in categories else 0
            )

            new_category = st.selectbox(
                "Category",
                categories,
                index=category_index
            )

        with col2:

            new_date = st.date_input(
                "Purchase Date",
                value=date.fromisoformat(purchase_date),
                max_value=date.today()
            )

            new_price = st.number_input(
                "Purchase Price (₹)",
                min_value=0.0,
                value=float(price or 0),
                step=500.0
            )

            new_source = st.text_input(
                "Purchased From",
                value=source or ""
            )

            new_serial = st.text_input(
                "Serial Number",
                value=serial or ""
            )

        col3, col4 = st.columns(2)

        with col3:

            new_duration = st.number_input(
                "Warranty Duration",
                min_value=1,
                max_value=120,
                value=int(duration),
                step=1
            )

        with col4:

            new_unit = st.selectbox(
                "Warranty Unit",
                ["Years", "Months"],
                index=0 if unit == "Years" else 1
            )

        update_button = st.form_submit_button(
            "Update Product",
            use_container_width=True
        )

        if update_button:

            if not new_name.strip():

                st.error("Product name cannot be empty.")

            else:

                updated = update_product(
                    product_id,
                    user_id,
                    new_name.strip(),
                    new_brand.strip(),
                    new_model.strip(),
                    new_category,
                    new_date,
                    new_price,
                    new_source.strip(),
                    new_serial.strip(),
                    int(new_duration),
                    new_unit
                )

                if updated:

                    st.success("Product updated successfully!")

                    st.rerun()

                else:

                    st.error("Product could not be updated.")

    st.divider()

    st.warning(
        "Deleting a product will also delete its associated "
        "documents and reminders."
    )

    confirm_delete = st.checkbox(
        f"I want to delete {name}"
    )

    if st.button(
        "🗑️ Delete Product",
        disabled=not confirm_delete
    ):

        deleted = delete_product(product_id, user_id)

        if deleted:

            st.success("Product deleted successfully!")

            st.rerun()

        else:

            st.error("Product could not be deleted.")


# -----------------------------------
# MAIN PRODUCT MANAGEMENT PAGE
# -----------------------------------

def render_products(user):

    st.title("📦 My Products")

    st.caption(
        "Manage all the products you have purchased."
    )

    st.divider()

    tab1, tab2, tab3 = st.tabs(
        [
            "➕ Add Product",
            "📋 View Products",
            "✏️ Manage Products"
        ]
    )

    with tab1:

        add_product_page(user["user_id"])

    with tab2:

        view_products_page(user["user_id"])

    with tab3:

        manage_products_page(user["user_id"])
