
import streamlit as st
import os
from datetime import datetime

from database.db_connection import get_connection
from modules.product_manager import get_products


# -----------------------------------
# FILE VALIDATION
# -----------------------------------

ALLOWED_EXTENSIONS = ["pdf", "jpg", "jpeg", "png"]

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

def validate_file(uploaded_file):

    allowed_extensions = [
        "pdf",
        "jpg",
        "jpeg",
        "png"
    ]

    file_extension = os.path.splitext(
        uploaded_file.name
    )[1].lower().replace(".", "")

    if file_extension not in allowed_extensions:
        return False, "Only PDF and image files are allowed."

    if uploaded_file.size > MAX_FILE_SIZE:
        return False, "File size must be below 10 MB."

    file_data = uploaded_file.getvalue()

    # Check PDF signature
    if file_extension == "pdf":

        if not file_data.startswith(b"%PDF-"):
            return False, "Invalid PDF file."

    # Check JPEG signature
    elif file_extension in ["jpg", "jpeg"]:

        if not file_data.startswith(b"\xff\xd8\xff"):
            return False, "Invalid JPEG image."

    # Check PNG signature
    elif file_extension == "png":

        if not file_data.startswith(b"\x89PNG\r\n\x1a\n"):
            return False, "Invalid PNG image."

    return True, "File is valid."

# -----------------------------------
# SAVE DOCUMENT IN DATABASE
# -----------------------------------

def save_document(user_id, product_id, document_type, uploaded_file):

    # Validate uploaded file
    valid, message = validate_file(uploaded_file)

    if not valid:
        return False, message

    connection = get_connection()
    cursor = connection.cursor()

    # Check whether product belongs to logged-in buyer
    cursor.execute("""
        SELECT product_id
        FROM products
        WHERE product_id = ? AND user_id = ?
    """, (product_id, user_id))

    product = cursor.fetchone()

    if product is None:
        connection.close()
        return False, "Product not found or access denied."

    # Read actual file contents
    file_data = uploaded_file.getvalue()

    # Get file details
    file_name = uploaded_file.name
    file_type = uploaded_file.type or "application/octet-stream"
    file_size = uploaded_file.size

    # Insert document into database
    cursor.execute("""
        INSERT INTO documents (
            product_id,
            document_type,
            file_name,
            file_type,
            file_size,
            file_data
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        product_id,
        document_type,
        file_name,
        file_type,
        file_size,
        file_data
    ))

    connection.commit()
    connection.close()

    return True, "Document uploaded successfully!"


# -----------------------------------
# GET ALL BUYER DOCUMENTS
# -----------------------------------

def get_documents(user_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            documents.document_id,
            documents.product_id,
            documents.document_type,
            documents.file_name,
            documents.file_type,
            documents.file_size,
            documents.uploaded_at,
            products.product_name,
            products.brand
        FROM documents
        INNER JOIN products
        ON documents.product_id = products.product_id
        WHERE products.user_id = ?
        ORDER BY documents.document_id DESC
    """, (user_id,))

    documents = cursor.fetchall()

    connection.close()

    return documents


# -----------------------------------
# GET DOCUMENT CONTENT
# -----------------------------------

def get_document_data(document_id, user_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            documents.file_name,
            documents.file_type,
            documents.file_data
        FROM documents
        INNER JOIN products
        ON documents.product_id = products.product_id
        WHERE documents.document_id = ?
        AND products.user_id = ?
    """, (document_id, user_id))

    document = cursor.fetchone()

    connection.close()

    return document


# -----------------------------------
# DELETE DOCUMENT
# -----------------------------------

def delete_document(document_id, user_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM documents
        WHERE document_id = ?
        AND product_id IN (
            SELECT product_id
            FROM products
            WHERE user_id = ?
        )
    """, (document_id, user_id))

    connection.commit()

    deleted = cursor.rowcount > 0

    connection.close()

    return deleted


# -----------------------------------
# DOCUMENT UPLOAD PAGE
# -----------------------------------

def upload_document_page(user_id):

    st.subheader("📤 Upload Product Documents")

    products = get_products(user_id)

    if not products:

        st.warning(
            "You haven't registered any products yet. "
            "Please add a product before uploading documents."
        )

        return

    # Create product selection
    product_options = {
        f"{p[0]} - {p[1]} ({p[2] or 'No Brand'})": p[0]
        for p in products
    }

    with st.form("document_upload_form"):

        selected_product = st.selectbox(
            "Select Purchased Product",
            list(product_options.keys())
        )

        document_type = st.selectbox(
            "Document Type",
            [
                "Invoice",
                "Receipt",
                "Warranty Card",
                "Product Image",
                "Other"
            ]
        )

        uploaded_file = st.file_uploader(
            "Choose a PDF or Image",
            type=ALLOWED_EXTENSIONS,
            help="Maximum file size: 10 MB"
        )

        submitted = st.form_submit_button(
            "Upload Document",
            use_container_width=True
        )

        if submitted:

            product_id = product_options[selected_product]

            success, message = save_document(
                user_id,
                product_id,
                document_type,
                uploaded_file
            )

            if success:

                st.success(message)

                st.rerun()

            else:

                st.error(message)

    # Camera upload
    st.divider()

    st.subheader("📷 Capture Document Using Camera")

    st.caption(
        "You can use your webcam or supported device camera "
        "to capture an invoice or warranty card."
    )

    camera_product = st.selectbox(
        "Select Product for Camera Upload",
        list(product_options.keys()),
        key="camera_product"
    )

    camera_type = st.selectbox(
        "Select Document Type",
        ["Invoice", "Receipt", "Warranty Card", "Product Image", "Other"],
        key="camera_document_type"
    )

    camera_file = st.camera_input(
        "Take a Document Photograph"
    )

    if camera_file is not None:

        st.image(camera_file, caption="Captured document")

        if st.button("Save Captured Document"):

            product_id = product_options[camera_product]

            success, message = save_document(
                user_id,
                product_id,
                camera_type,
                camera_file
            )

            if success:

                st.success(message)

                st.rerun()

            else:

                st.error(message)


# -----------------------------------
# VIEW AND DOWNLOAD DOCUMENTS
# -----------------------------------

def view_documents_page(user_id):

    st.subheader("📁 Your Digital Document Vault")

    documents = get_documents(user_id)

    if not documents:

        st.info(
            "Your document vault is empty. "
            "Upload your first invoice or warranty card."
        )

        return

    # Filter documents
    document_types = [
        "All",
        "Invoice",
        "Receipt",
        "Warranty Card",
        "Product Image",
        "Other"
    ]

    selected_type = st.selectbox(
        "Filter by Document Type",
        document_types
    )

    search = st.text_input(
        "🔍 Search by file name or product"
    )

    filtered_documents = []

    for document in documents:

        doc_type = document[2]
        file_name = document[3].lower()
        product_name = document[7].lower()

        matches_type = (
            selected_type == "All"
            or selected_type == doc_type
        )

        matches_search = (
            search.lower() in file_name
            or search.lower() in product_name
        )

        if matches_type and matches_search:

            filtered_documents.append(document)

    if not filtered_documents:

        st.warning("No matching documents found.")

        return

    st.write(f"**Total Documents: {len(filtered_documents)}**")

    # Display documents
    for document in filtered_documents:

        (
            document_id,
            product_id,
            document_type,
            file_name,
            file_type,
            file_size,
            uploaded_at,
            product_name,
            brand
        ) = document

        with st.container(border=True):

            col1, col2 = st.columns([3, 1])

            with col1:

                st.markdown(f"### 📄 {file_name}")

                st.write(f"**Product:** {product_name}")

                st.write(f"**Brand:** {brand or 'Not provided'}")

                st.write(f"**Type:** {document_type}")

                st.caption(
                    f"Uploaded: {uploaded_at}"
                )

                st.caption(
                    f"File size: {file_size / 1024:.2f} KB"
                )

            # Retrieve actual file data
            file_data = get_document_data(
                document_id,
                user_id
            )

            if file_data is None:
                st.error("Document could not be retrieved.")
                continue

            actual_name, actual_type, actual_data = file_data

            # Image preview
            if actual_type.startswith("image/"):

                st.image(
                    actual_data,
                    caption=actual_name,
                    width=300
                )

            else:

                st.info(
                    "PDF document. Use the download option to view it."
                )

            # Download document
            st.download_button(
                label="⬇️ Download Document",
                data=actual_data,
                file_name=actual_name,
                mime=actual_type,
                key=f"download_{document_id}",
                use_container_width=True
            )

            # Delete document
            if st.button(
                "🗑️ Delete Document",
                key=f"delete_{document_id}"
            ):

                deleted = delete_document(
                    document_id,
                    user_id
                )

                if deleted:

                    st.success("Document deleted successfully!")

                    st.rerun()

                else:

                    st.error("Unable to delete document.")


# -----------------------------------
# MAIN DOCUMENT VAULT PAGE
# -----------------------------------

def render_document_vault(user):

    st.title("📁 My Digital Document Vault")

    st.caption(
        "All your purchase invoices, receipts and warranty cards "
        "in one place."
    )

    st.divider()

    tab1, tab2 = st.tabs(
        [
            "📤 Upload Documents",
            "📂 View My Documents"
        ]
    )

    with tab1:

        upload_document_page(user["user_id"])

    with tab2:

        view_documents_page(user["user_id"])
