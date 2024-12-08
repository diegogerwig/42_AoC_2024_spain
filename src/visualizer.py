import matplotlib.pyplot as plt
import seaborn as sns
from typing import Optional
import pandas as pd

class AOCVisualizer:
    """Visualizer for AOC data analysis."""

    def __init__(self, data: pd.DataFrame):
        """Initialize visualizer with data."""
        self.data = data

    def plot_points_distribution(self, figsize=(10, 6)) -> Optional[plt.Figure]:
        """Plot distribution of points."""
        try:
            plt.figure(figsize=figsize)
            sns.histplot(data=self.data, x='points', bins=30)
            plt.title('Distribution of Points')
            plt.xlabel('Points')
            plt.ylabel('Count')
            return plt.gcf()
        except Exception as e:
            print(f"Error plotting points distribution: {e}")
            return None

    def plot_streak_distribution(self, figsize=(10, 6)) -> Optional[plt.Figure]:
        """Plot distribution of streaks."""
        try:
            plt.figure(figsize=figsize)
            sns.histplot(data=self.data, x='streak', bins=30)
            plt.title('Distribution of Streaks')
            plt.xlabel('Streak')
            plt.ylabel('Count')
            return plt.gcf()
        except Exception as e:
            print(f"Error plotting streak distribution: {e}")
            return None

    def plot_points_vs_days(self, figsize=(10, 6)) -> Optional[plt.Figure]:
        """Plot points vs days completed."""
        try:
            plt.figure(figsize=figsize)
            sns.scatterplot(data=self.data, x='completed_days', y='points')
            plt.title('Points vs Days Completed')
            plt.xlabel('Days Completed')
            plt.ylabel('Points')
            return plt.gcf()
        except Exception as e:
            print(f"Error plotting points vs days: {e}")
            return None

    def plot_top_users(self, n=10, figsize=(12, 6)) -> Optional[plt.Figure]:
        """Plot top N users by points."""
        try:
            top_users = self.data.nlargest(n, 'points')
            plt.figure(figsize=figsize)
            sns.barplot(data=top_users, x='login', y='points')
            plt.title(f'Top {n} Users by Points')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            return plt.gcf()
        except Exception as e:
            print(f"Error plotting top users: {e}")
            return None