import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.scraper import AOCScraper

# Define campus color mapping
CAMPUS_COLORS = {
    'UDZ': '#00FF00',  # Green
    'BCN': '#FFD700',  # Yellow
    'MAL': '#00FFFF',  # Cyan
    'MAD': '#FF00FF'   # Magenta
}

def load_data():
    """Load and cache data from scraper silently"""
    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def _load():
        import sys
        import io
        
        # Temporarily redirect stdout to capture scraper output
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        
        try:
            scraper = AOCScraper()
            df = scraper.scrape_data()
            
            # Reset stdout
            sys.stdout = old_stdout
            
            return df.sort_values('points', ascending=False).reset_index(drop=True)
        except Exception as e:
            # Reset stdout even if there's an error
            sys.stdout = old_stdout
            raise e
    
    return _load()

def get_campus_metrics(df):
    """Calculate metrics for each campus"""
    campus_metrics = {}
    
    for campus in sorted(df['campus'].unique()):
        campus_data = df[df['campus'] == campus]
        metrics = {
            'Students': len(campus_data),
            'Avg Points': f"{campus_data['points'].mean():.1f}",
            'Max Points': f"{campus_data['points'].max():.1f}",
            'Avg Streak': f"{campus_data['streak'].mean():.1f}",
            'Max Streak': int(campus_data['streak'].max()),
            'Total Gold': int(campus_data['gold_stars'].sum()),
            'Total Silver': int(campus_data['silver_stars'].sum()),
            'Completion Rate': f"{(campus_data['total_stars'].sum() / (len(campus_data) * 50)) * 100:.1f}%"
        }
        campus_metrics[campus] = metrics
    
    return campus_metrics

def plot_stars_distribution(df):
    """Plot distribution of gold and silver stars"""
    melted_df = pd.melt(
        df,
        value_vars=['gold_stars', 'silver_stars'],
        var_name='star_type',
        value_name='count'
    )
    
    fig = px.box(
        melted_df,
        x='star_type',
        y='count',
        color='star_type',
        points='all',
        color_discrete_map={
            'gold_stars': '#FFD700',
            'silver_stars': '#C0C0C0'
        },
        title='Stars Distribution'
    )
    
    fig.update_layout(height=500, title_x=0.5)
    return fig

def plot_completion_heatmap(df):
    """Create challenge completion heatmap"""
    day_columns = [col for col in df.columns if col.startswith('day_')]
    completion_matrix = df[day_columns].values
    
    fig = go.Figure(data=go.Heatmap(
        z=completion_matrix.T,
        colorscale=[
            [0, 'white'],
            [0.5, '#C0C0C0'],
            [1, '#FFD700']
        ],
        zmin=0,
        zmax=2
    ))
    
    fig.update_layout(
        title='Challenge Completion Status',
        title_x=0.5,
        xaxis_title='Participant Index',
        yaxis_title='Day',
        height=500
    )
    return fig

def plot_completion_rate(df):
    """Plot completion rate over time by campus"""
    day_columns = [col for col in df.columns if col.startswith('day_')]
    completion_data = []
    
    for campus in df['campus'].unique():
        campus_data = df[df['campus'] == campus]
        for day in day_columns:
            day_num = int(day.split('_')[1])
            completion = (campus_data[day] > 0).sum() / len(campus_data) * 100
            completion_data.append({
                'Day': day_num,
                'Rate': completion,
                'Campus': campus
            })
    
    completion_df = pd.DataFrame(completion_data)
    
    fig = px.line(
        completion_df,
        x='Day',
        y='Rate',
        color='Campus',
        title='Daily Completion Rate by Campus',
        labels={'Rate': 'Completion Rate (%)'},
        color_discrete_map=CAMPUS_COLORS
    )
    
    fig.update_layout(height=500, title_x=0.5)
    return fig

def plot_points_vs_days(df):
    """Create scatter plot of points vs completed days"""
    fig = px.scatter(
        df,
        x="completed_days",
        y="points",
        color="campus",
        size="total_stars",
        hover_data=["login"],
        title="Points vs Days Completed",
        color_discrete_map=CAMPUS_COLORS
    )
    
    fig.update_layout(height=500, title_x=0.5)
    return fig

def plot_campus_progress(df):
    """Create radar chart of campus performance"""
    campus_stats = df.groupby('campus').agg({
        'points': 'mean',
        'streak': 'mean',
        'completed_days': 'mean',
        'gold_stars': 'mean',
        'silver_stars': 'mean'
    }).round(2)
    
    fig = go.Figure()
    
    for campus in campus_stats.index:
        fig.add_trace(go.Scatterpolar(
            r=campus_stats.loc[campus],
            theta=campus_stats.columns,
            name=campus,
            line_color=CAMPUS_COLORS.get(campus, '#808080')
        ))
    
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, showticklabels=True)),
        showlegend=True,
        title='Campus Performance Overview',
        height=500,
        title_x=0.5
    )
    return fig

def plot_points_distribution(df):
    """Create box plot of points distribution by campus"""
    fig = px.box(
        df,
        x="campus",
        y="points",
        color="campus",
        points="all",
        title="Points Distribution by Campus",
        color_discrete_map=CAMPUS_COLORS
    )
    
    fig.add_hline(
        y=df['points'].median(),
        line_dash="dash",
        line_color="gray",
        annotation_text=f"Global Median: {df['points'].median():.1f}"
    )
    
    fig.update_layout(height=500, title_x=0.5, showlegend=False)
    return fig

def apply_filters(df):
    """Apply user-selected filters to the dataframe"""
    st.sidebar.header("🎯 Filters")
    
    # Campus filter
    campus_options = ["All"] + sorted(df["campus"].unique().tolist())
    selected_campus = st.sidebar.selectbox("📍 Select Campus", campus_options)
    
    # Points range filter
    points_range = st.sidebar.slider(
        "🎮 Points Range",
        min_value=float(df["points"].min()),
        max_value=float(df["points"].max()),
        value=(float(df["points"].min()), float(df["points"].max()))
    )
    
    # Star filters
    gold_range = st.sidebar.slider(
        "⭐ Gold Stars",
        min_value=int(df["gold_stars"].min()),
        max_value=int(df["gold_stars"].max()),
        value=(int(df["gold_stars"].min()), int(df["gold_stars"].max()))
    )
    
    silver_range = st.sidebar.slider(
        "🌟 Silver Stars",
        min_value=int(df["silver_stars"].min()),
        max_value=int(df["silver_stars"].max()),
        value=(int(df["silver_stars"].min()), int(df["silver_stars"].max()))
    )

    # Streak filter
    streak_range = st.sidebar.slider(
        "🔥 Streak Range",
        min_value=int(df["streak"].min()),
        max_value=int(df["streak"].max()),
        value=(int(df["streak"].min()), int(df["streak"].max()))
    )

    # Completed days filter
    days_range = st.sidebar.slider(
        "📅 Days Completed",
        min_value=int(df["completed_days"].min()),
        max_value=int(df["completed_days"].max()),
        value=(int(df["completed_days"].min()), int(df["completed_days"].max()))
    )

    # Search by login
    search_login = st.sidebar.text_input("🔍 Search by Login").strip().lower()

    # Apply filters
    mask = (
        (df["points"].between(points_range[0], points_range[1])) &
        (df["streak"].between(streak_range[0], streak_range[1])) &
        (df["completed_days"].between(days_range[0], days_range[1])) &
        (df["gold_stars"].between(gold_range[0], gold_range[1])) &
        (df["silver_stars"].between(silver_range[0], silver_range[1]))
    )
    
    if selected_campus != "All":
        mask = mask & (df["campus"] == selected_campus)
    
    if search_login:
        mask = mask & (df["login"].str.lower().str.contains(search_login))
    
    filtered_df = df[mask].copy()
    
    # Sort options
    st.sidebar.subheader("📊 Sort Options")
    sort_by = st.sidebar.selectbox(
        "Sort by",
        ["Points", "Gold Stars", "Silver Stars", "Total Stars", "Streak", "Days Completed"]
    )
    sort_order = st.sidebar.radio("Order", ["Descending", "Ascending"])
    
    # Apply sorting
    sort_column = sort_by.lower().replace(" ", "_")
    ascending = sort_order == "Ascending"
    filtered_df = filtered_df.sort_values(sort_column, ascending=ascending).reset_index(drop=True)

    # Filter summary
    st.sidebar.markdown("---")
    st.sidebar.subheader("📈 Filter Summary")
    st.sidebar.write(f"Showing {len(filtered_df)} of {len(df)} participants")
    
    # Reset filters button
    if st.sidebar.button("🔄 Reset Filters"):
        st.rerun()
    
    return filtered_df


def main():
    st.set_page_config(page_title="42 Spain AoC 2024 Dashboard", layout="wide")
    
    # Simple header
    st.title("💫 42 Spain Advent of Code 2024 Dashboard")
    
    try:
        df = load_data()
        filtered_df = apply_filters(df)
        
        # Global and Campus Metrics Section
        st.markdown("---")
        st.markdown("""
            <style>
                /* Container styles */
                div[data-testid="metric-container"] {
                    background-color: #1E1E1E;
                    border: 1px solid #333333;
                    border-radius: 5px;
                    color: #FFFFFF;
                    margin: 1px;
                    height: 50px;  /* Reduced height slightly */
                    display: flex;
                    flex-direction: column;
                }
                
                /* Metric value styles */
                div[data-testid="metric-container"] div[data-testid="metric-value"] {
                    color: #FFFFFF;
                    font-size: 1rem;
                    text-align: center;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    height: 30px;  /* Fixed height for values */
                }
                
                /* Column header styles */
                div.metric-header {
                    color: #CCCCCC;
                    font-size: 0.8rem;  /* Increased size for column headers */
                    text-align: center;
                    padding: 2px 0;
                    height: 20px;  /* Fixed height for headers */
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
                
                /* Campus header styles */
                div.campus-header {
                    background-color: #2E2E2E;
                    padding: 1px 8px;  /* Reduced vertical padding */
                    border-radius: 5px;
                    margin: 2px 0px;  /* Reduced margin */
                    border-left: 5px solid;
                    height: 24px;  /* Fixed height for campus headers */
                    display: flex;
                    align-items: center;
                }
                
                /* Campus header text */
                div.campus-header h2, div.campus-header h3 {
                    font-size: 1.1rem;  /* Increased size for campus names */
                    margin: 0;
                    padding: 0;
                }

                /* Global metrics header */
                div.campus-header h2 {
                    font-size: 1rem;  /* Slightly smaller than campus names */
                }
                
                /* Hide delta values */
                div[data-testid="metric-container"] div[data-testid="metric-delta"] {
                    display: none !important;
                }

                /* Ensure content stays within bounds */
                div[data-testid="metric-container"] > div {
                    overflow: hidden;
                    white-space: nowrap;
                    text-overflow: ellipsis;
                }
            </style>
        """, unsafe_allow_html=True)

        # Global Metrics Header
        st.markdown('<div class="campus-header" style="border-left-color: #FFD700;"><h2 style="color: white;">🌍 Global Metrics</h2></div>', unsafe_allow_html=True)

        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.markdown('<div class="metric-header">Total Participants</div>', unsafe_allow_html=True)
            st.metric("Total Participants", len(filtered_df), label_visibility="hidden")

        with col2:
            st.markdown('<div class="metric-header">Average Points</div>', unsafe_allow_html=True)
            st.metric("Average Points", f"{filtered_df['points'].mean():.1f}", label_visibility="hidden")

        with col3:
            st.markdown('<div class="metric-header">Gold Stars</div>', unsafe_allow_html=True)
            st.metric("Gold Stars", int(filtered_df['gold_stars'].sum()), label_visibility="hidden")

        with col4:
            st.markdown('<div class="metric-header">Silver Stars</div>', unsafe_allow_html=True)
            st.metric("Silver Stars", int(filtered_df['silver_stars'].sum()), label_visibility="hidden")

        with col5:
            st.markdown('<div class="metric-header">Completion Rate</div>', unsafe_allow_html=True)
            completion_rate = (filtered_df['total_stars'].sum() / (len(filtered_df) * 50)) * 100
            st.metric("Completion Rate", f"{completion_rate:.1f}%", label_visibility="hidden")

                
        # Campus metrics with styled headers
        campus_metrics = get_campus_metrics(filtered_df)
        
        # Define campus colors
        campus_colors = {
            'UDZ': '#00FF00',  # Green
            'BCN': '#FFD700',  # Yellow
            'MAL': '#00FFFF',  # Cyan
            'MAD': '#FF00FF'   # Magenta
        }
        
        for campus in campus_metrics:
            st.markdown(f"""
                <div class="campus-header" style="border-left-color: {campus_colors.get(campus, '#FFFFFF')};">
                    <h3 style="color: white;">🏛️ {campus} Campus</h3>
                </div>
            """, unsafe_allow_html=True)
            
            metrics = campus_metrics[campus]
            cols = st.columns(5)
            
            with cols[0]:
                st.markdown('<div class="metric-header">Students</div>', unsafe_allow_html=True)
                st.metric("Students", metrics['Students'], label_visibility="hidden")
            with cols[1]:
                st.markdown('<div class="metric-header">Points (Avg/Max)</div>', unsafe_allow_html=True)
                st.metric("Points", f"{metrics['Avg Points']}/{metrics['Max Points']}", label_visibility="hidden")
            with cols[2]:
                st.markdown('<div class="metric-header">Streak (Avg/Max)</div>', unsafe_allow_html=True)
                st.metric("Streak", f"{metrics['Avg Streak']}/{metrics['Max Streak']}", label_visibility="hidden")
            with cols[3]:
                st.markdown('<div class="metric-header">Stars (Gold/Silver)</div>', unsafe_allow_html=True)
                st.metric("Stars", f"{metrics['Total Gold']}/{metrics['Total Silver']}", label_visibility="hidden")
            with cols[4]:
                st.markdown('<div class="metric-header">Completion Rate</div>', unsafe_allow_html=True)
                st.metric("Completion Rate", metrics['Completion Rate'], label_visibility="hidden")
        
        st.markdown("---")
        tab1, tab2, tab3 = st.tabs(["📈 Star Analysis", "🌟 Progress Tracking", "📊 Campus Comparison"])
        
        with tab1:
            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(plot_stars_distribution(filtered_df))
            with col2:
                st.plotly_chart(plot_completion_heatmap(filtered_df))
        
        with tab2:
            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(plot_completion_rate(filtered_df))
            with col2:
                st.plotly_chart(plot_points_vs_days(filtered_df))
        
        with tab3:
            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(plot_campus_progress(filtered_df))
            with col2:
                st.plotly_chart(plot_points_distribution(filtered_df))
        
        # Detailed Data
        st.markdown("---")
        st.subheader("🔍 Detailed Data")
        st.dataframe(filtered_df)

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