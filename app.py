import streamlit as st
import pandas as pd
from src.data_processing import (
    load_data,
    create_metrics_dataframe,
    plot_stars_distribution,
    plot_completion_heatmap,
    plot_completion_rate,
    plot_points_vs_days,
    plot_campus_progress,
    plot_points_distribution
)
from src.utils import suppress_plotly_warnings

def apply_filters(df):
    """Apply user-selected filters to the dataframe"""
    # Initialize session state for filters if not exists
    if 'filter_state' not in st.session_state:
        st.session_state.filter_state = {
            'campus': "All",
            'points_range': (float(df["points"].min()), float(df["points"].max())),
            'gold_range': (int(df["gold_stars"].min()), int(df["gold_stars"].max())),
            'silver_range': (int(df["silver_stars"].min()), int(df["silver_stars"].max())),
            'streak_range': (int(df["streak"].min()), int(df["streak"].max())),
            'days_range': (int(df["completed_days"].min()), int(df["completed_days"].max())),
            'search_login': "",
            'sort_by': "Points",
            'sort_order': "Descending"
        }

    st.sidebar.header("🎯 Filters")
    
    # Reset filters button
    if st.sidebar.button("🔄 Reset Filters"):
        st.session_state.filter_state = {
            'campus': "All",
            'points_range': (float(df["points"].min()), float(df["points"].max())),
            'gold_range': (int(df["gold_stars"].min()), int(df["gold_stars"].max())),
            'silver_range': (int(df["silver_stars"].min()), int(df["silver_stars"].max())),
            'streak_range': (int(df["streak"].min()), int(df["streak"].max())),
            'days_range': (int(df["completed_days"].min()), int(df["completed_days"].max())),
            'search_login': "",
            'sort_by': "Points",
            'sort_order': "Descending"
        }
        st.experimental_rerun()

    # Campus filter
    campus_options = ["All"] + sorted(df["campus"].unique().tolist())
    st.session_state.filter_state['campus'] = st.sidebar.selectbox(
        "📍 Select Campus", 
        campus_options,
        key='campus_select',
        index=campus_options.index(st.session_state.filter_state['campus'])
    )
    
    # Points range filter
    st.session_state.filter_state['points_range'] = st.sidebar.slider(
        "🎮 Points Range",
        min_value=float(df["points"].min()),
        max_value=float(df["points"].max()),
        value=st.session_state.filter_state['points_range'],
        key='points_slider'
    )
    
    # Star filters
    st.session_state.filter_state['gold_range'] = st.sidebar.slider(
        "⭐ Gold Stars",
        min_value=int(df["gold_stars"].min()),
        max_value=int(df["gold_stars"].max()),
        value=st.session_state.filter_state['gold_range'],
        key='gold_slider'
    )
    
    st.session_state.filter_state['silver_range'] = st.sidebar.slider(
        "🌟 Silver Stars",
        min_value=int(df["silver_stars"].min()),
        max_value=int(df["silver_stars"].max()),
        value=st.session_state.filter_state['silver_range'],
        key='silver_slider'
    )

    # Streak filter
    st.session_state.filter_state['streak_range'] = st.sidebar.slider(
        "🔥 Streak Range",
        min_value=int(df["streak"].min()),
        max_value=int(df["streak"].max()),
        value=st.session_state.filter_state['streak_range'],
        key='streak_slider'
    )

    # Completed days filter
    st.session_state.filter_state['days_range'] = st.sidebar.slider(
        "📅 Days Completed",
        min_value=int(df["completed_days"].min()),
        max_value=int(df["completed_days"].max()),
        value=st.session_state.filter_state['days_range'],
        key='days_slider'
    )

    # Search by login
    st.session_state.filter_state['search_login'] = st.sidebar.text_input(
        "🔍 Search by Login",
        value=st.session_state.filter_state['search_login'],
        key='search_input'
    ).strip().lower()

    # Apply filters
    mask = (
        (df["points"].between(st.session_state.filter_state['points_range'][0], 
                            st.session_state.filter_state['points_range'][1])) &
        (df["streak"].between(st.session_state.filter_state['streak_range'][0], 
                            st.session_state.filter_state['streak_range'][1])) &
        (df["completed_days"].between(st.session_state.filter_state['days_range'][0], 
                                    st.session_state.filter_state['days_range'][1])) &
        (df["gold_stars"].between(st.session_state.filter_state['gold_range'][0], 
                                st.session_state.filter_state['gold_range'][1])) &
        (df["silver_stars"].between(st.session_state.filter_state['silver_range'][0], 
                                  st.session_state.filter_state['silver_range'][1]))
    )
    
    if st.session_state.filter_state['campus'] != "All":
        mask = mask & (df["campus"] == st.session_state.filter_state['campus'])
    
    if st.session_state.filter_state['search_login']:
        mask = mask & (df["login"].str.lower().str.contains(st.session_state.filter_state['search_login']))
    
    filtered_df = df[mask].copy()
    
    # Sort options
    st.sidebar.subheader("📊 Sort Options")
    st.session_state.filter_state['sort_by'] = st.sidebar.selectbox(
        "Sort by",
        ["Points", "Gold Stars", "Silver Stars", "Total Stars", "Streak", "Days Completed"],
        key='sort_select',
        index=["Points", "Gold Stars", "Silver Stars", "Total Stars", "Streak", "Days Completed"].index(st.session_state.filter_state['sort_by'])
    )
    
    st.session_state.filter_state['sort_order'] = st.sidebar.radio(
        "Order", 
        ["Descending", "Ascending"],
        key='sort_order',
        index=["Descending", "Ascending"].index(st.session_state.filter_state['sort_order'])
    )
    
    # Apply sorting
    sort_column = st.session_state.filter_state['sort_by'].lower().replace(" ", "_")
    ascending = st.session_state.filter_state['sort_order'] == "Ascending"
    filtered_df = filtered_df.sort_values(sort_column, ascending=ascending).reset_index(drop=True)

    # Filter summary
    st.sidebar.markdown("---")
    st.sidebar.subheader("📈 Filter Summary")
    st.sidebar.write(f"Showing {len(filtered_df)} of {len(df)} participants")
    
    return filtered_df

def main():
    suppress_plotly_warnings()
    st.set_page_config(page_title="🎄 42 Spain AoC 2024", layout="wide")
    
    st.title("💫 42 Spain | 🎄Advent of Code 2024 Dashboard")
    
    try:
        df = load_data()
        filtered_df = apply_filters(df)

        # Table styling
        st.markdown("""
            <style>
                /* Base table style */
                div[data-testid="stTable"] table {
                    width: 100%;
                    table-layout: fixed;
                    border-collapse: collapse;
                }
                
                /* Header cells */
                div[data-testid="stTable"] th {
                    background-color: #2E2E2E;
                    color: #AAAAAA;
                    font-weight: normal;
                    padding: 8px;
                    font-size: 0.9em;
                    text-align: center !important;
                    vertical-align: middle;
                }
                
                /* All data cells */
                div[data-testid="stTable"] td {
                    background-color: #1E1E1E;
                    color: white;
                    padding: 8px;
                    text-align: center !important;
                    vertical-align: middle;
                }
                
                /* Global metrics row */
                div[data-testid="stTable"] tr:first-child td {
                    background-color: #2E2E2E;
                    font-weight: bold;
                }
                
                /* Section column (first column) */
                div[data-testid="stTable"] td:first-child,
                div[data-testid="stTable"] th:first-child {
                    text-align: left !important;
                    width: 15%;
                    padding-left: 15px;
                }
                
                /* Column-specific widths */
                div[data-testid="stTable"] td:nth-child(2),
                div[data-testid="stTable"] th:nth-child(2) {
                    width: 10%;  /* Students */
                }
                
                div[data-testid="stTable"] td:nth-child(3),
                div[data-testid="stTable"] th:nth-child(3) {
                    width: 20%;  /* Points */
                }
                
                div[data-testid="stTable"] td:nth-child(4),
                div[data-testid="stTable"] th:nth-child(4) {
                    width: 20%;  /* Streak */
                }
                
                div[data-testid="stTable"] td:nth-child(5),
                div[data-testid="stTable"] th:nth-child(5) {
                    width: 20%;  /* Stars */
                }
                
                div[data-testid="stTable"] td:nth-child(6),
                div[data-testid="stTable"] th:nth-child(6) {
                    width: 15%;  /* Completion */
                }

                /* Force center alignment for all cells except first column */
                div[data-testid="stTable"] td:not(:first-child),
                div[data-testid="stTable"] th:not(:first-child) {
                    text-align: center !important;
                    display: table-cell;
                    vertical-align: middle;
                    line-height: normal;
                    white-space: nowrap;
                }

                /* Tab styling */
                button[data-baseweb="tab"] {
                    font-size: 1.2rem !important;
                    font-weight: bold !important;
                }
                button[data-baseweb="tab"] p {
                    font-size: 1.2rem !important;
                }
            </style>
        """, unsafe_allow_html=True)

        # Performance Metrics Table
        st.subheader("📊 Performance Metrics")
        
        # Combine global and campus metrics
        global_df = create_metrics_dataframe(filtered_df, is_global=True)
        campus_df = create_metrics_dataframe(filtered_df, is_global=False)
        metrics_df = pd.concat([global_df, campus_df], ignore_index=True)
        
        # Display combined table
        st.table(metrics_df.set_index('Section'))

        # Visualizations
        st.markdown("---")
        tab1, tab2, tab3 = st.tabs(["📈 Star Analysis", "🌟 Progress Tracking", "📊 Campus Comparison"])
        
        with tab1:
            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(plot_stars_distribution(filtered_df), use_container_width=True)
            with col2:
                st.plotly_chart(plot_completion_heatmap(filtered_df), use_container_width=True)
        
        with tab2:
            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(plot_completion_rate(filtered_df), use_container_width=True)
            with col2:
                st.plotly_chart(plot_points_vs_days(filtered_df), use_container_width=True)
        
        with tab3:
            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(plot_campus_progress(filtered_df), use_container_width=True)
            with col2:
                st.plotly_chart(plot_points_distribution(filtered_df), use_container_width=True)
        
        # Detailed Data
        st.markdown("---")
        st.subheader("🔍 Detailed Data")
        st.dataframe(
            filtered_df,
            use_container_width=True,  
        )

        # Footer
        st.markdown(
            """
            ---
            <div style="text-align: center; font-size: 1.1em; padding: 8px; background-color: #333; color: #fff; border-radius: 4px;">
                Developed by <a href="https://github.com/diegogerwig" target="_blank" style="color: #fff;"><img src="https://github.com/fluidicon.png" height="16" style="vertical-align:middle; padding-right: 4px;"/>Diego Gerwig</a> |
                <a href="https://profile.intra.42.fr/users/dgerwig-" target="_blank" style="color: #fff;"><img src="https://logowik.com/content/uploads/images/423918.logowik.com.webp" height="16" style="vertical-align:middle; padding-right: 4px;"/>dgerwig-</a> | 2024
            </div>
            """,
            unsafe_allow_html=True
        )

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()