import pandas as pd
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error

# Define campus colors
CAMPUS_COLORS = {
    'UDZ': '#00FF00',  # Green
    'BCN': '#FFD700',  # Yellow
    'MAL': '#00FFFF',  # Cyan
    'MAD': '#FF00FF'   # Magenta
}

def calculate_daily_success_rate(df):
    """
    Calculate daily success rate for each campus based on total campus users
    Success rate = (total stars obtained in day) / (possible stars from total campus users) * 100
    """
    df = df.copy()
    current_day = datetime.now().day
    
    daily_stats = {}
    
    for campus in df['campus'].unique():
        campus_df = df[df['campus'] == campus].copy()
        total_campus_users = len(campus_df)
        days_data = []
        
        for day in range(1, current_day + 1):
            day_col = f'day_{day}'
            
            # Get users with stars for this day
            day_users = campus_df[campus_df[day_col] > 0]
            active_users = len(day_users)
            
            if total_campus_users == 0:
                continue
            
            # Count stars properly - distinguishing between 1 and 2 stars
            one_star = len(day_users[day_users[day_col] == 1])
            two_stars = len(day_users[day_users[day_col] == 2])
            total_stars = one_star + (two_stars * 2)
            possible_stars = total_campus_users * 2  # Each user can get up to 2 stars
            
            # Calculate success rate based on total possible stars
            success_rate = (total_stars / possible_stars * 100)
            
            days_data.append({
                'day': day,
                'success_rate': success_rate,
                'active_users': active_users,
                'total_users': total_campus_users,
                'one_star': one_star,
                'two_stars': two_stars,
                'total_stars': total_stars,
                'possible_stars': possible_stars
            })
        
        if days_data:
            daily_stats[campus] = pd.DataFrame(days_data)
    
    return daily_stats

def train_prediction_model(completion_data):
    """Train linear model using recent data to predict future rates"""
    X = completion_data[['day']].values
    y = completion_data['success_rate'].values
    
    # Use only recent data (last 5 days) for trend calculation
    recent_points = min(5, len(X))
    X_recent = X[-recent_points:]
    y_recent = y[-recent_points:]
    
    model = LinearRegression()
    model.fit(X_recent, y_recent)
    
    # Calculate metrics using all data
    y_pred = model.predict(X)
    r2 = r2_score(y, y_pred)
    mse = mean_squared_error(y, y_pred)
    mae = mean_absolute_error(y, y_pred)
    
    return {
        'model': model,
        'r2_score': r2,
        'rmse': np.sqrt(mse),
        'mae': mae
    }

def predict_metrics(df):
    """Predict success rates for each campus"""
    predictions = {}
    daily_stats = calculate_daily_success_rate(df)
    current_day = datetime.now().day
    
    for campus, stats_df in daily_stats.items():
        try:
            if len(stats_df) < 2:
                continue
                
            # Train model
            model_info = train_prediction_model(stats_df)
            
            # Project future rates
            future_days = np.array(range(current_day, 26)).reshape(-1, 1)
            projected_rates = model_info['model'].predict(future_days)
            
            # Cap predictions between 0 and 100
            projected_rates = np.clip(projected_rates, 0, 100)
            
            predictions[campus] = {
                'model_metrics': model_info,
                'daily_stats': stats_df,
                'projected_days': future_days.flatten(),
                'projected_rates': projected_rates
            }
            
        except Exception as e:
            print(f"Error predicting for campus {campus}: {str(e)}")
            continue
    
    return predictions

def plot_predictions(filtered_df):
    """Create visualization of daily success rates and projections"""
    current_day = datetime.now().day
    predictions = predict_metrics(filtered_df)
    
    if not predictions:
        return go.Figure()
    
    fig = go.Figure()
    
    for campus, pred in predictions.items():
        actual_data = pred['daily_stats']
        
        # Add actual success rate line
        fig.add_trace(go.Scatter(
            name=f'{campus}',
            x=actual_data['day'],
            y=actual_data['success_rate'],
            mode='lines+markers',
            line=dict(width=3, color=CAMPUS_COLORS[campus]),
            marker=dict(size=8, color=CAMPUS_COLORS[campus]),
            hovertemplate=(
                'Day %{x}<br>' +
                'Success Rate: %{y:.1f}%<br>' +
                'Active/Total: %{customdata[0]}/%{customdata[1]}<br>' +
                '2 Stars: %{customdata[2]}<br>' +
                '1 Star: %{customdata[3]}<br>' +
                'Total Stars: %{customdata[4]} / %{customdata[5]}' +
                '<extra></extra>'
            ),
            customdata=np.column_stack((
                actual_data['active_users'],
                actual_data['total_users'],
                actual_data['two_stars'],
                actual_data['one_star'],
                actual_data['total_stars'],
                actual_data['possible_stars']
            ))
        ))
        
        # Add projected rates
        fig.add_trace(go.Scatter(
            name='',
            x=pred['projected_days'],
            y=pred['projected_rates'],
            mode='lines',
            line=dict(dash='dash', color=CAMPUS_COLORS[campus]),
            hovertemplate='Day %{x:.0f}<br>Projected Rate: %{y:.1f}%<extra></extra>',
            showlegend=False
        ))

    fig.update_layout(
        title='Daily Success Rate by Campus',
        xaxis_title='December Day',
        yaxis_title='Success Rate (%)',
        template='plotly_dark',
        height=500,
        showlegend=True,
        xaxis=dict(
            tickmode='array',
            ticktext=list(range(1, 26)),
            tickvals=list(range(1, 26)),
            gridcolor='rgba(128, 128, 128, 0.2)',
            range=[0, 26]
        ),
        yaxis=dict(
            gridcolor='rgba(128, 128, 128, 0.2)',
            range=[0, 100]
        ),
        shapes=[dict(
            type='line',
            x0=current_day,
            x1=current_day,
            y0=0,
            y1=1,
            yref='paper',
            line=dict(color='rgba(255, 255, 255, 0.5)', width=2, dash='dot'),
        )],
        annotations=[dict(
            x=current_day,
            y=1.05,
            yref='paper',
            text='Today',
            showarrow=False,
            font=dict(color='rgba(255, 255, 255, 0.8)')
        )]
    )
    
    return fig

def create_prediction_metrics(filtered_df):
    """Create a DataFrame with success rate metrics"""
    predictions = predict_metrics(filtered_df)
    
    if not predictions:
        return pd.DataFrame()
    
    metrics_data = []
    for campus, pred in predictions.items():
        final_rate = pred['projected_rates'][-1]
        current_stats = pred['daily_stats'].iloc[-1]
        trend = final_rate - current_stats['success_rate']
        
        metrics_data.append({
            'Campus': campus,
            'Active / Total': f"{int(current_stats['active_users'])} / {int(current_stats['total_users'])}",
            'Success Rate': f"{current_stats['success_rate']:.1f}%",
            'Stars (2★/1★)': f"{int(current_stats['two_stars'])} / {int(current_stats['one_star'])}",
            'Total Stars': f"{int(current_stats['total_stars'])} / {int(current_stats['possible_stars'])}",
            'Dec 25 Proj.': f"{final_rate:.1f}%",
            'Trend': f"{trend:+.1f}%"
        })
    
    return pd.DataFrame(metrics_data)

def create_model_metrics(filtered_df):
    """Create a DataFrame with model evaluation metrics"""
    predictions = predict_metrics(filtered_df)
    
    if not predictions:
        return pd.DataFrame()
    
    model_data = []
    for campus, pred in predictions.items():
        model_metrics = pred['model_metrics']
        current_stats = pred['daily_stats'].iloc[-1]
        participation_rate = (current_stats['active_users'] / current_stats['total_users']) * 100
        
        model_data.append({
            'Campus': campus,
            'R² Score': f"{model_metrics['r2_score']:.3f}",
            'RMSE': f"{model_metrics['rmse']:.1f}%",
            'MAE': f"{model_metrics['mae']:.1f}%",
            'Part. Rate': f"{participation_rate:.1f}%"
        })
    
    return pd.DataFrame(model_data)