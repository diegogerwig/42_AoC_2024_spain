# analytics/analytics_viewer.py
import streamlit as st
import json
import pandas as pd
import plotly.express as px
from pathlib import Path
from datetime import datetime

def load_analytics_data():
    """Load analytics data from file"""
    data_file = Path('analytics/analytics_data/analytics_data.json')
    if data_file.exists():
        with open(data_file, 'r') as f:
            return json.load(f)
    return None

def show_analytics_dashboard():
    """Display analytics dashboard"""
    st.set_page_config(page_title="Analytics Dashboard", layout="wide")
    st.title("📊 Analytics Dashboard")
    
    data = load_analytics_data()
    if not data:
        st.error("No analytics data found")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Page Views
        st.header("📈 Page Views")
        if data.get('page_views'):
            fig = px.bar(
                x=list(data['page_views'].keys()),
                y=list(data['page_views'].values()),
                title="Page Views Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No page views data available")
        
        # Button Clicks
        st.header("🖱️ Button Interactions")
        if data.get('button_clicks'):
            fig = px.bar(
                x=list(data['button_clicks'].keys()),
                y=list(data['button_clicks'].values()),
                title="Button Click Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No button clicks data available")
    
    with col2:
        # Filter Usage
        st.header("🔍 Filter Usage")
        if data.get('filter_usage'):
            for filter_name, usages in data['filter_usage'].items():
                if usages:
                    st.subheader(f"{filter_name} Filter Usage")
                    df = pd.DataFrame(usages)
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
                    st.line_chart(df.set_index('timestamp')['value'])
        else:
            st.info("No filter usage data available")
    
    # Search Queries
    st.header("🔎 Recent Searches")
    if data.get('search_queries'):
        searches_df = pd.DataFrame(data['search_queries'])
        searches_df['timestamp'] = pd.to_datetime(searches_df['timestamp'])
        st.dataframe(
            searches_df.sort_values('timestamp', ascending=False)
            .head(10)
        )
    else:
        st.info("No search queries data available")
    
    # Errors
    st.header("⚠️ Error Log")
    if data.get('errors'):
        errors_df = pd.DataFrame(data['errors'])
        errors_df['timestamp'] = pd.to_datetime(errors_df['timestamp'])
        st.dataframe(
            errors_df.sort_values('timestamp', ascending=False)
        )
    else:
        st.info("No errors logged")

if __name__ == "__main__":
    show_analytics_dashboard()