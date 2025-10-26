"""
Streamlit Dashboard for CCA Platform Performance Metrics
Displays user onboarding metrics from the backend API
"""

import streamlit as st
import requests
from datetime import datetime
import pandas as pd
import time

# Page configuration
st.set_page_config(
    page_title="CCA Platform Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling - Dark Mode Compatible
st.markdown("""
    <style>
    .main-header {
        font-size: 2.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
        padding: 1rem 0;
    }
    .stMetric {
        background: rgba(255, 255, 255, 0.05);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        transition: all 0.3s;
    }
    .stMetric:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 16px rgba(102, 126, 234, 0.3);
        border-color: rgba(102, 126, 234, 0.5);
    }
    .metric-label {
        font-size: 0.9rem;
        color: rgba(255, 255, 255, 0.7);
        font-weight: 600;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #fff;
    }
    .environment-badge {
        display: inline-block;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
        margin: 0.5rem 0;
    }
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(255, 255, 255, 0.05);
        padding: 0.5rem;
        border-radius: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
    }
    /* Dark theme adjustments */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #1e1e2e 0%, #2a2a3e 100%);
    }
    .stDataFrame {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 8px;
    }
    h1, h2, h3 {
        color: #fff !important;
    }
    </style>
""", unsafe_allow_html=True)

# API Endpoints
API_ENDPOINTS = {
    "Stage": "https://web.stage.apichicchic.com",
    "Production": "https://web.prod.apichicchic.com",
    "Local": "http://localhost:8000"
}

# Session state management
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'dashboard_api_key' not in st.session_state:
    st.session_state.dashboard_api_key = ""
if 'x_api_key' not in st.session_state:
    st.session_state.x_api_key = ""
if 'environment' not in st.session_state:
    st.session_state.environment = "Stage"
if 'data' not in st.session_state:
    st.session_state.data = None
if 'last_fetch' not in st.session_state:
    st.session_state.last_fetch = None


def authenticate():
    """Simple authentication using API key"""
    if not st.session_state.dashboard_api_key:
        st.error("⚠️ Please enter an API key")
        return False

    if not st.session_state.x_api_key:
        st.error("⚠️ Please enter an X-API-Key")
        return False
    return True


def fetch_data(api_url, dashboard_api_key, x_api_key):
    """Fetch data from the API"""
    try:
        # Construct the full URL
        full_url = f"{api_url}/v1/metrics/performance"
        params = {"secure_api_key": dashboard_api_key}
        headers = {
            "x-api-key": x_api_key,
            "content-type": "application/json",
            "accept": "application/json"
        }
        
        response = requests.get(full_url, params=params, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            # The response comes in a specific format, extract the payload
            if 'payload' in data:
                return data['payload']
            else:
                return data
        elif response.status_code == 401:
            st.error("🔐 Unauthorized: Invalid API key")
            return None
        else:
            st.error(f"❌ Error {response.status_code}: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Connection error: {str(e)}")
        return None


def display_overview_metrics(data):
    """Display overview metrics at the top"""
    user_data = data.get('user', {})
    
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="👥 Total Users",
            value=f"{user_data.get('total_count', 0):,}",
            delta=None
        )
    
    with col2:
        st.metric(
            label="✅ Active Users",
            value=f"{user_data.get('active_count', 0):,}",
            delta=None
        )
    
    with col3:
        st.metric(
            label="❌ Inactive Users",
            value=f"{user_data.get('inactive_count', 0):,}",
            delta=None
        )


def display_time_period_metrics(data, period_key, period_label):
    """Display metrics for a specific time period"""
    user_data = data.get('user', {})
    period_data = user_data.get(period_key, {})
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown(f"### {period_label}")
        count = period_data.get('count', 0)
        st.markdown(f"**Total New Users:** {count:,}")
        
        # Display breakdown
        types_data = user_data.get('types', {})
        breakdown = {}
        for user_type in ['customer', 'artist', 'business']:
            type_data = types_data.get(user_type, {})
            period_type_data = {}
            if period_key == 'new_users_24_hrs':
                period_type_data = type_data.get('new_24_hours', {})
            elif period_key == 'new_users_7_days':
                period_type_data = type_data.get('new_7_days', {})
            elif period_key == 'new_users_30_days':
                period_type_data = type_data.get('new_30_days', {})
            breakdown[user_type] = period_type_data.get('count', 0)
        
        # Display breakdown in expander
        with st.expander("View Breakdown"):
            st.write(f"**Customer:** {breakdown.get('customer', 0):,}")
            st.write(f"**Artist:** {breakdown.get('artist', 0):,}")
            st.write(f"**Business:** {breakdown.get('business', 0):,}")
    
    with col2:
        # Display preview table
        preview_data = period_data.get('preview', [])
        if preview_data:
            # Convert to DataFrame for better display
            df_data = []
            for item in preview_data:
                account_type = item.get('type', 'N/A')
                df_data.append({
                    'Type': account_type.replace('_ACCOUNT', '').title(),
                    'Display Name': item.get('display_name', 'N/A'),
                    'Account ID': item.get('account_id', 'N/A')[:8] + '...',
                    'Created': item.get('created', 'N/A')[:10] if item.get('created') != 'N/A' else 'N/A'
                })
            
            if df_data:
                df = pd.DataFrame(df_data)
                st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No recent users to display")


def display_metrics_by_type(data, user_type, label):
    """Display metrics for a specific user type"""
    user_data = data.get('user', {})
    types_data = user_data.get('types', {})
    type_data = types_data.get(user_type, {})
    
    st.markdown(f"### {label}")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        period_data = type_data.get('new_24_hours', {})
        count = period_data.get('count', 0)
        st.metric("24 Hours", f"{count:,}")
    
    with col2:
        period_data = type_data.get('new_7_days', {})
        count = period_data.get('count', 0)
        st.metric("7 Days", f"{count:,}")
    
    with col3:
        period_data = type_data.get('new_30_days', {})
        count = period_data.get('count', 0)
        st.metric("30 Days", f"{count:,}")
    
    # Show preview for 24 hours
    st.markdown("#### Recent 24 Hours")
    preview_data = type_data.get('new_24_hours', {}).get('preview', [])
    if preview_data:
        df_data = []
        for item in preview_data:
            df_data.append({
                'Display Name': item.get('display_name', 'N/A'),
                'Account ID': item.get('account_id', 'N/A')[:8] + '...',
                'Type': item.get('type', 'N/A'),
                'Created': item.get('created', 'N/A')[:10] if item.get('created') != 'N/A' else 'N/A'
            })
        
        if df_data:
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info(f"No {user_type} users in the last 24 hours")


def main():
    """Main dashboard function"""
    
    # Sidebar for authentication
    with st.sidebar:
        st.markdown("## 🔐 Authentication")
        st.markdown("---")
        
        # Environment selection
        st.markdown("### 🌍 Environment")
        environment = st.radio(
            "Select Environment",
            options=["Stage", "Production", "Local"],
            index=["Stage", "Production", "Local"].index(st.session_state.environment) if st.session_state.environment in ["Stage", "Production", "Local"] else 0,
            help="Choose the API environment"
        )
        st.session_state.environment = environment
        
        # Get the API URL based on selected environment
        api_url = API_ENDPOINTS.get(environment, "http://localhost:8000")
        
        # Display environment badge
        env_colors = {
            "Stage": "background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;",
            "Production": "background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white;",
            "Local": "background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white;"
        }
        current_style = env_colors.get(environment, env_colors.get("Stage"))
        st.markdown(
            f'<div class="environment-badge" style="{current_style}">{environment}</div>',
            unsafe_allow_html=True
        )
        
        st.markdown("---")
        st.markdown("### 🔑 API Credentials")
        
        dashboard_api_key = st.text_input(
            "Dashboard API Key",
            type="password",
            value=st.session_state.dashboard_api_key,
            help="Enter your secure API key to access the dashboard"
        )
        
        st.session_state.dashboard_api_key = dashboard_api_key
        
        x_api_key = st.text_input(
            "X-API-Key Header",
            type="password",
            value=st.session_state.x_api_key,
            help="Enter your X-API-Key header value"
        )
        
        st.session_state.x_api_key = x_api_key
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔓 Load Data", type="primary", use_container_width=True):
                if authenticate():
                    with st.spinner("Fetching data..."):
                        data = fetch_data(
                            api_url, 
                            st.session_state.dashboard_api_key, 
                            st.session_state.x_api_key
                        )
                        if data:
                            st.session_state.data = data
                            st.session_state.last_fetch = datetime.now()
                            st.session_state.authenticated = True
                            st.success("✅ Data loaded!")
                            time.sleep(1)
                            st.rerun()
        
        with col2:
            if st.button("🔄 Refresh", use_container_width=True):
                with st.spinner("Refreshing..."):
                    data = fetch_data(
                        api_url, 
                        st.session_state.dashboard_api_key, 
                        st.session_state.x_api_key
                    )
                    if data:
                        st.session_state.data = data
                        st.session_state.last_fetch = datetime.now()
                        st.success("✅ Refreshed!")
                        time.sleep(1)
                        st.rerun()
        
        if st.session_state.last_fetch:
            st.markdown(f"**Last Updated:** {st.session_state.last_fetch.strftime('%Y-%m-%d %H:%M:%S')}")
        
        st.markdown("---")
        st.markdown("### 📋 Quick Start")
        st.markdown("""
        <small style="color: rgba(255,255,255,0.7);">
        1. Select environment (Stage/Prod)<br>
        2. Enter API keys<br>
        3. Click "Load Data"<br>
        4. Explore metrics
        </small>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### ℹ️ About")
        st.markdown("""
        <small style="color: rgba(255,255,255,0.7);">
        This dashboard provides real-time insights into user onboarding and platform performance metrics.
        </small>
        """, unsafe_allow_html=True)
    
    # Main content
    st.markdown('<h1 class="main-header">📊 CCA Platform Dashboard</h1>', unsafe_allow_html=True)
    
    if not st.session_state.authenticated or not st.session_state.data:
        # Get the current API URL
        current_env = st.session_state.environment
        api_url = API_ENDPOINTS.get(current_env, "http://localhost:8000")
        
        col1, col2 = st.columns([1, 3])
        with col2:
            st.info("👈 **Please authenticate using the sidebar to view metrics**")
            st.markdown("---")
            
            st.markdown("""
            ### 📊 Dashboard Features:
            
            - **📈 Overview Metrics**: Total, active, and inactive user counts
            - **⏰ Time-based Analysis**: User signups for 24h, 7d, and 30d periods
            - **👥 User Type Breakdown**: Separate metrics for Customers, Artists, and Businesses
            - **👤 Recent Signups Preview**: Latest user registrations with details
            - **🔄 Live Updates**: Refresh data in real-time
            
            ### 🎯 Current Environment:
            """)
            
            env_colors = {
                "Stage": "🎨 Stage Environment",
                "Production": "🚀 Production Environment", 
                "Local": "💻 Local Environment"
            }
            
            st.success(f"**{env_colors.get(current_env, 'Stage')}**")
            st.caption(f"Endpoint: `{api_url}`")
        return
    
    data = st.session_state.data
    
    # Display Overview with environment badge
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("## 📈 Overview Metrics")
    with col2:
        env_colors = {
            "Stage": "background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 0.3rem 1rem; border-radius: 20px;",
            "Production": "background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 0.3rem 1rem; border-radius: 20px;",
            "Local": "background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; padding: 0.3rem 1rem; border-radius: 20px;"
        }
        # Get the style for current environment
        overview_style = env_colors.get(st.session_state.environment, env_colors.get("Stage"))
        st.markdown(
            f'<div style="{overview_style}; font-weight: 600;">{st.session_state.environment}</div>',
            unsafe_allow_html=True
        )
    
    display_overview_metrics(data)
    
    st.markdown("---")
    
    # Display Time Period Metrics
    st.markdown("## 📅 New User Signups by Time Period")
    
    tab1, tab2, tab3 = st.tabs(["🕐 Last 24 Hours", "📆 Last 7 Days", "📅 Last 30 Days"])
    
    with tab1:
        st.markdown("<br>", unsafe_allow_html=True)
        display_time_period_metrics(data, 'new_users_24_hrs', '🕐 Last 24 Hours')
    
    with tab2:
        st.markdown("<br>", unsafe_allow_html=True)
        display_time_period_metrics(data, 'new_users_7_days', '📆 Last 7 Days')
    
    with tab3:
        st.markdown("<br>", unsafe_allow_html=True)
        display_time_period_metrics(data, 'new_users_30_days', '📅 Last 30 Days')
    
    st.markdown("---")
    
    # Display Metrics by User Type
    st.markdown("## 👥 User Metrics by Type")
    
    type_tab1, type_tab2, type_tab3 = st.tabs(["👤 Customers", "🎨 Artists", "🏢 Businesses"])
    
    with type_tab1:
        st.markdown("<br>", unsafe_allow_html=True)
        display_metrics_by_type(data, 'customer', '👤 Customer Metrics')
    
    with type_tab2:
        st.markdown("<br>", unsafe_allow_html=True)
        display_metrics_by_type(data, 'artist', '🎨 Artist Metrics')
    
    with type_tab3:
        st.markdown("<br>", unsafe_allow_html=True)
        display_metrics_by_type(data, 'business', '🏢 Business Metrics')
    
    # Footer
    st.markdown("---")
    col1, col2 = st.columns([1, 3])
    with col2:
        st.markdown(
            "<div style='text-align: center; color: rgba(255,255,255,0.5); padding: 1rem;'>"
            "<small>© 2024 CCA Platform | Built with Streamlit ⚡</small>"
            "</div>",
            unsafe_allow_html=True
        )


if __name__ == "__main__":
    main()

