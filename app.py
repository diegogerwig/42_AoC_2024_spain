import streamlit as st
import pandas as pd
from src.app_utils import *
from src.app_operations import *
from src.app_visualization import *
from src.app_predictions import *
import logging

from analytics.analytics_logger import AnalyticsLogger
analytics = AnalyticsLogger()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def init_session_state(df):
    """Initialize session state with default values"""
    if 'reset_counter' not in st.session_state:
        st.session_state.reset_counter = 0
        
    if 'filter_state' not in st.session_state:
        st.session_state.filter_state = get_default_filter_state(df)

def get_default_filter_state(df):
    """Get default filter state values"""
    return {
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


def apply_filters(df):
    """Apply user-selected filters to the dataframe"""
    init_session_state(df)
    
    st.sidebar.header("🎯 Filters")
    
    # Reset filters button
    if st.sidebar.button("🔄 Reset Filters", key=f'reset_button_{st.session_state.reset_counter}'):
        st.session_state.reset_counter += 1
        st.session_state.filter_state = get_default_filter_state(df)
        st.rerun()
    
    # Campus filter
    campus_options = ["All"] + sorted(df["campus"].unique().tolist())
    st.session_state.filter_state['campus'] = st.sidebar.selectbox(
        "📍 Select Campus", 
        campus_options,
        key=f'campus_select_{st.session_state.reset_counter}',
        index=campus_options.index(st.session_state.filter_state['campus'])
    )
    
    # Points range filter
    st.session_state.filter_state['points_range'] = st.sidebar.slider(
        "🎮 Points Range",
        min_value=float(df["points"].min()),
        max_value=float(df["points"].max()),
        value=st.session_state.filter_state['points_range'],
        key=f'points_slider_{st.session_state.reset_counter}'
    )
    
    # Star filters
    st.session_state.filter_state['gold_range'] = st.sidebar.slider(
        "⭐ Gold Stars",
        min_value=int(df["gold_stars"].min()),
        max_value=int(df["gold_stars"].max()),
        value=st.session_state.filter_state['gold_range'],
        key=f'gold_slider_{st.session_state.reset_counter}'
    )
    
    st.session_state.filter_state['silver_range'] = st.sidebar.slider(
        "🌟 Silver Stars",
        min_value=int(df["silver_stars"].min()),
        max_value=int(df["silver_stars"].max()),
        value=st.session_state.filter_state['silver_range'],
        key=f'silver_slider_{st.session_state.reset_counter}'
    )

    # Streak filter
    st.session_state.filter_state['streak_range'] = st.sidebar.slider(
        "🔥 Streak Range",
        min_value=int(df["streak"].min()),
        max_value=int(df["streak"].max()),
        value=st.session_state.filter_state['streak_range'],
        key=f'streak_slider_{st.session_state.reset_counter}'
    )

    # Completed days filter
    st.session_state.filter_state['days_range'] = st.sidebar.slider(
        "📅 Days Completed",
        min_value=int(df["completed_days"].min()),
        max_value=int(df["completed_days"].max()),
        value=st.session_state.filter_state['days_range'],
        key=f'days_slider_{st.session_state.reset_counter}'
    )

    # Search by login
    st.session_state.filter_state['search_login'] = st.sidebar.text_input(
        "🔍 Search by Login",
        value=st.session_state.filter_state['search_login'],
        key=f'search_input_{st.session_state.reset_counter}'
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
        key=f'sort_select_{st.session_state.reset_counter}',
        index=["Points", "Gold Stars", "Silver Stars", "Total Stars", "Streak", "Days Completed"].index(st.session_state.filter_state['sort_by'])
    )
    
    st.session_state.filter_state['sort_order'] = st.sidebar.radio(
        "Order", 
        ["Descending", "Ascending"],
        key=f'sort_order_{st.session_state.reset_counter}',
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


def display_prediction_tables(filtered_df):
    """Display prediction and model metrics tables with consistent styling"""
    
    # Define common table styles
    table_styles = [
        {'selector': 'table', 'props': [
            ('width', '100%'),
            ('border-collapse', 'collapse'),
            ('margin', '0px'),
            ('table-layout', 'fixed')
        ]},
        {'selector': 'th', 'props': [
            ('background-color', '#2E2E2E'),
            ('color', '#AAAAAA'),
            ('font-weight', 'normal'),
            ('padding', '12px 8px'),
            ('font-size', '0.9em'),
            ('text-align', 'center'),
            ('vertical-align', 'middle'),
            ('border', '1px solid #333')
        ]},
        {'selector': 'td', 'props': [
            ('background-color', '#1E1E1E'),
            ('color', 'white'),
            ('padding', '8px'),
            ('text-align', 'center'),
            ('vertical-align', 'middle'),
            ('border', '1px solid #333'),
            ('white-space', 'nowrap')
        ]},
        # Specific width for each column in prediction metrics
        {'selector': 'td:nth-child(1), th:nth-child(1)', 'props': [('width', '15%')]},  # Campus
        {'selector': 'td:nth-child(2), th:nth-child(2)', 'props': [('width', '15%')]},  # Active/Total
        {'selector': 'td:nth-child(3), th:nth-child(3)', 'props': [('width', '15%')]},  # Current Rate
        {'selector': 'td:nth-child(4), th:nth-child(4)', 'props': [('width', '15%')]},  # Stars
        {'selector': 'td:nth-child(5), th:nth-child(5)', 'props': [('width', '15%')]},  # Today Stars
        {'selector': 'td:nth-child(6), th:nth-child(6)', 'props': [('width', '12%')]},  # Projection
        {'selector': 'td:nth-child(7), th:nth-child(7)', 'props': [('width', '13%')]},  # Trend
    ]

    # Get prediction metrics
    prediction_metrics = create_prediction_metrics(filtered_df)
    if not prediction_metrics.empty:
        st.markdown("### 📊 Prediction Metrics")
        st.markdown(
            prediction_metrics.style
            .set_table_styles(table_styles)
            .hide(axis="index")
            .to_html(escape=False),
            unsafe_allow_html=True
        )

    # Adjust styles for model metrics table (fewer columns)
    model_table_styles = table_styles.copy()
    model_table_styles.extend([
        {'selector': 'td:nth-child(1), th:nth-child(1)', 'props': [('width', '20%')]},  # Campus
        {'selector': 'td:nth-child(2), th:nth-child(2)', 'props': [('width', '20%')]},  # R² Score
        {'selector': 'td:nth-child(3), th:nth-child(3)', 'props': [('width', '20%')]},  # RMSE
        {'selector': 'td:nth-child(4), th:nth-child(4)', 'props': [('width', '20%')]},  # MAE
        {'selector': 'td:nth-child(5), th:nth-child(5)', 'props': [('width', '20%')]},  # Part. Rate
    ])

    # Get model metrics
    model_metrics = create_model_metrics(filtered_df)
    if not model_metrics.empty:
        st.markdown("### 🔬 Model Evaluation Metrics")
        st.markdown(
            model_metrics.style
            .set_table_styles(model_table_styles)
            .hide(axis="index")
            .to_html(escape=False),
            unsafe_allow_html=True
        )


def main():
    # Inicializa el analytics
    analytics = AnalyticsLogger()
    
    # Registra la vista de página
    analytics.log_event('page_view', 'main')

    suppress_plotly_warnings()
    st.set_page_config(page_title="🎄 42 Spain AoC 2024", layout="wide")
    
    st.title("💫 42 Spain  | 🎄Advent of Code 2024 Dashboard")
    
    try:
        df = load_data()

        init_session_state(df)
        if 'filter_state' in st.session_state:
            analytics.log_event('filter', ('campus', st.session_state.filter_state['campus']))
            analytics.log_event('filter', ('points_range', st.session_state.filter_state['points_range']))
            analytics.log_event('filter', ('search_login', st.session_state.filter_state['search_login']))
        
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
                    font-size: 1.6rem !important;
                    font-weight: bold !important;
                }
                button[data-baseweb="tab"] p {
                    font-size: 1.6rem !important;
                    font-weight: bold !important;
                }
            </style>
        """, unsafe_allow_html=True)


        # Performance Metrics Table
        st.markdown("---")
        st.subheader("📊 Performance Metrics")

        # Combine global and campus metrics
        global_df = create_metrics_dataframe(filtered_df, is_global=True)
        campus_df = create_metrics_dataframe(filtered_df, is_global=False)
        metrics_df = pd.concat([global_df, campus_df], ignore_index=True)

        # Define table styles once
        table_styles = [
            # Base table style
            {'selector': 'table', 'props': [
                ('width', '100%'),
                ('border-collapse', 'collapse'),
                ('margin', '0px'),
                ('table-layout', 'fixed')
            ]},
            # Header cells
            {'selector': 'th', 'props': [
                ('background-color', '#2E2E2E'),
                ('color', '#AAAAAA'),
                ('font-weight', 'normal'),
                ('padding', '12px 8px'),
                ('font-size', '0.9em'),
                ('text-align', 'center'),
                ('vertical-align', 'middle'),
                ('border', '1px solid #333'),
                ('line-height', '1.2'),
                ('white-space', 'normal')
            ]},
            # Data cells
            {'selector': 'td', 'props': [
                ('background-color', '#1E1E1E'),
                ('color', 'white'),
                ('padding', '8px'),
                ('text-align', 'center'),
                ('vertical-align', 'middle'),
                ('border', '1px solid #333'),
                ('white-space', 'nowrap')
            ]},
            # First row (Global)
            {'selector': 'tr:first-child td', 'props': [
                ('background-color', '#2E2E2E'),
                ('font-weight', 'bold')
            ]},
            # Column widths
            {'selector': 'td:nth-child(1), th:nth-child(1)', 'props': [('width', '16%')]},  # Section
            {'selector': 'td:nth-child(2), th:nth-child(2)', 'props': [('width', '14%')]},  # Students
            {'selector': 'td:nth-child(3), th:nth-child(3)', 'props': [('width', '12%')]},  # Participation
            {'selector': 'td:nth-child(4), th:nth-child(4)', 'props': [('width', '14%')]},  # Points
            {'selector': 'td:nth-child(5), th:nth-child(5)', 'props': [('width', '14%')]},  # Streak
            {'selector': 'td:nth-child(6), th:nth-child(6)', 'props': [('width', '14%')]},  # Stars
            {'selector': 'td:nth-child(7), th:nth-child(7)', 'props': [('width', '16%')]},  # Success Rate
            # First column alignment
            {'selector': 'td:first-child, th:first-child', 'props': [
                ('text-align', 'left'),
                ('padding-left', '15px')
            ]}
        ]

        # Display styled table
        st.markdown(
            metrics_df.style
            .set_table_styles(table_styles)
            .hide(axis="index")
            .to_html(escape=False),
            unsafe_allow_html=True
        )


        # Top 5 Ranking Table
        st.markdown("---")
        st.subheader("🏆 Top 5 Ranking")

        # Prepare ranking data
        top_points = filtered_df['points'].unique()[:5]
        ranking_data = []

        for i, points in enumerate(top_points, 1):
            students = filtered_df[filtered_df['points'] == points]
            
            colored_logins = [
                f'<span style="color: {CAMPUS_COLORS[row["campus"]]}">{row["login"]}</span>'
                for _, row in students.iterrows()
            ]
            
            first_student = students.iloc[0]
            
            ranking_data.append({
                'Rank': f'<div style="text-align: center">{i}</div>',
                'Points': f'<div style="text-align: center">{points:.1f}</div>',
                'Gold Stars': f'<div style="text-align: center">{first_student["gold_stars"]}</div>',
                'Silver Stars': f'<div style="text-align: center">{first_student["silver_stars"]}</div>',
                'Streak': f'<div style="text-align: center">{first_student["streak"]}</div>',
                'Number of Students': f'<div style="text-align: center">{len(students)}</div>',
                'BCN Students': f'<div style="text-align: center">{len(students.loc[students["campus"] == "BCN"])}</div>',
                'MAD Students': f'<div style="text-align: center">{len(students.loc[students["campus"] == "MAD"])}</div>',
                'MAL Students': f'<div style="text-align: center">{len(students.loc[students["campus"] == "MAL"])}</div>',
                'UDZ Students': f'<div style="text-align: center">{len(students.loc[students["campus"] == "UDZ"])}</div>',
                'Students': '  ||  '.join(colored_logins),
            })

        ranking_df = pd.DataFrame(ranking_data)

        st.markdown(
            ranking_df.style
            .set_table_styles([
                {'selector': 'th', 'props': [
                    ('background-color', '#2E2E2E'),
                    ('color', '#AAAAAA'),
                    ('font-weight', 'normal'),
                    ('padding', '8px'),
                    ('font-size', '0.9em'),
                    ('text-align', 'center'),
                    ('vertical-align', 'middle')
                ]},
                {'selector': 'td', 'props': [
                    ('background-color', '#1E1E1E'),
                    ('color', 'white'),
                    ('padding', '8px'),
                    ('text-align', 'center'),
                    ('vertical-align', 'middle')
                ]},
                {'selector': 'td:nth-child(3)', 'props': [
                    ('text-align', 'left'),
                    ('padding-left', '15px')
                ]},
                {'selector': 'td:first-child', 'props': [
                    ('font-weight', 'bold'),
                    ('font-size', '1.2em'),
                    ('width', '5%')
                ]},
                {'selector': 'td:nth-child(1)', 'props': [('width', '6%')]},
                {'selector': 'td:nth-child(2)', 'props': [('width', '6%')]},
                {'selector': 'td:nth-child(3)', 'props': [('width', '6%')]},
                {'selector': 'td:nth-child(4)', 'props': [('width', '6%')]},
                {'selector': 'td:nth-child(5)', 'props': [('width', '6%')]},
                {'selector': 'td:nth-child(6)', 'props': [('width', '6%')]},
                {'selector': 'td:nth-child(7)', 'props': [('width', '4%')]},
                {'selector': 'td:nth-child(8)', 'props': [('width', '4%')]},
                {'selector': 'td:nth-child(9)', 'props': [('width', '4%')]},
                {'selector': 'td:nth-child(10)', 'props': [('width', '4%')]},
                {'selector': 'td:nth-child(11)', 'props': [('width', '40%')]}
            ])
            .hide(axis="index")
            .to_html(escape=False),
            unsafe_allow_html=True
        )


        # Visualizations
        st.markdown("---")
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Campus Comparison", "🌟 Progress Tracking", "📈 Star Analysis", "🔮 Predictions"])
        
        with tab1:
            col1, col2 = st.columns(2)
            with col2:
                st.plotly_chart(plot_campus_progress(filtered_df), use_container_width=True)
            with col1:
                st.plotly_chart(plot_points_distribution(filtered_df), use_container_width=True)
        
        with tab2:
            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(plot_success_rate(filtered_df), use_container_width=True)
            with col2:
                st.plotly_chart(plot_points_vs_days(filtered_df), use_container_width=True)

        with tab3:
            col1, col2 = st.columns(2)
            with col2:
                st.plotly_chart(plot_stars_distribution(filtered_df), use_container_width=True)
            with col1:
                st.plotly_chart(plot_star_totals_by_campus(filtered_df), use_container_width=True)
        
        with tab4:
            st.subheader("🔮 ML Predictions by Campus")
            
            display_prediction_tables(filtered_df)

            # Display prediction metrics
            st.markdown("### 📊 Prediction Metrics")
            prediction_metrics = create_prediction_metrics(filtered_df)
            # st.dataframe(prediction_metrics, use_container_width=True)

            # Display model metrics
            st.markdown("### 🔬 Model Evaluation Metrics")
            model_metrics = create_model_metrics(filtered_df)
            # st.dataframe(model_metrics, use_container_width=True)
            
            # Display prediction visualization
            st.markdown("### 📈 Current vs Predicted Points")
            st.plotly_chart(plot_predictions(filtered_df), use_container_width=True)

            # Add explanation
            st.markdown("""
            **About these predictions:**
            * Predictions are based on the success rate of active users
            * The model uses linear regression on the last 5 days to identify recent trends
            * Success rate = (obtained stars) / (possible stars from active users) × 100
            * Model quality metrics:
                * R² Score: How well the model fits the data (closer to 1 is better)
                * RMSE: Average prediction error in percentage points
                * MAE: Average absolute error in percentage points
            * Each active user can earn up to 2 stars per day 
            * Projections follow current trends but actual results may vary
            """)
        
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
            <style>
                .custom-link {
                    color: #fff; 
                    text-decoration: none; 
                }
                .custom-link img {
                    background: transparent; 
                    vertical-align: middle; 
                    padding-right: 4px; 
                }
            </style>
            <div style="text-align: center; font-size: 1.1em; padding: 8px; background-color: #333; color: #fff; border-radius: 4px;">
                Developed by 
                <a href="https://github.com/diegogerwig" target="_blank" class="custom-link">
                    <img src="https://github.com/fluidicon.png" height="16"/>Diego Gerwig
                </a> |
                <a href="https://profile.intra.42.fr/users/dgerwig-" target="_blank" class="custom-link">
                    <img src="https://logowik.com/content/uploads/images/423918.logowik.com.webp" height="16"/>dgerwig-
                </a> | 
                <span style="color: #fff;">2024</span>
            </div>
            """,
            unsafe_allow_html=True
        )

    except Exception as e:
        analytics.log_event('error', str(e))
        st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()