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


def create_metrics_dataframe(df, is_global=True):
    """Create a formatted dataframe for metrics"""
    if is_global:
        data = {
            'Section': ['🌍 Global'],
            'Students': [len(df)],
            'Points (Avg/Max)': [f"{df['points'].mean():.1f}/{df['points'].max():.1f}"],
            'Streak (Avg/Max)': [f"{df['streak'].mean():.1f}/{df['streak'].max()}"],
            'Stars (Gold/Silver)': [f"{int(df['gold_stars'].sum())}/{int(df['silver_stars'].sum())}"],
            'Completion Rate': [f"{(df['total_stars'].sum() / (len(df) * 50)) * 100:.1f}%"]
        }
    else:
        data = []
        for campus in sorted(df['campus'].unique()):
            campus_data = df[df['campus'] == campus]
            data.append({
                'Section': f"🏛️ {campus}",
                'Students': len(campus_data),
                'Points (Avg/Max)': f"{campus_data['points'].mean():.1f}/{campus_data['points'].max():.1f}",
                'Streak (Avg/Max)': f"{campus_data['streak'].mean():.1f}/{campus_data['streak'].max()}",
                'Stars (Gold/Silver)': f"{int(campus_data['gold_stars'].sum())}/{int(campus_data['silver_stars'].sum())}",
                'Completion Rate': f"{(campus_data['total_stars'].sum() / (len(campus_data) * 50)) * 100:.1f}%"
            })
    return pd.DataFrame(data)

def main():
    st.set_page_config(page_title="42 Spain AoC 2024 Dashboard", layout="wide")
    
    st.title("💫 42 Spain Advent of Code 2024 Dashboard")
    
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