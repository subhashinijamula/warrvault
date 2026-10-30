# 🔐 WarrVault – Digital Warranty Manager

**Your Purchases. Your Documents. Your Warranty.**

WarrVault is a personal digital warranty and document management application built using Python and Streamlit. It helps buyers organize their purchased products, securely store invoices and warranty documents, track warranty expiry dates, and manage reminders in one place.

## 🚀 Features

### 👤 User Authentication
- Buyer registration and login.
- Password hashing using bcrypt.
- Profile management.
- Password change functionality.

### 📦 Product Management
- Add, view, edit, and delete purchased products.
- Store product details, brand, model, category, and serial number.
- Automatically calculate warranty expiry dates.
- Search and filter products.

### 📁 Digital Document Vault
- Upload invoices, receipts, and warranty cards.
- Support PDF, JPG, JPEG, and PNG files.
- Capture documents using the camera.
- Store document content in SQLite.
- Preview and download uploaded documents.

### 🛡️ Warranty Tracker
- Track active warranties.
- Identify warranties expiring within 30 days.
- Identify expired warranties.
- Correct warranty expiry dates.

### 🔔 Warranty Reminders
- Automatically generate reminders 30, 15, and 7 days before expiry.
- Generate expiry-day reminders.
- View upcoming, due, and completed reminders.

### 📊 Analytics Dashboard
- View total registered products.
- Calculate total purchase value.
- Analyze category-wise spending.
- Visualize warranty status distribution.
- View purchase history.

### 👤 Profile Management
- View account information.
- Update name and email.
- Change account password.

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Application logic |
| Streamlit | User interface |
| SQLite | Database management |
| Pandas | Data analysis |
| Plotly | Interactive charts |
| bcrypt | Password hashing |
| python-dateutil | Warranty date calculations |
| Pillow | Image handling |
| Git & GitHub | Version control |

## 📂 Project Structure

```text
WarrVault/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── authentication/
│   └── auth_manager.py
│
├── database/
│   ├── __init__.py
│   ├── db_connection.py
│   └── db_setup.py
│
├── modules/
│   ├── __init__.py
│   ├── dashboard.py
│   ├── product_manager.py
│   ├── document_manager.py
│   ├── warranty_tracker.py
│   ├── reminders.py
│   ├── analytics.py
│   └── profile_manager.py
│
└── venv/
```

## ⚙️ Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/WarrVault.git
```

### 2. Navigate to the project folder

```bash
cd WarrVault
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

### 4. Activate the virtual environment

For Windows:

```bash
venv\Scripts\activate
```

### 5. Install the required packages

```bash
pip install -r requirements.txt
```

### 6. Initialize the database

```bash
python -m database.db_setup
```

### 7. Run the application

```bash
streamlit run app.py
```

The application will open in your browser.

## 🗄️ Database

WarrVault uses SQLite to store:

- Buyer account information.
- Product information.
- Uploaded documents as binary data.
- Warranty reminders.
- Login sessions.

The database file is created locally when the database setup script is executed.

## 🔮 Future Enhancements

- Persistent cloud database and document storage.
- Reliable persistent login across browser sessions.
- Email and mobile notifications.
- AI-powered document information extraction.
- Machine learning-based warranty insights.
- Cloud deployment.

## 🎯 Project Objective

The objective of WarrVault is to provide buyers with a centralized platform to manage product purchases, preserve important documents, and stay informed about warranty expiration dates.

---

**Developed with Python and Streamlit.**
