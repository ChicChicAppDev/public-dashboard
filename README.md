# CCA Platform Performance Dashboard

A Streamlit-based dashboard for viewing real-time performance metrics from the CCA Platform backend.

## Features

- 📊 **Overview Metrics**: Total, active, and inactive user counts
- 📅 **Time Period Analysis**: New signups in the last 24 hours, 7 days, and 30 days
- 👥 **User Type Breakdown**: Metrics for Customers, Artists, and Business accounts
- 🔄 **Live Data**: Real-time updates from the backend API
- 🔐 **Secure Authentication**: API key-based access control

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Running the Dashboard

1. Start the Streamlit app:
```bash
streamlit run app.py
```

2. The dashboard will open in your browser at `http://localhost:8501`

## Configuration

### Authentication

- Enter your secure API key in the sidebar
- Update the API base URL if your backend is running on a different host/port
- Default API URL: `http://localhost:8000`

### API Endpoint

The dashboard connects to:
```
GET {API_URL}/web/v1/metrics/performance
```

Query Parameters:
- `secure_api_key`: Your authentication token

## Usage

1. **Load Data**: Click the "Load Data" button in the sidebar after entering your API key
2. **Refresh**: Use the "Refresh" button to update the metrics with the latest data
3. **Explore Metrics**: Navigate through different tabs to view:
   - Overview metrics
   - New signups by time period
   - User metrics by type

## Dashboard Sections

### Overview
- Total Users count
- Active Users count
- Inactive Users count

### Time Period Metrics
- Last 24 Hours: Recent signups with breakdown
- Last 7 Days: Weekly user growth
- Last 30 Days: Monthly user trends

### User Type Breakdown
- Customer metrics
- Artist metrics
- Business metrics
- Recent user previews

## Development

To run in development mode with auto-reload:

```bash
streamlit run app.py --server.runOnSave true
```

## Requirements

- Python 3.8+
- Streamlit 1.32.0+
- Pandas 2.0.0+
- Requests 2.32.0+

## Deployment

This dashboard can be deployed to:
- Streamlit Cloud
- Docker container
- Kubernetes cluster
- Any platform supporting Streamlit

For production deployment, ensure:
- Environment variables for configuration
- Secure API key management
- SSL/TLS encryption
- Rate limiting considerations

## License

© 2024 CCA Platform
