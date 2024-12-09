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
    """Load and cache data from scraper"""
    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def _load():
        scraper = AOCScraper()
        df = scraper.scrape_data()
        return df.sort_values('points', ascending=False).reset_index(drop=True)
    return _load()

def show_campus_summary(df):
    """Display summary metrics for each campus"""
    st.subheader("📊 Campus Summary")
    
    # Calculate metrics per campus
    campus_metrics = []
    for campus in sorted(df['campus'].unique()):
        campus_data = df[df['campus'] == campus]
        metrics = {
            'Campus': campus,
            'Students': len(campus_data),
            'Avg Points': f"{campus_data['points'].mean():.1f}",
            'Max Points': f"{campus_data['points'].max():.1f}",
            'Avg Streak': f"{campus_data['streak'].mean():.1f}",
            'Max Streak': int(campus_data['streak'].max()),
            'Avg Days': f"{campus_data['completed_days'].mean():.1f}",
            'Total Gold': int(campus_data['gold_stars'].sum()),
            'Total Silver': int(campus_data['silver_stars'].sum())
        }
        campus_metrics.append(metrics)
    
    # Create metrics DataFrame and display
    metrics_df = pd.DataFrame(campus_metrics)
    st.dataframe(
        metrics_df,
        hide_index=True,
        column_config={
            'Campus': st.column_config.Column(width='small'),
            'Students': st.column_config.NumberColumn(width='small'),
            'Avg Points': st.column_config.Column(width='small'),
            'Max Points': st.column_config.Column(width='small'),
            'Avg Streak': st.column_config.Column(width='small'),
            'Max Streak': st.column_config.NumberColumn(width='small'),
            'Avg Days': st.column_config.Column(width='small'),
            'Total Gold': st.column_config.NumberColumn(width='small'),
            'Total Silver': st.column_config.NumberColumn(width='small')
        }
    )

def plot_streak_distribution(df):
    """Create interactive histogram for streak distribution"""
    fig = px.histogram(
        df,
        x="streak",
        color="campus",
        color_discrete_map=CAMPUS_COLORS,
        title="Streak Distribution by Campus",
        labels={
            "streak": "Streak",
            "count": "Number of Users",
            "campus": "Campus"
        },
        marginal="box"
    )
    
    fig.update_layout(
        height=500,
        title_x=0.5,
        barmode='overlay'
    )
    
    fig.update_traces(opacity=0.75)
    
    return fig

def plot_points_vs_days(df):
    """Create interactive scatter plot for points vs completed days"""
    fig = px.scatter(
        df,
        x="completed_days",
        y="points",
        color="campus",
        size="streak",
        hover_data=["login"],
        color_discrete_map=CAMPUS_COLORS,
        title="Points vs Completed Days by Campus",
        labels={
            "completed_days": "Completed Days",
            "points": "Points",
            "campus": "Campus",
            "streak": "Streak",
            "login": "User"
        }
    )
    
    fig.update_layout(
        height=500,
        title_x=0.5,
    )
    
    return fig

def plot_completion_rate(df):
    """Create completion rate over time visualization"""
    day_columns = [col for col in df.columns if col.startswith('day_')]
    completion_data = []
    
    for campus in df['campus'].unique():
        campus_data = df[df['campus'] == campus]
        for day in day_columns:
            day_num = int(day.split('_')[1])
            completed = (campus_data[day] > 0).sum()
            rate = (completed / len(campus_data)) * 100
            completion_data.append({
                'Day': day_num,
                'Rate': rate,
                'Campus': campus
            })
    
    completion_df = pd.DataFrame(completion_data)
    
    fig = px.line(
        completion_df,
        x='Day',
        y='Rate',
        color='Campus',
        color_discrete_map=CAMPUS_COLORS,
        title='Daily Completion Rate by Campus',
        labels={
            'Day': 'Challenge Day',
            'Rate': 'Completion Rate (%)',
            'Campus': 'Campus'
        }
    )
    
    fig.update_layout(
        height=500,
        title_x=0.5,
        xaxis=dict(tickmode='linear'),
        yaxis=dict(range=[0, 100])
    )
    
    return fig

def plot_time_investment(df):
    """Create time investment analysis plot"""
    fig = px.scatter(
        df,
        x="completed_days",
        y="points",
        color="campus",
        trendline="ols",
        color_discrete_map=CAMPUS_COLORS,
        title="Time Investment Analysis",
        labels={
            "completed_days": "Days Completed",
            "points": "Points",
            "campus": "Campus"
        }
    )
    
    fig.update_layout(
        height=500,
        title_x=0.5,
    )
    
    return fig

def plot_campus_progress(df):
    """Create campus progress visualization"""
    campus_stats = df.groupby('campus').agg({
        'points': ['mean', 'max'],
        'streak': ['mean', 'max'],
        'completed_days': ['mean', 'count']
    }).round(2)
    
    campus_stats.columns = ['avg_points', 'max_points', 'avg_streak', 
                          'max_streak', 'avg_days', 'total_users']
    campus_stats = campus_stats.reset_index()
    
    fig = go.Figure()
    
    for campus in campus_stats['campus']:
        campus_data = campus_stats[campus_stats['campus'] == campus]
        fig.add_trace(go.Scatterpolar(
            r=[
                campus_data['avg_points'].iloc[0],
                campus_data['avg_streak'].iloc[0],
                campus_data['avg_days'].iloc[0],
                campus_data['total_users'].iloc[0]
            ],
            theta=['Avg Points', 'Avg Streak', 'Avg Days', 'Total Users'],
            name=campus,
            line_color=CAMPUS_COLORS[campus]
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max(campus_stats['avg_points'].max(),
                             campus_stats['avg_streak'].max(),
                             campus_stats['avg_days'].max(),
                             campus_stats['total_users'].max())]
            )),
        showlegend=True,
        title='Campus Performance Overview',
        height=500
    )
    
    return fig

def plot_points_distribution(df):
    """Create points distribution visualization"""
    fig = px.box(
        df,
        x="campus",
        y="points",
        color="campus",
        points="all",
        color_discrete_map=CAMPUS_COLORS,
        title="Points Distribution by Campus",
        labels={
            "campus": "Campus",
            "points": "Points"
        }
    )
    
    fig.update_layout(
        height=500,
        title_x=0.5,
    )
    
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
        min_value=int(df["points"].min()),
        max_value=int(df["points"].max()),
        value=(int(df["points"].min()), int(df["points"].max()))
    )
    
    # Streak range filter
    streak_range = st.sidebar.slider(
        "🔥 Streak Range",
        min_value=int(df["streak"].min()),
        max_value=int(df["streak"].max()),
        value=(int(df["streak"].min()), int(df["streak"].max()))
    )

    # Completed days filter
    days_range = st.sidebar.slider(
        "📅 Completed Days Range",
        min_value=int(df["completed_days"].min()),
        max_value=int(df["completed_days"].max()),
        value=(int(df["completed_days"].min()), int(df["completed_days"].max()))
    )

    # Gold stars filter
    gold_range = st.sidebar.slider(
        "⭐ Gold Stars Range",
        min_value=int(df["gold_stars"].min()),
        max_value=int(df["gold_stars"].max()),
        value=(int(df["gold_stars"].min()), int(df["gold_stars"].max()))
    )

    # Silver stars filter
    silver_range = st.sidebar.slider(
        "🌟 Silver Stars Range",
        min_value=int(df["silver_stars"].min()),
        max_value=int(df["silver_stars"].max()),
        value=(int(df["silver_stars"].min()), int(df["silver_stars"].max()))
    )

    # Search by login
    search_login = st.sidebar.text_input("🔍 Search by Login").strip().lower()

    # Sort options
    st.sidebar.subheader("📊 Sort Options")
    sort_by = st.sidebar.selectbox(
        "Sort by",
        ["Points", "Streak", "Completed Days", "Gold Stars", "Silver Stars"]
    )
    sort_order = st.sidebar.radio(
        "Order",
        ["Descending", "Ascending"]
    )

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

    # Apply sorting
    sort_column = sort_by.lower().replace(" ", "_")
    ascending = sort_order == "Ascending"
    filtered_df = filtered_df.sort_values(sort_column, ascending=ascending).reset_index(drop=True)

    # Add filter summary to sidebar
    st.sidebar.markdown("---")
    st.sidebar.subheader("📈 Filter Summary")
    st.sidebar.write(f"Showing {len(filtered_df)} of {len(df)} users")
    if len(filtered_df) < len(df):
        st.sidebar.write("Active filters:")
        if selected_campus != "All":
            st.sidebar.write(f"• Campus: {selected_campus}")
        if search_login:
            st.sidebar.write(f"• Login search: {search_login}")
        if points_range != (df["points"].min(), df["points"].max()):
            st.sidebar.write(f"• Points filter active")
        if streak_range != (df["streak"].min(), df["streak"].max()):
            st.sidebar.write(f"• Streak filter active")
        if days_range != (df["completed_days"].min(), df["completed_days"].max()):
            st.sidebar.write(f"• Days filter active")
        if gold_range != (df["gold_stars"].min(), df["gold_stars"].max()):
            st.sidebar.write(f"• Gold stars filter active")
        if silver_range != (df["silver_stars"].min(), df["silver_stars"].max()):
            st.sidebar.write(f"• Silver stars filter active")

    # Reset filters button
    if st.sidebar.button("🔄 Reset All Filters"):
        st.experimental_rerun()
    
    return filtered_df

def create_header():
    """Create header with logo and title"""
    col1, col2 = st.columns([1, 4])
    
    with col1:
        try:
            with open("img/42_logo.svg", "r") as f:
                svg_content = f.read().strip()
            st.markdown(f'<div style="padding: 10px;"><style>svg {{ width: 100px; height: auto; }} svg path, svg * {{ fill: white !important; stroke: white !important; }}</style>{svg_content}</div>', unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error loading logo: {str(e)}")
    
    with col2:
        st.title("💫 42 Spain Advent of Code 2024 Analysis 📊")

def main():
    # Page configuration
    st.set_page_config(
        page_title="💫 42 Spain Advent of Code 2024 Analysis",
        layout="wide"
    )
    
    # Header
    create_header()
    
    # Load data
    df = load_data()
    
    # Show campus summary
    show_campus_summary(df)
    
    # Apply filters
    filtered_df = apply_filters(df)
    
    # Show global metrics
    st.markdown("---")
    st.subheader("🎯 Global Metrics")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Users", len(filtered_df))
    with col2:
        st.metric("Average Points", f"{filtered_df['points'].mean():.1f}")
    with col3:
        st.metric("Max Streak", int(filtered_df['streak'].max()))
    with col4:
        st.metric("Average Days Completed", f"{filtered_df['completed_days'].mean():.1f}")
    
    # Display visualizations in tabs
    st.markdown("---")
    tab1, tab2, tab3 = st.tabs(["📈 Main Metrics", "🌟 Progress Analysis", "📊 Campus Comparison"])
    
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            try:
                st.plotly_chart(plot_streak_distribution(filtered_df), use_container_width=True)
            except Exception as e:
                st.error(f"Error in streak distribution: {e}")
        with col2:
            try:
                st.plotly_chart(plot_points_vs_days(filtered_df), use_container_width=True)
            except Exception as e:
                st.error(f"Error in points vs days: {e}")
    
    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            try:
                st.plotly_chart(plot_completion_rate(filtered_df), use_container_width=True)
            except Exception as e:
                st.error(f"Error in completion rate: {e}")
        with col2:
            try:
                st.plotly_chart(plot_time_investment(filtered_df), use_container_width=True)
            except Exception as e:
                st.error(f"Error in time investment: {e}")
    
    with tab3:
        col1, col2 = st.columns(2)
        with col1:
            try:
                st.plotly_chart(plot_campus_progress(filtered_df), use_container_width=True)
            except Exception as e:
                st.error(f"Error in campus progress: {e}")
        with col2:
            try:
                st.plotly_chart(plot_points_distribution(filtered_df), use_container_width=True)
            except Exception as e:
                st.error(f"Error in points distribution: {e}")
            
    # Show filtered data table
    st.markdown("---")
    st.subheader("🔍 Detailed Data")
    st.dataframe(
        filtered_df,
        column_config={
            "points": st.column_config.NumberColumn(format="%.1f"),
            "streak": st.column_config.NumberColumn(format="%d"),
            "completed_days": st.column_config.NumberColumn(format="%d"),
            "gold_stars": st.column_config.NumberColumn(format="%d"),
            "silver_stars": st.column_config.NumberColumn(format="%d")
        },
        hide_index=False,
        height=400
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

if __name__ == "__main__":
    main()