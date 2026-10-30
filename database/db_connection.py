
import sqlite3
import os

# Get the current project directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Set database file path
DB_PATH = os.path.join(BASE_DIR, "database", "warrvault.db")


# Function to connect to database
def get_connection():

    connection = sqlite3.connect(DB_PATH)

    # Enable foreign key relationships
    connection.execute("PRAGMA foreign_keys = ON")

    return connection
