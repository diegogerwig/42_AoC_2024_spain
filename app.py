# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.scraper import AOCScraper

# Define campus color mapping
CAMPUS_COLORS = {
    'UDZ': '#98FB98',  # Pale Green
    'BCN': '#FFD700',  # Gold
    'MAL': '#00CED1',  # Turquoise
    'MAD': '#FF69B4'   # Pink
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
            'Total Gold': int(campus_data['gold_stars'].sum()),
            'Total Silver': int(campus_data['silver_stars'].sum()),
            'Completion Rate': f"{(campus_data['total_stars'].sum() / (len(campus_data) * 50)) * 100:.1f}%"
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
            'Total Gold': st.column_config.NumberColumn(width='small'),
            'Total Silver': st.column_config.NumberColumn(width='small'),
            'Completion Rate': st.column_config.Column(width='small')
        }
    )

def plot_stars_distribution(df):
    """Plot distribution of gold and silver stars"""
    fig = px.box(
        pd.melt(
            df,
            value_vars=['gold_stars', 'silver_stars'],
            var_name='star_type',
            value_name='count'
        ),
        x='star_type',
        y='count',
        color='star_type',
        points='all',
        color_discrete_map={
            'gold_stars': '#FFD700',
            'silver_stars': '#C0C0C0'
        },
        title='Stars Distribution',
        labels={
            'star_type': 'Star Type',
            'count': 'Number of Stars'
        }
    )
    
    fig.update_layout(height=500, title_x=0.5)
    return fig

def plot_points_vs_days(df):
    """Create interactive scatter plot for points vs completed days"""
    fig = px.scatter(
        df,
        x="completed_days",
        y="points",
        color="campus",
        size="total_stars",
        hover_data=["login", "gold_stars", "silver_stars"],
        color_discrete_map=CAMPUS_COLORS,
        title="Points vs Days with Stars",
        labels={
            "completed_days": "Days with Stars",
            "points": "Points",
            "campus": "Campus",
            "total_stars": "Total Stars",
            "login": "User"
        }
    )
    
    fig.update_layout(height=500, title_x=0.5)
    return fig

def plot_completion_rate(df):
    """Create completion rate visualization"""
    day_columns = [col for col in df.columns if col.startswith('day_')]
    completion_data = []
    
    for campus in df['campus'].unique():
        campus_data = df[df['campus'] == campus]
        for day in day_columns:
            day_num = int(day.split('_')[1])
            silver = (campus_data[day] >= 1).sum()
            gold = (campus_data[day] == 2).sum()
            total_users = len(campus_data)
            silver_rate = (silver / total_users) * 100
            gold_rate = (gold / total_users) * 100
            completion_data.extend([
                {'Day': day_num, 'Rate': silver_rate, 'Type': 'Silver', 'Campus': campus},
                {'Day': day_num, 'Rate': gold_rate, 'Type': 'Gold', 'Campus': campus}
            ])
    
    completion_df = pd.DataFrame(completion_data)
    
    fig = px.line(
        completion_df,
        x='Day',
        y='Rate',
        color='Campus',
        line_dash='Type',
        color_discrete_map=CAMPUS_COLORS,
        title='Daily Star Completion Rate by Campus',
        labels={
            'Day': 'Challenge Day',
            'Rate': 'Completion Rate (%)',
            'Campus': 'Campus',
            'Type': 'Star Type'
        }
    )
    
    fig.update_layout(
        height=500,
        title_x=0.5,
        xaxis=dict(tickmode='linear'),
        yaxis=dict(range=[0, 100])
    )
    
    return fig

def plot_campus_progress(df):
    """Create campus progress visualization"""
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

def plot_completion_heatmap(df):
    """Create challenge completion heatmap"""
    day_columns = [col for col in df.columns if col.startswith('day_')]
    completion_matrix = df[day_columns].values
    
    fig = go.Figure(data=go.Heatmap(
        z=completion_matrix.T,
        colorscale=[
            [0, 'white'],      # No stars
            [0.5, '#C0C0C0'],  # Silver stars
            [1, '#FFD700']     # Gold stars
        ],
        zmin=0,
        zmax=2,
        showscale=True,
        colorbar=dict(
            ticktext=['No Stars', 'Silver Star', 'Gold Stars'],
            tickvals=[0, 1, 2],
            tickmode='array'
        )
    ))
    
    fig.update_layout(
        title='Challenge Completion Status',
        xaxis_title='Participant Index',
        yaxis_title='Day',
        height=600,
        title_x=0.5
    )
    
    return fig

def plot_points_distribution(df):
    """Create points distribution visualization by campus"""
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

    # Add median line
    fig.add_hline(
        y=df['points'].median(),
        line_dash="dash",
        line_color="gray",
        annotation_text=f"Global Median: {df['points'].median():.1f}"
    )
    
    fig.update_layout(
        height=500,
        title_x=0.5,
        showlegend=False,
        xaxis_title="Campus",
        yaxis_title="Points"
    )
    
    # Personalizar el hover
    fig.update_traces(
        hovertemplate="<br>".join([
            "Campus: %{x}",
            "Points: %{y:.1f}",
            "<extra></extra>"
        ])
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

    # Streak range filter
    streak_range = st.sidebar.slider(
        "🔥 Streak Range",
        min_value=int(df["streak"].min()),
        max_value=int(df["streak"].max()),
        value=(int(df["streak"].min()), int(df["streak"].max()))
    )

    # Completed days filter
    days_range = st.sidebar.slider(
        "📅 Days with Stars",
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
        ["Points", "Gold Stars", "Silver Stars", "Total Stars", "Streak", "Days with Stars"]
    )
    sort_order = st.sidebar.radio("Order", ["Descending", "Ascending"])
    
    # Apply sorting
    sort_column = sort_by.lower().replace(" ", "_")
    ascending = sort_order == "Ascending"
    filtered_df = filtered_df.sort_values(sort_column, ascending=ascending).reset_index(drop=True)

    # Filter summary
    st.sidebar.markdown("---")
    st.sidebar.subheader("📈 Filter Summary")
    st.sidebar.write(f"Showing {len(filtered_df)} of {len(df)} users")
    
    # Reset filters button
    if st.sidebar.button("🔄 Reset All Filters"):
        st.experimental_rerun()
    
    return filtered_df

def main():
    # Page configuration
    st.set_page_config(
        page_title="💫 42 Spain Advent of Code 2024 Analysis",
        layout="wide"
    )
    
    # Header
    st.title("💫 42 Spain Advent of Code 2024 Analysis 📊")
    
    # Load data
    df = load_data()
    
    # Show campus summary
    show_campus_summary(df)
    
    # Apply filters
    filtered_df = apply_filters(df)
    
    # Show global metrics
    st.markdown("---")
    st.subheader("🎯 Global Metrics")
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Total Users", len(filtered_df))
    with col2:
        st.metric("Average Points", f"{filtered_df['points'].mean():.1f}")
    with col3:
        st.metric("Gold Stars", int(filtered_df['gold_stars'].sum()))
    with col4:
        st.metric("Silver Stars", int(filtered_df['silver_stars'].sum()))
    with col5:
        completion_rate = (filtered_df['total_stars'].sum() / (len(filtered_df) * 50)) * 100
        st.metric("Completion Rate", f"{completion_rate:.1f}%")
    
    # Display visualizations in tabs
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
            "silver_stars": st.column_config.NumberColumn(format="%d"),
            "total_stars": st.column_config.NumberColumn(format="%d")
        },
        hide_index=False,
        height=400
    )