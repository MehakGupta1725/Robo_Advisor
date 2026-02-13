import streamlit as st
import numpy as np
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import warnings
import json
import os
import re
import hashlib
from scipy.optimize import minimize

warnings.filterwarnings('ignore')

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="FinFlow India - Robo Advisory Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# INSTITUTIONAL COLOR SCHEME
# ============================================================================

COLOR_SCHEME = {
    'primary': '#1E40AF',           
    'primary_dark': '#1E3A8A',      
    'primary_light': '#3B82F6',     
    'secondary': '#0891B2',         
    'accent': '#DC2626',            
    'success': '#059669',           
    'warning': '#F59E0B',           
    'background': '#F8FAFC',        
    'surface': '#FFFFFF',           
    'border': '#E2E8F0',            
    'text_primary': '#1E293B',      
    'text_secondary': '#64748B',    
}

# ============================================================================
# PROFESSIONAL CSS STYLING
# ============================================================================

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Sora:wght@400;500;600;700&display=swap');
    
    :root {{
        --primary: {COLOR_SCHEME['primary']};
        --primary-dark: {COLOR_SCHEME['primary_dark']};
        --secondary: {COLOR_SCHEME['secondary']};
        --bg: {COLOR_SCHEME['background']};
        --text: {COLOR_SCHEME['text_primary']};
    }}
    
    * {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }}
    
    html, body {{
        background-color: {COLOR_SCHEME['background']};
        color: {COLOR_SCHEME['text_primary']};
    }}
    
    .main {{
        padding: 0;
    }}
    
    .stApp {{
        background-color: {COLOR_SCHEME['background']};
    }}
    
    h1, h2, h3, h4, h5, h6 {{
        font-family: 'Sora', sans-serif;
        font-weight: 700;
        color: {COLOR_SCHEME['text_primary']};
        letter-spacing: -0.5px;
    }}
    
    h1 {{
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }}
    
    h2 {{
        font-size: 1.875rem;
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-bottom: 3px solid {COLOR_SCHEME['primary']};
        padding-bottom: 0.5rem;
    }}
    
    h3 {{
        font-size: 1.25rem;
        margin-bottom: 0.75rem;
    }}
    
    p {{
        color: {COLOR_SCHEME['text_secondary']};
        line-height: 1.6;
        font-size: 0.95rem;
    }}
    
    /* Dashboard Header */
    .dashboard-header {{
        background: linear-gradient(135deg, {COLOR_SCHEME['primary']} 0%, {COLOR_SCHEME['primary_dark']} 100%);
        padding: 3rem 2.5rem;
        border-radius: 0;
        color: white;
        margin-bottom: 2rem;
    }}
    
    .dashboard-header h1 {{
        color: white;
        margin: 0;
        font-size: 2.2rem;
    }}
    
    .dashboard-header p {{
        color: rgba(255, 255, 255, 0.9);
        font-size: 1.05rem;
        margin-bottom: 0;
    }}
    
    /* Cards */
    .metric-card {{
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid {COLOR_SCHEME['border']};
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
    }}
    
    .metric-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }}
    
    .metric-card-top {{
        border-top: 3px solid {COLOR_SCHEME['primary']};
    }}
    
    .metric-label {{
        color: {COLOR_SCHEME['text_secondary']};
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.5rem;
    }}
    
    .metric-value {{
        color: {COLOR_SCHEME['text_primary']};
        font-size: 1.75rem;
        font-weight: 700;
        margin: 0;
    }}
    
    .metric-change {{
        color: {COLOR_SCHEME['success']};
        font-size: 0.9rem;
        font-weight: 500;
        margin-top: 0.5rem;
    }}
    
    /* Buttons */
    .stButton > button {{
        border-radius: 8px;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        border: none;
        transition: all 0.3s ease;
        cursor: pointer;
    }}
    
    .stButton > button[type="primary"] {{
        background: linear-gradient(135deg, {COLOR_SCHEME['primary']} 0%, {COLOR_SCHEME['primary_dark']} 100%);
        color: white;
        box-shadow: 0 4px 12px rgba(30, 64, 175, 0.3);
    }}
    
    .stButton > button[type="primary"]:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(30, 64, 175, 0.4);
    }}
    
    /* Input Fields */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select,
    .stNumberInput > div > div > input,
    .stSlider > div > div > div > input {{
        border-radius: 8px;
        border: 1px solid {COLOR_SCHEME['border']} !important;
        padding: 0.75rem !important;
        font-size: 0.95rem !important;
        transition: all 0.3s ease !important;
    }}
    
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus,
    .stNumberInput > div > div > input:focus {{
        border-color: {COLOR_SCHEME['primary']} !important;
        box-shadow: 0 0 0 3px rgba(30, 64, 175, 0.1) !important;
    }}
    
    /* Messages */
    .stSuccess {{
        background-color: #ECFDF5 !important;
        color: #065F46 !important;
        border-left: 4px solid {COLOR_SCHEME['success']} !important;
    }}
    
    .stError {{
        background-color: #FEE2E2 !important;
        color: #7F1D1D !important;
        border-left: 4px solid {COLOR_SCHEME['accent']} !important;
    }}
    
    .stWarning {{
        background-color: #FFFBEB !important;
        color: #78350F !important;
        border-left: 4px solid {COLOR_SCHEME['warning']} !important;
    }}
    
    .stInfo {{
        background-color: #F0F9FF !important;
        color: #0C2340 !important;
        border-left: 4px solid {COLOR_SCHEME['primary']} !important;
    }}
    
    /* Sidebar */
    .sidebar {{
        background: white;
    }}
    
    .sidebar [data-testid="stSidebarNav"] {{
        background: white;
    }}
    
    /* Divider */
    hr {{
        border: none;
        height: 1px;
        background: {COLOR_SCHEME['border']};
        margin: 2rem 0;
    }}
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 0.5rem;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        background-color: {COLOR_SCHEME['background']};
        color: {COLOR_SCHEME['text_secondary']};
        font-weight: 600;
        transition: all 0.3s ease;
    }}
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {{
        background: {COLOR_SCHEME['primary']};
        color: white;
    }}
    
    /* DataFrame */
    .stDataFrame {{
        border-radius: 8px;
        overflow: hidden;
    }}
    
    /* Responsive */
    @media (max-width: 768px) {{
        .dashboard-header {{
            padding: 1.5rem;
        }}
        
        h1 {{
            font-size: 1.75rem;
        }}
        
        h2 {{
            font-size: 1.4rem;
        }}
        
        .metric-value {{
            font-size: 1.5rem;
        }}
    }}
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# AUTHENTICATION SYSTEM
# ============================================================================

USERS_FILE = "users_data.json"

def hash_password(password):
    """Hash password using SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    """Load registered users from JSON file."""
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    """Save users to JSON file."""
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

def validate_email(email):
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength."""
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    if not any(char.isupper() for char in password):
        return False, "Password must contain at least one uppercase letter"
    if not any(char.isdigit() for char in password):
        return False, "Password must contain at least one digit"
    return True, "Password is strong"

def register_user(email, password, fullname):
    """Register a new user."""
    users = load_users()
    if email in users:
        return False, "Email already registered!"
    
    is_valid, msg = validate_password(password)
    if not is_valid:
        return False, msg
    
    if not validate_email(email):
        return False, "Invalid email format!"
    
    users[email] = {
        "password": hash_password(password),
        "fullname": fullname,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    save_users(users)
    return True, "Account created successfully! Please login."

def login_user(email, password):
    """Authenticate user login."""
    users = load_users()
    if email not in users:
        return False, "Email not found!"
    
    if users[email]["password"] != hash_password(password):
        return False, "Incorrect password!"
    
    return True, "Login successful!"

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_email" not in st.session_state:
    st.session_state.user_email = None
if "user_name" not in st.session_state:
    st.session_state.user_name = None
if "page" not in st.session_state:
    st.session_state.page = "login"
if "risk_profile" not in st.session_state:
    st.session_state.risk_profile = "Moderate"

# ============================================================================
# AUTHENTICATION PAGES
# ============================================================================

def show_login_page():
    """Display the professional login page."""
    st.markdown("""
        <style>
            .login-background {
                background: linear-gradient(135deg, #1E40AF 0%, #1E3A8A 50%, #0891B2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                z-index: -1;
            }
            
            .login-container {
                display: flex;
                align-items: center;
                justify-content: center;
                min-height: 100vh;
                padding: 10px;
            }
            
            .login-card {
                background: white;
                border-radius: 20px;
                padding: 2.5rem 2.2rem;
                max-width: 400px;
                width: 100%;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                animation: slideUp 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
            }
            
            @keyframes slideUp {
                from {
                    opacity: 0;
                    transform: translateY(40px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            
            .login-header {
                text-align: center;
                margin-bottom: 1.8rem;
            }
            
            .login-logo {
                font-size: 3rem;
                margin-bottom: 0.5rem;
                display: inline-block;
                animation: bounce 2s infinite;
            }
            
            @keyframes bounce {
                0%, 100% { transform: translateY(0); }
                50% { transform: translateY(-10px); }
            }
            
            .login-title {
                color: #1E293B;
                font-size: 1.6rem;
                font-weight: 700;
                margin: 0.3rem 0 0 0;
                font-family: 'Sora', sans-serif;
            }
            
            .login-subtitle {
                color: #64748B;
                font-size: 0.85rem;
                margin: 0.4rem 0 0 0;
                font-weight: 400;
            }
            
            .login-separator {
                width: 50px;
                height: 3px;
                background: linear-gradient(90deg, #1E40AF, #0891B2);
                margin: 1rem auto;
                border-radius: 2px;
            }
            
            .login-form-group {
                margin-bottom: 1rem;
            }
            
            .login-label {
                display: block;
                color: #1E293B;
                font-weight: 600;
                font-size: 0.85rem;
                margin-bottom: 0.5rem;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            .login-input {
                width: 100%;
                padding: 0.75rem 1rem;
                border: 2px solid #E2E8F0;
                border-radius: 8px;
                font-size: 0.9rem;
                transition: all 0.3s ease;
                background: #F8FAFC;
                font-family: 'Inter', sans-serif;
                color: #1E293B;
                box-sizing: border-box;
            }
            
            .login-input::placeholder {
                color: #CBD5E1;
            }
            
            .login-input:hover {
                border-color: #1E40AF;
                background: white;
            }
            
            .login-input:focus {
                outline: none;
                border-color: #1E40AF;
                background: white;
                box-shadow: 0 0 0 3px rgba(30, 64, 175, 0.1);
            }
            
            .login-button {
                width: 100%;
                padding: 0.95rem;
                background: linear-gradient(135deg, #1E40AF 0%, #1E3A8A 100%);
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 0.95rem;
                font-weight: 700;
                cursor: pointer;
                transition: all 0.3s ease;
                margin-top: 1rem;
                box-shadow: 0 4px 15px rgba(30, 64, 175, 0.3);
            }
            
            .login-button:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(30, 64, 175, 0.4);
            }
            
            .login-button:active {
                transform: translateY(0);
            }
            
            .login-divider {
                text-align: center;
                margin: 1.2rem 0 1rem 0;
                color: #CBD5E1;
                font-size: 0.8rem;
            }
            
            .login-divider::before,
            .login-divider::after {
                content: '';
                display: inline-block;
                width: 45%;
                height: 1px;
                background: #E2E8F0;
                vertical-align: middle;
            }
            
            .login-divider::before {
                margin-right: 0.5rem;
            }
            
            .login-divider::after {
                margin-left: 0.5rem;
            }
            
            .login-footer {
                text-align: center;
                margin-top: 1rem;
                color: #64748B;
                font-size: 0.8rem;
            }
            
            .login-footer a, .login-footer button {
                color: #1E40AF;
                text-decoration: none;
                font-weight: 600;
                background: none;
                border: none;
                cursor: pointer;
                padding: 0;
                font-size: 0.8rem;
                transition: color 0.3s ease;
            }
            
            .login-footer a:hover, .login-footer button:hover {
                color: #1E3A8A;
                text-decoration: underline;
            }
            
            .feature-highlights {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 0.8rem;
                margin-top: 1.3rem;
                padding-top: 1.2rem;
                border-top: 1px solid #E2E8F0;
            }
            
            .feature-item {
                text-align: center;
                font-size: 0.75rem;
                color: #64748B;
            }
            
            .feature-icon {
                font-size: 1.4rem;
                margin-bottom: 0.3rem;
            }
        </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2.5, 1])
    
    with col2:
        st.markdown("""
            <div class='login-header'>
                <div class='login-logo'>📊</div>
                <h1 class='login-title'>FinFlow India</h1>
                <p class='login-subtitle'>Smart Investment Advisory</p>
                <div class='login-separator'></div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
            <div style='text-align: center; margin-bottom: 1.3rem;'>
                <h2 style='color: #1E293B; font-size: 1.3rem; margin: 0 0 0.3rem 0; font-family: Sora;'>Sign In</h2>
                <p style='color: #64748B; margin: 0; font-size: 0.85rem;'>Manage your portfolio</p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form", clear_on_submit=False):
            email = st.text_input("Email", placeholder="you@example.com", key="login_email")
            password = st.text_input("Password", type="password", placeholder="Enter password", key="login_password")
            
            submit_button = st.form_submit_button(
                "🔐 Sign In", 
                use_container_width=True, 
                type="primary"
            )
            
            if submit_button:
                if not email or not password:
                    st.error("❌ Please enter both email and password!")
                else:
                    success, message = login_user(email, password)
                    if success:
                        st.session_state.authenticated = True
                        st.session_state.user_email = email
                        users = load_users()
                        st.session_state.user_name = users[email]["fullname"]
                        st.success("✅ " + message)
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ " + message)
        
        st.markdown("""
            <div class='login-divider'>or</div>
        """, unsafe_allow_html=True)
        
        col1_demo, col2_signup = st.columns([1, 1])
        
        with col1_demo:
            if st.button("📌 Demo", use_container_width=True, key="demo_btn"):
                st.info("📧 demo@example.com | 🔑 Demo123")
        
        with col2_signup:
            if st.button("✨ Sign Up", use_container_width=True, key="to_signup"):
                st.session_state.page = "signup"
                st.rerun()
        
        st.markdown("""
            <div class='feature-highlights'>
                <div class='feature-item'>
                    <div class='feature-icon'>🎯</div>
                    <div>Smart</div>
                </div>
                <div class='feature-item'>
                    <div class='feature-icon'>📊</div>
                    <div>Analytics</div>
                </div>
                <div class='feature-item'>
                    <div class='feature-icon'>🔒</div>
                    <div>Secure</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

def show_signup_page():
    """Display the professional signup page."""
    st.markdown("""
        <style>
            .signup-container {
                display: flex;
                align-items: center;
                justify-content: center;
                min-height: 100vh;
                padding: 10px;
            }
            
            .signup-card {
                background: white;
                border-radius: 20px;
                padding: 2.5rem 2.2rem;
                max-width: 430px;
                width: 100%;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                animation: slideUp 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
            }
            
            .signup-header {
                text-align: center;
                margin-bottom: 1.6rem;
            }
            
            .signup-logo {
                font-size: 3rem;
                margin-bottom: 0.5rem;
                display: inline-block;
                animation: bounce 2s infinite;
            }
            
            .signup-title {
                color: #1E293B;
                font-size: 1.6rem;
                font-weight: 700;
                margin: 0.3rem 0 0 0;
                font-family: 'Sora', sans-serif;
            }
            
            .signup-subtitle {
                color: #64748B;
                font-size: 0.85rem;
                margin: 0.3rem 0 0 0;
            }
            
            .signup-separator {
                width: 50px;
                height: 3px;
                background: linear-gradient(90deg, #10B981, #059669);
                margin: 1rem auto;
                border-radius: 2px;
            }
            
            .password-strength {
                margin-top: 0.4rem;
                font-size: 0.75rem;
                padding: 0.5rem 0.8rem;
                border-radius: 6px;
                background: #F0F4F8;
                border-left: 4px solid #10B981;
            }
            
            .strength-indicator {
                font-weight: 600;
                margin-bottom: 0.3rem;
            }
            
            .requirement-item {
                display: flex;
                align-items: center;
                font-size: 0.75rem;
                margin: 0.25rem 0;
                color: #64748B;
            }
            
            .requirement-check {
                display: inline-block;
                width: 14px;
                height: 14px;
                border-radius: 50%;
                margin-right: 0.4rem;
                text-align: center;
                line-height: 14px;
                font-size: 0.65rem;
                font-weight: bold;
            }
            
            .requirement-met {
                background: #D1FAE5;
                color: #065F46;
            }
            
            .requirement-unmet {
                background: #FEE2E2;
                color: #991B1B;
            }
            
            .signup-button {
                width: 100%;
                padding: 0.9rem;
                background: linear-gradient(135deg, #10B981 0%, #059669 100%);
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 0.95rem;
                font-weight: 700;
                cursor: pointer;
                transition: all 0.3s ease;
                margin-top: 0.9rem;
                box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
            }
            
            .signup-button:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(16, 185, 129, 0.4);
            }
        </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2.5, 1])
    
    with col2:
        st.markdown("""
            <div class='signup-header'>
                <div class='signup-logo'>✨</div>
                <h1 class='signup-title'>Join FinFlow India</h1>
                <p class='signup-subtitle'>Start your wealth journey</p>
                <div class='signup-separator'></div>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("signup_form", clear_on_submit=False):
            fullname = st.text_input("Full Name", placeholder="John Doe", key="signup_name")
            email = st.text_input("Email Address", placeholder="you@example.com", key="signup_email")
            password = st.text_input("Password", type="password", placeholder="Create a strong password", key="signup_password")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Re-enter your password", key="signup_confirm")
            
            # Password strength indicator
            if password:
                is_valid, validation_msg = validate_password(password)
                strength = 0
                strength_text = "Weak"
                
                if len(password) >= 6:
                    strength += 1
                if any(c.isupper() for c in password):
                    strength += 1
                if any(c.isdigit() for c in password):
                    strength += 1
                
                if strength <= 1:
                    strength_text = "Weak"
                elif strength == 2:
                    strength_text = "Fair"
                else:
                    strength_text = "Strong"
                
                st.markdown(f"""
                    <div class='password-strength'>
                    <div class='strength-indicator'>✅ {strength_text}</div>
                    <div class='requirement-item'>
                        <div class='requirement-check {'requirement-met' if len(password) >= 6 else 'requirement-unmet'}'>{'✓' if len(password) >= 6 else '✗'}</div>
                        6+ characters
                    </div>
                    <div class='requirement-item'>
                        <div class='requirement-check {'requirement-met' if any(c.isupper() for c in password) else 'requirement-unmet'}'>{'✓' if any(c.isupper() for c in password) else '✗'}</div>
                        Uppercase
                    </div>
                    <div class='requirement-item'>
                        <div class='requirement-check {'requirement-met' if any(c.isdigit() for c in password) else 'requirement-unmet'}'>{'✓' if any(c.isdigit() for c in password) else '✗'}</div>
                        Number
                    </div>
                    </div>
                """, unsafe_allow_html=True)
            
            submit_button = st.form_submit_button("🚀 Create Account", use_container_width=True, type="primary")
            
            if submit_button:
                if not all([fullname, email, password, confirm_password]):
                    st.error("❌ Please fill in all fields!")
                elif password != confirm_password:
                    st.error("❌ Passwords do not match!")
                elif not validate_email(email):
                    st.error("❌ Please enter a valid email address!")
                else:
                    is_valid, msg = validate_password(password)
                    if not is_valid:
                        st.error(f"❌ {msg}")
                    else:
                        success, message = register_user(email, password, fullname)
                        if success:
                            st.success("✅ " + message)
                            st.balloons()
                            st.sleep(1.5)
                            st.session_state.page = "login"
                            st.rerun()
                        else:
                            st.error("❌ " + message)
        
        if st.button("↩️ Back to Login", use_container_width=True, key="back_to_login"):
            st.session_state.page = "login"
            st.rerun()

# ============================================================================
# MAIN APPLICATION - REDIRECT TO AUTH IF NOT LOGGED IN
# ============================================================================

if not st.session_state.authenticated:
    if st.session_state.page == "signup":
        show_signup_page()
    else:
        show_login_page()
    st.stop()

# ============================================================================
# ASSET DATABASE & PORTFOLIO STRATEGIES
# ============================================================================

ASSET_DATABASE = {
    'NIFTY 50': '^NSEI',
    'NIFTY IT': '^CNXIT',
    'NIFTY MIDCAP 50': '^NSMID50',
    'Government Bonds': 'GILT.NS',
    'Gold ETF': '^NSEINDEXG',
    'Bank NIFTY': '^NSEBANK',
    'PSU Stocks': '^CNXINFRA',
    'NIFTY 100': '^NSEI',
}

PORTFOLIO_STRATEGIES = {
    'Conservative': {
        'description': 'Low risk, stable returns. Suitable for retirees and risk-averse investors.',
        'allocation': {'GILT.NS': 0.70, '^NSEI': 0.25, '^NSEINDEXG': 0.05},
        'expected_return': 0.065,
        'volatility': 0.08
    },
    'Moderate': {
        'description': 'Balanced approach. Suitable for long-term investors with moderate risk tolerance.',
        'allocation': {'^NSEI': 0.50, 'GILT.NS': 0.40, '^NSMID50': 0.05, '^NSEINDEXG': 0.05},
        'expected_return': 0.095,
        'volatility': 0.12
    },
    'Aggressive': {
        'description': 'Growth-focused. Suitable for investors with high risk tolerance and longer time horizons.',
        'allocation': {'^NSEI': 0.35, '^CNXIT': 0.30, '^NSMID50': 0.20, '^NSEBANK': 0.15},
        'expected_return': 0.140,
        'volatility': 0.18
    },
    'Growth': {
        'description': 'Emphasizes capital appreciation through Indian equities.',
        'allocation': {'^CNXIT': 0.35, '^NSEI': 0.35, '^NSMID50': 0.20, '^NSEINDEXG': 0.10},
        'expected_return': 0.125,
        'volatility': 0.16
    },
    'Income': {
        'description': 'Focus on stable income through bonds and dividend stocks.',
        'allocation': {'GILT.NS': 0.50, '^NSEBANK': 0.30, '^NSEI': 0.15, '^NSEINDEXG': 0.05},
        'expected_return': 0.080,
        'volatility': 0.09
    }
}

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

@st.cache_data(ttl=3600)
def fetch_asset_data(ticker, years=5):
    """Fetch historical asset data."""
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365*years)
        data = yf.download(ticker, start=start_date, end=end_date, progress=False, quiet=True)
        if data is None or data.empty:
            return None
        return data['Adj Close']
    except:
        return None

def create_metric_card(label, value, change=None, color="primary"):
    """Create a professional metric card."""
    change_html = ""
    if change is not None:
        change_color = "success" if change >= 0 else "accent"
        change_html = f"""
        <div style='color: {COLOR_SCHEME[change_color]}; font-size: 0.9rem; font-weight: 500; margin-top: 0.5rem;'>
            {'↑' if change >= 0 else '↓'} {abs(change):.2f}%
        </div>
        """
    
    st.markdown(f"""
        <div class='metric-card metric-card-top' style='border-top-color: {COLOR_SCHEME[color]};'>
            <div class='metric-label'>{label}</div>
            <div class='metric-value'>{value}</div>
            {change_html}
        </div>
    """, unsafe_allow_html=True)

def create_dashboard_header(title, subtitle=""):
    """Create professional dashboard header."""
    subtitle_html = f"<p>{subtitle}</p>" if subtitle else ""
    st.markdown(f"""
        <div class='dashboard-header'>
            <h1>{title}</h1>
            {subtitle_html}
        </div>
    """, unsafe_allow_html=True)

# ============================================================================
# SIDEBAR CONFIGURATION
# ============================================================================

with st.sidebar:
    st.markdown(f"### 👤 {st.session_state.user_name}")
    st.markdown(f"📧 {st.session_state.user_email}")
    st.markdown("---")
    
    if st.button("🔓 Logout", use_container_width=True, key="logout_btn"):
        st.session_state.authenticated = False
        st.session_state.user_email = None
        st.session_state.user_name = None
        st.rerun()
    
    st.markdown("---")
    st.markdown("### ⚙️ Investment Settings")
    
    # Portfolio Strategy Selection
    strategy = st.selectbox(
        "Select Portfolio Strategy",
        list(PORTFOLIO_STRATEGIES.keys()),
        index=1,
        help="Choose your investment strategy"
    )
    st.session_state.risk_profile = strategy
    
    # Display strategy description
    st.caption(PORTFOLIO_STRATEGIES[strategy]['description'])
    
    st.markdown("---")
    
    # Investment Parameters
    st.markdown("### 💰 Investment Parameters")
    
    investment_amount = st.number_input(
        "Initial Investment (₹)",
        min_value=50000.0,
        max_value=50000000.0,
        value=500000.0,
        step=50000.0,
    )
    
    investment_horizon = st.number_input(
        "Investment Horizon (Years)",
        min_value=1,
        max_value=50,
        value=20,
    )
    
    monthly_contribution = st.number_input(
        "Monthly Contribution (₹)",
        min_value=0.0,
        max_value=500000.0,
        value=10000.0,
        step=1000.0,
    )

# ============================================================================
# MAIN CONTENT
# ============================================================================

create_dashboard_header(
    "🎯 FinFlow India - Robo Advisory Dashboard",
    f"Personalized portfolio management for {st.session_state.user_name} | {st.session_state.risk_profile} Strategy"
)

# Portfolio Overview Section
st.markdown("### 📊 Portfolio Overview")

col1, col2, col3, col4 = st.columns(4)

strategy_data = PORTFOLIO_STRATEGIES[st.session_state.risk_profile]

with col1:
    create_metric_card("Expected Return", f"{strategy_data['expected_return']*100:.1f}%", color="primary")

with col2:
    create_metric_card("Annual Volatility", f"{strategy_data['volatility']*100:.1f}%", color="secondary")

with col3:
    create_metric_card("Investment Amount", f"₹{investment_amount:,.0f}", color="success")

with col4:
    create_metric_card("Portfolio Assets", str(len(strategy_data['allocation'])), color="warning")

st.markdown("")

# Asset Allocation Section
st.markdown("### 💼 Recommended Asset Allocation")

col_alloc, col_comp = st.columns([1, 1])

with col_alloc:
    # Pie Chart using Plotly
    allocation = strategy_data['allocation']
    fig_pie = go.Figure(data=[go.Pie(
        labels=list(allocation.keys()),
        values=list(allocation.values()),
        hole=0,
        textposition="inside",
        textinfo="label+percent",
        hovertemplate="<b>%{label}</b><br>%{value:.1%}<extra></extra>",
        marker=dict(
            colors=[COLOR_SCHEME['primary'], COLOR_SCHEME['secondary'], 
                   COLOR_SCHEME['success'], COLOR_SCHEME['warning']],
            line=dict(color=COLOR_SCHEME['surface'], width=2)
        )
    )])
    fig_pie.update_layout(
        height=400,
        showlegend=True,
        margin=dict(t=0, b=0, l=0, r=0),
        paper_bgcolor=COLOR_SCHEME['background'],
        plot_bgcolor=COLOR_SCHEME['background'],
        font=dict(family="Inter", color=COLOR_SCHEME['text_primary'])
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with col_comp:
    # Allocation Table
    allocation_data = []
    for ticker, weight in allocation.items():
        allocation_data.append({
            'Asset': ticker,
            'Weight': f"{weight*100:.1f}%",
            'Amount': f"${investment_amount*weight:,.0f}"
        })
    
    allocation_df = pd.DataFrame(allocation_data)
    st.dataframe(allocation_df, use_container_width=True, height=400, hide_index=True)

st.markdown("")

# Asset Performance Section
st.markdown("### 📈 Historical Performance Analysis")

# Load data for selected assets
with st.spinner("📥 Loading market data..."):
    prices_data = {}
    for ticker in strategy_data['allocation'].keys():
        prices_data[ticker] = fetch_asset_data(ticker, years=5)

# Create performance chart
if all(prices is not None for prices in prices_data.values()):
    fig_perf = go.Figure()
    
    for ticker, prices in prices_data.items():
        normalized = (prices / prices.iloc[0]) * 100
        fig_perf.add_trace(go.Scatter(
            x=normalized.index,
            y=normalized.values,
            name=ticker,
            mode='lines',
            line=dict(width=2.5),
            hovertemplate="<b>%{fullData.name}</b><br>%{x|%Y-%m-%d}<br>%{y:.2f}<extra></extra>"
        ))
    
    fig_perf.update_layout(
        title="Normalized Asset Performance (5-Year Period)",
        xaxis_title="Date",
        yaxis_title="Indexed Value (Base = 100)",
        hovermode="x unified",
        height=450,
        template="plotly_white",
        paper_bgcolor=COLOR_SCHEME['background'],
        plot_bgcolor=COLOR_SCHEME['surface'],
        font=dict(family="Inter", color=COLOR_SCHEME['text_primary']),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(t=60, b=60, l=60, r=60)
    )
    
    st.plotly_chart(fig_perf, use_container_width=True)

st.markdown("")

# Monte Carlo Simulation
st.markdown("### 🎲 Monte Carlo Simulation - Retirement Projections")

tab1, tab2 = st.tabs(["Projection", "Statistics"])

with tab1:
    col_sim1, col_sim2 = st.columns([3, 1])
    
    with col_sim1:
        with st.spinner("⏳ Running 1,000 Monte Carlo simulations..."):
            np.random.seed(42)
            num_simulations = 1000
            num_months = investment_horizon * 12
            
            daily_return = strategy_data['expected_return'] / 252
            daily_volatility = strategy_data['volatility'] / np.sqrt(252)
            
            final_values = []
            paths = np.zeros((num_months, num_simulations))
            
            for sim in range(num_simulations):
                portfolio_value = investment_amount
                for month in range(num_months):
                    # Add monthly contribution
                    portfolio_value += monthly_contribution
                    
                    # Generate monthly return
                    monthly_ret = np.random.normal(daily_return * 21, daily_volatility * np.sqrt(21))
                    portfolio_value *= (1 + monthly_ret)
                    
                    paths[int(month), sim] = portfolio_value
                
                final_values.append(portfolio_value)
            
            final_values = np.array(final_values)
            
            # Create percentile paths
            percentile_5 = np.percentile(paths, 5, axis=1)
            percentile_50 = np.percentile(paths, 50, axis=1)
            percentile_95 = np.percentile(paths, 95, axis=1)
            
            # Plot trajectories
            fig_mc = go.Figure()
            
            # Add sample paths (transparent)
            for sim in range(min(100, num_simulations)):
                fig_mc.add_trace(go.Scatter(
                    x=np.arange(num_months),
                    y=paths[:, sim],
                    mode='lines',
                    line=dict(color=COLOR_SCHEME['primary'], width=0.5),
                    opacity=0.05,
                    hoverinfo='skip',
                    showlegend=False
                ))
            
            # Add percentile lines
            months = np.arange(num_months)
            
            fig_mc.add_trace(go.Scatter(
                x=months,
                y=percentile_95,
                fill=None,
                mode='lines',
                name='95th Percentile (Best Case)',
                line=dict(color=COLOR_SCHEME['success'], width=2, dash='dash'),
                hovertemplate="95th: $%{y:,.0f}<extra></extra>"
            ))
            
            fig_mc.add_trace(go.Scatter(
                x=months,
                y=percentile_50,
                fill='tonexty',
                mode='lines',
                name='50th Percentile (Median)',
                line=dict(color=COLOR_SCHEME['primary'], width=3),
                fillcolor=f"rgba(30, 64, 175, 0.2)",
                hovertemplate="Median: $%{y:,.0f}<extra></extra>"
            ))
            
            fig_mc.add_trace(go.Scatter(
                x=months,
                y=percentile_5,
                fill='tonexty',
                mode='lines',
                name='5th Percentile (Worst Case)',
                line=dict(color=COLOR_SCHEME['accent'], width=2, dash='dash'),
                fillcolor=f"rgba(220, 38, 38, 0.1)",
                hovertemplate="5th: $%{y:,.0f}<extra></extra>"
            ))
            
            fig_mc.update_layout(
                title=f"Projected Portfolio Value Over {investment_horizon} Years",
                xaxis_title="Months",
                yaxis_title="Portfolio Value ($)",
                height=500,
                template="plotly_white",
                hovermode="x unified",
                paper_bgcolor=COLOR_SCHEME['background'],
                plot_bgcolor=COLOR_SCHEME['surface'],
                font=dict(family="Inter", color=COLOR_SCHEME['text_primary']),
                yaxis=dict(tickformat="$,"),
                margin=dict(t=60, b=60, l=80, r=60)
            )
            
            st.plotly_chart(fig_mc, use_container_width=True)

with tab2:
    # Statistics
    stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
    
    with stat_col1:
        create_metric_card(
            "5th Percentile",
            f"${np.percentile(final_values, 5):,.0f}",
            ((np.percentile(final_values, 5) / investment_amount - 1) * 100),
            "accent"
        )
    
    with stat_col2:
        create_metric_card(
            "Median (50th)",
            f"${np.percentile(final_values, 50):,.0f}",
            ((np.percentile(final_values, 50) / investment_amount - 1) * 100),
            "primary"
        )
    
    with stat_col3:
        create_metric_card(
            "95th Percentile",
            f"${np.percentile(final_values, 95):,.0f}",
            ((np.percentile(final_values, 95) / investment_amount - 1) * 100),
            "success"
        )
    
    with stat_col4:
        create_metric_card(
            "Expected Value",
            f"${np.mean(final_values):,.0f}",
            ((np.mean(final_values) / investment_amount - 1) * 100)
        )
    
    st.markdown("")
    
    # Distribution
    fig_dist = go.Figure()
    fig_dist.add_trace(go.Histogram(
        x=final_values,
        nbinsx=50,
        name="Simulation Results",
        marker=dict(color=COLOR_SCHEME['primary']),
        hovertemplate="Portfolio Value: $%{x:,.0f}<br>Frequency: %{y}<extra></extra>"
    ))
    
    fig_dist.update_layout(
        title="Distribution of Final Portfolio Values",
        xaxis_title="Final Portfolio Value ($)",
        yaxis_title="Frequency",
        height=400,
        template="plotly_white",
        paper_bgcolor=COLOR_SCHEME['background'],
        plot_bgcolor=COLOR_SCHEME['surface'],
        font=dict(family="Inter", color=COLOR_SCHEME['text_primary']),
        xaxis=dict(tickformat="$,"),
        margin=dict(t=60, b=60, l=80, r=60),
        showlegend=False
    )
    
    st.plotly_chart(fig_dist, use_container_width=True)

st.markdown("")

# Risk Analysis Section
st.markdown("### 📊 Risk Analysis")

col_risk1, col_risk2 = st.columns([1, 1])

with col_risk1:
    # Correlation Matrix
    if all(prices is not None for prices in prices_data.values()):
        returns_dict = {}
        for ticker, prices in prices_data.items():
            if len(prices) > 1:
                returns_dict[ticker] = prices.pct_change().dropna()
        
        if returns_dict:
            returns_df = pd.DataFrame(returns_dict)
            corr_matrix = returns_df.corr()
            
            fig_corr = go.Figure(data=go.Heatmap(
                z=corr_matrix.values,
                x=corr_matrix.columns,
                y=corr_matrix.columns,
                colorscale='RdYlGn',
                zmid=0,
                zmin=-1,
                zmax=1,
                text=np.round(corr_matrix.values, 2),
                texttemplate='%{text:.2f}',
                textfont={"size": 10},
                colorbar=dict(title="Correlation"),
                hovertemplate="%{y} - %{x}<br>%{z:.3f}<extra></extra>"
            ))
            
            fig_corr.update_layout(
                title="Asset Correlation Matrix",
                height=400,
                template="plotly_white",
                paper_bgcolor=COLOR_SCHEME['background'],
                plot_bgcolor=COLOR_SCHEME['surface'],
                font=dict(family="Inter", color=COLOR_SCHEME['text_primary']),
                margin=dict(t=60, b=60, l=100, r=80)
            )
            
            st.plotly_chart(fig_corr, use_container_width=True)

with col_risk2:
    # Risk-Return Scatter
    risk_return_data = []
    for ticker, prices in prices_data.items():
        if prices is not None and len(prices) > 1:
            returns = prices.pct_change().dropna()
            annual_return = returns.mean() * 252
            annual_volatility = returns.std() * np.sqrt(252)
            risk_return_data.append({
                'ticker': ticker,
                'return': annual_return,
                'volatility': annual_volatility
            })
    
    if risk_return_data:
        risk_df = pd.DataFrame(risk_return_data)
        
        fig_risk = go.Figure()
        
        fig_risk.add_trace(go.Scatter(
            x=risk_df['volatility'] * 100,
            y=risk_df['return'] * 100,
            mode='markers+text',
            text=risk_df['ticker'],
            textposition="top center",
            marker=dict(
                size=12,
                color=COLOR_SCHEME['primary'],
                opacity=0.7,
                line=dict(width=2, color='white')
            ),
            hovertemplate="<b>%{text}</b><br>Volatility: %{x:.1f}%<br>Return: %{y:.1f}%<extra></extra>"
        ))
        
        # Add portfolio point
        fig_risk.add_trace(go.Scatter(
            x=[strategy_data['volatility'] * 100],
            y=[strategy_data['expected_return'] * 100],
            mode='markers+text',
            text=['Portfolio'],
            textposition="top center",
            marker=dict(
                size=15,
                color=COLOR_SCHEME['success'],
                symbol='star',
                line=dict(width=2, color='white')
            ),
            name='Portfolio',
            hovertemplate="<b>Portfolio</b><br>Volatility: %{x:.1f}%<br>Return: %{y:.1f}%<extra></extra>"
        ))
        
        fig_risk.update_layout(
            title="Risk-Return Profile",
            xaxis_title="Volatility (Standard Deviation %)",
            yaxis_title="Expected Annual Return (%)",
            height=400,
            template="plotly_white",
            paper_bgcolor=COLOR_SCHEME['background'],
            plot_bgcolor=COLOR_SCHEME['surface'],
            font=dict(family="Inter", color=COLOR_SCHEME['text_primary']),
            hovermode="closest",
            margin=dict(t=60, b=60, l=80, r=60)
        )
        
        st.plotly_chart(fig_risk, use_container_width=True)

st.markdown("")

# Strategy Comparison
st.markdown("### 🔗 Strategy Comparison")

comparison_data = []
for strat_name, strat_config in PORTFOLIO_STRATEGIES.items():
    sharpe = strat_config['expected_return'] / strat_config['volatility']
    comparison_data.append({
        'Strategy': strat_name,
        'Expected Return': f"{strat_config['expected_return']*100:.1f}%",
        'Volatility': f"{strat_config['volatility']*100:.1f}%",
        'Sharpe Ratio': f"{sharpe:.2f}",
        'Assets': len(strat_config['allocation'])
    })

comparison_df = pd.DataFrame(comparison_data)
st.dataframe(comparison_df, use_container_width=True, hide_index=True)

st.markdown("")

# Footer Disclaimer
st.markdown(f"""
---
### ⚠️ Important Disclaimer

This application is provided for **educational and informational purposes only** and does not constitute financial, investment, or legal advice. 

- **No Guarantees**: Past performance does not guarantee future results. Market conditions are unpredictable.
- **Professional Advice**: Always consult a qualified financial advisor before making investment decisions.
- **Risk Disclosure**: All investments involve risk, including potential loss of principal.
- **Data Source**: Historical data sourced from Yahoo Finance. Market data may have delays or inaccuracies.

---
© 2026 **FinFlow** - Professional Robo Advisory Platform | All Rights Reserved
""")
