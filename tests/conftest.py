import pytest
import pandas as pd

@pytest.fixture
def sample_data():
    return pd.DataFrame({
        'login': ['user1', 'user2', 'user3'],
        'campus': ['campus1', 'campus2', 'campus1'],
        'streak': [5, 3, 4],
        'points': [100, 50, 75],
        'days': [10, 5, 7]
    })

@pytest.fixture
def sample_stats():
    return {
        'general': {
            'total_users': 3,
            'unique_campuses': 2,
            'average_points': 75,
            'max_streak': 5
        },
        'correlations': pd.DataFrame({
            'points': [1.0, 0.8, 0.7],
            'streak': [0.8, 1.0, 0.6],
            'days': [0.7, 0.6, 1.0]
        }, index=['points', 'streak', 'days'])
    }