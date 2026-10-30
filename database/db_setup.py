
from database.db_connection import get_connection


def create_tables():

    connection = get_connection()

    cursor = connection.cursor()

    # 1. Users Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (

            user_id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            email TEXT UNIQUE NOT NULL,

            password_hash TEXT NOT NULL,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 2. Products Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (

            product_id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER NOT NULL,

            product_name TEXT NOT NULL,

            brand TEXT,

            model TEXT,

            category TEXT,

            purchase_date DATE NOT NULL,

            purchase_price REAL,

            purchase_source TEXT,

            serial_number TEXT,

            warranty_duration INTEGER NOT NULL,

            warranty_unit TEXT NOT NULL,

            expiry_date DATE NOT NULL,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (user_id)
            REFERENCES users(user_id)
            ON DELETE CASCADE
        )
    """)

    # 3. Documents Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (

            document_id INTEGER PRIMARY KEY AUTOINCREMENT,

            product_id INTEGER NOT NULL,

            document_type TEXT NOT NULL,

            file_name TEXT NOT NULL,

            file_type TEXT NOT NULL,

            file_size INTEGER,

            file_data BLOB NOT NULL,

            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (product_id)
            REFERENCES products(product_id)
            ON DELETE CASCADE
        )
    """)

    # 4. Reminders Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reminders (

            reminder_id INTEGER PRIMARY KEY AUTOINCREMENT,

            product_id INTEGER NOT NULL,

            reminder_date DATE NOT NULL,

            reminder_type TEXT NOT NULL,

            status TEXT DEFAULT 'Pending',

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (product_id)
            REFERENCES products(product_id)
            ON DELETE CASCADE
        )
    """)

    connection.commit()

    connection.close()

    print("All WarrVault database tables created successfully!")


if __name__ == "__main__":
    create_tables()
