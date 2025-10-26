"""
Streamlit Dashboard for CCA Platform Performance Metrics
Displays user onboarding metrics from the backend API
"""
# pylint: disable=import-error

import streamlit as st  # type: ignore
import requests
from datetime import datetime
import pandas as pd  # type: ignore
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
    h1, h2, h3, h4 {
        color: #fff !important;
    }
    /* Info boxes styling */
    .stInfo {
        background: rgba(59, 130, 246, 0.1);
        border: 1px solid rgba(59, 130, 246, 0.3);
    }
    /* Table styling */
    [data-testid="stDataFrame"],
    [data-testid="stDataFrame"] > * {
        color: rgba(255, 255, 255, 0.9);
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
            label="❌ Deactivated Users",
            value=f"{user_data.get('inactive_count', 0):,}",
            delta=None
        )


def display_time_period_overview(data):
    """Display overview of all time periods broken down by user type"""
    user_data = data.get('user', {})
    types_data = user_data.get('types', {})
    
    # Period keys and labels
    periods = [
        ('new_24_hours', '🕐 Last 24 hours'),
        ('new_7_days', '📆 Last 7 days'),
        ('new_30_days', '📅 Last 30 days')
    ]
    
    type_info = [
        ('customer', '👥 Customers Onboarded'),
        ('artist', '👥 Artists Onboarded'),
        ('business', '👥 Businesses Onboarded')
    ]
    
    # Create layout for each time period
    for idx, (period_key, period_label) in enumerate(periods):
        st.markdown(f"### {period_label}")
        
        cols = st.columns(3)
        for type_idx, (user_type, type_label) in enumerate(type_info):
            with cols[type_idx]:
                type_data = types_data.get(user_type, {})
                period_data = type_data.get(period_key, {})
                count = period_data.get('count', 0)
                st.metric(type_label, f"{count:,}", delta=None)
        
        # Add spacing between periods
        if idx < len(periods) - 1:
            st.markdown("<br>", unsafe_allow_html=True)


def display_metrics_by_type(data, user_type, label):
    """Display metrics for a specific user type"""
    user_data = data.get('user', {})
    types_data = user_data.get('types', {})
    type_data = types_data.get(user_type, {})
    
    # Show preview tables for all time periods with metrics inline
    preview_tabs = st.tabs(["🕐 24 Hours", "📆 7 Days", "📅 30 Days"])
    
    with preview_tabs[0]:
        period_data = type_data.get('new_24_hours', {})
        count = period_data.get('count', 0)
        st.metric(f"📊 New {label} - 24 Hours", f"{count:,}", delta=None)
        
        preview_data = period_data.get('preview', [])
        if preview_data:
            df_data = []
            for item in preview_data:
                df_data.append({
                    'Display Name': item.get('display_name', 'N/A'),
                    'User ID': item.get('user_id', 'N/A')[:8] + '...' if len(item.get('user_id', '')) > 8 else item.get('user_id', 'N/A'),
                    'Created': item.get('created', 'N/A')[:10] if item.get('created') != 'N/A' else 'N/A'
                })
            
            if df_data:
                df = pd.DataFrame(df_data)
                st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info(f"No {label} users in the last 24 hours")
    
    with preview_tabs[1]:
        period_data = type_data.get('new_7_days', {})
        count = period_data.get('count', 0)
        st.metric(f"📊 New {label} - 7 Days", f"{count:,}", delta=None)
        
        preview_data = period_data.get('preview', [])
        if preview_data:
            df_data = []
            for item in preview_data:
                df_data.append({
                    'Display Name': item.get('display_name', 'N/A'),
                    'User ID': item.get('user_id', 'N/A')[:8] + '...' if len(item.get('user_id', '')) > 8 else item.get('user_id', 'N/A'),
                    'Created': item.get('created', 'N/A')[:10] if item.get('created') != 'N/A' else 'N/A'
                })
            
            if df_data:
                df = pd.DataFrame(df_data)
                st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info(f"No {label} users in the last 7 days")
    
    with preview_tabs[2]:
        period_data = type_data.get('new_30_days', {})
        count = period_data.get('count', 0)
        st.metric(f"📊 New {label} - 30 Days", f"{count:,}", delta=None)
        
        preview_data = period_data.get('preview', [])
        if preview_data:
            df_data = []
            for item in preview_data:
                occupation = item.get('occupation', '') if item.get('occupation') else ''
                slug = item.get('slug', '') if item.get('slug') else ''
                
                df_data.append({
                    'Display Name': item.get('display_name', 'N/A'),
                    'User ID': item.get('user_id', 'N/A')[:8] + '...' if len(item.get('user_id', '')) > 8 else item.get('user_id', 'N/A'),
                    'Created': item.get('created', 'N/A')[:10] if item.get('created') != 'N/A' else 'N/A',
                    'Occupation': occupation if occupation else 'N/A',
                    'Slug': slug if slug else 'N/A'
                })
            
            if df_data:
                df = pd.DataFrame(df_data)
                st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info(f"No {label} users in the last 30 days")


def display_country_insights(data):
    """Display country-based insights from user.by_country."""
    user_data = data.get('user', {})
    by_country = user_data.get('by_country') or data.get('by_country') or {}

    st.markdown("## 🌍 Country Insights")

    if not by_country:
        st.info("No country-based insights available")
        return

    # Aggregate summary metrics
    countries = list(by_country.keys())
    total_new_last_30d = 0
    for country_code, country_info in by_country.items():
        total_new_last_30d += country_info.get('total_last_30_days', 0) or 0

    c1, c2 = st.columns(2)
    with c1:
        st.metric("🌐 Countries represented (last 30d)", f"{len(countries):,}")
    with c2:
        st.metric("🆕 New users last 30d (all countries)", f"{total_new_last_30d:,}")

    # Bar chart: new users last 30 days by country
    rows = []
    for country_code, country_info in by_country.items():
        rows.append({
            'Country': country_code,
            'New Users (30d)': country_info.get('total_last_30_days', 0) or 0
        })
    if rows:
        df_by_country = pd.DataFrame(rows).sort_values('New Users (30d)', ascending=False)
        st.bar_chart(df_by_country.set_index('Country'))

    # Breakdown table by type per country
    breakdown_rows = []
    for country_code, country_info in by_country.items():
        customer = (country_info.get('customer') or {}).get('count', 0) or 0
        artist = (country_info.get('artist') or {}).get('count', 0) or 0
        business = (country_info.get('business') or {}).get('count', 0) or 0
        breakdown_rows.append({
            'Country': country_code,
            'Customers (30d)': customer,
            'Artists (30d)': artist,
            'Businesses (30d)': business,
            'Total (30d)': customer + artist + business
        })
    if breakdown_rows:
        df_breakdown = pd.DataFrame(breakdown_rows).sort_values('Total (30d)', ascending=False)
        st.dataframe(df_breakdown, use_container_width=True, hide_index=True)

    # Map of recent signups (uses preview lat/lon when present)
    points = []
    for country_code, country_info in by_country.items():
        for user_type in ['customer', 'artist', 'business']:
            previews = (country_info.get(user_type) or {}).get('preview') or []
            for item in previews:
                lat = item.get('latitude')
                lon = item.get('longitude')
                if lat is not None and lon is not None:
                    points.append({
                        'lat': lat,
                        'lon': lon,
                        'Country': country_code,
                        'Type': user_type.capitalize(),
                        'Name': item.get('display_name', 'N/A'),
                        'Created': (item.get('created') or '')[:19]
                    })
    if points:
        st.markdown("### 🗺️ Recent signups map (last 30d)")
        df_points = pd.DataFrame(points)
        st.map(df_points[['lat', 'lon']])


def display_booking_insights(data):
    """Display booking insights for the last 30 days."""
    booking = data.get('booking', {})
    last_30 = booking.get('last_30_days', {})
    insights = last_30.get('insights', {})
    preview = last_30.get('preview') or []

    st.markdown("## 🧾 Booking Insights")

    if not last_30:
        st.info("No booking data available")
        return

    total = insights.get('total_last_30d', len(preview) if isinstance(preview, list) else 0) or 0
    by_status = insights.get('by_status') or {}
    total_revenue = insights.get('total_revenue_30d')
    avg_value = insights.get('avg_booking_value')

    # Identify currency context from preview if consistent
    currencies = sorted({item.get('currency') for item in preview if item.get('currency')})
    currency_label = currencies[0] if len(currencies) == 1 else None

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("🧾 Total bookings (30d)", f"{total:,}")
    with m2:
        completed = by_status.get('COMPLETED', 0) or 0
        st.metric("✅ Completed", f"{completed:,}")
    with m3:
        booked = by_status.get('BOOKED', 0) or 0
        st.metric("🗓️ Booked", f"{booked:,}")
    with m4:
        if total_revenue is not None:
            prefix = f"{currency_label} " if currency_label else ""
            st.metric("💰 Revenue (30d)", f"{prefix}{total_revenue:,.2f}")

    # Average value metric
    if avg_value is not None:
        prefix = f"{currency_label} " if currency_label else ""
        st.metric("💳 Avg booking value", f"{prefix}{avg_value:,.2f}")

    # Status breakdown chart
    if by_status:
        status_rows = [{'Status': k, 'Count': v or 0} for k, v in by_status.items()]
        df_status = pd.DataFrame(status_rows).sort_values('Count', ascending=False)
        st.bar_chart(df_status.set_index('Status'))

    # Bookings per day (by from_time)
    if preview:
        daily_counts = {}
        for item in preview:
            dt = item.get('from_time') or item.get('created')
            if dt:
                day = dt[:10]
                daily_counts[day] = daily_counts.get(day, 0) + 1
        if daily_counts:
            df_daily = pd.DataFrame(sorted(daily_counts.items()), columns=['Date', 'Bookings']).set_index('Date')
            st.line_chart(df_daily)

    # Top service providers by revenue (from preview)
    if preview:
        provider_rev = {}
        for item in preview:
            provider = item.get('service_provider_name') or 'Unknown'
            price = item.get('total_price') or 0
            provider_rev[provider] = provider_rev.get(provider, 0) + price
        if provider_rev:
            top_rows = sorted(provider_rev.items(), key=lambda x: x[1], reverse=True)[:5]
            df_top = pd.DataFrame(top_rows, columns=['Service Provider', 'Revenue']).set_index('Service Provider')
            st.markdown("### 🏆 Top service providers (by revenue)")
            st.bar_chart(df_top)

    # Preview table
    if preview:
        table_rows = []
        for item in preview:
            table_rows.append({
                'Booking ID': (item.get('booking_id') or '')[:8] + '...' if item.get('booking_id') else 'N/A',
                'Status': item.get('status', 'N/A'),
                'Type': item.get('type', 'N/A'),
                'Total Price': item.get('total_price', 0),
                'Currency': item.get('currency', ''),
                'From': (item.get('from_time') or '')[:19],
                'To': (item.get('to_time') or '')[:19],
                'Customer': item.get('customer_name', 'N/A'),
                'Provider': item.get('service_provider_name', 'N/A')
            })
        df_preview = pd.DataFrame(table_rows)
        st.dataframe(df_preview, use_container_width=True, hide_index=True)

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
    st.markdown("## 📈 Time Periods")
    display_time_period_overview(data)
    
    st.markdown("---")
    
    # Display Metrics by User Type
    st.markdown("## 👥 User Metrics by Type")
    
    type_tab1, type_tab2, type_tab3 = st.tabs(["👤 Customers", "🎨 Artists", "🏢 Businesses"])
    
    with type_tab1:
        display_metrics_by_type(data, 'customer', 'Customers')
    
    with type_tab2:
        display_metrics_by_type(data, 'artist', 'Artists')
    
    with type_tab3:
        display_metrics_by_type(data, 'business', 'Businesses')
    
    st.markdown("---")
    # Country insights
    display_country_insights(data)

    st.markdown("---")
    # Booking insights
    display_booking_insights(data)

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

