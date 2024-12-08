import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.scraper import AOCScraper
from src.analyzer import AOCAnalyzer

# Define campus color mapping
CAMPUS_COLORS = {
    'URD': '#00FF00',  # Green
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

def apply_filters(df):
    """Apply user-selected filters to the dataframe"""
    st.sidebar.header("Filters")
    
    # Campus filter
    campus_options = ["All"] + sorted(df["campus"].unique().tolist())
    selected_campus = st.sidebar.selectbox("Select Campus", campus_options)
    
    # Points range filter
    points_range = st.sidebar.slider(
        "Points Range",
        min_value=int(df["points"].min()),
        max_value=int(df["points"].max()),
        value=(int(df["points"].min()), int(df["points"].max()))
    )
    
    # Streak range filter
    streak_range = st.sidebar.slider(
        "Streak Range",
        min_value=int(df["streak"].min()),
        max_value=int(df["streak"].max()),
        value=(int(df["streak"].min()), int(df["streak"].max()))
    )
    
    # Apply filters
    mask = (
        (df["points"].between(points_range[0], points_range[1])) &
        (df["streak"].between(streak_range[0], streak_range[1]))
    )
    
    if selected_campus != "All":
        mask = mask & (df["campus"] == selected_campus)
    
    filtered_df = df[mask].copy()
    return filtered_df.sort_values('points', ascending=False).reset_index(drop=True)

def plot_points_vs_days(df):
    """Create interactive scatter plot"""
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

def plot_points_distribution(df):
    """Create interactive box plot"""
    fig = px.box(
        df,
        x="campus",
        y="points",
        points="all",
        color="campus",
        color_discrete_map=CAMPUS_COLORS,
        hover_data=["login"],
        title="Points Distribution by Campus",
        labels={
            "campus": "Campus",
            "points": "Points",
            "login": "User"
        }
    )
    
    fig.update_layout(
        height=500,
        title_x=0.5,
    )
    
    return fig

def plot_streak_distribution(df):
    """Create interactive histogram"""
    fig = px.histogram(
        df,
        x="streak",
        color="campus",
        color_discrete_map=CAMPUS_COLORS,
        title="Streak Distribution",
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

def show_metrics(df):
    """Display key metrics"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Users", len(df))
    with col2:
        st.metric("Average Points", f"{df['points'].mean():.1f}")
    with col3:
        st.metric("Max Streak", int(df['streak'].max()))
    with col4:
        st.metric("Average Completed Days", f"{df['completed_days'].mean():.1f}")

def show_debug_info(df):
    """Display debug information in sidebar"""
    st.sidebar.write("Debug Information:")
    st.sidebar.write(f"Total records: {len(df)}")
    st.sidebar.write(f"Available columns: {df.columns.tolist()}")
    st.sidebar.write("Data sample:")
    st.sidebar.dataframe(
        df[['login', 'points', 'completed_days', 'gold_stars', 'silver_stars']].head(),
        height=200
    )

def main():
    # Page configuration
    st.set_page_config(
        page_title="💫 42 Spain Advent of Code 2024 Analysis",
        layout="wide"
    )
    
    # Title
    st.title("💫 42 Spain Advent of Code 2024 Analysis 📊")
    
    # Load data
    df = load_data()
    
    # Show debug information
    # show_debug_info(df)
    
    # Apply filters
    filtered_df = apply_filters(df)
    
    # Show metrics
    show_metrics(filtered_df)
    
    # Display visualizations in a grid
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(plot_streak_distribution(filtered_df), use_container_width=True)
    
    with col2:
        st.plotly_chart(plot_points_vs_days(filtered_df), use_container_width=True)
    
    # Show points distribution
    st.plotly_chart(plot_points_distribution(filtered_df), use_container_width=True)
    
    # Show filtered data table
    st.header("Filtered Data")
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