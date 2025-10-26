"""
Customer Dashboard - Streamlit App
This dashboard shows the number of customers joining our platform.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

# Page configuration
st.set_page_config(
    page_title="Customer Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title and description
st.title("📊 Customer Growth Dashboard")
st.markdown("Track the growth of customers joining our platform")

# Load data
@st.cache_data
def load_data():
    """Load customer data from CSV file"""
    data_path = os.path.join(os.path.dirname(__file__), 'data', 'customers.csv')
    df = pd.read_csv(data_path)
    df['date'] = pd.to_datetime(df['date'])
    return df

try:
    df = load_data()
    
    # Sidebar filters
    st.sidebar.header("Filters")
    
    # Date range filter
    min_date = df['date'].min()
    max_date = df['date'].max()
    
    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # Plan filter
    plans = ['All'] + sorted(df['plan'].unique().tolist())
    selected_plan = st.sidebar.selectbox("Select Plan", plans)
    
    # Filter data
    if len(date_range) == 2:
        mask = (df['date'] >= pd.to_datetime(date_range[0])) & (df['date'] <= pd.to_datetime(date_range[1]))
        filtered_df = df[mask]
    else:
        filtered_df = df
    
    if selected_plan != 'All':
        filtered_df = filtered_df[filtered_df['plan'] == selected_plan]
    
    # Key metrics
    st.header("Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Customers",
            value=len(filtered_df),
            delta=f"{len(filtered_df) - len(df) if selected_plan != 'All' else len(filtered_df)}"
        )
    
    with col2:
        # Calculate average customers per month
        if len(filtered_df) > 0:
            months = (filtered_df['date'].max() - filtered_df['date'].min()).days / 30.44
            avg_per_month = len(filtered_df) / months if months > 0 else len(filtered_df)
            st.metric(
                label="Avg Customers/Month",
                value=f"{avg_per_month:.1f}"
            )
        else:
            st.metric(label="Avg Customers/Month", value="0")
    
    with col3:
        # Count by plan
        plan_counts = filtered_df['plan'].value_counts()
        most_popular_plan = plan_counts.index[0] if len(plan_counts) > 0 else "N/A"
        st.metric(
            label="Most Popular Plan",
            value=most_popular_plan
        )
    
    with col4:
        # Latest customer
        if len(filtered_df) > 0:
            latest_customer = filtered_df.sort_values('date', ascending=False).iloc[0]
            days_ago = (datetime.now() - latest_customer['date']).days
            st.metric(
                label="Latest Customer",
                value=latest_customer['customer_name'],
                delta=f"{days_ago} days ago"
            )
        else:
            st.metric(label="Latest Customer", value="N/A")
    
    # Cumulative customer growth chart
    st.header("Customer Growth Over Time")
    
    # Prepare cumulative data
    growth_df = filtered_df.sort_values('date').copy()
    growth_df['cumulative_customers'] = range(1, len(growth_df) + 1)
    
    # Create line chart
    fig_growth = px.line(
        growth_df,
        x='date',
        y='cumulative_customers',
        title='Cumulative Customer Growth',
        labels={'cumulative_customers': 'Total Customers', 'date': 'Date'},
        template='plotly_white'
    )
    
    fig_growth.update_traces(line_color='#1f77b4', line_width=3)
    fig_growth.update_layout(
        hovermode='x unified',
        height=400
    )
    
    st.plotly_chart(fig_growth, use_container_width=True)
    
    # Two column layout for additional charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Customers by Plan")
        plan_distribution = filtered_df['plan'].value_counts().reset_index()
        plan_distribution.columns = ['plan', 'count']
        
        fig_plan = px.pie(
            plan_distribution,
            values='count',
            names='plan',
            title='Distribution by Plan Type',
            template='plotly_white',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        
        fig_plan.update_traces(textposition='inside', textinfo='percent+label')
        fig_plan.update_layout(height=400)
        
        st.plotly_chart(fig_plan, use_container_width=True)
    
    with col2:
        st.subheader("Monthly Signups")
        
        # Group by month
        monthly_df = filtered_df.copy()
        monthly_df['month'] = monthly_df['date'].dt.to_period('M').astype(str)
        monthly_signups = monthly_df.groupby('month').size().reset_index(name='signups')
        
        fig_monthly = px.bar(
            monthly_signups,
            x='month',
            y='signups',
            title='Customer Signups by Month',
            labels={'signups': 'Number of Signups', 'month': 'Month'},
            template='plotly_white',
            color='signups',
            color_continuous_scale='Blues'
        )
        
        fig_monthly.update_layout(
            showlegend=False,
            height=400
        )
        
        st.plotly_chart(fig_monthly, use_container_width=True)
    
    # Customer data table
    st.header("Customer Details")
    
    # Display options
    show_table = st.checkbox("Show customer data table", value=False)
    
    if show_table:
        # Format the dataframe for display
        display_df = filtered_df.sort_values('date', ascending=False).copy()
        display_df['date'] = display_df['date'].dt.strftime('%Y-%m-%d')
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "customer_id": "ID",
                "customer_name": "Name",
                "email": "Email",
                "plan": "Plan",
                "date": "Join Date"
            }
        )
        
        # Download button
        csv = display_df.to_csv(index=False)
        st.download_button(
            label="Download Customer Data",
            data=csv,
            file_name=f"customers_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

except FileNotFoundError:
    st.error("⚠️ Customer data file not found. Please ensure 'data/customers.csv' exists.")
except Exception as e:
    st.error(f"⚠️ An error occurred: {str(e)}")
    st.exception(e)

# Footer
st.markdown("---")
st.markdown("*Dashboard last updated: {}*".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
