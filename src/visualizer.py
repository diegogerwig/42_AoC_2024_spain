import matplotlib.pyplot as plt
import seaborn as sns
from typing import Optional, Tuple, Union, List
import pandas as pd
import numpy as np
from matplotlib.figure import Figure
import plotly.graph_objects as go

class AOCVisualizer:
    """Class for visualizing Advent of Code participation data."""

    def __init__(self, data: pd.DataFrame):
        """
        Initialize the visualizer with participant data.

        Args:
            data (pd.DataFrame): DataFrame containing AOC participant data
        """
        self._validate_data(data)
        self.data = data
        self.campus_colors = {
            'MAD': '#FF69B4',  # Pink
            'BCN': '#FFD700',  # Gold
            'MAL': '#00CED1',  # Turquoise
            'UDZ': '#98FB98'   # Pale Green
        }

    def _validate_data(self, data: pd.DataFrame) -> None:
        """Validate input data has required columns."""
        required_columns = {'points', 'streak', 'completed_days', 'login', 'campus'}
        missing_columns = required_columns - set(data.columns)
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")

    def plot_points_distribution(self, figsize: Tuple[int, int] = (10, 6)) -> Optional[Figure]:
        """Create a histogram showing the distribution of points."""
        try:
            plt.figure(figsize=figsize)
            sns.histplot(
                data=self.data, 
                x='points', 
                bins=30,
                color='skyblue',
                edgecolor='black',
                hue='campus',
                palette=self.campus_colors
            )
            plt.title('Distribution of Points by Campus', pad=20)
            plt.xlabel('Points')
            plt.ylabel('Count')
            plt.grid(True, alpha=0.3)
            return plt.gcf()
        except Exception as e:
            print(f"Error plotting points distribution: {str(e)}")
            return None

    def plot_streak_distribution(self, figsize: Tuple[int, int] = (10, 6)) -> Optional[Figure]:
        """Create a histogram showing the distribution of participant streaks."""
        try:
            plt.figure(figsize=figsize)
            sns.histplot(
                data=self.data, 
                x='streak', 
                bins=30,
                hue='campus',
                palette=self.campus_colors,
                edgecolor='black'
            )
            plt.title('Distribution of Streaks by Campus', pad=20)
            plt.xlabel('Streak')
            plt.ylabel('Count')
            plt.grid(True, alpha=0.3)
            return plt.gcf()
        except Exception as e:
            print(f"Error plotting streak distribution: {str(e)}")
            return None

    def plot_points_vs_days(self, figsize: Tuple[int, int] = (10, 6)) -> Optional[Figure]:
        """Create a scatter plot comparing points earned versus days completed."""
        try:
            plt.figure(figsize=figsize)
            sns.scatterplot(
                data=self.data, 
                x='completed_days', 
                y='points',
                hue='campus',
                palette=self.campus_colors,
                size='streak',
                sizes=(50, 200),
                alpha=0.6
            )
            plt.title('Points vs Days Completed by Campus', pad=20)
            plt.xlabel('Days Completed')
            plt.ylabel('Points')
            plt.grid(True, alpha=0.3)
            return plt.gcf()
        except Exception as e:
            print(f"Error plotting points vs days: {str(e)}")
            return None

    def plot_top_users(self, n: int = 10, figsize: Tuple[int, int] = (12, 6)) -> Optional[Figure]:
        """Create a bar plot showing the top N users by points."""
        try:
            if n <= 0:
                raise ValueError("Number of users must be positive")
            if n > len(self.data):
                n = len(self.data)

            top_users = self.data.nlargest(n, 'points')
            plt.figure(figsize=figsize)
            sns.barplot(
                data=top_users, 
                x='login', 
                y='points',
                hue='campus',
                palette=self.campus_colors
            )
            plt.title(f'Top {n} Users by Points', pad=20)
            plt.xticks(rotation=45, ha='right')
            plt.grid(True, alpha=0.3, axis='y')
            plt.tight_layout()
            return plt.gcf()
        except Exception as e:
            print(f"Error plotting top users: {str(e)}")
            return None

    def plot_campus_comparison(self, figsize: Tuple[int, int] = (12, 6)) -> Optional[Figure]:
        """Create a box plot comparing points across campuses."""
        try:
            plt.figure(figsize=figsize)
            sns.boxplot(
                data=self.data,
                x='campus',
                y='points',
                palette=self.campus_colors
            )
            plt.title('Points Distribution by Campus', pad=20)
            plt.xlabel('Campus')
            plt.ylabel('Points')
            plt.grid(True, alpha=0.3)
            return plt.gcf()
        except Exception as e:
            print(f"Error plotting campus comparison: {str(e)}")
            return None

    def plot_completion_heatmap(self, figsize: Tuple[int, int] = (15, 8)) -> Optional[Figure]:
        """Create a heatmap showing completion patterns for each day."""
        try:
            day_columns = [col for col in self.data.columns if col.startswith('day_')]
            completion_data = self.data[day_columns].copy()
            
            plt.figure(figsize=figsize)
            sns.heatmap(
                completion_data.T,
                cmap='YlOrRd',
                cbar_kws={'label': 'Completion Status'}
            )
            plt.title('Challenge Completion Heatmap', pad=20)
            plt.xlabel('Participant Index')
            plt.ylabel('Day')
            return plt.gcf()
        except Exception as e:
            print(f"Error plotting completion heatmap: {str(e)}")
            return None

    def plot_daily_completion_rate(self, figsize: Tuple[int, int] = (12, 6)) -> Optional[Figure]:
        """Plot the completion rate for each day."""
        try:
            day_columns = [col for col in self.data.columns if col.startswith('day_')]
            completion_rates = []
            
            for day in day_columns:
                completed = (self.data[day] > 0).sum()
                rate = (completed / len(self.data)) * 100
                completion_rates.append(rate)
            
            plt.figure(figsize=figsize)
            plt.plot(range(1, len(day_columns) + 1), completion_rates, 'o-', linewidth=2)
            plt.title('Daily Challenge Completion Rate', pad=20)
            plt.xlabel('Day')
            plt.ylabel('Completion Rate (%)')
            plt.grid(True, alpha=0.3)
            plt.xticks(range(1, len(day_columns) + 1))
            return plt.gcf()
        except Exception as e:
            print(f"Error plotting daily completion rate: {str(e)}")
            return None

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
        
        # Define default color for unknown campus
        default_color = '#808080'  # Gray
        
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
                line_color=CAMPUS_COLORS.get(campus, default_color)  # Use default color if campus not found
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

    def plot_time_investment(self, figsize: Tuple[int, int] = (10, 6)) -> Optional[Figure]:
        """Plot the relationship between time investment (completed days) and points."""
        try:
            plt.figure(figsize=figsize)
            sns.regplot(
                data=self.data,
                x='completed_days',
                y='points',
                scatter_kws={'alpha': 0.5},
                line_kws={'color': 'red'}
            )
            plt.title('Time Investment vs Points', pad=20)
            plt.xlabel('Days Completed')
            plt.ylabel('Points')
            plt.grid(True, alpha=0.3)
            return plt.gcf()
        except Exception as e:
            print(f"Error plotting time investment: {str(e)}")
            return None

    def close_all_plots(self) -> None:
        """Close all open matplotlib plots to free memory."""
        plt.close('all')