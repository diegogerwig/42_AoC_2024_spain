import pandas as pd
import numpy as np

class AOCAnalyzer:
    @staticmethod
    def generate_statistics(df):
        """Generates detailed statistics from the dataframe"""
        stats = {}
        
        # General statistics
        stats['general'] = {
            'total_users': len(df),
            'unique_campuses': df['campus'].nunique(),
            'average_points': df['points'].mean(),
            'median_points': df['points'].median(),
            'max_points': df['points'].max(),
            'average_streak': df['streak'].mean(),
            'max_streak': df['streak'].max(),
            'average_days': df['days'].mean(),
        }
        
        # Statistics by campus
        stats['by_campus'] = df.groupby('campus').agg({
            'login': 'count',
            'points': ['mean', 'median', 'max', 'min', 'std'],
            'streak': ['mean', 'max'],
            'days': ['mean', 'max']
        }).round(2)
        
        # Correlations
        stats['correlations'] = df[['points', 'streak', 'days']].corr()
        
        # Percentiles
        stats['percentiles'] = df[['points', 'streak', 'days']].quantile([0.25, 0.5, 0.75])
        
        return stats

    @staticmethod
    def get_top_users(df, n=10):
        """Returns top N users by points"""
        return df.nlargest(n, 'points')