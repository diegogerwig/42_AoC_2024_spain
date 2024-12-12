import streamlit as st
from datetime import datetime
import time
import json

# Initialize session state for enhanced analytics
if 'analytics' not in st.session_state:
    st.session_state.analytics = {
        'session_start': time.time(),
        'page_views': {},
        'button_clicks': {},
        'time_per_page': {},
        'last_page': None,
        'last_page_time': time.time()
    }

def track_interaction(action_type, action_name):
    """Track any user interaction"""
    current_time = time.time()
    
    # Update page timing if changing pages
    if action_type == 'page_view':
        if st.session_state.analytics['last_page']:
            last_page = st.session_state.analytics['last_page']
            time_spent = current_time - st.session_state.analytics['last_page_time']
            
            if last_page not in st.session_state.analytics['time_per_page']:
                st.session_state.analytics['time_per_page'][last_page] = []
            
            st.session_state.analytics['time_per_page'][last_page].append(time_spent)
        
        st.session_state.analytics['last_page'] = action_name
        st.session_state.analytics['last_page_time'] = current_time

    # Track page views
    if action_type == 'page_view':
        if action_name not in st.session_state.analytics['page_views']:
            st.session_state.analytics['page_views'][action_name] = 0
        st.session_state.analytics['page_views'][action_name] += 1

    # Track button clicks
    elif action_type == 'button_click':
        if action_name not in st.session_state.analytics['button_clicks']:
            st.session_state.analytics['button_clicks'][action_name] = 0
        st.session_state.analytics['button_clicks'][action_name] += 1

def show_enhanced_analytics():
    """Display detailed analytics dashboard"""
    st.sidebar.title("📊 Enhanced Analytics")
    
    # Session Duration
    current_duration = time.time() - st.session_state.analytics['session_start']
    st.sidebar.metric("Session Duration", f"{int(current_duration/60)}m {int(current_duration%60)}s")

    # Page Views
    st.sidebar.subheader("Page Views")
    for page, count in st.session_state.analytics['page_views'].items():
        st.sidebar.text(f"{page}: {count} views")

    # Average Time per Page
    st.sidebar.subheader("Avg Time per Page")
    for page, times in st.session_state.analytics['time_per_page'].items():
        avg_time = sum(times) / len(times)
        st.sidebar.text(f"{page}: {int(avg_time)}s")

    # Button Interactions
    if st.session_state.analytics['button_clicks']:
        st.sidebar.subheader("Button Clicks")
        for button, count in st.session_state.analytics['button_clicks'].items():
            st.sidebar.text(f"{button}: {count} clicks")

def main():
    # Track page view for main page
    track_interaction('page_view', 'main')
    
    # Your existing app code here
    st.title("42 Spain - AoC 2024")
    
    # Example navigation
    pages = ["Home", "Problems", "Leaderboard"]
    selected_page = st.selectbox("Navigation", pages)
    track_interaction('page_view', selected_page)
    
    # Example interaction tracking
    if st.button("Submit Solution"):
        track_interaction('button_click', 'submit_solution')
        st.success("Solution submitted!")
    
    # Show analytics in sidebar
    show_enhanced_analytics()

if __name__ == "__main__":
    main()