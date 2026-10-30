
import streamlit as st
import extra_streamlit_components as stx
from datetime import datetime, timedelta
from modules.dashboard import render_dashboard
from modules.product_manager import render_products
from modules.document_manager import render_document_vault
from modules.warranty_tracker import render_warranty_tracker
from modules.reminders import render_reminders
from modules.analytics import render_analytics
from modules.profile_manager import render_profile
from authentication.auth_manager import (
    register_user,
    login_user,
    create_login_session,
    get_user_by_session_token,
    revoke_login_session
)


# --------------------------------
# PAGE CONFIGURATION
# --------------------------------

st.set_page_config(
    page_title="WarrVault | Digital Warranty Manager",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize browser cookie manager
cookie_manager = stx.CookieManager(
    key="warrvault_cookie_manager"
)
# --------------------------------
# CUSTOM CSS
# --------------------------------

def load_css():

    st.markdown("""
    <style>

    /* Main application background */

    .stApp {
        background:
            linear-gradient(
                120deg,
                rgba(7, 13, 30, 0.97),
                rgba(15, 25, 52, 0.94),
                rgba(29, 19, 57, 0.94)
            ),
            url("https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=2000&q=80");

        background-size: cover;
        background-position: center;
        background-attachment: fixed;

        color: #F5F7FF;
    }

    /* Main content spacing */

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1100px;
    }

    /* Hide Streamlit header */

    header[data-testid="stHeader"] {
        background: transparent;
    }

    /* Main headings */

    h1 {
        color: #FFFFFF !important;
        font-weight: 800 !important;
        letter-spacing: -1px;
    }

    h2, h3 {
        color: #E8EDFF !important;
    }

    p, label {
        color: #C4CEE3;
    }

    /* Brand logo */

    .brand {
        font-size: 34px;
        font-weight: 800;
        color: #FFFFFF;
        letter-spacing: 1px;
        text-align: center;
    }

    .brand span {
        color: #5595FF;
    }

    .tagline {
        text-align: center;
        color: #AEBBD5;
        font-size: 15px;
        margin-top: 8px;
        margin-bottom: 30px;
    }

    /* Glass effect cards */

    .glass-card {
        background: rgba(255, 255, 255, 0.07);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 20px;
        padding: 28px;
        backdrop-filter: blur(15px);
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.25);
    }

    /* Hero section */

    .hero-title {
        font-size: 46px;
        font-weight: 800;
        line-height: 1.2;
        color: #FFFFFF;
        text-align: center;
    }

    .hero-title span {
        background: linear-gradient(
            90deg,
            #54A1FF,
            #A77BFF
        );

        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .hero-description {
        text-align: center;
        color: #BAC7E0;
        font-size: 16px;
        line-height: 1.8;
        max-width: 650px;
        margin: 15px auto 25px auto;
    }

    /* Input fields */

    div[data-baseweb="input"] {
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.13);
        border-radius: 10px;
    }

    div[data-baseweb="input"] input {
        color: #FFFFFF !important;
        background: transparent !important;
    }

    div[data-baseweb="base-input"] input {
        color: #FFFFFF !important;
    }

    div[data-baseweb="input"]:focus-within {
        border: 1px solid #5595FF;
        box-shadow: 0 0 12px rgba(85, 149, 255, 0.25);
    }

    /* Buttons */

    .stButton > button,
    .stFormSubmitButton > button {
        background: linear-gradient(
            90deg,
            #347EFF,
            #815BFF
        );

        color: #FFFFFF !important;
        border: none;
        border-radius: 10px;
        height: 48px;
        font-weight: 700;
        transition: all 0.3s ease;
    }

    .stButton > button:hover,
    .stFormSubmitButton > button:hover {
        background: linear-gradient(
            90deg,
            #5595FF,
            #A17FFF
        );

        box-shadow: 0 5px 20px rgba(91, 115, 255, 0.4);
        transform: translateY(-2px);
    }

    /* Forms */

    [data-testid="stForm"] {
        background: rgba(255, 255, 255, 0.07);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 18px;
        padding: 28px;
        backdrop-filter: blur(15px);
    }

    /* Divider */

    hr {
        border-color: rgba(255, 255, 255, 0.15);
    }

    /* Dashboard welcome card */

    .welcome-card {
        background: linear-gradient(
            120deg,
            rgba(44, 103, 220, 0.25),
            rgba(122, 79, 211, 0.25)
        );

        border: 1px solid rgba(255,255,255,0.14);
        padding: 28px;
        border-radius: 18px;
        margin-bottom: 25px;
    }

    /* Footer */

    .footer {
        text-align: center;
        color: #8492AD;
        font-size: 12px;
        margin-top: 50px;
    }

    /* Alerts */

    [data-testid="stAlert"] {
        border-radius: 12px;
    }

    
/* Sidebar background */

section[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #101A30,
        #171B38
    );

    border-right: 1px solid rgba(255,255,255,0.12);
}

/* Sidebar text */

section[data-testid="stSidebar"] * {
    color: #E5ECFF;
}

/* Sidebar radio navigation */

section[data-testid="stSidebar"] div[role="radiogroup"] {
    gap: 10px;
}

/* Sidebar navigation labels */

section[data-testid="stSidebar"] label {
    background: rgba(255,255,255,0.04);
    border-radius: 10px;
    padding: 10px;
    transition: 0.3s;
}

section[data-testid="stSidebar"] label:hover {
    background: rgba(75,130,255,0.2);
}

/* Metric cards */

div[data-testid="stMetric"] {
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.13);
    border-radius: 14px;
    padding: 18px;
}

/* Metric values */

div[data-testid="stMetricValue"] {
    color: #FFFFFF;
    font-weight: 800;
}

/* Sidebar divider */

section[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.15);
}

    </style>
    """, unsafe_allow_html=True)


load_css()


# --------------------------------
# SESSION STATE
# --------------------------------
# --------------------------------
# SESSION STATE AND LOGIN RESTORE
# --------------------------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = None

if "page" not in st.session_state:
    st.session_state.page = "Welcome"

if "session_token" not in st.session_state:
    st.session_state.session_token = None


# Restore login using browser cookie
if not st.session_state.logged_in:

    saved_token = cookie_manager.get("warrvault_session")

    if saved_token:

        user = get_user_by_session_token(saved_token)

        if user:

            st.session_state.logged_in = True
            st.session_state.user = user
            st.session_state.session_token = saved_token
# --------------------------------
# BRAND HEADER
# --------------------------------

def brand_header():

    st.markdown("""
        <div class="brand">
            🔐 Warr<span>Vault</span>
        </div>

        <div class="tagline">
            Your Purchases. Your Documents. Your Warranty.
        </div>
    """, unsafe_allow_html=True)


# --------------------------------
# WELCOME PAGE
# --------------------------------

def welcome_page():

    brand_header()

    st.write("")

    st.markdown("""
        <div class="hero-title">
            Keep Everything <span>Protected.</span>
            <br>
            Keep Everything <span>Organized.</span>
        </div>

        <div class="hero-description">
            Never lose your purchase invoices, receipts or warranty cards again.
            Store all your product documents in one secure digital vault
            and keep track of every warranty.
        </div>
    """, unsafe_allow_html=True)

    st.write("")

    col1, col2, col3 = st.columns([1, 1.5, 1])

    with col2:

        if st.button(
            "Create Your Account  →",
            use_container_width=True
        ):

            st.session_state.page = "Register"
            st.rerun()

        if st.button(
            "Already have an account? Login",
            use_container_width=True
        ):

            st.session_state.page = "Login"
            st.rerun()

    st.divider()

 
    # Feature section heading
    st.markdown(
        "<h3 style='text-align:center;'>"
        "Everything You Need in One Place"
        "</h3>",
        unsafe_allow_html=True
    )

    # Feature cards
    with st.container(border=True):

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(
                "<div style='text-align:center;'>"
                "<div style='font-size:40px;'>📦</div>"
                "<h4>Product Management</h4>"
                "<p>Manage all your purchased products.</p>"
                "</div>",
                unsafe_allow_html=True
            )

        with col2:
            st.markdown(
                "<div style='text-align:center;'>"
                "<div style='font-size:40px;'>📁</div>"
                "<h4>Digital Vault</h4>"
                "<p>Store invoices, receipts and warranty cards.</p>"
                "</div>",
                unsafe_allow_html=True
            )

        with col3:
            st.markdown(
                "<div style='text-align:center;'>"
                "<div style='font-size:40px;'>🛡️</div>"
                "<h4>Warranty Tracking</h4>"
                "<p>Track warranty dates and expiry reminders.</p>"
                "</div>",
                unsafe_allow_html=True
            )

    st.markdown("""
        <div class="footer">
            © 2026 WarrVault | Your Personal Digital Warranty Manager
        </div>
    """, unsafe_allow_html=True)


# --------------------------------
# REGISTRATION PAGE
# --------------------------------

def registration_page():

    brand_header()

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:

        st.markdown(
            "<h2 style='text-align:center;'>Create Your Account</h2>",
            unsafe_allow_html=True
        )

        st.markdown(
            "<p style='text-align:center;'>Join WarrVault and organize your purchases.</p>",
            unsafe_allow_html=True
        )

        with st.form("registration_form"):

            name = st.text_input("Full Name")

            email = st.text_input("Email Address")

            password = st.text_input(
                "Password",
                type="password"
            )

            confirm_password = st.text_input(
                "Confirm Password",
                type="password"
            )

            submitted = st.form_submit_button(
                "Create Account",
                use_container_width=True
            )

            if submitted:

                if not name.strip() or not email.strip() or not password:
                    st.error("Please fill all required fields.")
                elif (
                    "@" not in email
                    or "." not in email.split("@")[-1]
                    or " " in email
                ):
                    st.error("Please enter a valid email address.")
                elif len(password) < 8:
                    st.error("Password must contain at least 8 characters.")

                elif not any(char.isupper() for char in password):
                    st.error("Password must contain at least one uppercase letter.")

                elif not any(char.islower() for char in password):
                    st.error("Password must contain at least one lowercase letter.")

                elif not any(char.isdigit() for char in password):
                    st.error("Password must contain at least one number.")
                elif password != confirm_password:
                    st.error("Passwords do not match!")

                else:

                    success, message = register_user(
                        name.strip(),
                        email.strip().lower(),
                        password
                    )

                    if success:

                        st.success(message)

                        st.session_state.page = "Login"

                        st.rerun()

                    else:

                        st.error(message)

        if st.button("← Back to Welcome", use_container_width=True):

            st.session_state.page = "Welcome"
            st.rerun()


# --------------------------------
# LOGIN PAGE
# --------------------------------

def login_page():

    brand_header()

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:

        st.markdown(
            "<h2 style='text-align:center;'>Welcome Back!</h2>",
            unsafe_allow_html=True
        )

        st.markdown(
            "<p style='text-align:center;'>Login to access your personal vault.</p>",
            unsafe_allow_html=True
        )

        with st.form("login_form"):

            email = st.text_input("Email Address")

            password = st.text_input(
                "Password",
                type="password"
            )

            submitted = st.form_submit_button(
                "Login to WarrVault",
                use_container_width=True
            )

            if submitted:

                if not email.strip() or not password:

                    st.error("Please enter email and password.")

                else:

                    user = login_user(
                        email.strip().lower(),
                        password
                    )

                    if user:

                        # Create a persistent login session
                        session_token = create_login_session(user["user_id"])

                        # Save login information in Streamlit
                        st.session_state.logged_in = True
                        st.session_state.user = user
                        st.session_state.session_token = session_token

                        # Save the token in the browser for 30 days
                        cookie_manager.set(
                            "warrvault_session",
                            session_token,
                            expires_at=datetime.now() + timedelta(days=30)
                        )

                        st.rerun()

                    else:

                        st.error("Invalid email or password!")

        if st.button("Create New Account", use_container_width=True):

            st.session_state.page = "Register"
            st.rerun()


# --------------------------------
# DASHBOARD PLACEHOLDER
# --------------------------------

def dashboard_page():

    # Sidebar branding
    with st.sidebar:

        st.markdown(
            "<h2 style='color:#5595FF;'>🔐 WarrVault</h2>",
            unsafe_allow_html=True
        )

        st.caption("PERSONAL WARRANTY MANAGER")

        st.divider()

        st.write("**MAIN MENU**")

        selected_page = st.radio(
            "Navigation",
            [
                "🏠 Dashboard",
                "📦 My Products",
                "📁 Document Vault",
                "🛡️ Warranty Tracker",
                "🔔 Reminders",
                "📊 Analytics",
                "👤 My Profile"
            ],
            label_visibility="collapsed"
        )

        st.divider()

        st.write(f"Logged in as **{st.session_state.user['name']}**")

        if st.button("🚪 Logout", use_container_width=True):

            # Revoke the saved login session
            revoke_login_session(
                st.session_state.session_token
            )

            # Remove the browser cookie
            cookie_manager.delete("warrvault_session")

            # Clear Streamlit login information
            st.session_state.logged_in = False
            st.session_state.user = None
            st.session_state.session_token = None
            st.session_state.page = "Welcome"

            st.rerun()

    # Main page navigation
    if selected_page == "🏠 Dashboard":

        render_dashboard(st.session_state.user)

    elif selected_page == "📦 My Products":
        render_products(st.session_state.user)


    elif selected_page == "📁 Document Vault":
        render_document_vault(st.session_state.user)

    elif selected_page == "🛡️ Warranty Tracker":
        render_warranty_tracker(st.session_state.user)

    elif selected_page == "🔔 Reminders":
        render_reminders(st.session_state.user)

    elif selected_page == "📊 Analytics":
        render_analytics(st.session_state.user)
    elif selected_page == "👤 My Profile":
        render_profile(st.session_state.user)
# --------------------------------
# MAIN APPLICATION ROUTING
# --------------------------------

if st.session_state.logged_in:

    dashboard_page()

else:

    if st.session_state.page == "Welcome":

        welcome_page()

    elif st.session_state.page == "Register":

        registration_page()

    elif st.session_state.page == "Login":

        login_page()
