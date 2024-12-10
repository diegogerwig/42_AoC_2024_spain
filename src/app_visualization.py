import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Define campus color mapping
CAMPUS_COLORS = {
    'UDZ': '#00FF00',  # Green
    'BCN': '#FFD700',  # Yellow
    'MAL': '#00FFFF',  # Cyan
    'MAD': '#FF00FF'   # Magenta
}


# Define common styling
def apply_common_style(fig):
    """Apply common styling to all plots"""
    dark_gray = '#2F2F2F'
    
    fig.update_layout(
        plot_bgcolor=dark_gray,
        paper_bgcolor=dark_gray,
        font=dict(color='white'),
        margin=dict(l=60, r=60, t=80, b=60),
        legend=dict(bgcolor=dark_gray),
        height=500,
        title=dict(
            x=0.5,
            y=0.95,
            xanchor='center',
            yanchor='top',
            font=dict(
                size=24
            )
        ),
        xaxis=dict(
            gridcolor='rgba(255,255,255,0.1)',
            zerolinecolor='rgba(255,255,255,0.2)'
        ),
        yaxis=dict(
            gridcolor='rgba(255,255,255,0.1)',
            zerolinecolor='rgba(255,255,255,0.2)',
            rangemode='nonnegative',  # Force y-axis to start at 0
            range=[0, None]  # Explicitly set minimum to 0
        )
    )
    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,255,255,0.1)')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,255,255,0.1)')
    
    return fig


def plot_stars_distribution(df):
    """Plot distribution of gold and silver stars"""
    melted_df = pd.melt(
        df,
        value_vars=['gold_stars', 'silver_stars'],
        var_name='star_type',
        value_name='count'
    )
    melted_df['star_type'] = pd.Categorical(melted_df['star_type'])
    
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
        title='Stars Distribution',
        category_orders={"star_type": ["gold_stars", "silver_stars"]}
    )
    
    fig = apply_common_style(fig)
    fig.update_layout(showlegend=False)  # Remove legend
    
    return fig


def plot_star_totals_by_campus(df):
    """Create a line chart that shows the total number of stars per day for each campus and total."""
    current_day = len([col for col in df.columns if col.startswith('day_')])
    day_columns = [f'day_{i}' for i in range(1, current_day + 1)]
    
    stars_data = []
    
    for campus in df['campus'].unique():
        campus_mask = df['campus'] == campus
        for day in day_columns:
            day_num = int(day.split('_')[1])
            total_stars = df[campus_mask][day].sum()
            stars_data.append({
                'Day': day_num,
                'Stars': total_stars,
                'Campus': campus
            })
    
    for day in day_columns:
        day_num = int(day.split('_')[1])
        total_stars = df[day].sum()
        stars_data.append({
            'Day': day_num,
            'Stars': total_stars,
            'Campus': 'ALL'
        })
    
    stars_df = pd.DataFrame(stars_data)
    
    colors = CAMPUS_COLORS.copy()
    colors['ALL'] = '#FFFFFF'
    
    fig = px.line(
        stars_df,
        x='Day',
        y='Stars',
        color='Campus',
        title='Total Stars by Campus per Day',
        labels={'Stars': 'Number of Stars'},
        color_discrete_map=colors
    )
    
    for trace in fig.data:
        if trace.name == 'ALL':
            trace.line.width = 4
            trace.line.dash = None
    
    fig = apply_common_style(fig)
    fig.update_layout(yaxis=dict(rangemode='nonnegative'))

    return fig


def plot_success_rate(df):
    """Plot success rate over time by campus"""
    current_day = len([col for col in df.columns if col.startswith('day_')])
    day_columns = [f'day_{i}' for i in range(1, current_day + 1)]
    success_data = []
    
    for campus in df['campus'].unique():
        campus_mask = df['campus'] == campus
        for day in day_columns:
            day_num = int(day.split('_')[1])
            success = (df[campus_mask][day] > 0).sum() / campus_mask.sum() * 100
            success_data.append({
                'Day': day_num,
                'Rate': success,
                'Campus': campus
            })
    
    success_df = pd.DataFrame(success_data)
    
    fig = px.line(
        success_df,
        x='Day',
        y='Rate',
        color='Campus',
        title='Daily Success Rate by Campus',
        labels={'Rate': 'Success Rate (%)'},
        color_discrete_map=CAMPUS_COLORS
    )
    
    return apply_common_style(fig)


def plot_points_vs_days(df):
    """Create scatter plot of points vs completed days"""
    df = df.copy()
    df['campus'] = pd.Categorical(df['campus'])
    
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
    
    return apply_common_style(fig)


def plot_campus_progress(df):
    """Create a clean trend visualization focusing on key metrics"""
    # Calculate weekly averages to reduce noise
    current_day = len([col for col in df.columns if col.startswith('day_')])
    days = list(range(1, current_day + 1))
    
    trend_data = []
    
    for campus in df['campus'].unique():
        campus_data = df[df['campus'] == campus]
        
        # Calculate average points for each day
        for day in days:
            day_col = f'day_{day}'
            avg_points = campus_data[day_col].mean()
            
            trend_data.append({
                'Campus': campus,
                'Day': day,
                'Average_Points': avg_points
            })
    
    trend_df = pd.DataFrame(trend_data)
    
    # Create the plot
    fig = px.line(
        trend_df,
        x='Day',
        y='Average_Points',
        color='Campus',
        title='Campus Progress Over Time',
        labels={'Average_Points': 'Average Points per Student'},
        color_discrete_map=CAMPUS_COLORS
    )
    
    # Apply styling
    fig = apply_common_style(fig)
    
    # Additional customization for clarity
    fig.update_layout(
        # More space between elements
        margin=dict(l=80, r=80, t=100, b=80),
        
        # Improve legend positioning
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='center',
            x=0.5
        ),
        
        # Additional styling
        yaxis_title='Average Points',
        xaxis_title='Day Number',
        hovermode='x unified'
    )
    
    # Make lines thicker for better visibility
    fig.update_traces(
        line=dict(width=3),
        mode='lines'  # Remove markers for cleaner look
    )
    
    return fig


def plot_points_distribution(df):
    """Create box plot of points distribution by campus"""
    df = df.copy()
    df['campus'] = pd.Categorical(df['campus'])
    
    fig = px.box(
        df,
        x="campus",
        y="points",
        color="campus",
        points="all",
        title="Points Distribution by Campus",
        color_discrete_map=CAMPUS_COLORS
    )
    
    fig = apply_common_style(fig)
    
    fig.add_hline(
        y=df['points'].median(),
        line_dash="dash",
        line_color="white",
        annotation=dict(
            text=f"Global Median: {df['points'].median():.1f}",
            font=dict(color="white")
        )
    )
    
    fig.update_layout(showlegend=False)
    return fig