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

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stMetric {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .metric-label {
        font-size: 0.85rem;
        color: #666;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: bold;
        color: #1f77b4;
    }
    </style>
""", unsafe_allow_html=True)

# Session state management
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'dashboard_api_key' not in st.session_state:
    st.session_state.dashboard_api_key = ""
if 'x-api-key' not in st.session_state:
    st.session_state.x-api-key = ""
if 'api_url' not in st.session_state:
    st.session_state.api_url = "http://localhost:8000"
if 'data' not in st.session_state:
    st.session_state.data = None
if 'last_fetch' not in st.session_state:
    st.session_state.last_fetch = None


def authenticate():
    """Simple authentication using API key"""
    if not st.session_state.dashboard_api_key:
        st.error("⚠️ Please enter an API key")
        return False

    if not st.session_state.x-api-key:
        st.error("⚠️ Please enter an X-API-Key")
        return False
    return True


def fetch_data(api_url, api_key):
    """Fetch data from the API"""
    try:
        # Construct the full URL
        full_url = f"{api_url}/v1/metrics/performance"
        params = {"secure_api_key": dashboard_api_key}
        headers = {"x-api-key": x-api-key,
                   "content-type": "application/json",
                   "accept": "application/json"}
        
        response = requests.get(full_url, params=params, headers=headers, timeout=10)
        
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
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Total Users",
            value=f"{user_data.get('total_count', 0):,}",
            delta=None
        )
    
    with col2:
        st.metric(
            label="Active Users",
            value=f"{user_data.get('active_count', 0):,}",
            delta=None
        )
    
    with col3:
        st.metric(
            label="Inactive Users",
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
                user_info = item.get('user', {})
                account_type = item.get('account_type', 'N/A')
                df_data.append({
                    'Type': account_type.replace('_account', '').title(),
                    'Username': user_info.get('username', 'N/A'),
                    'Email': user_info.get('email', 'N/A'),
                    'First Name': user_info.get('first_name', 'N/A'),
                    'Last Name': user_info.get('last_name', 'N/A'),
                    'Created': item.get('created', 'N/A')
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
            user_info = item.get('user', {})
            df_data.append({
                'Username': user_info.get('username', 'N/A'),
                'Email': user_info.get('email', 'N/A'),
                'First Name': user_info.get('first_name', 'N/A'),
                'Last Name': user_info.get('last_name', 'N/A'),
                'Created': item.get('created', 'N/A')
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
        
        api_key = st.text_input(
            "Enter API Key",
            type="password",
            value=st.session_state.api_key,
            help="Enter your secure API key to access the dashboard"
        )
        
        st.session_state.api_key = api_key
        
        # API URL configuration
        api_url = st.text_input(
            "API Base URL",
            value=st.session_state.api_url,
            help="Backend API base URL (e.g., http://localhost:8000)"
        )
        st.session_state.api_url = api_url
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔓 Load Data", type="primary", use_container_width=True):
                if authenticate():
                    with st.spinner("Fetching data..."):
                        data = fetch_data(st.session_state.api_url, st.session_state.api_key)
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
                    data = fetch_data(st.session_state.api_url, st.session_state.api_key)
                    if data:
                        st.session_state.data = data
                        st.session_state.last_fetch = datetime.now()
                        st.success("✅ Refreshed!")
                        time.sleep(1)
                        st.rerun()
        
        if st.session_state.last_fetch:
            st.markdown(f"**Last Updated:** {st.session_state.last_fetch.strftime('%Y-%m-%d %H:%M:%S')}")
        
        st.markdown("---")
        st.markdown("### 📋 Instructions")
        st.markdown("""
        1. Enter your secure API key
        2. Update API URL if needed
        3. Click "Load Data" button
        4. View metrics below
        """)
    
    # Main content
    st.markdown('<h1 class="main-header">📊 CCA Platform Performance Dashboard</h1>', unsafe_allow_html=True)
    
    if not st.session_state.authenticated or not st.session_state.data:
        st.info("👈 Please authenticate using the sidebar to view metrics")
        st.markdown("---")
        st.markdown("""
        ### What this dashboard shows:
        - **Total Users**: Complete user count across all types
        - **Active/Inactive Users**: User status breakdown
        - **New Signups**: Recent user registrations by time period
        - **User Types**: Breakdown by Customer, Artist, and Business accounts
        - **Recent Users**: Preview of latest signups with details
        """)
        return
    
    data = st.session_state.data
    
    # Display Overview
    st.markdown("## 📈 Overview")
    display_overview_metrics(data)
    
    st.markdown("---")
    
    # Display Time Period Metrics
    st.markdown("## 📅 New User Signups by Time Period")
    
    tab1, tab2, tab3 = st.tabs(["🕐 Last 24 Hours", "📆 Last 7 Days", "📅 Last 30 Days"])
    
    with tab1:
        display_time_period_metrics(data, 'new_users_24_hrs', '🕐 Last 24 Hours')
    
    with tab2:
        display_time_period_metrics(data, 'new_users_7_days', '📆 Last 7 Days')
    
    with tab3:
        display_time_period_metrics(data, 'new_users_30_days', '📅 Last 30 Days')
    
    st.markdown("---")
    
    # Display Metrics by User Type
    st.markdown("## 👥 User Metrics by Type")
    
    type_tab1, type_tab2, type_tab3 = st.tabs(["👤 Customers", "🎨 Artists", "🏢 Businesses"])
    
    with type_tab1:
        display_metrics_by_type(data, 'customer', '👤 Customer Metrics')
    
    with type_tab2:
        display_metrics_by_type(data, 'artist', '🎨 Artist Metrics')
    
    with type_tab3:
        display_metrics_by_type(data, 'business', '🏢 Business Metrics')
    
    # Footer
    st.markdown("---")
    st.markdown(
        f"<div style='text-align: center; color: #666; padding: 1rem;'>"
        f"© 2024 CCA Platform | Built with Streamlit"
        f"</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()

