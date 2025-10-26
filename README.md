# Customer Growth Dashboard 📊

A Streamlit-based dashboard application for tracking and visualizing customer growth on our platform.

## Features

- **Real-time Metrics**: Track total customers, average monthly signups, most popular plan, and latest customer
- **Interactive Visualizations**:
  - Cumulative customer growth over time (line chart)
  - Customer distribution by plan type (pie chart)
  - Monthly signup trends (bar chart)
- **Advanced Filtering**: Filter data by date range and subscription plan
- **Data Export**: Download customer data as CSV
- **Responsive Design**: Works on desktop and mobile devices

## Installation

1. Clone the repository:
```bash
git clone https://github.com/ChicChicAppDev/public-dashboard.git
cd public-dashboard
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the Streamlit dashboard:
```bash
streamlit run app.py
```

The dashboard will open in your default web browser at `http://localhost:8501`

## Data

Sample customer data is stored in `data/customers.csv`. The CSV file contains:
- `date`: Customer join date
- `customer_id`: Unique customer identifier
- `customer_name`: Customer name
- `email`: Customer email address
- `plan`: Subscription plan (Basic, Premium, or Enterprise)

To use your own data, replace the `data/customers.csv` file with your customer data following the same format.

## Dashboard Sections

### Key Metrics
- **Total Customers**: Current number of customers
- **Avg Customers/Month**: Average customer acquisition rate
- **Most Popular Plan**: Most subscribed plan type
- **Latest Customer**: Most recent customer signup

### Customer Growth Over Time
Interactive line chart showing cumulative customer growth

### Customers by Plan
Pie chart displaying the distribution of customers across different plans

### Monthly Signups
Bar chart showing customer acquisition trends by month

### Customer Details
Optional data table with download functionality for detailed customer information

## Technology Stack

- **Streamlit**: Web application framework
- **Pandas**: Data manipulation and analysis
- **Plotly**: Interactive visualizations

## License

This project is open source and available under the MIT License.